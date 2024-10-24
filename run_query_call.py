import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pyautogui
import re
import os

# in terminal run `safaridriver --enable` to enable safari automation
# test driver with `safaridriver --version`

# create webdriver
driver = webdriver.Safari()

# Load CSV files for each as running independent searches 
call_signs = pd.read_csv('SET PATH/call_query.csv')

# remove station suffix
call_signs['call_sign'] = call_signs['call_sign'].str.replace(r'[-_].*', '', regex=True)

# navigate to page
url = "https://www.v-soft.com/on-line-based-software/zipsignal"

# Timeout value in seconds
timeout = 10


# Create directory for output if it doesn't exist
os.makedirs('query_output', exist_ok=True)

# Prevent sleep
def stay_awake():
    pyautogui.press('shift')

# Function to process the table and additional info
def process_table(call_sign, retry_count=0):
    try:
        # Get service, principal city, and FCC facility ID
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/center[1]/table/tbody/tr/td/center/p/font'))
        )
        text_content = element.text
        
        # Extract service
        service_match = re.search(r'Service:\s*(\w+)', text_content)
        service = service_match.group(1) if service_match else "Unknown"
        
        # Extract principal city
        city_match = re.search(r'Principal City:\s*([A-Z\s]+),\s*([A-Z]{2})', text_content)
        principal_city = f"{city_match.group(1).strip()}, {city_match.group(2).strip()}" if city_match else "Unknown"
        
        # Extract FCC facility ID
        fcc_id_match = re.search(r'FCC Facility ID:\s*(\d+)', text_content)
        fcc_facility_id = fcc_id_match.group(1) if fcc_id_match else "Unknown"
        
        # Show station info
        print(f"Station: {call_sign}, Service: {service}, Principal City: {principal_city}, FCC Facility ID: {fcc_facility_id}")

        # Construct the XPath dynamically based on table index
        table_xpath = '/html/body/center[1]/table/tbody/tr/td/center/table/tbody'
        table = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, table_xpath))
        )
        print(f'Processing Table for station: {call_sign}')
        
        # Get the first row as headers
        first_row = table.find_element(By.XPATH, './/tr[1]')
        headers = [cell.text for cell in first_row.find_elements(By.TAG_NAME, 'td')]
        
        # Get all subsequent rows as data
        rows = table.find_elements(By.XPATH, './/tr[position()>1]')
        data = [[cell.text for cell in row.find_elements(By.TAG_NAME, 'td')] for row in rows]
        
        print(f"Headers: {headers}")
        print(f"Data (first row): {data[0] if data else 'No data'}")
        
        # Validate header and row column count
        if data and len(headers) == len(data[0]):
            df = pd.DataFrame(data, columns=headers)
            
            # Assign station data directly to all rows
            df['service'] = service
            df['principal_city'] = principal_city
            df['fcc_facility_id'] = fcc_facility_id
            
            # Save the DataFrame to a CSV file
            df.to_csv(f'query_output/{call_sign}.csv', index=False)
        else:
            print(f'Error with station {call_sign}: headers and data do not match')
    
    except TimeoutException:
        print(f"Table not found for station {call_sign}. Checking for suggestions...")
        
        # Limit the number of retries to prevent getting stuck
        if retry_count >= 3:
            print(f"Max retries reached for station {call_sign}. Skipping...")
            return
        
        # Error page handling
        suggestions_xpath = '/html/body/center[1]/table/tbody/tr/td/center/br[3]/following-sibling::a[1]'
        try:
            first_suggestion = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, suggestions_xpath))
            )
            # Store the text of the first suggestion before clicking
            suggestion_text = first_suggestion.text
            print(f"Clicking the first suggestion: {suggestion_text}")
            first_suggestion.click()
            time.sleep(2)  # Wait for the page to load
            
            # Process table again with the stored suggestion text, incrementing retry count
            process_table(suggestion_text, retry_count + 1)
        except TimeoutException:
            print(f"No clickable suggestion found for station {call_sign}. Returning to main page.")
            driver.get(url)

    except NoSuchElementException as e:
        print(f'Error processing table for station {call_sign}: {e}')
    except StaleElementReferenceException as e:
        print(f'Stale element error for station {call_sign}: {e}')
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Start processing each call sign
print('Starting search for zip codes covered by query station')

for index, row in call_signs.iterrows():
    call_sign = row['call_sign']
    time.sleep(1)  # Wait for a moment to avoid overwhelming the server
    
    # Stay awake periodically
    if index % 5 == 0:
        stay_awake()
    
    try:
        # Navigate to the page
        driver.get(url)

        # Wait for the call sign input field to appear and enter the call sign
        call_field = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, 'call'))  # Adjust the ID if necessary
        )
        call_field.clear()
        call_field.send_keys(call_sign)

        # Wait for the submit button to appear and click it
        find_call = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="findzips"]/p[1]/input[2]'))  # Adjust XPath if necessary
        )
        find_call.click()

        # Process the table for the call sign
        process_table(call_sign)

    except (TimeoutException, NoSuchElementException) as e:
        print(f'Error with call sign {call_sign}: {e}')
        driver.get(url)  # Return to the main page if an error occurs

# Close the browser
driver.quit()
print('All station call signs processed successfully')
