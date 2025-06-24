import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading
import os
import re
import json


driver_lock = threading.Lock()
confirmation_received = threading.Event()


options = uc.ChromeOptions()
profile_directory = f"Profile"
if not os.path.exists(profile_directory):
    os.makedirs(profile_directory)

with driver_lock:
    options.user_data_dir = profile_directory
    try:
        driver = uc.Chrome(options=options)
    except Exception:
        print(f"Lỗi")
        time.sleep(180)
        exit()

driver.maximize_window()

problem_list = []

for page_num in range(1, 6):
    driver.get(f"http://oj.28tech.com.vn/organization/8-ngon-ng-lp-trinh-python/problems/?order=-solved&page={page_num}")
    driver.execute_script("document.body.style.zoom='25%'")

    problem_table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "problem-table"))
    )

    table_body_rows = problem_table.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")

    for table_row in table_body_rows:
        solved_cell = table_row.find_element(By.CLASS_NAME, "solved")
        if solved_cell.get_attribute("solved") == "1":
            problem_name_element = table_row.find_element(By.CLASS_NAME, "problem-name")
            href = problem_name_element.find_element(By.TAG_NAME, "a").get_attribute("href")
            problem_name = problem_name_element.text
            problem_name = re.sub(r'Bài \d+\.\s*', '', problem_name)
            category = table_row.find_element(By.CLASS_NAME, "category").text

            problem_list.append({
                "href": href,
                "problem_name": problem_name,
                "category": category
            })
# ---------------------------------------------------------------------------------------------------------------------

for problem_item in problem_list:
    try:
        driver.get(problem_item["href"])
        driver.execute_script("document.body.style.zoom='25%'")

        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "raw_problem"))
        )

        description_div = driver.find_element(By.XPATH, "//iframe[@id='raw_problem']/following-sibling::div[1]")

        copy_buttons = description_div.find_elements(By.CLASS_NAME, "copy-clipboard")
        for copy_btn in copy_buttons:
            try:
                driver.execute_script("arguments[0].remove()", copy_btn)
            except:
                pass

        problem_item["description"] = description_div.text.strip()

        try:
            my_submissions_link = driver.find_element(By.XPATH, "//a[text()='My submissions']")
            submissions_url = my_submissions_link.get_attribute("href")
            driver.get(submissions_url)
            driver.execute_script("document.body.style.zoom='25%'")
        except:
            problem_item["source_href"] = ""
            problem_item["source_code"] = ""
            continue

        try:
            submission_row_list = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((
                    By.XPATH, "//div[contains(@class, 'submission-row')]"
                ))
            )

            for submission_row in submission_row_list:
                try:
                    result_cell = submission_row.find_element(By.CLASS_NAME, "sub-result")
                    if "AC" in result_cell.get_attribute("class"):
                        source_link = submission_row.find_element(By.XPATH, ".//div[@class='sub-prop']//a[contains(@href, '/src/')]")
                        source_href = source_link.get_attribute("href")
                        problem_item["source_href"] = source_href

                        driver.get(source_href)
                        driver.execute_script("document.body.style.zoom='25%'")

                        source_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".source-wrap code"))
                        )
                        problem_item["source_code"] = source_element.text.strip()
                        break
                except:
                    pass
            else:
                problem_item["source_href"] = ""
                problem_item["source_code"] = ""
        except:
            problem_item["source_href"] = ""
            problem_item["source_code"] = ""
    except:
        pass
# ---------------------------------------------------------------------------------------------------------------------

driver.get("http://oj.28tech.com.vn/organization/8-ngon-ng-lp-trinh-python/contests/")
driver.execute_script("document.body.style.zoom='25%'")

try:
    contest_table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "contest-list.table.striped"))
    )

    contest_table_rows = contest_table.find_elements(By.TAG_NAME, "tr")
    contest_link_list = []

    for contest_table_row in contest_table_rows:
        try:
            contest_block_link = contest_table_row.find_element(By.CLASS_NAME, "contest-block").find_element(By.TAG_NAME, "a")
            contest_href = contest_block_link.get_attribute("href")
            if contest_href:
                contest_link_list.append(contest_href)
        except:
            pass
except:
    contest_link_list = []
# ---------------------------------------------------------------------------------------------------------------------

for contest_url in contest_link_list:
    try:
        driver.get(contest_url)
        driver.execute_script("document.body.style.zoom='25%'")
        contest_problem_table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "contest-problems"))
        )

        contest_problem_rows = contest_problem_table.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")

        for contest_problem_row in contest_problem_rows:
            try:
                problem_a = contest_problem_row.find_element(By.CSS_SELECTOR, "td:nth-child(3) a")
                href = problem_a.get_attribute("href")
                problem_name = problem_a.text.strip()
                problem_name = re.sub(r'Bài \d+\.\s*', '', problem_name)
                category = ""
                problem_list.append({
                    "href": href,
                    "problem_name": problem_name,
                    "category": category
                })
            except:
                pass
    except:
        pass
# ---------------------------------------------------------------------------------------------------------------------

for problem_item in problem_list:
    try:
        driver.get(problem_item["href"])
        driver.execute_script("document.body.style.zoom='25%'")
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "raw_problem"))
        )
        description_div = driver.find_element(By.XPATH, "//iframe[@id='raw_problem']/following-sibling::div[1]")
        copy_buttons = description_div.find_elements(By.CLASS_NAME, "copy-clipboard")
        for copy_btn in copy_buttons:
            try:
                driver.execute_script("arguments[0].remove()", copy_btn)
            except:
                pass
        problem_item["description"] = description_div.text.strip()
        try:
            my_submissions_link = driver.find_element(By.XPATH, "//a[text()='My submissions']")
            submissions_url = my_submissions_link.get_attribute("href")
            driver.get(submissions_url)
            driver.execute_script("document.body.style.zoom='25%'")
        except:
            problem_item["source_href"] = ""
            problem_item["source_code"] = ""
            continue
        try:
            submission_row_list = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((
                    By.XPATH, "//div[contains(@class, 'submission-row')]"
                ))
            )
            for submission_row in submission_row_list:
                try:
                    result_cell = submission_row.find_element(By.CLASS_NAME, "sub-result")
                    if "AC" in result_cell.get_attribute("class"):
                        source_link = submission_row.find_element(By.XPATH, ".//div[@class='sub-prop']//a[contains(@href, '/src/')]")
                        source_href = source_link.get_attribute("href")
                        problem_item["source_href"] = source_href
                        driver.get(source_href)
                        driver.execute_script("document.body.style.zoom='25%'")
                        source_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".source-wrap code"))
                        )
                        problem_item["source_code"] = source_element.text.strip()
                        break
                except:
                    pass
            else:
                problem_item["source_href"] = ""
                problem_item["source_code"] = ""
        except:
            problem_item["source_href"] = ""
            problem_item["source_code"] = ""
    except:
        pass

with open("Dataset/dataset.json", "w", encoding="utf-8") as f:
    json.dump(problem_list, f, ensure_ascii=False, indent=2)

driver.quit()
