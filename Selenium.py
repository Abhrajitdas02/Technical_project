import threading
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import csv
import hashlib
from bs4 import BeautifulSoup
import pandas as pd


options = webdriver.ChromeOptions()
options.add_argument("--disable-logging")
options.add_argument("--headless")

def load_all_images(driver, max_wait_time=30, pause_time=3):
   start_time = time.time()
   last_height = driver.execute_script("return document.body.scrollHeight")

   while time.time() - start_time < max_wait_time:
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            time.sleep(2)
            new_height = driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
        last_height = new_height

   print("All elements, including images, should now be fully loaded.")


def html(driver, file_index):
    load_all_images(driver)
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
                data_dict['Title'].append(tag.get_text(strip=True).strip(
                    '"') if not tag.find_all(True) else '')
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


def compare(file_list, log_file="change.log"):
    count = 0
    with open(file_list[0], 'r', encoding='utf-8') as f1, open(file_list[1], 'r', encoding='utf-8') as f2:
        f1_lines = f1.readlines()
        f2_lines = f2.readlines()
    with open(log_file, "w", encoding="utf-8") as log:
        for row1 in f1_lines:
            if row1 not in f2_lines:
                count += 1
                log.write(f"Tag removed: {row1.strip()}\n")

        for row2 in f2_lines:
            if row2 not in f1_lines:
                count += 1
                log.write(f"Tag added: {row2.strip()}\n")
        if count == 0:
            log.write("No changes detected, Automation test Passed!!\n")
        else:
            log.write(f"Total changes detected: {count}\n")
        print(f"Comparison complete. Check {log_file} for details.")


def main(url1, url2):
    if not os.path.exists("data"):
        os.makedirs("data")

    thread1 = threading.Thread(target=fetch_and_save_to_csv, args=(url1, 0))
    thread2 = threading.Thread(target=fetch_and_save_to_csv, args=(url2, 1))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    print("Completed fetching tags in real time for both URLs.")

    compare([f"data/test0.csv", f"data/test1.csv"], log_file="change.log")


if __name__ == "__main__":
    url1 = "https://www.jiocinema.com/"
    url2 = "https://www.jiocinema.com/tv-shows"
    main(url1, url2)