# app.py
from flask import Flask, request, jsonify
import smtplib, os, atexit
from functions import load_firefox_driver, send_restock_email
# Imports, of course
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler

app = Flask(__name__)
gmail_user = os.environ.get('GMAIL_USER', None)
gmail_password = os.environ.get('GMAIL_PW', None)

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=60)
def proteinstatus():
    """This function checks whether apple pie protein powder is available on MM Sports"""
    # Initialize a Firefox webdriver
    print('Setting up driver...')
    driver = load_firefox_driver()
    driver.get('https://www.mmsports.se/Kosttillskott/Protein/Vassleprotein-Whey/Body-Science-Whey-100.html?gclid=CjwKCAjw_-D3BRBIEiwAjVMy7AJaBCisTox5QredRmOFc3ETJLJayGNN-3oqaVqXwOkl3-aiAWsbdRoCwcYQAvD_BwE')

    # We use .find_element_by_name here because we know the name
    productDropdown = Select(driver.find_element_by_name("product_options[628]"))
    productDropdown.select_by_value("29815")


    html = BeautifulSoup(driver.page_source, "html.parser")

    productInStock = html.select('div.product-status-ok')
    productNotInStock = html.select('div.product-status-nok')

    hasProduct = True if productInStock else False

    if hasProduct:
        print("Product back in stock")
        # send_restock_email('jackeaik@hotmail.com')
    else:
        print("Product not yet back in stock")
    
    # Quit driver and close browser
    driver.quit()

# Start a scheduler to check for protein powder every 30 minutes
# sched.add_job(func=proteinstatus, trigger="interval", minutes=1)
sched.start()

# Shut down the scheduler when exiting the app
# atexit.register(lambda: sched.shutdown())
