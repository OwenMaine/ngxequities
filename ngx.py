import time
import threading
import csv
from flask import Flask, jsonify, send_file, render_template, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_access_token'  # Change this!

jwt = JWTManager(app)

users = {
    "testuser": "password123"  # Example user
}



# Global variable to store scraped data from all pages
scraped_data = []
CSV_FILE = 'equities_data.csv'
URL = 'https://ngxgroup.com/exchange/data/equities-price-list/'

# Total number of pages to scrape (6 pages)
TOTAL_PAGES = 6

def scrape_current_page(driver):
    """Scrapes the table from the current page and returns a list of dictionaries."""
    data = []
    try:
        # Locate the element with id "content"
        content = driver.find_element(By.ID, "content")
    except NoSuchElementException:
        print("Content element with id 'content' not found.")
        return data

    try:
        # Locate the table within the content element
        table = content.find_element(By.TAG_NAME, "table")
    except NoSuchElementException:
        print("Table not found inside the content element.")
        return data

    # Extract table headers
    headers = []
    try:
        header_section = table.find_element(By.TAG_NAME, "thead")
        header_elems = header_section.find_elements(By.TAG_NAME, "th")
        headers = [elem.text.strip() for elem in header_elems]
    except Exception:
        # Fallback: if no <thead>, use first row as header.
        try:
            first_row = table.find_element(By.TAG_NAME, "tr")
            headers = [elem.text.strip() for elem in first_row.find_elements(By.TAG_NAME, "td")]
        except Exception as e:
            print("Could not extract headers:", e)
            return data

    # Extract table rows
    try:
        tbody = table.find_element(By.TAG_NAME, "tbody")
        rows = tbody.find_elements(By.TAG_NAME, "tr")
    except Exception:
        # Fallback if no <tbody> is available: use all rows excluding first (header)
        all_rows = table.find_elements(By.TAG_NAME, "tr")
        rows = all_rows[1:]
    
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if not cols:
            continue
        row_data = [col.text.strip() for col in cols]
        if len(row_data) < len(headers):
            continue
        data.append(dict(zip(headers, row_data)))
    
    return data

def scrape_all_pages():
    """Iterates through pages (up to TOTAL_PAGES) by clicking the 'Next' pagination button,
    and returns all scraped data from every page."""
    all_data = []
    driver = None
    current_page = 1
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=options)
        driver.get(URL)
        time.sleep(5)  # Allow time for JavaScript to render

        while current_page <= TOTAL_PAGES:
            page_data = scrape_current_page(driver)
            if page_data:
                all_data.extend(page_data)
                print(f"Scraped {len(page_data)} records on page {current_page}.")
            else:
                print(f"No records found on page {current_page}.")
            
            if current_page == TOTAL_PAGES:
                print("Reached the designated number of pages to scrape.")
                break

            # Try to find the "Next" button. Adjust the selector if necessary.
            try:
                next_button = driver.find_element(By.LINK_TEXT, "Next")
            except NoSuchElementException:
                print("No 'Next' button found; reached the last page.")
                break

            # Scroll into view and click the "Next" button using JavaScript to avoid interception.
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(5)  # Wait for the next page to load; adjust if needed.
            except ElementClickInterceptedException:
                print("Next button click was intercepted; attempting to remove overlay and retry.")
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(5)
            except Exception as e:
                print("Error clicking Next button:", e)
                break
            
            current_page += 1
        
    except Exception as e:
        print("Error during scraping all pages:", e)
    finally:
        if driver is not None:
            driver.quit()
    return all_data

def write_csv(data, headers):
    try:
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        print(f"CSV file '{CSV_FILE}' updated with {len(data)} records.")
    except Exception as e:
        print("Error writing CSV file:", e)

def scrape_data():
    global scraped_data
    data = scrape_all_pages()
    if not data:
        print("No data scraped from any page.")
        return
    scraped_data = data
    headers = list(data[0].keys())
    write_csv(data, headers)
    print(f"Total scraped records: {len(data)} at {time.strftime('%Y-%m-%d %H:%M:%S')}")

def continuous_scraping(interval=60):
    while True:
        scrape_data()
        time.sleep(interval)

@app.route('/')
def index():
    """Render the dashboard with the scraped data."""
    return render_template('index.html', data=scraped_data)

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username not in users or users[username] != password:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

@app.route('/api/data', methods=['GET'])
@jwt_required()
def get_data():
    return jsonify(scraped_data)

@app.route('/api/csv', methods=['GET'])
@jwt_required()
def get_csv():
    return send_file(CSV_FILE, as_attachment=True)

if __name__ == '__main__':
    # Start continuous scraping in a background thread.
    scraping_thread = threading.Thread(target=continuous_scraping, daemon=True)
    scraping_thread.start()
    
    # Start the Flask API server.
    app.run(host='0.0.0.0', port=5000)