from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
from pydantic import BaseModel

class ScrapeJobInput(BaseModel):
    url: str

def fetch_job_description_and_qualifications(url: str) -> dict:
    options = Options()
    # Use new headless mode (harder to detect)
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    
    # Real browser user agent
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Hide automation flags
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Remove webdriver property from navigator
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        driver.get(url)
        time.sleep(5)  # Increased wait time
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Check if we got blocked
        page_text = driver.page_source.lower()
        if "temporarily down" in page_text or "moved permanently" in page_text or "access denied" in page_text:
            print(f"Warning: Site may be blocking the request for {url}")
            return {"description": None, "qualifications": None, "full_text": ""}

        # Job boards selectors
        possible_divs = [
            {"attrs": {"data-automation-id": "jobPostingDescription"}},       # Workday
            {"class_": "jobsearch-JobComponent-description"},                 # Indeed
            {"class_": "description"},                                        # Greenhouse
            {"class_": "section page-centered"},                              # Lever
            {"id": "job-description"},                                        # generic
            {"class_": "job-description"},                                    # common class
            {"class_": "jd"},                                                 # short for job description
        ]

        jd_div = None
        for div_selector in possible_divs:
            jd_div = soup.find("div", **div_selector)
            if jd_div:
                break

        # Fallback: longest div with job-related keywords
        if not jd_div:
            divs = soup.find_all("div")
            potential_divs = []
            for div in divs:
                text = div.get_text(strip=True).lower()
                if len(text) > 500 and any(keyword in text for keyword in ["job", "description", "responsibilities", "qualifications", "requirements"]):
                    potential_divs.append(div)
            
            if potential_divs:
                jd_div = max(potential_divs, key=lambda d: len(d.get_text(strip=True)))
            else:
                jd_div = max(divs, key=lambda d: len(d.get_text(strip=True)), default=None)

        if not jd_div:
            return {"description": None, "qualifications": None, "full_text": ""}

        lines = []
        for elem in jd_div.descendants:
            if elem.name in ["p", "li", "ul", "ol", "h1", "h2", "h3", "h4"] and hasattr(elem, "get_text"):
                line = elem.get_text(separator=" ", strip=True)
                if line and line not in lines:
                    lines.append(line)

        full_text = "\n".join(lines)
        return {"description": full_text, "qualifications": None, "full_text": full_text}

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {"description": None, "qualifications": None, "full_text": ""}
    
    finally:
        driver.quit()

def scrape_job_description(url: str) -> str:
    """
    Scrape and return the full job description including qualifications as a single string.
    """
    result = fetch_job_description_and_qualifications(url)
    return result["full_text"]