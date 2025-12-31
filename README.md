# DevBlogg

DevBlogg is a CMS (Content Management System) inspired by dev.to, viblo, medium,... web application built with a Django REST Framework backend and a Vue frontend. It offers robust features for managing posts, comments, users, and user authentication, providing an intuitive and efficient user experience.

## Features
- **Core Functionality:**
- **Technical Features:**
	- REST API backend with Django REST Framework.
    - Token-based authentication using JWT and OAuth2.
	- Frontend SPA using Vue + Pinia + Vue Router, user-friendly and intuitive UI with Tailwind CSS.
    - Email Service: SMTP configuration supporting 2FA via App Passwords for robust security.
    - Modular and maintainable code structure for both frontend and backend.


## Installation & Setup
- Clone the Repository
```
git clone https://github.com/hahuy1708/DevBlogg.git
cd DevBlogg
```
### Backend
- Create and Activate virtualenv
```
cd backend
python -m venv venv
venv\Scripts\activate
```
- Install Dependencies
```
pip install -r requirements.txt
```
- Environment Configuration
    -  Create a `.env` file in the `backend/devblogg_backend/` directory with the following variables:
    ```
    DEBUG=True_or_False
    SECRET_KEY=your_django_secret_key

    DB_NAME=your_database_name
    DB_USER=your_database_user
    DB_PASSWORD=your_database_password
    DB_HOST=your_database_host
    DB_PORT=your_database_port
    
    EMAIL_HOST_USER=your_email_host
    EMAIL_HOST_PASSWORD=your_email_password
    EMAIL_HOST=your_email_host_address
    EMAIL_PORT=your_email_port
    EMAIL_USE_TLS=True_or_False
    ```
    See this [guide](https://www.geeksforgeeks.org/python/setup-sending-email-in-django-project/) for configuring your email sending service.
- Database Setup and Migrations
    1. Ensure MySQL is installed and running on your machine and run this command to create database:
    ```
    CREATE DATABASE your_database_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    ```
    2. Run Migrations
    ```
    cd backend/devblogg_backend
    python manage.py makemigrations
    python manage.py migrate
    ```
- How to run
```
python manage.py runserver
```