
import os
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate


genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


MEDICAL_DB_FAISS_PATH = "vectorstore/db_faiss"
MENTAL_HEALTH_DB_FAISS_PATH = "vectorstore/mental_health_db_faiss"

# Prompt Template
CUSTOM_PROMPT_TEMPLATE = """
Use the provided context to answer the user's question in a structured way.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Don't provide anything out of the given context.

    **Format the response as follows:**  
    - Use **numbered main points** (1., 2., 3.)  

    **Example Response:**  
    1. Main Topic in Bold
       - Supporting detail 1
       - Supporting detail 2
       - Important term: Explanation

    2. Another Main Topic in Bold
       - Supporting detail 1
       - Supporting detail 2
    **Context:** {context}  
    **Question:** {question}  

    **Response:**"""

def load_llm():
    return genai.GenerativeModel("gemini-2.5-flash-preview-04-17")

def run_query(query, selected_domain="medical"):
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db_path = MENTAL_HEALTH_DB_FAISS_PATH if selected_domain == "mental_health" else MEDICAL_DB_FAISS_PATH
    db = FAISS.load_local(db_path, embedding_model, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_kwargs={'k': 3})
    docs = retriever.get_relevant_documents(query)
    context = "\n\n".join(doc.page_content for doc in docs)
    prompt = CUSTOM_PROMPT_TEMPLATE.format(context=context, question=query)
    model = load_llm()
    response = model.generate_content(prompt)
    return {
         "result": response,
      }
