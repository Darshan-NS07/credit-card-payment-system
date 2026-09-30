# Credit Card Payment System

## Overview

Credit Card Payment System is a backend application developed using Django, FastAPI, and MySQL.

The application allows users to register, log in, manage their cards, make payments, and view their transaction history.

Django is used for authentication, card management, transaction management, and the admin panel. FastAPI is used for payment processing. Both backends use the same MySQL database.

For security, the application does not store complete card numbers or CVV values. Only masked card information and the last four digits of the card are stored.

> Payment processing in this project is simulated and does not connect to a real payment gateway.

---

## Features

- User registration and login
- JWT-based authentication
- JWT access and refresh tokens
- Token refresh
- Secure logout with refresh-token blacklisting
- User profile API
- Add, view, and delete cards
- Card number validation using the Luhn algorithm
- Card expiry validation
- Card ownership validation
- Card number masking
- Last four digits storage
- No CVV storage
- FastAPI payment processing
- PENDING, SUCCESS, and FAILED payment statuses
- Transaction history
- Transaction filtering
- Transaction detail API
- Admin-only CSV transaction export
- Django admin panel
- Daily transaction summary
- MySQL database
- Automated backend tests
- Postman API testing
- FastAPI Swagger documentation
- Docker support

---

## Technology Stack

### Backend

- Python
- Django
- Django REST Framework
- FastAPI
- SQLAlchemy
- Pydantic
- JWT

### Database

- MySQL

### Testing

- Pytest
- Pytest-Django
- Pytest-Cov

### API Testing

- Postman
- FastAPI Swagger / OpenAPI

### Development Tools

- Git
- GitHub
- VS Code
- Command Prompt

---

## System Architecture

```text
                         React Frontend
                              |
                +-------------+-------------+
                |                           |
                v                           v
         Django Backend              FastAPI Backend
                |                           |
       +--------+---------+                  |
       |        |         |                  |
      Auth    Cards   Transactions        Payments
       |        |         |                  |
       +--------+---------+------------------+
                         |
                         v
                       MySQL
```

---

## Project Structure

```text
credit_card_payment_system/
│
├── django_backend/
│   ├── config/
│   ├── users/
│   ├── cards/
│   ├── transactions/
│   ├── admin_panel/
│   ├── templates/
│   ├── pytest.ini
│   └── manage.py
│
├── fastapi_backend/
│   ├── core/
│   ├── database/
│   ├── routes/
│   ├── schemas/
│   ├── services/
│   └── main.py
│
├── tests/
│
├── docker/
│
├── venv/
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup and Installation

### 1. Clone the Repository

```bash
git clone <your-github-repository-url>
cd credit_card_payment_system
```

### 2. Create and Activate Virtual Environment

Create the virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```cmd
venv\Scripts\activate
```

### 3. Install Required Packages

```bash
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

```env
DJANGO_SECRET_KEY=your-django-secret
DB_NAME=credit_card_payment_db
DB_USER=root
DB_PASSWORD=mysql-password
DB_HOST=localhost
DB_PORT=3306
JWT_SECRET_KEY=your-jwt-secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

Do not commit the `.env` file to GitHub.

### 5. Create the MySQL Database

Create the database:

```sql
CREATE DATABASE credit_card_payment_db;
```

Both Django and FastAPI use this database.

### 6. Run Django Migrations

Move to the Django backend directory:

```cmd
cd django_backend
```

Run the migrations:

```cmd
python manage.py migrate
```

### 7. Start Django Backend

From the `django_backend` directory:

```cmd
python manage.py runserver
```

Django runs on:

```text
http://127.0.0.1:8000/
```

The Django admin panel is available at:

```text
http://127.0.0.1:8000/admin/
```

### 8. Start FastAPI Backend

Open another Command Prompt window.

Activate the virtual environment from the project root:

```cmd
venv\Scripts\activate
```

Move to the FastAPI backend directory:

```cmd
cd fastapi_backend
```

Start the FastAPI server:

```cmd
uvicorn main:app --reload --port 8001
```

FastAPI runs on:

```text
http://127.0.0.1:8001/
```

FastAPI provides interactive API documentation through Swagger:

```text
http://127.0.0.1:8001/docs
```

---

## Authentication

The application uses JWT authentication for protected APIs.

After successful login, the user receives an access token and a refresh token.

The access token must be sent in the request header when accessing protected APIs:

```text
Authorization: Bearer <access_token>
```

### Authentication APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register a new user |
| POST | `/api/auth/login/` | Login and obtain JWT tokens |
| POST | `/api/auth/token/refresh/` | Refresh the access token |
| GET | `/api/auth/profile/` | View the logged-in user's profile |
| POST | `/api/auth/logout/` | Logout and blacklist the refresh token |

---

## Card Management

Users can add, view, and delete their cards.

The application validates the card number using the Luhn algorithm and validates the expiry date.

Complete card numbers and CVV values are not stored in the database. Only the masked card number and last four digits are stored.

### Card APIs

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/cards/` | View user's cards |
| POST | `/api/cards/` | Add a card |
| DELETE | `/api/cards/<card_id>/` | Delete a card |

---

## Payment Processing

Payment processing is handled by FastAPI.

Before processing a payment, the API verifies that the card belongs to the logged-in user.

Payment processing is simulated and does not connect to a real payment gateway.

The transaction is initially created with `PENDING` status and then updated to either `SUCCESS` or `FAILED`.

### Payment API

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/payments/` | Process a payment |

Example request:

```json
{
    "card_id": 1,
    "amount": 5500,
    "currency": "INR"
}
```

Example response:

```json
{
    "message": "Payment processed successfully",
    "transaction_id": 1,
    "transaction_reference": "example-reference",
    "amount": 5500.0,
    "currency": "INR",
    "status": "SUCCESS",
    "failure_reason": null
}
```

---

## Transaction Management

Users can view their own transaction history.

Users cannot access transactions belonging to other users.

### Transaction APIs

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/transactions/` | View transaction history |
| GET | `/api/transactions/<transaction_id>/` | View transaction details |
| GET | `/api/transactions/export-csv/` | Export transactions as CSV |

Transactions can be filtered using:

- `status`
- `min_amount`
- `max_amount`
- `start_date`
- `end_date`

Example:

```text
/api/transactions/?status=SUCCESS
```

Another example:

```text
/api/transactions/?min_amount=1000&max_amount=10000
```

The CSV export endpoint is restricted to admin users.

---

## Admin Panel

Django Admin is used to manage users, cards, and transactions.

Admin URL:

```text
http://127.0.0.1:8000/admin/
```

The admin panel also provides a daily transaction summary.

The daily summary includes:

- Total transactions
- Successful transactions
- Failed transactions
- Pending transactions
- Total successful transaction amount

---

## Security

The application includes the following security measures:

- Passwords are stored using Django's password hashing.
- JWT authentication is required for protected APIs.
- JWT and Django secret keys are loaded from environment variables.
- Complete card numbers are not stored.
- CVV values are not stored.
- Card numbers are masked.
- Card ownership is checked before payment processing.
- Users can access only their own cards and transactions.
- Admin-only operations are protected.
- Database operations use Django ORM and SQLAlchemy ORM.
- `.env` is excluded through `.gitignore`.
- Database operations use ORM-based queries to help protect against SQL injection.
- JWT refresh tokens can be blacklisted during logout.

---

## Testing

Automated tests were added for authentication, card management, transactions, and payment processing.

### Django Tests

From the `django_backend` directory:

```cmd
python -m pytest
```

Current Django test result:

```text
34 passed
```

Django test coverage:

```text
93%
```

### FastAPI Payment Tests

The FastAPI payment module has automated tests covering payment processing and validation.

Current FastAPI payment test result:

```text
6 passed
```

FastAPI payment test coverage:

```text
84%
```

---

## Postman Testing

Postman was used to test the main APIs, including:

- User registration
- Login
- JWT authentication
- Profile
- Token refresh
- Logout
- Card management
- Payment processing
- Transaction history
- Transaction filters
- Transaction details
- CSV export
- Unauthorized access
- Card ownership validation

The Postman collection will be included with the final project submission.

---

## API Documentation

FastAPI provides interactive Swagger documentation through OpenAPI.

Swagger URL:

```text
http://127.0.0.1:8001/docs
```

The Swagger interface can be used to:

- View available endpoints
- View request schemas
- View response schemas
- Test FastAPI APIs
- Understand API parameters

Django APIs can be tested using Postman.

---

## Docker

Docker support is planned for containerizing the application.

The planned services are:

- Django
- FastAPI
- MySQL

Docker Compose will be used to run the services together.

Docker setup will be completed and tested before the final submission.

---

## Database

The application uses MySQL as the primary database.

The main database areas are:

- Users
- Cards
- Transactions

Django manages the application database models and migrations.

FastAPI uses SQLAlchemy to interact with the same MySQL database.

---

## Environment Variables

The application uses environment variables for configuration and sensitive information.

The main environment variables are:

| Variable | Description |
|---|---|
| `DJANGO_SECRET_KEY` | Django secret key |
| `DB_NAME` | MySQL database name |
| `DB_USER` | MySQL username |
| `DB_PASSWORD` | MySQL password |
| `DB_HOST` | MySQL host |
| `DB_PORT` | MySQL port |
| `JWT_SECRET_KEY` | JWT signing secret |
| `DEBUG` | Django debug setting |
| `ALLOWED_HOSTS` | Allowed Django hosts |

The `.env` file must not be committed to GitHub.

---

## Development URLs

### Django

```text
http://127.0.0.1:8000/
```

### Django Admin

```text
http://127.0.0.1:8000/admin/
```

### FastAPI

```text
http://127.0.0.1:8001/
```

### FastAPI Swagger

```text
http://127.0.0.1:8001/docs
```



## Screenshots

Screenshots demonstrating the project functionality are available in the `screenshoots` folder.

The screenshots include:
- Django Admin
- User management
- Card management
- Transaction management
- Daily transaction summary
- FastAPI Swagger/API documentation
- API testing and payment flow