from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BookCrawler:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--log-level=3")  # 로그 최소화

    def get_book_info(self, regno):
        url = f"https://hsel.hansung.ac.kr/data_search_list.mir?search_keyword_type1=regno&search_keyword1={regno}"
        driver = webdriver.Chrome(options=self.options)
        driver.get(url)

        # 이미지 차단: 속도 개선
        try:
            driver.execute_cdp_cmd('Network.setBlockedURLs', {"urls": ["*.png", "*.jpg", "*.jpeg", "*.gif"]})
            driver.execute_cdp_cmd('Network.enable', {})
        except:
            pass  # 일부 드라이버 환경에서 오류 나면 무시

        try:
            wait = WebDriverWait(driver, 3)

            title_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.book_title")))
            title = title_elem.text.strip().replace("단행본", "").strip()

            author_elem = driver.find_element(By.CSS_SELECTOR, "li.book_author span:nth-of-type(1)")
            publisher_elem = driver.find_element(By.CSS_SELECTOR, "li.book_author span:nth-of-type(2)")
            year_elem = driver.find_element(By.CSS_SELECTOR, "li.book_author span:nth-of-type(3)")
            call_no_elem = driver.find_element(By.CSS_SELECTOR, "li.book_site")

            book_info = {
                "제목": title,
                "저자": author_elem.text.replace("저자 :", "").strip(),
                "출판사": publisher_elem.text.replace("출판사 :", "").strip(),
                "출판연도": year_elem.text.replace("출판연도 :", "").strip(),
                "책 위치": call_no_elem.text.replace("청구기호 :", "").strip()
            }

        except Exception as e:
            book_info = {
                "오류": f"정보 추출 실패: {e}"
            }

        driver.quit()
        return book_info

# 테스트 코드
if __name__ == "__main__":
    crawler = BookCrawler()
    result = crawler.get_book_info("0788392")
    for k, v in result.items():
        print(f"{k}: {v}")
