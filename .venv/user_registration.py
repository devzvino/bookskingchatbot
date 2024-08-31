# user_registration.py

import mysql.connector
import os
from werkzeug.utils import secure_filename
import requests


def is_new_user(phone_number):
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE phone_number = %s", (phone_number,))
    user = cursor.fetchone()
    conn.close()
    return user is None


def register_user(phone_number, name, company_name, email, logo_path):
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
    )
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO users (phone_number, name, company_name, email, logo_path)
    VALUES (%s, %s, %s, %s, %s)
    """, (phone_number, name, company_name, email, logo_path))

    conn.commit()
    conn.close()


def validate_phone_number(phone_number):
    import re
    pattern = re.compile(r'^\+\d{10,15}$')
    return pattern.match(phone_number)


def download_file(url, file_path):
    """
    Download a file from a URL and save it to a specified path.
    """
    try:
        response = requests.get(url, auth=HTTPBasicAuth(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        ))
        response.raise_for_status()  # Raise an exception for HTTP errors
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully to {file_path}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")