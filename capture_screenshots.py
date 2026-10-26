"""
Script to capture screenshots for Task 3 and Task 7 using Selenium.
Saves:
- 03-admin-site.png
- 07-final.png
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions


def get_driver():
    # Try Edge first (default on Windows)
    try:
        options = EdgeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1400,1050")
        options.add_argument("--disable-gpu")
        driver = webdriver.Edge(options=options)
        print("Using Microsoft Edge WebDriver.")
        return driver
    except Exception as e:
        print(f"Edge initialization failed: {e}. Trying Chrome...")

    # Fallback to Chrome
    try:
        options = ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1400,1050")
        options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=options)
        print("Using Google Chrome WebDriver.")
        return driver
    except Exception as e:
        print(f"Chrome initialization failed: {e}")
        raise


def capture():
    driver = get_driver()
    try:
        # Task 3: Admin Site Screenshot
        print("Navigating to Django admin login...")
        driver.get("http://127.0.0.1:8000/admin/login/?next=/admin/")
        time.sleep(1)

        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")
        username_input.send_keys("admin")
        password_input.send_keys("admin123")
        password_input.submit()
        time.sleep(2)

        # Ensure on admin dashboard
        driver.get("http://127.0.0.1:8000/admin/")
        time.sleep(1)
        driver.save_screenshot("03-admin-site.png")
        print("Saved Task 3 screenshot: 03-admin-site.png")

        # Task 7: Final Exam Result Screenshot
        print("Navigating to student login...")
        driver.get("http://127.0.0.1:8000/onlinecourse/login/")
        time.sleep(1)

        user_input = driver.find_element(By.NAME, "username")
        psw_input = driver.find_element(By.NAME, "psw")
        user_input.send_keys("student")
        psw_input.send_keys("student123")
        psw_input.submit()
        time.sleep(2)

        print("Navigating to exam result page...")
        driver.get("http://127.0.0.1:8000/onlinecourse/course/1/submission/1/result/")
        time.sleep(1)
        driver.save_screenshot("07-final.png")
        print("Saved Task 7 screenshot: 07-final.png")

    finally:
        driver.quit()


if __name__ == '__main__':
    capture()
