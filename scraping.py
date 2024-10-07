
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import urllib.parse

def scrape_case_laws(search_term, limit=10):
    encoded_search_term = urllib.parse.quote(search_term)
    url = f"https://new.kenyalaw.org/search/?q={encoded_search_term}&court=High+Court&doc_type=Judgment"
    print(f"Opening URL: {url}")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        print("Page loaded successfully")

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        print(f"Page Title: {driver.title}")
        print(f"Current URL: {driver.current_url}")

        selectors_to_try = [
            ".case-item",
            ".search-result-item",
            "div[class*='result']",
            "div[class*='case']"
        ]

        results_found = False
        for selector in selectors_to_try:
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"Found results using selector: {selector}")
                results_found = True
                break
            except TimeoutException:
                print(f"Selector {selector} not found. Trying next...")

        if not results_found:
            print("No search results found using any of the attempted selectors.")
            driver.save_screenshot("error_screenshot.png")
            return []

        case_items = driver.find_elements(By.CSS_SELECTOR, selector)
        case_links = []

        for item in case_items[:limit]:  
            try:
                title_element = item.find_element(By.CSS_SELECTOR, "h3 a, h4 a, a")
                title = title_element.text.strip()
                link = title_element.get_attribute('href')
                case_links.append((title, link))
                print(f"Found case: {title}")
            except NoSuchElementException:
                print("Failed to extract details for a case item.")
                continue

            if len(case_links) >= limit:
                break

        print(f"Total cases found: {len(case_links)}")
        return case_links

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        driver.save_screenshot("error_screenshot.png")
        return []

    finally:
        driver.quit()

# Example usage
search_term = "family"
case_laws = scrape_case_laws(search_term, limit=10) 

print(f"Case Laws generated: {case_laws}")

# Print out the results
for title, link in case_laws:
    print(f"Case Title: {title}\nLink: {link}\n")


