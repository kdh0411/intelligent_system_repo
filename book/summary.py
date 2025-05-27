from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback

class BookDetailExtractor:
    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("window-size=1920x1080")
        options.add_argument("user-agent=Mozilla/5.0")
        self.options = options

    def get_details_by_rno(self, rno):
        return self._extract_details(rno=rno)

    def _extract_details(self, rno):
        driver = webdriver.Chrome(options=self.options)
        wait = WebDriverWait(driver, 10)
        details = {}

        try:
            detail_url = f"https://hsel.hansung.ac.kr/data_view.mir?rno={rno}&hloc_code=HSEL"
            driver.get(detail_url)

            headers = driver.find_elements(By.CSS_SELECTOR, "#panel h4.sub_title")
            valid_labels = ["책소개", "목차", "저자소개", "본문중에서"]

            for h in headers:
                try:
                    label = h.text.strip().replace("\xa0", "").replace(" ", "").replace("\n", "")
                    if label not in valid_labels:
                        continue

                    content_div = h.find_element(By.XPATH, "following-sibling::div[@class='well']")
                    content = content_div.get_attribute("innerHTML").strip()
                    content = content.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")

                    if content:
                        details[label] = content

                except Exception as e:
                    print(f"[{label}] 내용 추출 실패 (무시됨): {e}")
                    continue

        except Exception as e:
            traceback.print_exc()
            details = {"오류": f"❗ 상세정보 추출 실패: {e}"}
        finally:
            driver.quit()

        return details


# ✅ 테스트
if __name__ == "__main__":
    extractor = BookDetailExtractor()
    print("\n🔍 rno 기반 상세정보 테스트")
    res = extractor.get_details_by_rno("585694")  # 예시 책
    for k, v in res.items():
        print(f"[{k}]\n{v[:300]}...\n")
