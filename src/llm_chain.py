from langchain_google_genai import GoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from src.config import Config
from src.logger import setup_logger
logger = setup_logger(__name__)

def create_rag_chain(retriever):
    llm = GoogleGenerativeAI(
        model=Config.LLM_MODEL,
        temperature=Config.TEMPERATURE,
        max_tokens=Config.MAX_TOKENS
    )
    logger.info("Using LLM model: %s", Config.LLM_MODEL)

    system_prompt = """
    You are an expert assistant specialized in analyzing PDF documents with a strong focus on statistics and probability. Follow these steps:

    1. **Understand the User Query**: Break down the user's intent and what they want to know.
    2. **Extract from Context**: Refer only to the provided document content for relevant information.
    3. **Be Precise**:
    - For definitions, give exact, concise meanings.
    - For explanations, walk through concepts clearly and thoroughly.
    - For calculations, show detailed step-by-step reasoning.
    - For summaries, outline key points using bullet format if needed.

    4. **Respond like a tutor**: Explain in a simple, educational tone.

    Context:
    {context}

    User Question:
    {input}
    """

    logger.info("Creating RAG chain with model %s", Config.LLM_MODEL)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    question_answer_chain = create_stuff_documents_chain(llm, prompt=prompt)

    return create_retrieval_chain(
        retriever=retriever,
        combine_docs_chain=question_answer_chain,
    )
