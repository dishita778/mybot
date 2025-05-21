# from flask import Flask, request, jsonify, session
# from flask_cors import CORS
# from deep_translator import GoogleTranslator
# from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
# from langchain.chains import RetrievalQA
# from langchain_community.vectorstores import FAISS
# from langchain_core.prompts import PromptTemplate
# from dotenv import load_dotenv
# from connect_memory_with_llm import run_query
# # from auth_routes import auth_bp
# import os
# import sys
# import time
# import re
# import secrets

# # Ignore changes in venv for reloader
# venv_path = os.environ.get("VIRTUAL_ENV")
# if venv_path and venv_path in sys.path:
#     sys.path.remove(venv_path)

# # Generate random secret key (one-time print)
# print(secrets.token_hex(16))

# # Load environment variables
# load_dotenv()

# # Initialize app
# app = Flask(__name__)
# app.secret_key = "1690ec0701e8a05f6de538bfe58803ad"
# CORS(app)
# # app.register_blueprint(auth_bp, url_prefix="")

# # Constants
# DB_FAISS_PATH = "vectorstore/db_faiss"               # Medical Vector DB
# MH_FAISS_PATH = "vectorstore/mental_health_db_faiss"        # Mental Health Vector DB
# LANGUAGE_OPTIONS = {
#     "English": "en", "Hindi": "hi", "Gujarati": "gu", "Marathi": "mr",
#     "Spanish": "es", "French": "fr", "German": "de", "Chinese": "zh-cn",
#     "Japanese": "ja", "Arabic": "ar", "Tamil": "ta", "Telugu": "te",
#     "Bengali": "bn", "Kannada": "kn", "Malayalam": "ml", "Punjabi": "pa",
#     "Assamese": "as"
# }

# # Load vector store from FAISS
# def load_vectorstore(path):
#     embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
#     return FAISS.load_local(path, embedding_model, allow_dangerous_deserialization=True)

# # Load both vectorstores at startup
# vectorstore_medical = load_vectorstore(DB_FAISS_PATH)
# vectorstore_mental_health = load_vectorstore(MH_FAISS_PATH)

# # Load LLM from HuggingFace (Mistral model)
# def load_llm():
#     hf_token = os.environ.get("HF_TOKEN")
#     if not hf_token:
#         raise ValueError("Missing HuggingFace token in .env")
#     return HuggingFaceEndpoint(
#         repo_id="mistralai/Mistral-7B-Instruct-v0.3",
#         huggingfacehub_api_token=hf_token,
#         task="text-generation",
#         temperature=0.5,
#         model_kwargs={"max_length": 800}
#     )

# # Custom prompt template
# def set_custom_prompt():
#     return PromptTemplate(template="""
#     Use the provided context to answer the user's question in a structured way.
#     If you don't know the answer, just say that you don't know, don't try to make up an answer.
#     Don't provide anything out of the given context.

#     **Format the response as follows:**  
#     - Use **numbered main points** (1., 2., 3.)  

#     **Example Response:**  
#     1. Main Topic  
#        - Supporting detail 1  
#        - Supporting detail 2  
#        - **Important term**: Explanation  

#     2. Another Main Topic  
#        - Supporting detail 1  
#        - Supporting detail 2  

#     **Context:** {context}  
#     **Question:** {question}  

#     **Response:**""",
#         input_variables=["context", "question"]
#     )

# # Detect repeated nonsense
# def detect_gibberish(text):
#     if not text.strip():
#         return True
#     words = text.lower().split()
#     word_counts = {}
#     for word in words:
#         word_counts[word] = word_counts.get(word, 0) + 1
#     most_common_word, max_count = max(word_counts.items(), key=lambda x: x[1])
#     return max_count > len(words) * 0.4 or re.search(r"(\b\w+\b)(?:\s+\1){3,}", text)

# # Format result clearly
# def format_response(response_text):
#     formatted = []
#     for line in response_text.split("\n"):
#         line = line.strip()
#         if line.startswith(("1.", "2.", "3.")):
#             formatted.append(f"\n{line}")
#         elif line.startswith("-"):
#             formatted.append(f"   {line}")
#         else:
#             formatted.append(line)
#     return "\n".join(formatted).strip()

# # Main chatbot endpoint (Medical + Mental Health)
# @app.route("/ask", methods=["POST"])
# def ask():
#     try:
#         data = request.get_json()
#         query = data.get("query")
#         language = data.get("language", "English")
#         domain = data.get("domain", "medical")  # 👈 Default domain is medical

#         if not query:
#             return jsonify({"error": "Query is required"}), 400

#         # Load LLM
#         llm = load_llm()

#         # Choose which vectorstore
#         if domain.lower() == "mental_health":
#             vectorstore = vectorstore_mental_health
#         else:
#             vectorstore = vectorstore_medical

#         # LangChain RetrievalQA
#         qa_chain = RetrievalQA.from_chain_type(
#             llm=llm,
#             chain_type="stuff",
#             retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
#             return_source_documents=True,
#             chain_type_kwargs={"prompt": set_custom_prompt()}
#         )

#         # Run query
#         response = qa_chain.invoke({"query": query})
#         result = response["result"]

#         if detect_gibberish(result):
#             result = "I don't know."

#         formatted = format_response(result)

#         # Translate result
#         translated = GoogleTranslator(
#             source="auto",
#             target=LANGUAGE_OPTIONS.get(language, "en")
#         ).translate(formatted)

#         return jsonify({
#             "response": translated,
#             "source_documents": [doc.page_content for doc in response["source_documents"]]
#         })

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # Default simple chatbot endpoint
# @app.route('/chat', methods=['POST'])
# def chat():
#     data = request.get_json(silent=True)
#     print("Received data:", data)

#     if not data or 'message' not in data:
#         return jsonify({"error": "Invalid input. 'message' field is required."}), 400

#     user_message = data["message"]
#     print("User message:", user_message)

#     try:
#         response = run_query(user_message)
#         print("Response from run_query:", response)
#         return jsonify({"reply": response})
#     except Exception as e:
#         print("Error in run_query:", e)
#         return jsonify({"reply": "Something went wrong. Try again."})

# # Health check
# @app.route("/")
# def home():
#     return "Flask backend is running!"


from flask import Flask, request, jsonify, session
from flask_cors import CORS
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
from connect_memory_with_llm import run_query
import os
import sys
import re
import secrets
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import google.generativeai as genai
from auth_routes import auth_bp

# Ignore venv path for reloader
venv_path = os.environ.get("VIRTUAL_ENV")
if venv_path and venv_path in sys.path:
    sys.path.remove(venv_path)

print(secrets.token_hex(16))
load_dotenv()
app = Flask(__name__)
# app.secret_key = "1690ec0701e8a05f6de538bfe58803ad"
app.secret_key = os.environ.get("SECRET_KEY") 
CORS(app)
app.register_blueprint(auth_bp, url_prefix="")

DB_FAISS_PATH = "vectorstore/db_faiss"
MH_FAISS_PATH = "vectorstore/mental_health_db_faiss"

LANGUAGE_OPTIONS = {
    "English": "en", "Hindi": "hi", "Gujarati": "gu", "Marathi": "mr",
    "Spanish": "es", "French": "fr", "German": "de", "Chinese": "zh-cn",
    "Japanese": "ja", "Arabic": "ar", "Tamil": "ta", "Telugu": "te",
    "Bengali": "bn", "Kannada": "kn", "Malayalam": "ml", "Punjabi": "pa",
    "Assamese": "as"
}

def load_vectorstore(path):
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.load_local(path, embedding_model, allow_dangerous_deserialization=True)

vectorstore_medical = load_vectorstore(DB_FAISS_PATH)
vectorstore_mental_health = load_vectorstore(MH_FAISS_PATH)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def load_llm():
    try:
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))  # Use Gemini's API key
        print("Gemini LLM loaded.")
        return genai.GenerativeModel("gemini-1.5-pro-001")
    except Exception as e:
        print(f"Error loading Gemini LLM: {e}")
        raise

def set_custom_prompt():
 return PromptTemplate(template="""Use the provided context to answer the user's question in a structured way.
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
    Format the response with **numbered bullet points**, with each point and sub-point **on a new line**.

    Do NOT merge multiple points into the same line.Don't use provided content contains,The context does not describe.

    **Context:** {context}  
    **Question:** {question}  

    **Response:**""", input_variables=["context", "question"])

def detect_gibberish(text):
    if not text.strip():
        return True
    words = text.lower().split()
    word_counts = {}
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1
    most_common_word, max_count = max(word_counts.items(), key=lambda x: x[1])
    return max_count > len(words) * 0.4 or re.search(r"(\b\w+\b)(?:\s+\1){3,}", text)

def format_response(response_text):
    formatted = []
    for line in response_text.split("\n"):
        line = line.strip()
        if line.startswith(("1.", "2.", "3.")):
            formatted.append(f"{line}\n") #Add a line break after each point
        elif line.startswith("-"): 
            formatted.append(f"   {line}")
        else:
            formatted.append(line)
    return "\n".join(formatted).strip()

# def format_response(response_text):
#     lines = response_text.split("\n")
#     formatted = []
#     for line in lines:
#         line = line.strip()
#         if re.match(r"^\d+\.", line):  # Matches lines starting with 1., 2., 3., etc.
#             formatted.append(f"\n{line}")  # Start a new numbered point on its own line
#         elif line.startswith("-"):
#             formatted.append(f"\n   {line}")  # Indent sub-points with a new line
#         else:
#             formatted.append(f"{line}")
#     return "\n".join(formatted).strip()


@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        query = data.get("query")
        language = data.get("language", "English")
        domain = data.get("domain", "medical")

        if not query:
            return jsonify({"error": "Query is required"}), 400

        vectorstore = vectorstore_mental_health if domain.lower() == "mental_health" else vectorstore_medical
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        docs = retriever.get_relevant_documents(query)
        print("Retrieved Documents:")
        for i, doc in enumerate(docs):
         print(f"Doc {i+1}: {doc.page_content[:200]}...")  # Just show first 200 chars
        context = "\n\n".join(doc.page_content for doc in docs)
        # prompt = set_custom_prompt().format(context=context, question=query)
        mental_health_keywords = ["anxiety", "stress", "depression", "panic", "overwhelmed", "feeling low", "sad", "mental", "worry", "suicidal"]
        if domain.lower() == "medical":
         if any(word in query.lower() for word in mental_health_keywords):
          return jsonify({
            "response": (
                "It looks like you're asking about a mental health concern such as anxiety or stress. "
                "I'm really sorry you're feeling this way, and I want to help. "
                "**Please switch to Mental Health mode** so I can respond with proper guidance tailored for such situations. 💙"
            )
        })
        if domain.lower() == "mental_health":
            prompt = f"""
         You are a compassionate and empathetic mental health assistant.

         Your job is to support people who are feeling anxious, stressed, or overwhelmed. Always start by expressing empathy, like:
         "I'm really sorry you're feeling this way. Want to talk about what's causing it? Whether it's something specific or just a general sense of anxiety, I’m here to listen and help however I can."

         Then, gently offer helpful suggestions, breathing techniques, or emotional support. Do **not** refer to documents, chapters, or outside readings. Keep everything within your answer and emotionally supportive.

         Respond in this structure:
        1. Empathetic Opening  
          - Validate the user's feelings
           - Offer comfort and willingness to help

        2. Gentle Guidance  
        - Suggestions for coping (like deep breathing, journaling, or mindfulness)
        - Reassurance and encouragement

     **Context:** {context}
     **Question:** {query}

    **Response:**
        """
        else:
            # Default medical prompt
            prompt = set_custom_prompt().format(context=context, question=query)
        model=load_llm()
        model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17")
        gemini_response = model.generate_content(prompt)
        result = gemini_response.text

        if detect_gibberish(result):
            result = "I don't know."

        formatted = format_response(result)
        translated = GoogleTranslator(source="auto", target=LANGUAGE_OPTIONS.get(language, "en")).translate(formatted)
        
        print(f"Query received: {query}")
        print(f"Domain: {domain}")
        print("Using vectorstore:", "mental_health" if domain.lower() == "mental_health" else "medical")

        return jsonify({
            "response": translated,
        })


    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True)
    print("Received data:", data)

    if not data or 'message' not in data:
        return jsonify({"error": "Invalid input. 'message' field is required."}), 400

    user_message = data["message"]
    print("User message:", user_message)
    domain= data.get("domain", "medical")  # Default domain is medical

    try:
        response = run_query(user_message,selected_domain=domain)
        print("Response from run_query:", response)
        return jsonify({"reply": response})
    except Exception as e:
        print("Error in run_query:", e)
        return jsonify({"reply": "Something went wrong. Try again."})


@app.route("/")
def home():
    return "Flask backend is running with Gemini!"

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=5000)
