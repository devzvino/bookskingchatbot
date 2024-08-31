# invoice_processing.py

from flask import session, send_file
from twilio.twiml.messaging_response import MessagingResponse
import json
import os
from invoice_data import extract_invoice_data
from invoice_bot import create_confirmation_message, generate_invoice_pdf, check_missing_fields


def save_transaction(user_id, invoice_id, amount):
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
    )
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (user_id, invoice_id, amount, transaction_date) VALUES (%s, %s, %s, %s)",
        (user_id, invoice_id, amount, datetime.now())
    )
    conn.commit()
    conn.close()


def process_invoice_request(incoming_msg):
    """
    Process the invoice request based on incoming message.
    """
    invoice_data = extract_invoice_data(incoming_msg)
    missing_fields = check_missing_fields(invoice_data)

    if missing_fields:
        return f"Please provide the following missing details: {', '.join(missing_fields)}", None

    confirmation_message = create_confirmation_message(invoice_data)
    session['invoice_data'] = json.dumps(invoice_data)  # Store invoice data as JSON in the session
    return confirmation_message + "\n\nPlease confirm to proceed  \n1. Proceed \n2. Cancel", 'confirm'


def confirm_invoice(incoming_msg):
    """
    Confirm the invoice and generate PDF if confirmed.
    """
    if incoming_msg == '1':
        invoice_data = json.loads(session.get('invoice_data', '{}'))
        generate_invoice_pdf(invoice_data, user)

        pdf_path = os.path.join(os.getcwd(), 'invoice.pdf')

        if os.path.exists(pdf_path):
            return "Your invoice has been generated.", pdf_path
        else:
            return "Invoice not found. Please ensure the file exists in the root directory.", None

    elif incoming_msg == '2':
        return "Invoice creation cancelled. Please start over by typing 'hi' or 'hello'.", None
    else:
        return "Invalid input. Please type 'confirm' to proceed or 'cancel' to cancel.", None
