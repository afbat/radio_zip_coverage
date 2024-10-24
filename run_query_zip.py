import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pyautogui

# in terminal run `safaridriver --enable` to enable safari automation
# test driver with `safaridriver --version`

# create webdriver
driver = webdriver.Safari()

# Load CSV files for each as running independent searches 
call_signs = pd.read_csv('SET PATH/call_query.csv')
zip_codes = pd.read_csv('SET PATH/UP_zip_query.csv')

# navigate to page
url = "https://www.v-soft.com/on-line-based-software/zipsignal"

# Timeout value in seconds
timeout = 10

# prevent sleep
def stay_awake():
    pyautogui.press('shift')

# Start processing each zip code
print('Starting search for call signs available in each zip code')

for index, row in zip_codes.iterrows():
    zip_code = row['ZIP']
    time.sleep(1)  # Wait for a moment to avoid overwhelming the server
    
    # stay awake
    if index % 5 == 0: # run every 5 zips
        stay_awake()
    
    try:
        # Navigate to the page
        driver.get(url)
        
        # Wait for the zip code input field to appear and enter the zip code
        zip_field = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, 'zip'))
        )
        zip_field.clear()
        zip_field.send_keys(zip_code)

        # Wait for the submit button to appear and click it
        find_zip = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="findstations"]/p/input[2]'))
        )
        find_zip.click()
        
        # Function to process a table
        def process_table(table_index, table_type, zip_code):
            try:
                # Construct the XPath dynamically based on table index
                table_xpath = f'/html/body/center[1]/table/tbody/tr/td/center/table[{table_index}]/tbody'
                table = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, table_xpath))
                )
                print(f'Processing {table_type} Table for zip code: {zip_code}')
                
                # Get the first row as headers
                first_row = table.find_element(By.XPATH, './/tr[1]')
                headers = [cell.text for cell in first_row.find_elements(By.TAG_NAME, 'td')]
                
                # Get all subsequent rows as data
                rows = table.find_elements(By.XPATH, './/tr[position()>1]')
                data = [[cell.text for cell in row.find_elements(By.TAG_NAME, 'td')] for row in rows]
                
                print(f"{table_type} Headers: {headers}")
                print(f"{table_type} Data (first row): {data[0] if data else 'No data'}")
                
                # Validate header and row column count
                if data and len(headers) == len(data[0]):
                    df = pd.DataFrame(data, columns=headers)
                    df.to_csv(f'query_output/{table_type.lower()}_{zip_code}.csv', index=False)
                else:
                    print(f'Error with zip code {zip_code}: {table_type} headers and data do not match')
            
            except (TimeoutException, NoSuchElementException) as e:
                print(f'Error processing {table_type} table for zip code {zip_code}: {e}')
        
        # Process the FM and AM tables separately using their respective table indices
        process_table(1, "FM", zip_code)
        process_table(2, "AM", zip_code)
        
    except (TimeoutException, NoSuchElementException) as e:
        print(f'Error with zip code {zip_code}: {e}')

# Close the browser
driver.quit()
