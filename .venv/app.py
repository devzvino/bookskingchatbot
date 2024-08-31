# app.py

import os
from flask import Flask, request, jsonify, session, send_file
import mysql.connector
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from user_registration import is_new_user, register_user, validate_phone_number, download_file
from invoice_processing import process_invoice_request, confirm_invoice, save_transaction
from werkzeug.utils import secure_filename
from db_initialise import check_and_create_tables  # Import the initialization function

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

# Initialize database tables
check_and_create_tables()


def get_user_id(phone_number):
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM users WHERE phone_number = %s", (phone_number,))
    user = cursor.fetchone()
    conn.close()
    return user['id'] if user else None


def register_new_user(from_number):
    session['phone_number'] = from_number
    return (
        "Welcome! Please provide the following details to complete your registration:\n"
        "1. Your Name\n"
        "2. Company Name\n"
        "3. Email\n"
        "4. Company Logo (send as a file attachment)."
    )


@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.form.get('Body', '').strip()
    from_number = request.form.get('From', '').replace("whatsapp:", "")

    response = MessagingResponse()
    msg = response.message()

    # Validate phone number
    if not validate_phone_number(from_number):
        msg.body("Invalid phone number format. Please use the format: +1234567890")
        return str(response)

    # Check if user is new
    if is_new_user(from_number):
        print(from_number)
        if 'phone_number' not in session:
            msg.body(register_new_user(from_number))
            session['user_state'] = 'collecting_details'
            return str(response)

    # User is registered, proceed with regular workflow
    user_id = get_user_id(from_number)
    print(user_id)
    user_state = session.get('user_state', 'start')

    if user_state == 'collecting_details':
        if 'name' not in session:
            session['name'] = incoming_msg
            msg.body("Thank you! Now, please provide your company name.")
        elif 'company_name' not in session:
            session['company_name'] = incoming_msg
            msg.body("Great! Please provide your email address.")
        elif 'email' not in session:
            session['email'] = incoming_msg
            msg.body("Almost done! Please send your company logo as a file attachment.")
        # elif 'logo_path' not in session:
        #     if 'MediaUrl0' in request.form:
        #         logo_url = request.form['MediaUrl0']
        #         logo_filename = secure_filename(logo_url.split('/')[-1])
        #         logo_path = os.path.join('uploads', logo_filename)
        #         download_file(logo_url, logo_path)
        #         session['logo_path'] = logo_path
        #         register_user(
        #             session['phone_number'],
        #             session['name'],
        #             session['company_name'],
        #             session['email'],
        #             logo_path
        #         )
            msg.body("Thank you for registering! You can now start by typing 'hi' or 'hello'.")
            session.pop('phone_number', None)
            session.pop('name', None)
            session.pop('company_name', None)
            session.pop('email', None)
            session.pop('logo_path', None)
            session['user_state'] = 'start'
        #     else:
        #         msg.body("Please send your company logo as a file attachment.")
        return str(response)

    if user_state == 'start':
        if incoming_msg in ['hi', 'hello', 'hey', 'greetings']:
            msg.body(
                f"Hi, {user['Company Name']}\nWhat would you like to create?\n1. Invoice\n2. Quotation\n3. Receipt")
            session['user_state'] = 'choice'
        else:
            msg.body("Hi! Please type 'hi' or 'hello' to start.")

    elif user_state == 'choice':
        if incoming_msg == '1':
            msg.body(
                "Please provide the invoice details in the format:\nCompany Name, Client, Date, Invoice Items: (Description, Quantity, Price), Tax, Discounts, Terms, Banking Details.")
            session['user_state'] = 'invoice_details'
        elif incoming_msg == '2':
            msg.body("Quotation processing is under development.")
            session['user_state'] = 'start'
        elif incoming_msg == '3':
            msg.body("Receipt processing is under development.")
            session['user_state'] = 'start'
        else:
            msg.body("Invalid choice. Please type '1' for Invoice, '2' for Quotation, or '3' for Receipt.")

    elif user_state == 'invoice_details':
        response_msg, next_state = process_invoice_request(incoming_msg)
        msg.body(response_msg)
        if next_state:
            session['user_state'] = next_state

    elif user_state == 'confirm':
        response_msg, pdf_path = confirm_invoice(incoming_msg)
        msg.body(response_msg)
        if pdf_path:
            msg.media(request.url_root + 'invoice')
            # Save transaction
            if user_id:
                save_transaction(user_id, 'invoice_id', 100.00)  # Replace 'invoice_id' and amount with actual values
        session['user_state'] = 'start'

    return str(response)


@app.route('/invoice')
def serve_invoice():
    pdf_path = os.path.join(os.getcwd(), 'invoice.pdf')
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    else:
        return "Invoice not found.", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
