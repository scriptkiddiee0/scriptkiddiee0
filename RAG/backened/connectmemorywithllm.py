import os
from pathlib import Path
import getpass

from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatGoogleGenerativeAI, ChatOpenAI
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

CUSTOM_PROMPT_TEMPLATE = """
Use the pieces of information provided in the context to answer user's question.
If you dont know the answer, just say that you dont know, dont try to make up an answer.
Dont provide anything out of the given context

Context: {context}
Question: {question}

Start the answer directly. No small talk please.
"""


def set_custom_prompt(custom_prompt_template):
    return PromptTemplate(template=custom_prompt_template, input_variables=["context", "question"])


def get_gemini_api_key():
    return os.getenv("GEMINI_API_KEY")


def get_llm_model(api_key: str):
    return ChatOpenAI(
    model="LongCat-Flash-Thinking-2601",
    # stream_usage=True,
    # temperature=None,
    # max_tokens=None,
    # timeout=None,
    # reasoning_effort="low",
    # max_retries=2,
    api_key=os.getenv("LONGCAT_API_KEY"),  # If you prefer to pass api key in directly
    base_url="https://api.longcat.chat/openai",
    # organization="...",
    # other params...
)


def load_documents(data_dir="data"):
    docs = []
    data_path = Path(data_dir)
    if not data_path.exists():
        raise SystemExit(f"Error: data directory '{data_dir}' does not exist.")

    for path in sorted(data_path.rglob("*.txt")):
        docs.extend(TextLoader(str(path)).load())
    for path in sorted(data_path.rglob("*.pdf")):
        docs.extend(PyPDFLoader(str(path)).load())

    if not docs:
        raise SystemExit(f"No documents found in '{data_dir}'. Add .txt or .pdf files.")
    return docs


def build_vector_store(source_docs=None):
    if source_docs is None:
        source_docs = load_documents()

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return Chroma.from_documents(
        source_docs,
        embedding_model,
        collection_name="chatbot",
        persist_directory="./chroma_db",
    )


def get_qa_chain():
    api_key = get_gemini_api_key()
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY must be set in the environment.")

    llm_model = get_llm_model(api_key)
    vector_store = build_vector_store()
    return RetrievalQA.from_chain_type(
        llm=llm_model,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": set_custom_prompt(CUSTOM_PROMPT_TEMPLATE)},
    )


def answer_query(query: str, qa_chain=None):
    if qa_chain is None:
        qa_chain = get_qa_chain()
    return qa_chain.invoke({"query": query})


if __name__ == "__main__":
    api_key = get_gemini_api_key()
    if not api_key:
        api_key = getpass.getpass("Enter your Google AI API key: ")
        os.environ["GEMINI_API_KEY"] = api_key

    qa_chain = get_qa_chain()
    user_query = input("Write Query Here: ")
    response = qa_chain.invoke({"query": user_query})
    print("RESULT: ", response["result"])
    print("SOURCE DOCUMENTS: ", response["source_documents"])
