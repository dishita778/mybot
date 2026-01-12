rom flask import Flask, request, jsonify
from flask_cors import CORS
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
from connect_memory_with_llm import run_query
import os
import sys
import re
import secrets
import traceback

from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings

from google import genai

from auth_routes import auth_bp


venv_path = os.environ.get("VIRTUAL_ENV")
if venv_path and venv_path in sys.path:
    sys.path.remove(venv_path)

print(secrets.token_hex(16))
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")
CORS(app)
app.register_blueprint(auth_bp, url_prefix="")


client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


DB_FAISS_PATH = "vectorstore/db_faiss"
MH_FAISS_PATH = "vectorstore/mental_health_db_faiss"

LANGUAGE_OPTIONS = {
    "English": "en", "Hindi": "hi", "Gujarati": "gu", "Marathi": "mr",
    "Spanish": "es", "French": "fr", "German": "de", "Chinese": "zh-cn",
    "Japanese": "ja", "Arabic": "ar", "Tamil": "ta", "Telugu": "te",
    "Bengali": "bn", "Kannada": "kn", "Malayalam": "ml", "Punjabi": "pa",
    "Assamese": "as"
}

_vectorstores = {}

def load_vectorstore(path):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return FAISS.load_local(
        path,
        embeddings,
        allow_dangerous_deserialization=True
    )

def get_vectorstore(domain):
    if domain not in _vectorstores:
        path = MH_FAISS_PATH if domain == "mental_health" else DB_FAISS_PATH
        _vectorstores[domain] = load_vectorstore(path)
    return _vectorstores[domain]


def set_custom_prompt():
    return PromptTemplate(
        template="""Use the provided context to answer the user's question in a structured way.
If you don't know the answer, say "I don't know".

Use numbered points and bullet formatting.

Context:
{context}

Question:
{question}

Response:""",
        input_variables=["context", "question"]
    )


def detect_gibberish(text):
    if not text.strip():
        return True
    words = text.lower().split()
    most_common = max(words.count(w) for w in set(words))
    return most_common > len(words) * 0.4

def format_response(text):
    return text.strip()


@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        query = data.get("query", "").strip()
        language = data.get("language", "English")
        domain = data.get("domain", "medical").lower()

        if not query:
            return jsonify({"error": "Query is required"}), 400

 
        vectorstore = get_vectorstore(domain)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        docs = retriever.get_relevant_documents(query)

        context = (
            "\n\n".join(doc.page_content for doc in docs)
            if docs else "No relevant context found."
        )


        mental_health_keywords = [
            "anxiety", "stress", "depression", "panic",
            "overwhelmed", "sad", "mental", "worry", "suicidal"
        ]

        if domain == "medical" and any(k in query.lower() for k in mental_health_keywords):
            return jsonify({
                "response": (
                    "It looks like this may be a mental health concern. "
                    "Please switch to **Mental Health Mode** so I can help you better 💙"
                )
            })

        if domain == "mental_health":
            prompt = f"""
You are a compassionate and empathetic mental health assistant.

Respond with empathy and gentle guidance.

Context:
{context}

Question:
{query}

Response:
"""
        else:
            prompt = set_custom_prompt().format(
                context=context,
                question=query
            )

        
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            result = response.text
        except Exception as llm_error:
            print("Gemini error:", llm_error)
            return jsonify({
                "response": "AI model is temporarily unavailable. Please try again."
            })

        if detect_gibberish(result):
            result = "I don't know."

        formatted = format_response(result)
        translated = GoogleTranslator(
            source="auto",
            target=LANGUAGE_OPTIONS.get(language, "en")
        ).translate(formatted)

        return jsonify({"response": translated})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"error": "Invalid input"}), 400

    try:
        response = run_query(
            data["message"],
            selected_domain=data.get("domain", "medical")
        )
        return jsonify({"reply": response})
    except Exception:
        traceback.print_exc()
        return jsonify({"reply": "Something went wrong."})


@app.route("/")
def home():
    return "Flask backend is running with Gemini!"



if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=5000)

