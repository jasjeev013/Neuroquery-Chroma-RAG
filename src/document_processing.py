from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src.config import Config
from src.logger import setup_logger
logger = setup_logger(__name__)
import os

def process_pdfs(pdf_paths):
    """Process multiple PDF files into a vector store (fully synchronous version)."""
    documents = []
    
    for pdf_path in pdf_paths:
        try:
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            documents.extend(pages)
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            continue
    logger.info("Loaded %d documents from %d PDF files", len(documents), len(pdf_paths))
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
    )
    splits = text_splitter.split_documents(documents)
    logger.info("Split %d documents into %d chunks", len(documents), len(splits))
    # Create embeddings
    try:
        logger.info("Creating embeddings with model: %s", Config.GOOGLE_API_KEY)
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            api_key=Config.GOOGLE_API_KEY # Use environment variable or fallback to default
        )
        logger.info("Using embedding model: %s", Config.EMBEDDING_MODEL)
    except Exception as e:
        logger.error("Failed to create embeddings: %s", str(e))
        raise ValueError("Embedding model creation failed. Check your API key and model configuration.")
    
    # Create Chroma vectorstore with synchronous client
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=Config.PERSIST_DIR,
    )
    logger.info("Vectorstore created with %d chunks", len(splits))
    
    return vectorstore

def get_retriever(vectorstore):
    logger.info("Creating retriever with search_k=%d", Config.SEARCH_K)
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": Config.SEARCH_K}
    )