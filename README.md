# Expense-Split-APIs
# User and Expense Management System

## Overview

This application is a Django-based platform for user and expense management, featuring custom user authentication and expense tracking with various splitting methods.

## Features

- User registration and authentication with JWT.
- Expense tracking with methods for splitting expenses equally, exactly, or by percentage.
- Calculation of total expenses for users.

## Installation

Follow these steps to set up and run the application:

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
### 2. Create a Virtual Environment
Create and activate a virtual environment to manage dependencies:
python -m venv env
source env/bin/activate  # On Windows use: env\Scripts\activate

 ### 3. Install Dependencies
Install the required packages using pip:

bash
Copy code
pip install -r requirements.txt

### 4. Configure the Database
Update your database settings in settings.py as needed. The default configuration uses SQLite. For PostgreSQL or MySQL, adjust the DATABASES setting accordingly.

### 5. Apply Migrations
Run the migrations to set up the database schema:

bash
Copy code
python manage.py migrate

### 6. Run the Development Server
Start the Django development server:

bash
Copy code
python manage.py runserver
The application will be accessible at http://127.0.0.1:8000/.

API Endpoints
Authentication
POST /signup/: Register a new user.
POST /login/: Authenticate a user and receive JWT tokens.

Expenses
POST /expenses/: Create a new expense (authenticated users only).

GET /expenses/<int:expense_id>/: Retrieve details of a specific expense created by the authenticated user.

GET /user/<int:user_id>/total-expenses/: Calculate and return the total expenses for a specific user.

Models
User
Custom user model with email or phone-based authentication.

Expense
Tracks expenses created by users, with fields for description, amount, split method, and more.

ExpenseSplit
Represents how an expense is shared among users, including amount, person, and percentage.

Serializers
UserSerializer: Serializes user data for API responses.
RegisterSerializer: Handles user registration and validation.
LoginSerializer: Handles user authentication and JWT token generation.
ExpenseSerializer: Serializes expense data, including splits.
ExpenseCreateSerializer: Handles creation of expenses with validation for split methods.
Views
SignUpView: Handles user registration.
LoginView: Manages user authentication.
ExpenseListCreateView: Lists and creates expenses.
UserExpenseDetailView: Provides details of a specific expense.
UserOverallExpensesView: Calculates total expenses for a user.
