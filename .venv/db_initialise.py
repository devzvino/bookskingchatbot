# db_initialise.py

import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection credentials
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

def check_and_create_tables():
    # Establish the database connection
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()

    # SQL commands to check and create tables
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        phone_number VARCHAR(20) NOT NULL UNIQUE,
        name VARCHAR(255),
        company_name VARCHAR(255),
        email VARCHAR(255),
        logo_path VARCHAR(255),
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    create_transactions_table = """
    CREATE TABLE IF NOT EXISTS transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        invoice_id VARCHAR(50) NOT NULL,
        amount DECIMAL(10, 2) NOT NULL,
        transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """

    create_invoices_table = """
    CREATE TABLE IF NOT EXISTS invoices (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        company_name VARCHAR(255),
        client VARCHAR(255),
        date DATE,
        items TEXT,
        tax DECIMAL(10, 2),
        discounts DECIMAL(10, 2),
        terms TEXT,
        banking_details TEXT,
        pdf_path VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """

    # Execute the SQL commands
    try:
        cursor.execute(create_users_table)
        cursor.execute(create_transactions_table)
        cursor.execute(create_invoices_table)
        conn.commit()
        print("Tables checked and created if needed.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    check_and_create_tables()
