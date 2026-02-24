import imaplib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test connection
email = os.getenv('EMAIL_ADDRESS')
password = os.getenv('EMAIL_PASSWORD')

if not email or not password:
    print("Error: EMAIL_ADDRESS and EMAIL_PASSWORD must be set in .env file")
    exit(1)

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(email, password)
mail.select('inbox')
print("IMAP connection successful!")
mail.logout()