# rag/vector_store.py

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings  # ✅ 수정


import os

def create_vector_store(documents):
    return FAISS.from_documents(documents, OpenAIEmbeddings())

def save_vector_store(vectorstore, path="rag/faiss_index"):
    vectorstore.save_local(path)

def load_vector_store(path="rag/faiss_index"):
    return FAISS.load_local(
    path,
    OpenAIEmbeddings(),
    allow_dangerous_deserialization=True
    )

