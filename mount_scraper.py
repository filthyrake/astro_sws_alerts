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
if not all([phone_number, EMAIL, PASSWORD, URL]):
    missing = []
    if not phone_number:
        missing.append("PHONE_NUMBER")
    if not EMAIL:
        missing.append("EMAIL")
    if not PASSWORD:
        missing.append("PASSWORD")
    if not URL:
        missing.append("SWS_URL")
    print(f"Error: Missing required environment variables: {', '.join(missing)}")
    print("Please set all required environment variables before running this script.")
    sys.exit(1)
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")
driver1_results = soup.find(id="dvr_stat0")
driver2_results = soup.find(id="dvr_stat1")

def send_message(phone_number, message):
    recipient = phone_number + "@vtext.com"
    auth = (EMAIL, PASSWORD)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(auth[0], auth[1])

    server.sendmail(auth[0], recipient, message)

if __name__ == "__main__":
    soup = BeautifulSoup(page.content, "html.parser")
    driver1_results = soup.find(id="dvr_stat0")
    driver2_results = soup.find(id="dvr_stat1")

    if driver1_results.text not in ["Standstill", "Done"]:
      print("Fail!!")
      print(driver1_results.text)
      send_message(phone_number, driver1_results.text)
      exit()

    if driver2_results.text not in ["Standstill", "Done"]:
      print("Fail!!")
      print(driver2_results.text)
      send_message(phone_number, driver2_results.text)
      exit()
