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

# Validate that all required environment variables are set
required_vars = {
    "PHONE_NUMBER": phone_number,
    "EMAIL": EMAIL,
    "PASSWORD": PASSWORD,
    "SWS_URL": URL
}
missing = [name for name, value in required_vars.items() if not value]
if missing:
    print("Error: Missing required environment variables.")
    print("Please set all required environment variables before running this script.")
    print("See .env.example for configuration details.")
    sys.exit(1)

def send_message(phone_number, message):
    recipient = phone_number + "@vtext.com"
    auth = (EMAIL, PASSWORD)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(auth[0], auth[1])

    server.sendmail(auth[0], recipient, message)
    server.quit()

if __name__ == "__main__":
    page = requests.get(URL)
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
