from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import re
import threading
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()
options.add_argument("--disable-logging")
options.add_argument("--headless")
options.add_argument("--log-level=1")
options.add_experimental_option("excludeSwitches", ["enable-logging"])

def load_dynamic_content(driver, max_wait_time=60):
    def scroll_and_wait():
        last_height = driver.execute_script("return document.body.scrollHeight")
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for images and ads to load
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    scroll_and_wait()
    time.sleep(2)  
    images = driver.find_elements(By.TAG_NAME, "img")

    for img in images:
        driver.execute_script("arguments[0].scrollIntoView();", img)
        try:
            WebDriverWait(driver, 5).until(lambda d: img.get_attribute("complete") == "true")
        except Exception:
            print(f"Image did not load: {img.get_attribute('src')}")

    print("All elements, including dynamic images and ads, should now be fully loaded.")


def html(driver, file_index):
    load_dynamic_content(driver)

    page_source = driver.page_source
    cleaned_source = re.sub(r'<(script|style).*?>.*?</\1>', '', page_source, flags=re.DOTALL)
    soup = BeautifulSoup(cleaned_source, 'html.parser')

    body_content = soup.body
    body_html = str(body_content) if body_content else ""
    file_path = f"data/elements{file_index}.html"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(body_html)
    
    print(f"Page source saved successfully as {file_path}.")
    return file_path


def convert_to_csv(file_path, file_index):
    data_dict = {'Tag': [], 'Title': [], 'Class': [], 'ID': []}

    with open(file_path, "r", encoding="utf-8") as f:
        html_doc = f.read()
        soup = BeautifulSoup(html_doc, 'html.parser')
        for tag in soup.find_all(True):
            data_dict['Tag'].append(tag.name)
            if tag.name == 'img':
                data_dict['Title'].append(tag.get('alt', '').strip('"'))
            else:
                data_dict['Title'].append(tag.get_text(strip=True).strip('"') if not tag.find_all(True) else '')
            data_dict['Class'].append(tag.get('class', None))
            data_dict['ID'].append(tag.get('id', None))
    df = pd.DataFrame(data=data_dict)
    csv_path = f"data/test{file_index}.csv"
    df.to_csv(csv_path, index=False)
    print(f"Data saved successfully as {csv_path}.")
    return csv_path


def fetch_and_save_to_csv(url, file_index):
    with webdriver.Chrome(options=options) as driver:
        driver.get(url)
        html_path = html(driver, file_index)
        csv_path = convert_to_csv(html_path, file_index)
    return csv_path


def compare(file_list, log_file="change.log", key_column="Tag", fields_to_compare=["Class", "Title","ID"]):
    added_count = 0
    removed_count = 0
    modified_count = 0

    # Read the first CSV file into a dictionary by the key column
    with open(file_list[0], 'r', encoding='utf-8') as f1:
        reader1 = csv.DictReader(f1)
        data1 = {row[key_column]: row for row in reader1}

    # Read the second CSV file into a dictionary by the key column
    with open(file_list[1], 'r', encoding='utf-8') as f2:
        reader2 = csv.DictReader(f2)
        data2 = {row[key_column]: row for row in reader2}

    # Open the log file for writing changes
    with open(log_file, "w", encoding="utf-8") as log:
        # Check for removed tags (present in data1 but not in data2)
        for key in data1:
            if key not in data2:
                removed_count += 1
                log.write(f"Tag removed: {data1[key]}\n")

        # Check for added tags (present in data2 but not in data1)
        for key in data2:
            if key not in data1:
                added_count += 1
                log.write(f"Tag added: {data2[key]}\n")
                
            # Check for modified tags (same key in both, but differing fields)
            else:
                modified_fields = {}
                for field in fields_to_compare:
                    if data1[key].get(field) != data2[key].get(field):
                        modified_fields[field] = {
                            "file1": data1[key].get(field),
                            "file2": data2[key].get(field)
                        }

                if modified_fields:
                    modified_count += 1
                    log.write(f"Tag modified for {key}:\n")
                    for field, changes in modified_fields.items():
                        log.write(f"  {field}: {changes['file1']} -> {changes['file2']}\n")
        
        # Summary of changes
        total_changes = added_count + removed_count + modified_count
        if total_changes == 0:
            log.write("No changes detected, Automation test Passed!!\n")
        else:
            log.write(f"Total changes detected: {total_changes}\n")
            log.write(f"  Tags added: {added_count}\n")
            log.write(f"  Tags removed: {removed_count}\n")
            log.write(f"  Tags modified: {modified_count}\n")

    print(f"Comparison complete. Check {log_file} for details.")


def main(url1, url2):
    if not os.path.exists("data"):
        os.makedirs("data")

    # Create threads to fetch and save CSV data for both URLs
    thread1 = threading.Thread(target=fetch_and_save_to_csv, args=(url1, 0))
    thread2 = threading.Thread(target=fetch_and_save_to_csv, args=(url2, 1))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    print("Completed fetching tags in real time for both URLs.")

    # Compare the CSV data for differences
    compare([f"data/test0.csv", f"data/test1.csv"], log_file="change.log")


if __name__ == "__main__":
    url1 = "https://www.jiocinema.com/"
    url2 = "https://www.jiocinema.com/tv-shows"
    main(url1, url2)
