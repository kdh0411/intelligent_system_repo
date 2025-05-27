# book/summary_gpt.py

import os
from dotenv import load_dotenv
from openai import OpenAI

from langchain_community.callbacks.manager import get_openai_callback  

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

class BookSummaryGPT:
    def __init__(self):
        self.model = "gpt-4o"

    def get_summary(self, title: str, author: str) -> str:
        prompt = f"""
너는 도서 키오스크에 탑재된 도서 요약 챗봇이야.
다음 책의 제목과 저자만 보고, 그럴듯한 책 소개를 2~3문장으로 요약해줘.
모르면 상상해서 설명해도 돼. 단, 신뢰감 있게 써야 해.

제목: {title}
저자: {author}

요약:
"""
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    def get_summary_with_tokens(self, title: str, author: str) -> dict:
        prompt = f"""
너는 도서 키오스크에 탑재된 도서 요약 챗봇이야.
다음 책의 제목과 저자만 보고, 그럴듯한 책 소개를 2~3문장으로 요약해줘.
모르면 상상해서 설명해도 돼. 단, 신뢰감 있게 써야 해.

제목: {title}
저자: {author}

요약:
"""
        with get_openai_callback() as cb:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return {
                "response": response.choices[0].message.content.strip(),
                "tokens": {
                    "input": cb.prompt_tokens,
                    "output": cb.completion_tokens,
                    "total": cb.total_tokens,
                    "cost_usd": cb.total_cost
                }
            }

# ✅ 테스트 실행
if __name__ == "__main__":
    bot = BookSummaryGPT()
    title = "AI 포토샵 테크닉"
    author = "유은진진"

    print("📘 요약 결과:")
    print(bot.get_summary(title, author))

    print("\n📊 토큰 정보 포함:")
    result = bot.get_summary_with_tokens(title, author)
    print("📊 입력 토큰:", result["tokens"]["input"])
    print("📊 출력 토큰:", result["tokens"]["output"])
    print("📊 총 토큰:", result["tokens"]["total"])
    print("💵 예상 비용 (USD):", result["tokens"]["cost_usd"])
