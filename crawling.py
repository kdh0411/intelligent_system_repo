from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_book_info_by_regno(regno):
    url = f"https://hsel.hansung.ac.kr/data_search_list.mir?search_keyword_type1=regno&search_keyword1={regno}"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    try:
        title_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.book_title"))
        )
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

#테스트 코드
if __name__ == "__main__":
    regno = "0788392"
    info = get_book_info_by_regno(regno)
    for key, value in info.items():
        print(f"{key}: {value}")
