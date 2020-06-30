# app.py
from flask import Flask, request, jsonify
import smtplib, os, atexit
from functions import load_firefox_driver, send_restock_email
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

def run_selenium(restockUrl, restockEmail, dropdownName, dropdownId, dropdownValue, 
        trackContainer, trackValue, trackClass):
    # Initialize a Firefox webdriver
    driver = load_firefox_driver()
    driver.get(restockUrl)

    if dropdownId is not None or dropdownName is not None:
        productDropdown = None
        if dropdownId is not None:
            productDropdown = Select(driver.find_element_by_id(dropdownId))
        if dropdownName is not None:
            productDropdown = Select(driver.find_element_by_id(dropdownName))
        if productDropdown is not None and dropdownValue is not None:
            productDropdown.select_by_value(dropdownValue)
    
    html = BeautifulSoup(driver.page_source, "html.parser")

    hasProduct = False

    if trackContainer is not None:
        restockInfo = html.select(trackContainer) # Use css selector (can use find/findall too)
        for restockElement in restockInfo:
            if trackValue is not None:
                if restockElement.find(string=trackValue):
                    hasProduct = True
                if trackClass is not None:
                    if restockElement.has_attr('class'):
                        if restockElement['class'][0] == trackClass:
                            hasProduct = True

    if hasProduct:
        send_restock_email(restockEmail)

    driver.quit()

    
@app.route('/checkrestock', methods=['GET'])
def check_restock():
    # Retrieve parameters
    restockUrl = request.args.get("restockUrl", None)
    restockEmail = request.args.get("restockEmail", None)

    # If we need to choose a value from a dropdown (i.e. colour, taste for the current product etc.)
    dropdownName = request.args.get("dropdownName", None)
    dropdownId = request.args.get("dropdownId", None)
    dropdownValue = request.args.get("dropdownValue", None)

    # Set this parameter to search for a value within a given html tag
    trackContainer = request.args.get("trackValueContainer", None)
    # Set this parameter to search for an element with a specific class, i.e. div.product-status-ok
    trackValue = request.args.get("trackValue", None)
    trackClass = request.args.get("trackClass", None)

    if restockUrl is None:
        return f'The parameter restockUrl is mandatory'
    
    if (trackContainer is None or trackValue is None) and trackClass is None:
        return f'You have to search either by value (trackValue & trackValueContainer) or class (trackClass)'

    run_selenium(restockUrl, restockEmail, dropdownName, dropdownId, dropdownValue, 
        trackContainer, trackValue, trackClass)

    # scheduler = BlockingScheduler()

    # # Start a scheduler
    # scheduler.add_job(func=lambda: restockCheck(restockUrl, restockEmail, dropdownName, dropdownId, dropdownValue, 
    #     trackContainer, trackValue, trackClass), trigger="interval", minutes=30)
    # scheduler.start()

    # # Shut down the scheduler when exiting the app
    # atexit.register(lambda: sched.shutdown())
    

# Add cross origin policies to make it work on Heroku
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
