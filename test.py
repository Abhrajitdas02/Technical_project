import pandas as pd
import os
import time
import threading
import json
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
options.add_argument("--disable-logging")
options.add_argument("--headless")
options.add_argument("--log-level=1")
options.add_experimental_option("excludeSwitches", ["enable-logging"])

# Load dynamic content
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

def compare_csv_advanced(file1, file2, log_file="change.log", json_file="change.json"):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Identify added/removed rows
    added = pd.concat([df1, df2]).drop_duplicates(keep=False)
    removed = pd.concat([df2, df1]).drop_duplicates(keep=False)

    # Compare the DataFrames
    differences = df1.compare(df2)

    # Log changes to change.log
    with open(log_file, "w", encoding="utf-8") as log:
        log.write("===== CHANGE LOG =====\n\n")
        log.write(f"Added rows ({len(added)}):\n")
        log.write(f"{added}\n\n")
        
        log.write(f"Removed rows ({len(removed)}):\n")
        log.write(f"{removed}\n\n")
        
        log.write(f"Modified values:\n{differences}\n")
        if len(added) == 0 and len(removed) == 0 and differences.empty:
            log.write("No changes detected.\n")
        log.write("===== SUMMARY =====\n")
        log.write(f"Total rows added: {len(added)}\n")
        log.write(f"Total rows removed: {len(removed)}\n")
        log.write(f"Total modified: {len(differences)}\n")

    # Store the data in JSON file
    change_data = {
        "Added Rows": added.to_dict(orient="records"),
        "Removed Rows": removed.to_dict(orient="records"),
        "Modified Values": differences.to_dict(orient="records"),
        "Summary": {
            "Total rows added": len(added),
            "Total rows removed": len(removed),
            "Total modified": len(differences)
        }
    }

    with open(json_file, "w", encoding="utf-8") as json_output:
        json.dump(change_data, json_output, indent=4, ensure_ascii=False)
    
    print(f"Comparison complete. Check {log_file} and {json_file} for details.")

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

    # Compare the CSV data for differences using the updated compare_csv_advanced function
    compare_csv_advanced(f"data/test0.csv", f"data/test1.csv", log_file="change.log", json_file="change.json")

if __name__ == "__main__":
    url1 = "https://www.jiocinema.com/"
    url2 = "https://www.jiocinema.com/tv-shows"
    main(url1, url2)
