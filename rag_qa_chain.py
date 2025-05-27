# rag/rag_qa_chain.py

from langchain_openai import ChatOpenAI  
from langchain.chains import RetrievalQA
from langchain_community.callbacks.manager import get_openai_callback
from vector_store import load_vector_store
import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

def get_rag_qa_chain():
    vectorstore = load_vector_store()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

    return RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model="gpt-4o", temperature=0.3),
        retriever=retriever,
        return_source_documents=True
    )

# ✅ 테스트용 실행
if __name__ == "__main__":
    qa_chain = get_rag_qa_chain()
    question = "IT전공 책 보려면 몇층으로 가야하나요??"

    # ✅ 토큰 사용량 추적
    from langchain.callbacks import get_openai_callback
    with get_openai_callback() as cb:
        result = qa_chain.invoke({"query": question})
        print("📘 응답:", result["result"])
        print("\n📊 토큰 사용량:")
        print(f"- 입력 토큰: {cb.prompt_tokens}")
        print(f"- 출력 토큰: {cb.completion_tokens}")
        print(f"- 총 사용 토큰: {cb.total_tokens}")
        print(f"- 예상 비용 (USD): ${cb.total_cost:.5f}")
