import threading
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import logging
import csv
import json
from datetime import datetime


options = webdriver.ChromeOptions()
options.add_argument("--disable-logging")
options.add_argument("--headless")

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

def load_elements(driver):
    print("Scrolling to load elements...")
    last_height = driver.execute_script("return document.body.scrollHeight")          #Implementin the scroll function to fetch all code
    adaptive_wait_time = 0.5

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(adaptive_wait_time)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            try:
                WebDriverWait(driver, 3).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "img"))
                )
                break
            except Exception as e:
                logging.warning(f"Error while waiting for elements: {e}")
                break
        else:
            last_height = new_height
            adaptive_wait_time = min(adaptive_wait_time + 0.1, 2)

    print("All elements, including images, should now be fully loaded.")

def html(driver, file_index):                                                      #Setting the html source code in a html file
    try:
        print(f"Extracting HTML content for file index {file_index}...")
        load_elements(driver)
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
    except Exception as e:
        logging.error(f"Error in html function: {e}")

def convert_to_csv(file_path, file_index):                                      #convert the html code to relevent csv file with relevent details using web scrapping
    try:
        print(f"Converting HTML to CSV for file index {file_index}...")
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
    except Exception as e:
        logging.error(f"Error in convert_to_csv function: {e}")

def fetch_and_save_to_csv(url, file_index):
    try:
        print(f"Opening WebDriver for URL: {url}")
        with webdriver.Chrome(options=options) as driver:
            print(f"WebDriver started for URL: {url}")
            driver.get(url)
            print(f"Loading page: {url}")
            html_path = html(driver, file_index)
            csv_path = convert_to_csv(html_path, file_index)
        return csv_path
    except Exception as e:
        logging.error(f"Error in fetch_and_save_to_csv function for URL {url}: {e}")

def compare(file_list, log_file="change.log", json_file="change.json"):
    try:
        print("Comparing files for changes...")
        added_rows = []
        deleted_rows = []
        modified_rows = []

        
        with open(file_list[0], 'r', encoding='utf-8') as f1, open(file_list[1], 'r', encoding='utf-8') as f2:
            csv1 = list(csv.DictReader(f1))
            csv2 = list(csv.DictReader(f2))

        
        csv1_set = {frozenset(row.items()) for row in csv1}
        csv2_set = {frozenset(row.items()) for row in csv2}

       
        added_rows = [dict(row) for row in (csv2_set - csv1_set)]
        deleted_rows = [dict(row) for row in (csv1_set - csv2_set)]

        csv1_dict = {row["Tag"]: row for row in csv1 if "Tag" in row}
        csv2_dict = {row["Tag"]: row for row in csv2 if "Tag" in row}

        common_tags = set(csv1_dict.keys()) & set(csv2_dict.keys())
        for tag in common_tags:
            row1 = csv1_dict[tag]
            row2 = csv2_dict[tag]

            changes = {}
            for field in ["Title", "Class", "ID"]:
                if row1.get(field) != row2.get(field):
                    changes[field] = {"Old": row1.get(field, ""), "New": row2.get(field, "")}

            if changes:  
                modified_rows.append({"Tag": tag, "Changes": changes})

        print("Logging changes to file...")
        with open(log_file, 'w', encoding='utf-8') as log:
            log.write("===== CHANGE LOG =====\n\n")

            log.write(f"Added Rows ({len(added_rows)}):\n")
            for row in added_rows:
                log.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Added: {row}\n")
            log.write("\n")

            log.write(f"Deleted Rows ({len(deleted_rows)}):\n")
            for row in deleted_rows:
                log.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Deleted: {row}\n")
            log.write("\n")

            log.write(f"Modified Rows ({len(modified_rows)}):\n")
            for row in modified_rows:
                log.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Modified Tag: {row['Tag']}\n")
                for field, change in row["Changes"].items():
                    log.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {field}: Old: '{change['Old']}', New: '{change['New']}'\n")
            log.write("\n")

            if len(added_rows)+len(deleted_rows)+len(modified_rows)==0:
                log.write(f"No changes detected.\n")
            log.write("===== SUMMARY =====\n")
            log.write(f"Total rows added: {len(added_rows)}\n")
            log.write(f"Total rows deleted: {len(deleted_rows)}\n")
            log.write(f"Total rows modified: {len(modified_rows)}\n")
            log.write(f"Total rows modified: {len(added_rows)+len(deleted_rows)+len(modified_rows)}\n")

        print("Saving changes to JSON file...")
        changes_summary = {
            "AddedRows": added_rows,
            "DeletedRows": deleted_rows,
            "ModifiedRows": modified_rows,
            "Summary": {
                "TotalAdded": len(added_rows),
                "TotalDeleted": len(deleted_rows),
                "TotalModified": len(modified_rows),
                "TotalChanges": len(added_rows)+len(deleted_rows)+len(modified_rows)
            }
        }
        with open(json_file, 'w', encoding='utf-8') as json_out:
            json.dump(changes_summary, json_out, indent=4)

        logging.info(f"Comparison complete. Check {log_file} and {json_file} for details.")

    except Exception as e:
        logging.error(f"Error in compare function: {e}")

def main(url1, url2): 
    try:
        print("Setting up data directory...")
        if not os.path.exists("data"):
            os.makedirs("data")

        print("Starting threads for URL fetching...")                                   #Space Complexity- O(N)
        thread1 = threading.Thread(target=fetch_and_save_to_csv, args=(url1, 0))        #Time Complexity-O(N)
        thread2 = threading.Thread(target=fetch_and_save_to_csv, args=(url2, 1))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        print("Completed fetching tags in real time for both URLs.")
        compare(["data/test0.csv", "data/test1.csv"])
    except Exception as e:
        logging.error(f"Error in main function: {e}")

# if __name__ == "__main__":
#     url1 = "https://www.jiocinema.com/"
#     url2 = "https://www.jiocinema.com/tv-shows"
#     main(url1, url2)

if __name__ == "__main__":
    url1 = "https://www.geeksforgeeks.org/"
    url2 = "https://www.geeksforgeeks.org/"
    main(url1, url2)

    

    


