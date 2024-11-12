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


options = webdriver.ChromeOptions()
options.add_argument("--disable-logging")
options.add_argument("--headless")

logging.basicConfig(filename='change.log', level=logging.INFO, format='%(asctime)s - %(message)s')

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

def convert_to_csv(file_path, file_index):                                        #convert the html code to relevent csv file with relevent details using web scrapping
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

def compare(file_list, log_file="change.log"):
    try:
        print("Comparing files for changes...")
        count = 0
        added_tags = []
        deleted_tags = []
        modified_tags = []

        with open(file_list[0], 'r', encoding='utf-8') as f1, open(file_list[1], 'r', encoding='utf-8') as f2:
            f1 = [line.strip() for line in f1.readlines()]
            f2= [line.strip() for line in f2.readlines()]

        f1_set = set(f1)
        f2_set = set(f2)

        added_tags = list(f2_set - f1_set)
        deleted_tags = list(f1_set - f2_set)

        for line in f1_set & f2_set:
            if f1.count(line) != f2.count(line):
                modified_tags.append(line)
                count += 1

        print("Logging changes to file...")
        logging.info("===== CHANGE LOG =====")

        logging.info(f"Added Tags ({len(added_tags)}):")
        for tag in added_tags:
            logging.info(f"  - {tag}")
        
        logging.info("")

        logging.info(f"Deleted Tags ({len(deleted_tags)}):")
        for tag in deleted_tags:
            logging.info(f"  - {tag}")

        logging.info("")

        logging.info(f"Modified Tags ({len(modified_tags)}):")
        for tag in modified_tags:
            logging.info(f"  - {tag}")

        if count == 0:
            logging.info("No changes detected.")

        logging.info("===== SUMMARY =====")
        logging.info(f"Total tags added: {len(added_tags)}")
        logging.info(f"Total tags deleted: {len(deleted_tags)}")
        logging.info(f"Total tags modified: {len(modified_tags)}")
        logging.info(f"Total changes detected: {len(added_tags) + len(deleted_tags) + len(modified_tags)}")


        print(f"Comparison complete. Check {log_file} for details.")
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

if __name__ == "__main__":
    url1 = "https://www.jiocinema.com/"
    url2 = "https://www.jiocinema.com/tv-shows"
    main(url1, url2)

# if __name__ == "__main__":
#     url1 = "https://www.geeksforgeeks.org/"
#     url2 = "https://www.geeksforgeeks.org/"
#     main(url1, url2)
    
# if __name__ == "__main__":
#     url1 = "https://www.geeksforgeeks.org/"
#     url2 = "https://www.geeksforgeeks.org/"
#     main(url1, url2)


