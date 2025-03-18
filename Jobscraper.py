from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import pandas as pd
import time


def setup_driver():
    options = Options()
    # if you want to Run in headless mode 
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# To calculate date from hours ago 
def calculate_date_from_hours_ago(hours_ago):
    return (datetime.now() - timedelta(hours=hours_ago)).strftime("%m/%d/%Y %H:%M")

# Initialize WebDriver
driver = setup_driver()
wait = WebDriverWait(driver, 10)  

try:
    # Step 1: Copy and paste link from from seek 
    driver.get('')
    driver.maximize_window()

    # Step 2: Input keyword into the search bar (Which job that you wanna scrape)
    search_bar = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="keywords-input"]')))
    search_bar.send_keys("General Practitioner")

    # Step 3: if you want to add any classifiacation or else just commment it
    classification_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//label[@data-automation="classificationDropDownList"]')))
    classification_dropdown.click()

    # Step 4: Select "Healthcare & Medical"
    healthcare_option = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="classificationsPanel"]/nav/ul/li[15]/a/span/span[1]')))
    healthcare_option.click()

    # Step 5: Click somewhere to close dropdown
    driver.find_element(By.XPATH, '//*[@id="SearchBar"]').click()
    time.sleep(2)  # Small delay to ensure dropdown closes

    # Step 6: Click on the "Date Listed" dropdown to set the dat as you need 
    date_listed_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@data-automation="toggleDateListedPanel"]')))
    date_listed_dropdown.click()
    time.sleep(2)  
    
    # Step 7: Select "Last 30 days" radio button
    last_30_days_option = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="RefineDateListed__radiogroup-6"]/a/span/span')))
    last_30_days_option.click()
    time.sleep(2)  # Allow the selection to apply

    # Step 6: Click the search button
    search_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="searchButton"]')))
    search_button.click()

    # Step 8: Allow results page to load
    wait.until(EC.presence_of_element_located((By.XPATH, '//article')))

    jobs = []
    max_pages = 50  # Limit scraping to 50 pagesn (set you limit as you want)
    current_page = 1

    while current_page <= max_pages:
        print(f"Scraping page {current_page}...")
        job_cards = driver.find_elements(By.XPATH, '//article')

        for card in job_cards:
            try:
                title = card.find_element(By.XPATH, './/a[@data-automation="jobTitle"]').text.strip()
                company = card.find_element(By.XPATH, './/a[@data-automation="jobCompany"]').text.strip()
                location = card.find_element(By.XPATH, './/span[@data-automation="jobLocation"]').text.strip()
                job_link = "https://www.seek.co.au" + card.find_element(By.XPATH, './/a[@data-automation="jobTitle"]').get_attribute('href')

                try:
                    profession = card.find_element(By.XPATH, './/span[@data-automation="jobSubClassification"]').text.strip()
                except:
                    profession = "N/A"

                try:
                    classification = card.find_element(By.XPATH, './/span[@data-automation="jobClassification"]').text.strip()
                except:
                    classification = "N/A"

                try:
                    salary = card.find_element(By.XPATH, './/span[@data-automation="jobSalary"]').text.strip()
                except:
                    salary = "Not Provided"

                try:
                    posted_date_text = card.find_element(By.XPATH, './/span[@data-automation="jobListingDate"]').text.strip()
                    if "h ago" in posted_date_text:
                        hours_ago = int(posted_date_text.replace("h ago", "").strip())
                        posted_date = calculate_date_from_hours_ago(hours_ago)
                    else:
                        posted_date = posted_date_text
                except:
                    posted_date = "Unknown"

                jobs.append({
                    'Title': title,
                    'Company': company,
                    'Location': location,
                    'Classification': classification,
                    'Profession': profession,
                    'Salary': salary,
                    'Posted Date': posted_date,
                    'Link': job_link
                })
            except Exception as e:
                print(f"Error processing a job card: {e}")

        try:
            # Step 8: Click on the next page button (if available)
            next_page_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[6]/div/section/div[2]/div/div/div[1]/div/div/div/div/div[1]/div/div[2]/div/nav/ul/li[3]/a/span')))
            next_page_button.click()
            current_page += 1
            wait.until(EC.presence_of_element_located((By.XPATH, '//article')))
        except:
            print("No more pages available.")
            break

    # Step 9: Save results to CSV
    df = pd.DataFrame(jobs)
    df.to_csv('Scraped_data.csv', index=False)
    print("Job data saved to Scraped_data.csv")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
