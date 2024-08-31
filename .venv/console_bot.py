# Import necessary libraries
from dotenv import load_dotenv
import os
from invoice_data import extract_invoice_data
from invoice_bot import parse_extracted_data, check_missing_fields, create_confirmation_message, generate_invoice_pdf

# Load environment variables from .env file
load_dotenv()
user ='Rilpix Private Limited'

def main():
    """
    Main function to run the console application.
    """
    print("Welcome to the Invoice Bot!")

    while True:
        # Prompt the user with options
        print(f"Hi, {user}\nWhat would you like to create?\n1. Invoice\n2. Quotation\n3. Receipt")
        print("Type 'exit' to quit the application.")

        # Get user input
        user_input = input("Enter your choice: ").strip().lower()

        # Handle user choice
        if user_input in ['hi', 'hello', 'hey', 'greetings']:
            print("\nWhat would you like to create today?\n1. Invoice\n2. Quotation\n3. Receipt")

        elif user_input == '1':
            print(
                "\nPlease provide the invoice details in the format:\nCompany Name, Client, Date, Invoice Items: (Description, Quantity, Price), Tax, Discounts, Terms, Banking Details.")
            details = input("Enter invoice details: ")

            # Process invoice details
            invoice_data = extract_invoice_data(details)
            missing_fields = check_missing_fields(invoice_data)

            if missing_fields:
                print(f"Please provide the following missing details: {', '.join(missing_fields)}")
            else:
                confirmation_message = create_confirmation_message(invoice_data)
                print(confirmation_message)
                # Ask for confirmation
                get_user_confirmation(invoice_data)

        elif user_input == '2':
            print("\nQuotation processing is under development.")
            # Implement the quotation logic here

        elif user_input == '3':
            print("\nReceipt processing is under development.")
            # Implement the receipt logic here

        elif user_input == 'exit':
            print("Exiting the application. Goodbye!")
            break

        else:
            print("Invalid input. Please type 'hi' or a number (1, 2, or 3).")


def get_user_confirmation(invoice_data):
        print('1.Confirm')
        print('2.Cancel')
        confirm = input("Your answer: ").strip().lower()
        if confirm == '1':
            # Generate the PDF invoice
            pdf_path = generate_invoice_pdf(invoice_data)
            print(f"Invoice generated successfully. PDF saved at: {pdf_path}")
        elif confirm == '2':
            print("Invoice creation cancelled.")
        else:
            print("Invalid input. Please type 'confirm' or 'cancel'.")

if __name__ == '__main__':
    main()
