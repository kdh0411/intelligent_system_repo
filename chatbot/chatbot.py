import subprocess

class ChatBot:
    def __init__(self, model="mistral:instruct"):
        self.model = model

    def ask(self, query: str) -> str:
        try:
            # 한글 & 간결한 응답을 유도하는 프롬프트
            prompt = f"다음 질문에 대해 한국어로 간결하게 답변해줘: {query}"
            result = subprocess.run(
                ["ollama", "run", self.model, prompt],
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            return result.stdout.strip()
        except Exception as e:
            return f"⚠️ 오류 발생: {e}"

if __name__ == "__main__":
    bot = ChatBot()
    question = "AI 도서관 키오스크의 기능을 알려줘"
    response = bot.ask(question)
    print("💬 챗봇 응답:", response)
