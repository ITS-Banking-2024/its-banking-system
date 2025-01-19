# ITS-BANK

## Project Overview
This project is a **Banking System** that includes key features such as:

1. **Account Management**:
   - Checking, Savings, and Custody account types with unique functionality.
2. **Stock Trading**:
   - Buy and sell stocks via a custody account.
   - Real-time stock price updates using `yfinance`.
3. **Transaction History**:
   - View transaction history for all account types.
4. **Web Interface**:
   - User-friendly UI for customer actions like making transactions, viewing transaction history, savings deposit/withdrawal, stock market interactions, and ATM transactions.
5**ATM Transactions**:
   - Withdrawal support for Checking accounts via PIN-based authentication.

## Features


### 1. Stock Trading
- Custody account holders can:
  - Buy stocks based on available funds.
  - Sell stocks they currently own.
- Real-time stock prices are fetched using the `yfinance` API.
- The stock market dashboard provides detailed portfolio information, including profit/loss calculations.

### 2. Savings Transactions
- Deposit and withdrawal functionality for Savings Accounts.
- Reference accounts (linked Checking Accounts) are used for transactions.

### 3. Transaction History
- Users can view their transaction history filtered by timeframes (e.g., 30 days, 60 days, or all-time).
- For transactions made via ATM, the history reflects "ATM withdrawal" for clarity.

### 4. ATM Transactions
- ATM transactions are restricted to **Checking Accounts**.
- PIN authentication is required to authorize ATM transactions.
- Users can withdraw or deposit money using the ATM interface.

---

## Testing the UI

### **0. Customer creating and account opening (optional)**
- Navigate to admin page by entering the URL:
  ```
  http://127.0.0.1:8000/admin/
  ```
- Default admin credentials:
```
 username: admin
 password: admin
```
- Admin page is meant to be used by the bank officials on bank premises to add customers and open accounts

### **1. Access Customer Dashboard & Account Details**
- For testing the default user can be used:
 ```
 username: user1
 password: user1   
 ```
- Navigate to the customer's dashboard page by entering the URL:
  ```
  http://127.0.0.1:8000/customers/dashboard/
  ```
- Actions available:
  - Select which account you want to interact with.
  - Open account details page by clicking on the specific account

#### Checking Account
- Actions available:
  - View account details
  - Create new transaction (test by sending preferred amount to an existing checking account of another customer: c9e76ebf-8702-48f1-bc6b-7262e8525196)
  - View transaction history filtered by timeframes (e.g., 30 days, 60 days, or all-time).
 
#### Savings Account
- Actions available:
  - View account details
  - Deposit money from reference checking account to savings account
  - Withdraw money from savings account to reference checking account

#### Custody Account
- Actions available:
  - View account details
  - Interact with the Stock Market
  - View stock transaction history


### **3. Stock Trading**
#### Stock Market Dashboard
- Features:
  - View available stocks and their prices in the Discover Tab. Only the stocks that the bank offers are available for purchase. By the default the bank owns these 5 stocks ("AAPL", "MSFT", "GOOGL", "AMZN", "TSLA")
  - Access the portfolio to check owned stocks, quantities, and total value.
  - Buy and sell stocks.


### **4. Mock ATM**
- Navigate to the mock ATM transaction page using the Mock ATM button in the Checking Account details page or using the link:
  ```
  http://127.0.0.1:8000/accounts/64429150-1b19-41db-97e9-17a7bbe2d05f/atm_transaction/
  ```
- Features:
  - Enter PIN and the desired transaction amount.
  - Submit the transaction and view the success/failure screen.

#### **Postman Request for Testing**
- **Method**: `POST`
- **URL**: `http://127.0.0.1:8000/accounts/64429150-1b19-41db-97e9-17a7bbe2d05f/atm_transaction/`
- **Headers**:
  - `Content-Type`: `application/json`
- **Body (JSON)**:
  ```json
  {
    "pin": "1234",
    "amount": 100.0
  }
  ```


# SWD Django Demo
The project can be used as a reference for the SWD lab course.
This project consists of several apps with a focus on loose coupling and dependency injection.
A good article about separation of concerns in Django projects can be found `https://emcarrio.medium.com/business-logic-in-a-django-project-a25abc64718c`.
Good Django tutorials can be found `https://www.djangoproject.com/start/` or `https://cs50.harvard.edu/web/2020/weeks/3/`.

## Requirements
You need to have a working python installation on your local system. Best-Practise is to use python from the official website: https://www.python.org/.
Please use the **latest 3.11** version available (https://www.python.org/downloads/). 

Notice: The version 3.12 seems NOT to be compatible with the dependency-injector-package (https://python-dependency-injector.ets-labs.org/main/changelog.html)


## Installation

1. Clone the repository. `git clone git@its-git.fh-salzburg.ac.at:SWD/djangodemo.git` or `git clone https://its-git.fh-salzburg.ac.at/SWD/djangodemo.git`
2. Install Poetry: `https://python-poetry.org/docs/#installation`
   - Mac/Linux: `curl -sSL https://install.python-poetry.org | python3 -`
   - Windows (Powershell): `(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -`
     - Note: On Windows sometimes `python` does not work in the shell but the alias `py` does!
     - Note: When you want to exectue python in a shell and the Windows App-Store opens - you need to deactive this Windows-Behavior: https://stackoverflow.com/questions/58754860/cmd-opens-windows-store-when-i-type-python
     - Note: On Windows you have to add poetry to the path: `%APPDATA%\Python\Scripts`

### Usage

1. Activate the virtual environment: `poetry shell`.
2. Install dependencies with the projects main directory: `poetry install`.
3. Create the database tables: `python manage.py migrate`
4. Create an admin user: `python manage.py createsuperuser`
5. Run unit tests: `python manage.py test -v 2`
6. Run the development server: `python manage.py runserver`.
7. Open the website in your browser: `http://localhost:8000/admin`, `http://localhost:8000/products`.

## IDE
There are a number of IDEs available for python development. You can choose between different variants like [VSCode](https://code.visualstudio.com/), [PyCharm](https://www.jetbrains.com/pycharm/), [VIM](https://realpython.com/vim-and-python-a-match-made-in-heaven/), ...

## Dependency Injection
This project uses the python dependency injection module, which is not part of Django itself.
`https://python-dependency-injector.ets-labs.org/examples/django.html`



