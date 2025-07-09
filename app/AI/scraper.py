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
    """
    Uses Selenium to fetch and extract the main job description and qualifications from a job posting URL.
    Looks for 'About the role' and 'About you' sections.
    """
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

        jd_div = soup.find("div", attrs={"data-automation-id": "jobPostingDescription"})  # Workday
        if jd_div is None:
            jd_div = soup.find("div", class_="jobsearch-JobComponent-description")  # Indeed fallback

        description = None
        qualifications = None

        if jd_div:
            collecting_desc = False
            desc_lines = []
            for elem in jd_div.descendants:
                if hasattr(elem, "get_text"):
                    text = elem.get_text(strip=True).lower()
                    if "responsibilit" in text and not collecting_desc:
                        collecting_desc = True
                        continue
                    if collecting_desc and ("about you" in text or "workday pay transparency" in text or "our approach to flexible work" in text):
                        break
                    if collecting_desc and elem.name in ["p", "ul", "ol", "li"]:
                        line = elem.get_text(separator=" ", strip=True)
                        if line and line not in desc_lines:
                            desc_lines.append(line)
            if desc_lines:
                description = "\n".join(desc_lines)

            collecting_qual = False
            qual_lines = []
            for elem in jd_div.descendants:
                if hasattr(elem, "get_text"):
                    text = elem.get_text(strip=True).lower()
                    if "about you" in text and not collecting_qual:
                        collecting_qual = True
                        continue
                    if collecting_qual and ("workday pay transparency" in text or "our approach to flexible work" in text):
                        break
                    if collecting_qual and elem.name in ["p", "ul", "ol", "li"]:
                        line = elem.get_text(separator=" ", strip=True)
                        if line and line not in qual_lines:
                            qual_lines.append(line)
            if qual_lines:
                qualifications = "\n".join(qual_lines)

        full_text = description or ""
        if qualifications:
            full_text += f"\n\nQualifications:\n{qualifications}"

        return {
            "description": description,
            "qualifications": qualifications,
            "full_text": full_text.strip()
        }
    finally:
        driver.quit()

def scrape_job_description(url: str) -> str:
    """
    Scrape and return the full job description including qualifications as a single string.
    """
    result = fetch_job_description_and_qualifications(url)
    return result["full_text"]
