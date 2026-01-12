
import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


MEDICAL_DATA_PATH = "dataaa/"
MENTAL_HEALTH_DATA_PATH = "mental_health_data/"

VECTORSTORE_DIR = "vectorstore"
MEDICAL_DB_FAISS_PATH = os.path.join(VECTORSTORE_DIR, "db_faiss")
MENTAL_HEALTH_DB_FAISS_PATH = os.path.join(VECTORSTORE_DIR, "mental_health_db_faiss")

os.makedirs(VECTORSTORE_DIR, exist_ok=True)

def load_pdf_files(folder_path):
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    loader = DirectoryLoader(
        folder_path,
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )

    docs = loader.load()

    for doc in docs:
        doc.metadata["source"] = doc.metadata.get(
            "source",
            doc.metadata.get("file_path", "Unknown")
        )

    return docs


medical_documents = load_pdf_files(MEDICAL_DATA_PATH)
mental_health_documents = load_pdf_files(MENTAL_HEALTH_DATA_PATH)



def create_chunks(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    return splitter.split_documents(documents)


medical_chunks = create_chunks(medical_documents)
mental_health_chunks = create_chunks(mental_health_documents)

def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


embedding_model = get_embedding_model()


print("Creating medical FAISS vectorstore...")
medical_db = FAISS.from_documents(medical_chunks, embedding_model)
medical_db.save_local(MEDICAL_DB_FAISS_PATH)

print("Medical vectorstore saved at:", MEDICAL_DB_FAISS_PATH)


print("Creating mental health FAISS vectorstore...")
mental_health_db = FAISS.from_documents(mental_health_chunks, embedding_model)
mental_health_db.save_local(MENTAL_HEALTH_DB_FAISS_PATH)

print("Mental health vectorstore saved at:", MENTAL_HEALTH_DB_FAISS_PATH)

print("Vectorstores created successfully.")

