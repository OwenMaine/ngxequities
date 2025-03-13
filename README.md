# Nigerian Stock Market Price List API

## Introduction

This project provides a web-based dashboard and API for getting and displaying stock market data from the Nigerian Stock Exchange . The data includes company names, previous closing prices, opening prices, highs, lows, closing prices, changes, trades, volumes, values, and trade dates. The application is built using Flask, Selenium, and Bootstrap.

## Features

- **Web-based Dashboard**: A user-friendly interface to view the scraped stock market data.
- **API Endpoints**: Provides data in JSON format and a downloadable CSV file.
- **JWT Authentication**: Secures the API endpoints using JSON Web Tokens (JWT).

## Technologies Used

- **Flask**: A micro web framework for Python.
- **Selenium**: A browser automation tool.
- **Bootstrap**: A front-end framework for responsive web design.
- **Flask-JWT-Extended**: A Flask extension for JWT integration.

## Setup and Installation

### Prerequisites

- Python 3.6 or higher
- Chrome WebDriver
- Flask and other required Python libraries

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/owenmaine/ngxequities.git
   cd stock-market-dashboard
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Environment Variables**:
   Set the `FLASK_APP` environment variable to point to the main application file.
   ```bash
   export FLASK_APP=app.py
   ```

4. **Run the Application**:
   ```bash
   python ngx.py
   ```

## Application Structure

- **ngx.py**: The main Flask application file.
- **templates/index.html**: The HTML template for the dashboard.

## API Endpoints

### Authentication

#### Login
- **Endpoint**: `/login`
- **Method**: `POST`
- **Description**: Authenticates a user and returns a JWT.
- **Request Body**:
  ```json
  {
    "username": "testuser",
    "password": "password123"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "your_jwt_token"
  }
  ```

### Data Retrieval

#### Get Data
- **Endpoint**: `/api/data`
- **Method**: `GET`
- **Description**: Retrieves the scraped stock market data in JSON format.
- **Headers**:
  ```json
  {
    "Authorization": "Bearer your_jwt_token"
  }
  ```
- **Response**:
  ```json
  [
    {
      "Company": "Company A",
      "Previous Closing Price": "100",
      "Opening Price": "101",
      "High": "102",
      "Low": "99",
      "Close": "101",
      "Change": "1",
      "Trades": "500",
      "Volume": "10000",
      "Value": "1000000",
      "Trade Date": "2025-03-12"
    },
    ...
  ]
  ```

#### Download CSV
- **Endpoint**: `/api/csv`
- **Method**: `GET`
- **Description**: Downloads the scraped stock market data as a CSV file.
- **Headers**:
  ```json
  {
    "Authorization": "Bearer your_jwt_token"
  }
  ```
- **Response**: A CSV file containing the stock market data.

## How to Use the API

### Public Usage

1. **Authenticate**:
   - Send a POST request to `/login` with your username and password to receive a JWT.
2. **Access Data**:
   - Use the JWT received from the login step to access the protected endpoints `/api/data` and `/api/csv` by including it in the `Authorization` header of your requests.

### Example

#### Using `curl`:

```bash
# Login and get token
token=$(curl -X POST http://127.0.0.1:5000/login -H "Content-Type: application/json" -d '{"username": "testuser", "password": "password123"}' | jq -r .access_token)

# Get data
curl -X GET http://127.0.0.1:5000/api/data -H "Authorization: Bearer $token"

# Download CSV
curl -X GET http://127.0.0.1:5000/api/csv -H "Authorization: Bearer $token" --output equities_data.csv
```

#### Using Python:

```python
import requests

# Login and get token
login_url = 'http://127.0.0.1:5000/login'
login_data = {
    'username': 'testuser',
    'password': 'password123'
}
login_response = requests.post(login_url, json=login_data)
token = login_response.json()['access_token']

# Get data
data_url = 'http://127.0.0.1:5000/api/data'
headers = {
    'Authorization': f'Bearer {token}'
}
data_response = requests.get(data_url, headers=headers)
print(data_response.json())

# Download CSV
csv_url = 'http://127.0.0.1:5000/api/csv'
csv_response = requests.get(csv_url, headers=headers)
with open('equities_data.csv', 'wb') as f:
    f.write(csv_response.content)
```

This documentation provides a comprehensive guide to set up, run, and use the Nigerian Stock Market Price List API. For further questions or issues, please refer to the [GitHub repository](https://github.com/owenmaine/ngxequities) or contact the project maintainers.
