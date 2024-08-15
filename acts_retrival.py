import os
import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor

# Function to parse the laws from the fetched text
def parse_laws(text):
    law_entries = text.strip().split('\n')
    law_list = []

    for entry in law_entries:
        law_name = re.match(r'^(.*) 第', entry).group(1).strip()
        ordinals = re.findall(r'第 ([^條]+) 條', entry)[0]
        ordinal_list = [o.strip() for o in ordinals.split('、')]
        for ordinal in ordinal_list:
            law_list.append((law_name, ordinal))

    return law_list

# Function to initialize the Selenium WebDriver
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless Chrome (no GUI)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Function to fetch and parse laws for a given 判決字號

def fetch_and_parse_laws(driver, case_id):
    prefix = 'https://judgment.judicial.gov.tw/FJUD/data.aspx?ty=JD&id='
    suffix = case_id
    url = prefix + suffix
    
    max_retries = 20  # Maximum number of retries
    sleep_duration = 1  # Sleep duration between retries
    
    for attempt in range(max_retries):
        driver.get(url)
        time.sleep(sleep_duration)

        try:
            law_div = driver.find_element(By.ID, "JudrelaLaw")
            laws = law_div.find_elements(By.TAG_NAME, 'li')

            law_list = []
            if laws:
                for law in laws:
                    law_list += parse_laws(law.text)
                if law_list:  # If law_list is not empty, return it
                    return law_list
            # If the list is still empty, retry
        except Exception as e:
            print("Error on attempt", attempt + 1, ":", str(e))
            print("Case ID:", case_id)
        
        # If max retries reached, return an empty list
    print("Max retries reached for Case ID:", case_id)
    return []


# Function to process a single CSV file
def process_file(filename):
    driver = init_driver()
    filepath = os.path.join(embedded_dir, filename)
    df = pd.read_csv(filepath)
    if df['acts'].astype(str).str.len().any():
        return
    # Add a new 'acts' column by fetching and parsing laws for each 判決字號
    df['acts'] = df['判決字號'].apply(lambda x: fetch_and_parse_laws(driver, x))

    # Save the updated DataFrame with the original filename
    df.to_csv(filepath, index=False)
    
    # Rename the file by prefixing with '@'
    new_filename = '@' + filename
    new_filepath = os.path.join(embedded_dir, new_filename)
    os.rename(filepath, new_filepath)
    print(f"Processed and saved as: {new_filename}")

    driver.quit()

# Directory where the CSV files are stored
embedded_dir = '../acts'

# Get the list of CSV files to process
csv_files = [f for f in os.listdir(embedded_dir) if f.endswith('.csv')]

# Process files in parallel using a ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=16) as executor:
    executor.map(process_file, csv_files)
