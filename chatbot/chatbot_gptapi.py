# chatbot/chatbot_gptapi.py

import openai
import os
from dotenv import load_dotenv

load_dotenv()  # .env 파일 자동 로드

class ChatBot:
    def __init__(self, model="gpt-4o"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = model

    def ask(self, query: str) -> str:
        try:
            openai.api_key = self.api_key

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 AI 도서관 키오스크의 안내 챗봇입니다. 한국어로 친절하게 대답하세요."},
                    {"role": "user", "content": query}
                ],
                temperature=0.7
            )
            return response["choices"][0]["message"]["content"]

        except Exception as e:
            return f"⚠️ 오류 발생: {e}"


# ✅ 단독 테스트용
if __name__ == "__main__":
    bot = ChatBot()
    question = "AI 도서관 키오스크의 기능을 설명해줘"
    response = bot.ask(question)
    print("💬 GPT-4o 응답:", response)
