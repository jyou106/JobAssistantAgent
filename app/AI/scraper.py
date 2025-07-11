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
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Job boards
        possible_divs = [
            {"attrs": {"data-automation-id": "jobPostingDescription"}},       # Workday
            {"class_": "jobsearch-JobComponent-description"},                 # Indeed
            {"class_": "description"},                                        # Greenhouse
            {"class_": "section page-centered"},                              # Lever
            {"id": "job-description"},                                        # generic
        ]

        jd_div = None
        for div_selector in possible_divs:
            jd_div = soup.find("div", **div_selector)
            if jd_div:
                break

        # Fallback: longest div
        if not jd_div:
            divs = soup.find_all("div")
            jd_div = max(divs, key=lambda d: len(d.get_text(strip=True)), default=None)

        if not jd_div:
            return {"description": None, "qualifications": None, "full_text": ""}

        lines = []
        for elem in jd_div.descendants:
            if elem.name in ["p", "li", "ul", "ol"] and hasattr(elem, "get_text"):
                line = elem.get_text(separator=" ", strip=True)
                if line and line not in lines:
                    lines.append(line)

        full_text = "\n".join(lines)
        return {"description": full_text, "qualifications": None, "full_text": full_text}

    finally:
        driver.quit()

def scrape_job_description(url: str) -> str:
    """
    Scrape and return the full job description including qualifications as a single string.
    """
    result = fetch_job_description_and_qualifications(url)
    return result["full_text"]
