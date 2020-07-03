from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from email.message import EmailMessage
import smtplib, os, atexit

gmail_user = os.environ.get('GMAIL_USER', None)
gmail_password = os.environ.get('GMAIL_PW', None)

def load_firefox_driver():

    options = Options()

    options.binary_location = os.environ.get('FIREFOX_BIN')

    options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-smh-usage')
    options.add_argument('--no-sandbox')

    return webdriver.Firefox(executable_path=str(os.environ.get('GECKODRIVER_PATH')), options=options)

def send_restock_email(toEmail, scheduler = None):
    receivers = [toEmail]
    msg = EmailMessage()
    msg.set_content("The product on your watchlist is now available.")
    msg['Subject'] = 'Product is now back in stock!'
    msg['From'] = 'RestockBot - Product available'
    msg['To'] = toEmail
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)   
        server.send_message(msg)    
        server.quit()
        # if scheduler is not None:
            # if scheduler.running:
                # print('Shutting down scheduler')
                # Shutdown cron job if the product is back in stock and close any started processes
                # scheduler.shutdown(wait=False) 
        print("Successfully sent email")
    except err:
        print("Error: unable to send email")