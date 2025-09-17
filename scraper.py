from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def save_jobs_to_file(jobs, path, append=False):
    df = pd.DataFrame(jobs)

    if append and os.path.exists(path):
        try:
            existing = pd.read_csv(path)
            df = pd.concat([existing, df], ignore_index=True)
        except pd.errors.EmptyDataError:
            pass

    df.to_csv(path, index=False)
    df.to_json(path.replace('.csv', '.json'), orient='records', force_ascii=False)
    df.to_excel(path.replace('.csv', '.xlsx'), index=False)



def get_naukri_jobs(query, location, page=1, save=True):
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")  
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/119.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)

    
    query = query.replace(" ", "-").lower()
    location = location.replace(" ", "-").lower()
    url = f"https://www.naukri.com/{query}-jobs-in-{location}?page={page}"

    driver.get(url)
    time.sleep(5)  

    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    jobs = []
    for job in soup.find_all("div", class_="cust-job-tuple"):
        title = job.find("a", class_="title").get_text(strip=True) if job.find("a", class_="title") else "N/A"
        company_tag = job.find("a", class_="comp-name") or job.find("span", class_="comp-dtls")
        company = company_tag.get_text(strip=True) if company_tag else "N/A"
        link = job.find("a", class_="title").get("href") if job.find("a", class_="title") else "#"
        location_tag=job.find("span", class_="locWdth")
        location = location_tag.get_text(strip=True) if location_tag else "Not specified"
        jobs.append({"title": title, "company": company, "location": location ,"link": link})

    
    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("✅ Saved debug_page.html for inspection")

    driver.quit()

    
    if save and jobs:
        save_jobs_to_file(jobs, os.path.join(OUTPUT_FOLDER, "jobs.csv"), append=True)
        print(f"💾 Saved {len(jobs)} jobs to {OUTPUT_FOLDER}/jobs.csv")

    return jobs
