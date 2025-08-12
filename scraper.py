# scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# --- IMPORTANT: UPDATE THESE SELECTORS IF DARAZ CHANGES ITS WEBSITE ---
# These are the class names we found in Step 1.
TITLE_CLASS = 'pdp-mod-product-badge-title'
PRICE_CLASS = 'pdp-price_type_normal'
# --------------------------------------------------------------------

def get_product_info(url):
    """
    Scrapes a Daraz product page for its title and price.
    Uses Selenium for browser automation and BeautifulSoup for HTML parsing.
    """
    
    # Setup Chrome options for "headless" mode.
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # This is the modern way to run Selenium.
    service = ChromeService(ChromeDriverManager().install())
    
    # Initialize the Chrome driver.
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    title = None
    price = None
    
    try:
        print(f"Fetching URL: {url}")
        driver.get(url)
        time.sleep(5) 
        
        page_html = driver.page_source
        soup = BeautifulSoup(page_html, 'html.parser')
        
        # --- TITLE SCRAPING WITH DEBUGGING ---
        # Find the product title element by its tag (h1) and class name.
        title_element = soup.find('h1', class_=TITLE_CLASS)
        
        # DEBUG: See the raw title element that was found.
        print(f"DEBUG: Raw title element found: {title_element}")
        
        if title_element:
            # DEBUG: See the text inside the element before cleaning.
            print(f"DEBUG: Raw title text: '{title_element.text}'")
            title = title_element.text.strip()
        else:
            print(f"Warning: Could not find title with tag 'h1' and class '{TITLE_CLASS}'")
            title = "Title Not Found"

        # --- PRICE SCRAPING WITH DEBUGGING ---
        # Find the product price element by its tag (span) and class name.
        price_element = soup.find('span', class_=PRICE_CLASS)

        # DEBUG: See the raw price element that was found.
        print(f"DEBUG: Raw price element found: {price_element}")
        
        if price_element:
            # DEBUG: See the text inside the element before cleaning.
            print(f"DEBUG: Raw price text: '{price_element.text}'")
            price_str = price_element.text.strip().replace('Rs. ', '').replace(',', '')
            price = int(price_str) if price_str.isdigit() else 0
        else:
            print(f"Warning: Could not find price with class '{PRICE_CLASS}'")
            price = 0

        return title, price
        
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return "Scraping Error", 0
    finally:
        driver.quit()