import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__))) 
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.callbacks.manager import get_openai_callback
from rag.vector_store import load_vector_store


# 환경변수 로딩 (.env)
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# 간결한 프롬프트 설정
CONDENSED_PROMPT = PromptTemplate.from_template("""
당신은 한성대학교 학술정보관 안내를 도와주는 키오스크입니다.
아래 사용자 질문에 대해 핵심정보만 간결하게 1~2문장으로 답하세요.

문서 정보:{context}
                                                
질문: {question}
""")

class LibraryGuideBot:
    def __init__(self, k: int = 2):
        """
        RAG 기반 도서관 안내 챗봇 초기화
        :param k: 관련 문서 검색 개수 (기본 2개)
        """
        vectorstore = load_vector_store()
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(model="gpt-4o", temperature=0.3),
            retriever=vectorstore.as_retriever(search_kwargs={"k": k}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": CONDENSED_PROMPT}  # 👈 프롬프트 반영
        )

    def ask(self, user_input: str) -> str:
        """RAG로 응답 반환"""
        result = self.qa_chain.invoke({"query": user_input})
        return result["result"]

    def ask_with_tokens(self, user_input: str) -> dict:
        """응답 + 토큰 통계 반환"""
        with get_openai_callback() as cb:
            result = self.qa_chain.invoke({"query": user_input})
            return {
                "response": result["result"],
                "tokens": {
                    "input": cb.prompt_tokens,
                    "output": cb.completion_tokens,
                    "total": cb.total_tokens,
                    "cost_usd": cb.total_cost
                }
            }

# ✅ 테스트용 단독 실행
if __name__ == "__main__":
    bot = LibraryGuideBot()
    question = "IT전공 책 보려면 몇층으로 가야하나요??"

    # 일반 응답
    print("📘 응답:", bot.ask(question))

    # 토큰 통계 포함 응답
    print("\n📊 토큰 정보 포함:")
    result = bot.ask_with_tokens(question)
    print("📘 응답:", result["response"])
    print("📊 입력 토큰:", result["tokens"]["input"])
    print("📊 출력 토큰:", result["tokens"]["output"])
    print("📊 총 토큰:", result["tokens"]["total"])
    print("💵 예상 비용 (USD):", result["tokens"]["cost_usd"])
