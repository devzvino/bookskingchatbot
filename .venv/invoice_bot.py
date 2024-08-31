# invoice_bot.py

from datetime import datetime
from fpdf import FPDF
import openai
import os


# Set OpenAI API key
# openai.api_key = os.getenv('OPENAI_API_KEY')

# Helper function to extract invoice data from a message
# def extract_invoice_data(message):
#     """
#     Uses OpenAI API to extract invoice information from a user's message.

#     Args:
#         message (str): The message from the user containing invoice details.

#     Returns:
#         str: The extracted information in a structured text format.
#     """
#     # Prepare the prompt for OpenAI to extract invoice information
#     prompt = f"Extract invoice information from the following message: {message}\n\nInclude: Company Name, Service Provider, Client, Date, Invoice Items (Description, Quantity, Price), Tax, Discounts, Terms, Banking Details."

#     # Make a request to the OpenAI API
#     response = openai.Completion.create(
#         model="gpt-3.5-turbo",  # or "gpt-4" depending on your model availability
#         prompt=prompt,
#         max_tokens=300
#     )

#     # Return the extracted information from the response
#     return response.choices[0].text.strip()

def parse_extracted_data(extracted_data):
    """
    Parses the extracted data into a structured dictionary format.

    Args:
        extracted_data (str): The raw extracted data from OpenAI.

    Returns:
        dict: A dictionary containing the structured invoice data.
    """
    # Initialize a dictionary to store parsed data
    data = {
        'Company Name': None,
        'Client': None,
        'Date': None,
        'Invoice Items': [],
        'Tax': None,
        'Discounts': None,
        'Terms': None,
        'Banking Details': None
    }

    # Split the extracted data by lines and parse each line
    lines = extracted_data.split('\n')
    for line in lines:
        if line.startswith("Company Name:"):
            data['Company Name'] = line.split(":")[1].strip()
        elif line.startswith("Client:"):
            data['Client'] = line.split(":")[1].strip()
        elif line.startswith("Date:"):
            data['Date'] = line.split(":")[1].strip()
        elif line.startswith("Tax:"):
            data['Tax'] = line.split(":")[1].strip()
        elif line.startswith("Discounts:"):
            data['Discounts'] = line.split(":")[1].strip()
        elif line.startswith("Terms:"):
            data['Terms'] = line.split(":")[1].strip()
        elif line.startswith("Banking Details:"):
            data['Banking Details'] = line.split(":")[1].strip()
        elif line.startswith("Invoice Items:"):
            items = line.split(":")[1].strip()
            # Process each item in the list, assuming they are separated by commas or a similar format
            item_list = items.split(',')
            for item in item_list:
                # Assume items are in "Description, Quantity, Price" format
                parts = item.split(',')
                if len(parts) == 3:
                    data['Invoice Items'].append({
                        'Description': parts[0].strip(),
                        'Quantity': int(parts[1].strip()),
                        'Price': float(parts[2].strip())
                    })

    return data


def check_missing_fields(data):
    """
    Checks for any missing fields in the extracted invoice data.

    Args:
        data (dict): The dictionary containing extracted invoice data.

    Returns:
        str: A message prompting for missing details, or None if all details are present.
    """
    # List of required fields
    required_fields = ['Company Name', 'Client', 'Date', 'Invoice Items']
    # Check which fields are missing
    missing_fields = [field for field in required_fields if field not in data or not data[field]]

    # Return a message listing missing fields or None if all fields are present
    if missing_fields:
        return f"The following details are missing: {', '.join(missing_fields)}. Please provide them."
    else:
        return None


def create_confirmation_message(invoice_data):
    """
    Creates a confirmation message with the extracted invoice data for user review.

    Args:
        invoice_data (dict): The dictionary containing structured invoice data.

    Returns:
        str: A formatted message summarizing the invoice data for user confirmation.
    """
    # Start building the confirmation message
    confirmation_message = (
        f"Please confirm the following invoice details:\n"
        f"\nCompany Name: {invoice_data.get('Company Name', 'N/A')}\n"
        f"Client: {invoice_data.get('Client', 'N/A')}\n"
        f"Date: {invoice_data.get('Date', 'N/A')}\n"
        "Invoice Items:\n"
    )

    # Append each invoice item to the message
    for item in invoice_data.get('Invoice Items', []):
        description = item.get('Description', 'No description')
        quantity = item.get('Quantity', 1)
        price = item.get('Amount', 'N/A')
        total_price = quantity * price  # Calculate total price
        if quantity > 1:
            confirmation_message += f"- {description}, {quantity} items, ${total_price:.2f}\n"
        else:
            confirmation_message += f"- {description}, {quantity} item, ${total_price:.2f}\n"

    # Append other invoice details and instructions for the user
    confirmation_message += (
        f"Tax: {invoice_data.get('Tax', 'N/A')}\n"
        f"Discounts: {invoice_data.get('Discounts', 'N/A')}\n"
        f"Terms: {invoice_data.get('Terms', 'N/A')}\n"
        f"Banking Details: {invoice_data.get('Banking Details', 'N/A')}\n"
    )

    return confirmation_message


def generate_invoice_pdf(data, user):
    """
    Generates a PDF invoice based on the provided data.

    Args:
        data (dict): The dictionary containing structured invoice data.

    Returns:
        str: The file path of the generated PDF invoice.
        :param data:
        :param user:
    """
    print(data)
    # Initialize subtotal
    subtotal = 0.0
    invoice_items = data['Invoice Items']
    # Print out each amount to verify correctness

    for item in invoice_items:
        subtotal += item['Amount']

    # Calculate subtotal, discount, tax, and total
    print(subtotal)
    print(data['Invoice Items'])

    discount = subtotal * (data['Discounts']/100)
    print(discount)
    tax = (subtotal - discount) * (data['Tax']/100)

    total = (subtotal - discount) + tax

    # Create a new PDF object
    # Create PDF

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Invoice", ln=True, align='C')

    pdf.cell(200, 10, txt=f"Company: {user['Company Name']}", ln=True)
    pdf.cell(200, 10, txt=f"Client: {data['Client']}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {data['Date']}", ln=True)

    pdf.cell(200, 10, txt="Items:", ln=True)
    for item in data['Invoice Items']:
        pdf.cell(200, 10, txt=f"{item['Description']}: ${item['Amount']:.2f}", ln=True)

    pdf.cell(200, 10, txt=f"Subtotal: ${ subtotal:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Discount (10%): -${data['Discounts']:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Tax (5%): +${data['Tax']:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Total: ${total:.2f}", ln=True)

    pdf.cell(200, 10, txt=f"Terms: {data['Terms']}", ln=True)
    pdf.cell(200, 10, txt="Banking Details:", ln=True)
    pdf.cell(200, 10, txt=f"Bank: {data['Banking Details']}", ln=True)
    # pdf.cell(200, 10, txt=f"Account Number: {banking_details['Account Number']}", ln=True)
    # pdf.cell(200, 10, txt=f"Routing Number: {banking_details['Routing Number']}", ln=True)

    # Define the file path for the PDF
    pdf_file = 'invoice.pdf'
    # Save the PDF file
    pdf.output(pdf_file)

    return pdf_file
