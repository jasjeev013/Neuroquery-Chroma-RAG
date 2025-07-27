import tempfile
import os
from src.config import Config
import streamlit as st
import shutil
from src.logger import setup_logger
logger = setup_logger(__name__)

def reset_context():
    st.session_state.vectorstore = None
    st.session_state.rag_chain = None
    st.session_state.messages = []
    if os.path.exists(Config.PERSIST_DIR):
        shutil.rmtree(Config.PERSIST_DIR)
    temp_root = tempfile.gettempdir()
    for folder in os.listdir(temp_root):
        if "tmp" in folder:
            try:
                shutil.rmtree(os.path.join(temp_root, folder))
            except Exception:
                pass
            

def save_uploaded_files(uploaded_files):
    """Save uploaded files to temporary directory and return their paths."""
    temp_dir = tempfile.mkdtemp()
    file_paths = []
    if len(file_paths) > Config.MAX_FILES:
        logger.info("User uploaded %d PDF(s). More than the maximum allowed (%d)", len(uploaded_files), Config.MAX_FILES)
        raise ValueError(f"Maximum {Config.MAX_FILES} files allowed.")

    for uploaded_file in uploaded_files:
        if uploaded_file.name.lower().endswith('.pdf'):
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            file_paths.append(file_path)

    logger.info("Saved %d PDF(s) to temporary directory: %s", len(file_paths), temp_dir)
    return file_paths
