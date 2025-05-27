# rag/build_index.py

from loader import load_and_split_documents
from vector_store import create_vector_store, save_vector_store

if __name__ == "__main__":
    docs = load_and_split_documents("rag/library_guide_combined.txt")
    vs = create_vector_store(docs)
    save_vector_store(vs)
    print("✅ 벡터 인덱스 생성 완료!")
