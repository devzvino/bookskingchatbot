import re
from datetime import datetime

def extract_invoice_data(message):
    # Initialize data dictionary with default values
    data = {
        'Company Name': 'Your Company',  # Assuming 'Your Company' as the sender
        'Client': None,
        'Date': datetime.now().strftime('%Y-%m-%d'),
        'Invoice Items': [],
        'Tax': None,
        'Discounts': None,
        'Terms': None,
        'Banking Details': None
    }

    # Extract Client Name
    client_match = re.search(r'invoice for (.*?) for website development', message, re.IGNORECASE)
    if client_match:
        data['Client'] = client_match.group(1)

     # Extract Invoice Items
    items_match = re.search(r'Items:(.*?)(?=\.\s*[A-Z]|\.\s*$)', message, re.IGNORECASE)
    if items_match:
        items_text = items_match.group(1).strip()
        # Updated regex to avoid capturing leading commas and spaces
        items = re.findall(r'(\b[^,]+?):\s*\$(\d+)', items_text)
        for item in items:
            description = item[0].strip()
            amount = float(item[1])
            data['Invoice Items'].append({'Description': description, 'Amount': amount})

    # Extract Discount
    discount_match = re.search(r'Apply a (\d+)% discount', message)
    if discount_match:
        data['Discounts'] = float(discount_match.group(1))

    # Extract Tax
    tax_match = re.search(r'(\d+)% sales tax', message)
    if tax_match:
        data['Tax'] = float(tax_match.group(1))

    # Extract Terms
    terms_match = re.search(r'Terms are (.*?)(\.|\n)', message)
    if terms_match:
        data['Terms'] = terms_match.group(1).strip()

    # Extract Banking Details
    bank_match = re.search(r'Banking details: (.*)', message, re.IGNORECASE)
    if bank_match:
        data['Banking Details'] = bank_match.group(1).strip()

    return data

# # Example usage
# message = """Create an invoice for Dawlagd Logistics for website development services.
# Items: Website design in Figma: $200, Web development (Frontend & Backend): $500, Web deployment: $100, Web hosting for one year: $120. Apply a 10% discount and a 5% sales tax.
# Terms are net 30 days. Banking details: Bank of Example, Account Number: 123456789, Routing Number: 987654321."""
#
# invoice_data = extract_invoice_data(message)
# print(invoice_data)