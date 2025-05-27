from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback
import urllib.parse

class BookCrawler:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--log-level=3")
        self.options.add_argument("window-size=1920x1080")
        self.options.add_argument("user-agent=Mozilla/5.0")

    def get_book_info_by_regno(self, regno):
        url = f"https://hsel.hansung.ac.kr/data_search_list.mir?search_keyword_type1=regno&search_keyword1={regno}"
        return self._extract_info(url, regno)

    def get_book_info_by_title(self, title):
        encoded = urllib.parse.quote_plus(title)
        url = f"https://hsel.hansung.ac.kr/data_search_list.mir?search_keyword_type1=text&search_keyword1={encoded}&search_new=Y"
        return self._extract_info(url)

    def _extract_info(self, url, regno=None):
        driver = webdriver.Chrome(options=self.options)
        driver.set_window_size(1920, 1080)
        driver.get(url)

        book_info = {}

        try:
            wait = WebDriverWait(driver, 10)
            btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(@onclick, 'show_inner_html_layer')]")))
            driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            driver.execute_script("arguments[0].click();", btn)

            rno = btn.get_attribute("onclick").split("'")[1]
            book_info["rno"] = rno

            if regno:
                book_info["등록번호"] = regno

            wait.until(lambda d: d.find_element(By.CSS_SELECTOR, "table.table-condensed.table_data_view tbody tr td").text.strip() != "")
            row = driver.find_element(By.CSS_SELECTOR, "table.table-condensed.table_data_view tbody tr")
            cells = row.find_elements(By.CSS_SELECTOR, "td.text-center.hidden-xs.hidden-sm")

            location = cells[0].text.strip().replace("\n", " ") if len(cells) > 0 else "없음"

            # ✅ 책장위치 매핑
            shelf_map = {"6F": "4번 책장", "5F": "3번 책장", "4F": "2번 책장", "3F": "1번 책장"}
            shelf_position = next((shelf_map[floor] for floor in shelf_map if floor in location), None)

            book_info.update({
                "소장위치": location,
                "청구기호": cells[2].text.strip() if len(cells) > 2 else "없음",
                "도서상태": cells[3].text.strip() if len(cells) > 3 else "없음",
                "반납예정일": cells[4].text.strip() if len(cells) > 4 else "없음",
                "예약": cells[5].text.strip() if len(cells) > 5 else "없음"
            })

            if shelf_position:
                book_info["책장위치"] = shelf_position

            title_raw = driver.find_element(By.CSS_SELECTOR, "a.book_title").text.strip()
            title = title_raw.replace("단행본 ", "", 1) if title_raw.startswith("단행본 ") else title_raw

            author_elem = driver.find_element(By.CSS_SELECTOR, "li.book_author span:nth-of-type(1)")
            publisher_elem = driver.find_element(By.CSS_SELECTOR, "li.book_author span:nth-of-type(2)")
            year_elem = driver.find_element(By.CSS_SELECTOR, "li.book_author span:nth-of-type(3)")

            try:
                img_elem = driver.find_element(By.CSS_SELECTOR, "img#img_book")
                img_src = img_elem.get_attribute("src")
                if img_src.startswith("/"):
                    img_src = "https://hsel.hansung.ac.kr" + img_src
            except:
                img_src = None

            book_info.update({
                "제목": title,
                "저자": author_elem.text.replace("저자 :", "").strip(),
                "출판사": publisher_elem.text.replace("출판사 :", "").strip(),
                "출판연도": year_elem.text.replace("출판연도 :", "").strip(),
                "이미지": img_src
            })

        except Exception as e:
            traceback.print_exc()
            book_info = {
                "오류": "❗ 도서 정보를 찾을 수 없습니다. 등록번호나 제목을 다시 확인해 주세요."
            }

        driver.quit()
        return book_info


# ✅ 테스트 코드 실행
if __name__ == "__main__":
    crawler = BookCrawler()

    print("\n📘 [등록번호 기반 검색 테스트]")
    result1 = crawler.get_book_info_by_regno("0788392")  # 예시 등록번호
    for k, v in result1.items():
        print(f"{k}: {v}")

    print("\n📗 [제목 기반 검색 테스트]")
    result2 = crawler.get_book_info_by_title("AI 포토샵 테크닉")  # 예시 제목
    for k, v in result2.items():
        print(f"{k}: {v}")
