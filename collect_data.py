# goes links and collects data
from selenium import webdriver
import time, os
import pandas as pd
from parse import parse_html_document

SLEEP_TIME = 1.9

driver = webdriver.Chrome(executable_path='C:\\Projects\\IP\\Bot\\IndividualProject\\chromedriver.exe')
os.chdir('tasks')
folders = os.listdir()
correct_numbers = [4]

for folder in folders:
    os.chdir(folder)
    folder_number = int(folder[4:])
    try:
        url_list = open(f'task{folder_number}_urls.txt', 'r', encoding='utf-8')
    except FileNotFoundError:
        print(f'task{folder_number}_urls.txt does not exists')
        os.chdir('..')
        continue

    if folder_number not in correct_numbers:
        os.chdir('..')
        continue
        
    result_file = open(f'task{folder_number}.html', 'w+', encoding='utf-8')
    html_code = ""

    for url in url_list:
        print(url)
        driver.get(url=url)
        last_height = driver.execute_script('return document.body.scrollHeight')

        while True:
            # Scroll down to bottom
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(SLEEP_TIME)
            new_height = driver.execute_script('return document.body.scrollHeight')
            driver.execute_script('window.scrollTo(document.body.scrollHeight, document.body.scrollHeight - 500);')
            time.sleep(SLEEP_TIME/2)
            if new_height == last_height:
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                html_code = driver.page_source
                result_file.write(html_code)
                break
            last_height = new_height

    data = parse_html_document(f'task{folder_number}.html')
    data.to_csv(f'task{folder_number}.csv', index=None)
    os.chdir('..')
            
driver.close()
driver.quit()