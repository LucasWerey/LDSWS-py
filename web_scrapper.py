import json
import logging
import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


load_dotenv()

URL = os.getenv("URL")
TABLE_ELEMENT = os.getenv("TABLE_ELEMENT")
SELECTOR = os.getenv("SELECTOR")
NEXT_PAGE_XPATH = os.getenv("NEXT_PAGE_XPATH")
MAX_LOAD_MORE_CLICKS = os.getenv("MAX_LOAD_MORE_CLICKS")
BATCH_SIZE = os.getenv("BATCH_SIZE")
SCROLL_STEP = os.getenv("SCROLL_STEP")
SCROLL_DELAY = os.getenv("SCROLL_DELAY")
CLICK_DELAY = os.getenv("CLICK_DELAY")
TICKER_PATH = os.getenv("TICKER_PATH")
DIV = os.getenv("DIV")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    # options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)
    return driver


def save_icons_batch(icons, batch_num):
    filename = f"test_batch{batch_num*100}.json"
    with open(filename, "w") as f:
        json.dump(icons, f, indent=2)
    print(f"Saved batch {batch_num} with {len(icons)} icons")


def scroll_to_top(driver):
    driver.execute_script("window.scrollTo(0, 0);")
    current_position = driver.execute_script("return window.pageYOffset;")
    if current_position > 0:
        driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(SCROLL_DELAY * 2)


def click_load_more(driver):
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, NEXT_PAGE_XPATH))
        )

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, NEXT_PAGE_XPATH))
        )

        driver.execute_script(
            "arguments[0].scrollIntoView(true);", next_button)
        time.sleep(CLICK_DELAY)

        try:
            next_button.click()
        except:
            driver.execute_script("arguments[0].click();", next_button)

        time.sleep(CLICK_DELAY)

        scroll_to_top(driver)

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.TAG_NAME, TABLE_ELEMENT))
        )

        logger.info("Successfully clicked next page button and reset position")
        return True

    except Exception as e:
        logger.error(f"Failed to click next page button: {str(e)}")
        return False


def scroll_and_get_icons():
    driver = setup_driver()
    icons = {}
    load_more_clicks = 0
    icon_counter = 0
    batch_num = 1
    processed_icons = set()

    try:
        driver.get(URL)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, TABLE_ELEMENT))
        )

        while load_more_clicks < MAX_LOAD_MORE_CLICKS:
            rows = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "tr"))
            )

            for row in rows:
                try:
                    icon = row.find_element(By.CSS_SELECTOR, SELECTOR)
                    name_element = row.find_element(
                        By.CLASS_NAME, DIV)
                    name = name_element.text.strip()
                    src = icon.get_attribute('src')

                    ticker_element = row.find_element(By.XPATH, TICKER_PATH)
                    ticker = ticker_element.text.strip()

                    if name and src and ticker and name not in processed_icons:
                        icons[name] = {
                            'src': src,
                            'ticker': ticker
                        }
                        processed_icons.add(name)
                        icon_counter += 1
                        logger.info(f'Processed: {name} ({ticker})')

                        if icon_counter >= BATCH_SIZE:
                            save_icons_batch(icons, batch_num)
                            icons = {}
                            batch_num += 1
                            icon_counter = 0
                except Exception as e:
                    continue

            if not click_load_more(driver):
                break
            load_more_clicks += 1

        if icons:
            save_icons_batch(icons, batch_num)

        return processed_icons

    finally:
        driver.quit()


def main():
    logger.info("Starting web scraping process")
    icons = scroll_and_get_icons()
    logger.info(f"Completed scraping with {len(icons)} total icons processed")


if __name__ == "__main__":
    main()
