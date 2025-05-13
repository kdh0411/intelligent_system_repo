# book/summary.py

import requests
import json

class BookSummary:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://www.aladin.co.kr/ttb/api/ItemSearch.aspx"

    def get_summary(self, title, author):
        params = {
            "ttbkey": self.api_key,
            "Query": title,  # 제목만 검색
            "QueryType": "Title",
            "SearchTarget": "Book",
            "output": "js",
            "Version": "20131101"
        }

        try:
            response = requests.get(self.api_url, params=params)
            raw = response.text
            print("📥 응답 내용:\n", raw)
            # JSONP: ttb.api({...}) → {...}
            start = raw.find("{")
            end = raw.rfind("}")
            if start == -1 or end == -1:
                return "⚠️ 응답 파싱 실패"

            json_str = raw[start:end+1]
            data = json.loads(json_str)

            # author 포함된 항목만 필터링
            if "item" in data:
                for item in data["item"]:
                    if author in item.get("author", ""):
                        return item.get("description", "요약 정보가 없습니다.")
                return f"❌ '{author}' 저자 도서가 검색 결과에 없음."
            else:
                return "도서를 찾을 수 없습니다."

        except Exception as e:
            return f"⚠️ 오류 발생: {e}"

# 테스트 실행
if __name__ == "__main__":
    API_KEY = "thasdfekgsot0290901"
    bs = BookSummary(api_key=API_KEY)
    summary = bs.get_summary("한강", "박정래")
    print("📘 요약 결과:\n", summary)
