import requests
from bs4 import BeautifulSoup
import smtplib
import sys
import os

# Load credentials from environment variables
phone_number = os.getenv("PHONE_NUMBER")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
URL = os.getenv("SWS_URL")

def send_message(phone_number, message):
    if not phone_number:
        raise ValueError("phone_number is required")
    if not EMAIL or not PASSWORD:
        raise ValueError("EMAIL and PASSWORD environment variables must be set")
    
    recipient = phone_number + "@vtext.com"
    auth = (EMAIL, PASSWORD)

    server = None
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(auth[0], auth[1])
        server.sendmail(auth[0], recipient, message)
    except smtplib.SMTPAuthenticationError as e:
        print(f"Failed to authenticate with Gmail - check credentials: {e}")
        sys.exit(1)
    except smtplib.SMTPConnectError as e:
        print(f"Failed to connect to SMTP server: {e}")
        sys.exit(1)
    except smtplib.SMTPException as e:
        print(f"Failed to send SMS: {e}")
        sys.exit(1)
    finally:
        if server:
            try:
                server.quit()
            except Exception:
                pass  # Ignore errors when closing connection

if __name__ == "__main__":
    # Validate that all required environment variables are set
    required_vars = {
        "PHONE_NUMBER": phone_number,
        "EMAIL": EMAIL,
        "PASSWORD": PASSWORD,
        "SWS_URL": URL
    }
    missing = [name for name, value in required_vars.items() if not value]
    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}")
        print("Please set all required environment variables before running this script.")
        print("See .env.example for configuration details.")
        sys.exit(1)
    
    try:
        page = requests.get(URL, timeout=10)
        page.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to fetch the SWS page: {e}")
        sys.exit(1)
    
    soup = BeautifulSoup(page.content, "html.parser")
    driver1_results = soup.find(id="dvr_stat0")
    driver2_results = soup.find(id="dvr_stat1")

    if not driver1_results or not driver2_results:
        print("Error: Could not find driver status elements on the page")
        sys.exit(1)

    if driver1_results.text not in ["Standstill", "Done"]:
        print("Fail!!")
        print(driver1_results.text)
        send_message(phone_number, driver1_results.text)
        sys.exit(1)

    if driver2_results.text not in ["Standstill", "Done"]:
        print("Fail!!")
        print(driver2_results.text)
        send_message(phone_number, driver2_results.text)
        sys.exit(1)
