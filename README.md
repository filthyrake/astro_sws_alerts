Designed specifically with the JTW Astronomy GTR mount in mind, but this SHOULD work with pretty much any OnStepX mount running SWS.

This is NOT a complicated/fancy script - it just scrapes the SWS web interface and looks for keywords in the motor statuses and sends a text message alerting the user as appropriate.  I developed it as an easy way to detect/get notified about collisions.

## Setup

1. **Install dependencies:**
   ```bash
   pip install requests beautifulsoup4
   ```

2. **Configure environment variables:**
   
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and fill in your actual values:
   - `PHONE_NUMBER`: Your phone number (without carrier domain, e.g., 5551234567)
   - `EMAIL`: Your Gmail account for sending SMS alerts
   - `PASSWORD`: Your Gmail app password (see [Google's guide](https://support.google.com/accounts/answer/185833))
   - `SWS_URL`: URL to your SWS web interface (e.g., http://192.168.1.100/index.htm)
   
   **Important:** Never commit the `.env` file with real credentials to version control!

3. **Run the script:**
   
   Load environment variables and run:
   ```bash
   # On Linux/Mac:
   export $(cat .env | xargs) && python mount_scraper.py
   
   # Or use a tool like python-dotenv
   # pip install python-dotenv
   # Add to script: from dotenv import load_dotenv; load_dotenv()
   ```

4. **Set up as a Cron job or Lambda:**
   
   Run this as a Cron job or AWS Lambda function to regularly check the interface. There are almost certainly better ways to solve this, but it works.
