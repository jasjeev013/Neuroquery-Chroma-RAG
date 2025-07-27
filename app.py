# app.py
import asyncio
import nest_asyncio
nest_asyncio.apply()

import streamlit as st
from src.document_processing import process_pdfs, get_retriever
from src.llm_chain import create_rag_chain
from src.utils import save_uploaded_files,reset_context
from src.config import Config
from src.logger import setup_logger
logger = setup_logger(__name__)
import os
from dotenv import load_dotenv
load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
if google_api_key:
    os.environ["GOOGLE_API_KEY"] = google_api_key
else:
    logger.error("GOOGLE_API_KEY not found in environment variables.")

st.set_page_config(
    page_title="PDF Question Answering System",
    page_icon="📄",
    layout="centered"
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None

with st.sidebar:
    st.title("PDF Upload")
    st.write(f"Upload up to {Config.MAX_FILES} PDF files (max {Config.MAX_PAGES} pages each)")
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True
    )
    
    if uploaded_files and st.button("Process PDFs"):
        reset_context()  # Reset context before processing new files
        logger.info("User uploaded %d PDF(s)", len(uploaded_files))
        try:
            with st.spinner("Processing PDFs..."):
                pdf_paths = save_uploaded_files(uploaded_files)
                vectorstore = process_pdfs(pdf_paths)
                retriever = get_retriever(vectorstore)
                rag_chain = create_rag_chain(retriever)

                st.session_state.vectorstore = vectorstore
                st.session_state.rag_chain = rag_chain
                logger.info("RAG chain created successfully with %d documents", len(vectorstore._collection.get()['ids']))
                st.success("PDFs processed successfully!")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # Clear context if no file is uploaded
    if not uploaded_files and st.session_state.vectorstore:
        reset_context()
        st.success("Context cleared because no files are uploaded.")

    # Manual reset button
    if st.button("Clear All Context"):
        reset_context()
        st.success("Context and uploaded files cleared.")


st.title("📄 PDF Question Answering System")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about the PDFs"):
    if not st.session_state.rag_chain:
        st.error("Please upload and process PDF files first.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.rag_chain.invoke({"input": prompt})
                answer = response["answer"]

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                logger.error(f"Error generating answer: {str(e)}")
                st.error(f"Error generating answer: {str(e)}")
