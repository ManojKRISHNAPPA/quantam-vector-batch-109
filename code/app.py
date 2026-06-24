import os
import streamlit as st
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
)

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_ollama import ChatOllama


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Company RAG Assistant",
    page_icon="📄",
    layout="wide"
)

# =====================================================
# PATHS
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

DOCS_PATH = BASE_DIR.parent / "company_docs"
VECTOR_DB = str(BASE_DIR / "vectorstore")

DOC_FOLDER = str(DOCS_PATH)

# =====================================================
# API KEY INPUT
# =====================================================

st.sidebar.title("🔑 Configuration")



if "openai_key" not in st.session_state:
    st.session_state.openai_key = ""

st.session_state.openai_key = st.sidebar.text_input(
    "OpenAI API Key",
    value=st.session_state.openai_key,
    type="password",
    help="Enter your OpenAI API Key"
)

st.session_state.openai_key = st.sidebar.text_input(
    "groq API Key",
    value=st.session_state.openai_key,
    type="password",
    help="Enter your OpenAI API Key"
)

OPENAI_API_KEY = st.session_state.openai_key

if not OPENAI_API_KEY:
    st.warning("Please enter your OpenAI API Key in the sidebar.")
    st.stop()

# =====================================================
# LOAD DOCUMENTS
# =====================================================

def load_documents():
    loader = DirectoryLoader(
        DOC_FOLDER,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )

    return loader.load()


# =====================================================
# VECTOR STORE
# =====================================================

@st.cache_resource(show_spinner=False)
def create_or_load_vectorstore(api_key):

    os.makedirs(VECTOR_DB, exist_ok=True)

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=api_key
    )

    index_path = os.path.join(VECTOR_DB, "index.faiss")

    if os.path.exists(index_path):

        return FAISS.load_local(
            VECTOR_DB,
            embeddings,
            allow_dangerous_deserialization=True
        )

    st.info("Creating Vector Database... ⏳")

    docs = load_documents()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(docs)

    db = FAISS.from_documents(
        chunks,
        embeddings
    )

    db.save_local(VECTOR_DB)

    return db


# =====================================================
# LLM
# =====================================================

@st.cache_resource(show_spinner=False)
def load_llm(api_key):

    try:

        llm = ChatOllama(
            model="llama3.3"
        )

        llm.invoke("hello")

        st.sidebar.success("Using Ollama 🦙")

        return llm

    except Exception:

        st.sidebar.warning(
            "Ollama unavailable. Using GPT-4o-mini"
        )

        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=api_key
        )


# =====================================================
# INITIALIZE
# =====================================================

db = create_or_load_vectorstore(
    OPENAI_API_KEY
)

retriever = db.as_retriever(
    search_kwargs={"k": 4}
)

llm = load_llm(
    OPENAI_API_KEY
)

# =====================================================
# PROMPT
# =====================================================

prompt = ChatPromptTemplate.from_template(
    """
You are a company knowledge assistant.

Answer ONLY from the provided context.

If the answer is not available in the context, respond:

"I could not find that information in the documents."

Context:
{context}

Question:
{question}

Answer:
"""
)

# =====================================================
# FORMAT DOCUMENTS
# =====================================================

def format_docs(docs):

    return "\n\n".join(
        f"""
SOURCE: {doc.metadata.get('source', 'Unknown')}
PAGE: {doc.metadata.get('page', 'Unknown')}

{doc.page_content}
"""
        for doc in docs
    )

# =====================================================
# RAG CHAIN
# =====================================================

rag_chain = (
    {
        "context": retriever | RunnableLambda(format_docs),
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
)

# =====================================================
# UI
# =====================================================

st.title("📄 Company RAG Assistant")

st.caption(
    "Ask questions from your company PDF documents."
)

# =====================================================
# CHAT HISTORY
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =====================================================
# CHAT INPUT
# =====================================================

question = st.chat_input(
    "Ask something from company documents..."
)

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner("Searching documents..."):

            try:

                response = rag_chain.invoke(
                    question
                )

                answer = response.content

                st.markdown(answer)

                docs = retriever.invoke(
                    question
                )

                with st.expander(
                    "📚 Sources Used"
                ):

                    for i, doc in enumerate(
                        docs,
                        start=1
                    ):

                        st.markdown(
                            f"""
**{i}. File:** {os.path.basename(doc.metadata.get('source', 'Unknown'))}

**Page:** {doc.metadata.get('page', 'Unknown')}
"""
                        )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

            except Exception as e:

                st.error(
                    f"Error: {str(e)}"
                )

# =====================================================
# SIDEBAR INFO
# =====================================================

st.sidebar.markdown("---")

st.sidebar.info(
    f"""
📁 Documents Folder

{DOC_FOLDER}

📦 Vector Store

{VECTOR_DB}
"""
)