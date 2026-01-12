
import os
import traceback
from dotenv import load_dotenv
from google import genai
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate


load_dotenv()


_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set in environment")
        _client = genai.Client(api_key=api_key)
    return _client



MEDICAL_DB_FAISS_PATH = "vectorstore/db_faiss"
MENTAL_HEALTH_DB_FAISS_PATH = "vectorstore/mental_health_db_faiss"


CUSTOM_PROMPT_TEMPLATE = """
Use the provided context to answer the user's question in a structured way.
If you don't know the answer, just say that you don't know.

Context:
{context}

Question:
{question}

Response:
"""

PROMPT = PromptTemplate(
    template=CUSTOM_PROMPT_TEMPLATE,
    input_variables=["context", "question"]
)
_vectorstores = {}

def get_vectorstore(domain):
    if domain not in _vectorstores:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        path = (
            MENTAL_HEALTH_DB_FAISS_PATH
            if domain == "mental_health"
            else MEDICAL_DB_FAISS_PATH
        )
        _vectorstores[domain] = FAISS.load_local(
            path,
            embeddings,
            allow_dangerous_deserialization=True
        )
    return _vectorstores[domain]


def run_query(query, selected_domain="medical"):
    try:
      
        db = get_vectorstore(selected_domain)
        retriever = db.as_retriever(search_kwargs={"k": 3})
        docs = retriever.get_relevant_documents(query)

        context = (
            "\n\n".join(doc.page_content for doc in docs)
            if docs else "No relevant context found."
        )

        prompt = PROMPT.format(
            context=context,
            question=query
        )

        client = get_client()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        return {
            "result": response.text
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "result": "Something went wrong while processing your request."
        }
