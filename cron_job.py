# app.py
from flask import Flask, request, jsonify
import smtplib, os, atexit
# Imports, of course
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from email.message import EmailMessage
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler

app = Flask(__name__)
gmail_user = os.environ.get('GMAIL_USER', None)
gmail_password = os.environ.get('GMAIL_PW', None)

sched = BlockingScheduler()

def load_firefox_driver():

    options = Options()

    options.binary_location = os.environ.get('FIREFOX_BIN')

    options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-smh-usage')
    options.add_argument('--no-sandbox')

    return webdriver.Firefox(executable_path=str(os.environ.get('GECKODRIVER_PATH')), options=options)

def sendRestockEmail(toEmail):
    receivers = [toEmail]
    msg = EmailMessage()
    msg.set_content("The product on your watchlist is now available.")
    msg['Subject'] = 'Product is now back in stock!'
    msg['From'] = 'RestockBot'
    msg['To'] = toEmail
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)   
        server.send_message(msg)    
        server.quit()
        print("Successfully sent email")
    except:
        print("Error: unable to send email")


@sched.scheduled_job('interval', minutes=1)
def proteinstatus():
    """This function checks whether apple pie protein powder is available on MM Sports"""
    # Initialize a Firefox webdriver
    print('Setting up driver...')
    driver = load_firefox_driver()
    driver.get('https://www.mmsports.se/Kosttillskott/Protein/Vassleprotein-Whey/Body-Science-Whey-100.html?gclid=CjwKCAjw_-D3BRBIEiwAjVMy7AJaBCisTox5QredRmOFc3ETJLJayGNN-3oqaVqXwOkl3-aiAWsbdRoCwcYQAvD_BwE')

    print('Loaded driver with url')
    # We use .find_element_by_name here because we know the name
    productDropdown = Select(driver.find_element_by_name("product_options[628]"))
    productDropdown.select_by_value("29815")

    print('Do stuff on page')

    html = BeautifulSoup(driver.page_source, "html.parser")

    print('Select html...')

    productInStock = html.select('div.product-status-ok')
    productNotInStock = html.select('div.product-status-nok')

    hasProduct = True if productInStock else False

    if not hasProduct:
        print("Product back in stock")
        sendRestockEmail('jackeaik@hotmail.com')
    else:
        print("Product not yet back in stock")
    
    # Quit driver and close browser
    driver.quit()

# Start a scheduler to check for protein powder every 30 minutes
# sched.add_job(func=proteinstatus, trigger="interval", minutes=1)
sched.start()

# Shut down the scheduler when exiting the app
# atexit.register(lambda: sched.shutdown())
