from flask import Flask, request, jsonify
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
from invoice_data import extract_invoice_data
from invoice_bot import create_confirmation_message, generate_invoice_pdf, check_missing_fields
from werkzeug.utils import secure_filename
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Twilio client
twilio_client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))

def upload_file_to_twilio(file_path):
    """
    Upload a file to a publicly accessible location and return the URL.
    For demonstration purposes, assume the file is publicly accessible.
    """
    # In a real scenario, use a file hosting service and return the URL
    return file_path

def get_user_confirmation(invoice_data):
    """
    Generate confirmation message and return it.
    """
    confirmation_message = create_confirmation_message(invoice_data)
    return confirmation_message

user ='Rilpix Private Limited'

@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    """
    Respond to incoming WhatsApp messages and handle interactions.
    """
    incoming_msg = request.form.get('Body', '').strip().lower()
    from_number = request.form.get('From', '')

    # Initialize response
    response = MessagingResponse()
    msg = response.message()

    
    # Initialize user state
    user_state = request.cookies.get('user_state', 'start')

    if user_state == 'start':
        if incoming_msg in ['hi', 'hello', 'hey', 'greetings']:
            msg.body(f" Hi, {user}\nWhat would you like to create?\n1. Invoice\n2. Quotation\n3. Receipt")
            response.set_cookie('user_state', 'choice')
        else:
            msg.body("Hi! Please type 'hi' or 'hello' to start.")
    
    elif user_state == 'choice':
        if incoming_msg == '1':
            msg.body("Please provide the invoice details in the format:\nCompany Name, Client, Date, Invoice Items: (Description, Quantity, Price), Tax, Discounts, Terms, Banking Details.")
            response.set_cookie('user_state', 'invoice_details')
        elif incoming_msg == '2':
            msg.body("Quotation processing is under development.")
            response.set_cookie('user_state', 'start')
        elif incoming_msg == '3':
            msg.body("Receipt processing is under development.")
            response.set_cookie('user_state', 'start')
        else:
            msg.body("Invalid choice. Please type '1' for Invoice, '2' for Quotation, or '3' for Receipt.")
    
    elif user_state == 'invoice_details':
        invoice_data = extract_invoice_data(incoming_msg)
        missing_fields = check_missing_fields(invoice_data)
        
        if missing_fields:
            msg.body(f"Please provide the following missing details: {', '.join(missing_fields)}")
        else:
            confirmation_message = get_user_confirmation(invoice_data)
            msg.body(confirmation_message + "\n\nPlease type 'confirm' to proceed or 'cancel' to cancel.")
            response.set_cookie('user_state', 'confirm')
    
    elif user_state == 'confirm':
        if incoming_msg == 'confirm':
            # Generate the PDF invoice
            pdf_path = generate_invoice_pdf(invoice_data)
            
            # Upload the PDF to a publicly accessible location
            pdf_url = upload_file_to_twilio(pdf_path)
            
            # Send the PDF via WhatsApp
            msg.body("Your invoice has been generated.")
            msg.media(pdf_url)
            response.set_cookie('user_state', 'start')
        elif incoming_msg == 'cancel':
            msg.body("Invoice creation cancelled. Please start over by typing 'hi' or 'hello'.")
            response.set_cookie('user_state', 'start')
        else:
            msg.body("Invalid input. Please type 'confirm' to proceed or 'cancel' to cancel.")

    return str(response)

if __name__ == '__main__':
    # Get the port from environment variables or default to 5000
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
