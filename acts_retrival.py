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
    max_retries = 2  # Increase the number of retries
    sleep_duration = 2  # Increase sleep duration to allow more time between retries

    for attempt in range(max_retries):
        print(f"Attempt {attempt + 1} for case ID: {case_id} with URL: {url}")
        driver.get(url)
        time.sleep(sleep_duration)

        try:
            law_div = driver.find_element(By.ID, "JudrelaLaw")
            laws = law_div.find_elements(By.TAG_NAME, 'li')

            law_list = []
            if laws:
                for law in laws:
                    parsed_laws = parse_laws(law.text)
                    print(f"Parsed laws for {case_id}: {parsed_laws}")
                    law_list += parsed_laws
                if law_list:  # If law_list is not empty, return it
                    return law_list
            else:
                print(f"No laws found in attempt {attempt + 1} for {case_id}.")
        except Exception as e:
            print(f"Error on attempt {attempt + 1} for {case_id}: {str(e)}")
            continue

    # Max retries reached, returning empty list
    print(f"Max retries reached for {case_id}. Returning empty list.")
    return []


# Function to process a single CSV file
def process_file(filename):
    driver = init_driver()
    filepath = os.path.join(embedded_dir, filename)
    temp_filepath = filepath + ".temp"
    df = pd.read_csv(filepath)

    # If the 'acts' column doesn't exist, initialize it with empty lists
    if 'acts' not in df.columns:
        df['acts'] = [[] for _ in range(len(df))]

    # Fetch and parse laws for rows where 'acts' column is empty
    for index, row in df.iterrows():
        try:
            if not row['acts'] or pd.isna(row['acts']) or row['acts'] == "[]":
                print(f"Fetching laws for: {row['判決字號']}")  # Debugging print
                df.loc[index, 'acts'] = fetch_and_parse_laws(driver, row['判決字號'])
                print(f"Result for {row['判決字號']}: {df.loc[index, 'acts']}")  # Debugging print

            # Intermediate saving to avoid data loss
            if index % 100 == 0:  # Save every 100 records
                df.to_csv(temp_filepath, index=False)
                os.remove(filepath)  # Remove the original file
                os.rename(temp_filepath, filepath)  # Rename the temp file to the original file
                print(f"Intermediate save after {index + 1} rows.")

        except Exception as e:
            print(f"Error processing row {index} for {row['判決字號']}: {e}")
            continue

    # Final save after processing all rows
    df.to_csv(temp_filepath, index=False)
    os.remove(filepath)  # Remove the original file
    os.rename(temp_filepath, filepath)  # Rename the temp file to the original file
    print(f"Processed and saved: {filename}")

    driver.quit()

# Directory where the CSV files are stored
embedded_dir = '../acts'

# Get the list of CSV files to process
csv_files = [f for f in os.listdir(embedded_dir) if f.endswith('.csv')]

# Process files in parallel using a ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=16) as executor:
    executor.map(process_file, csv_files)
