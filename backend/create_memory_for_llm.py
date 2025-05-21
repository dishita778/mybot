# from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS

# # Step 1: Load raw PDF(s)
# DATA_PATH = "dataaa/"
# MENTAL_HEALTH_DATA_PATH = "mental_health_data/"

# def load_pdf_files(folder_path):
#     loader = DirectoryLoader(folder_path, glob='*.pdf', loader_cls=PyPDFLoader)
#     documents = loader.load()
#     return documents

# # Load Medical PDFs
# medical_documents = load_pdf_files(DATA_PATH)

# # Load Mental Health PDFs
# mental_health_documents = load_pdf_files(MENTAL_HEALTH_DATA_PATH)

# # Step 2: Create Chunks
# def create_chunks(extracted_data):
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
#     text_chunks = text_splitter.split_documents(extracted_data)
#     return text_chunks

# medical_text_chunks = create_chunks(medical_documents)
# mental_health_text_chunks = create_chunks(mental_health_documents)

# # Step 3: Create Vector Embeddings 
# def get_embedding_model():
#     embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
#     return embedding_model

# embedding_model = get_embedding_model()

# # Step 4: Store Medical embeddings in FAISS
# DB_FAISS_PATH = "vectorstore/db_faiss"
# db_medical = FAISS.from_documents(medical_text_chunks, embedding_model)
# db_medical.save_local(DB_FAISS_PATH)
# print("✅ Medical vectorstore created successfully!")

# # Step 4: Store Mental Health embeddings in FAISS
# MH_DB_FAISS_PATH = "vectorstore/mental_health_db_faiss"
# db_mental_health = FAISS.from_documents(mental_health_text_chunks, embedding_model)
# db_mental_health.save_local(MH_DB_FAISS_PATH)
# print("✅ Mental Health vectorstore created successfully!")

from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
# Step 1: Load raw PDF(s)
DATA_PATH = "dataaa/"
MENTAL_HEALTH_DATA_PATH = "mental_health_data/"

# def load_pdf_files(folder_path):
#     loader = DirectoryLoader(folder_path, glob='*.pdf', loader_cls=PyPDFLoader)
#     documents = loader.load()
#     for doc in documents:
#         if "source" not in doc.metadata:
#             doc.metadata["source"] = folder_path
#     return documents
def load_pdf_files(folder_path):
    loader = DirectoryLoader(folder_path, glob='*.pdf', loader_cls=PyPDFLoader)
    raw_docs = loader.load()
    for doc in raw_docs:
        doc.metadata["source"] = doc.metadata.get("source", doc.metadata.get("file_path", "Unknown"))
    return raw_docs


# Load Medical PDFs
medical_documents = load_pdf_files(DATA_PATH)

# Load Mental Health PDFs
mental_health_documents = load_pdf_files(MENTAL_HEALTH_DATA_PATH)

# Step 2: Create Chunks
def create_chunks(extracted_data):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    text_chunks = text_splitter.split_documents(extracted_data)
    return text_chunks

medical_text_chunks = create_chunks(medical_documents)
mental_health_text_chunks = create_chunks(mental_health_documents)

# Step 3: Create Vector Embeddings 
def get_embedding_model():
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return embedding_model

embedding_model = get_embedding_model()

# Step 4: Store Medical embeddings in FAISS
DB_FAISS_PATH = "vectorstore/db_faiss"
db_medical = FAISS.from_documents(medical_text_chunks, embedding_model)
db_medical.save_local(DB_FAISS_PATH)
print("✅ Medical vectorstore created successfully!")

# Step 4: Store Mental Health embeddings in FAISS
MH_DB_FAISS_PATH = "vectorstore/mental_health_db_faiss"
db_mental_health = FAISS.from_documents(mental_health_text_chunks, embedding_model)
db_mental_health.save_local(MH_DB_FAISS_PATH)
print("✅ Mental Health vectorstore created successfully!")