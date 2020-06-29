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
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
gmail_user = os.environ.get('GMAIL_USER', None)
gmail_password = os.environ.get('GMAIL_PW', None)

sched = BackgroundScheduler()

def load_firefox_driver():

    options = Options()

    options.binary_location = os.environ.get('FIREFOX_BIN')

    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    return webdriver.Firefox(executable_path=str(os.environ.get('GECKODRIVER_PATH')), firefox_options=options)

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

def restockCheck(restockUrl, restockEmail, dropdownName, dropdownId, dropdownValue, 
        trackContainer, trackValue, trackClass):
    # Initialize a Firefox webdriver
    driver = load_firefox_driver()

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
        sendRestockEmail(restockEmail)

    driver.quit()

    
@app.route('/addrestockwatcher', methods=['GET'])
def addrestockwatcher():
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

    scheduler = BackgroundScheduler()

    # Start a scheduler
    scheduler.add_job(func=lambda: restockCheck(restockUrl, restockEmail, dropdownName, dropdownId, dropdownValue, 
        trackContainer, trackValue, trackClass), trigger="interval", minutes=30)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: sched.shutdown())
    

# Add cross origin policies to make it work on Heroku
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


def proteinstatus():
    """This function checks whether apple pie protein powder is available on MM Sports"""
    # Initialize a Firefox webdriver
    driver = load_firefox_driver()
    driver.get('https://www.mmsports.se/Kosttillskott/Protein/Vassleprotein-Whey/Body-Science-Whey-100.html?gclid=CjwKCAjw_-D3BRBIEiwAjVMy7AJaBCisTox5QredRmOFc3ETJLJayGNN-3oqaVqXwOkl3-aiAWsbdRoCwcYQAvD_BwE')

    # We use .find_element_by_name here because we know the name
    productDropdown = Select(driver.find_element_by_name("product_options[628]"))
    productDropdown.select_by_value("29815")

    html = BeautifulSoup(driver.page_source, "html.parser")

    # TODO: Implement find by value
    restockInfo = html.select('div.product-stock-status')

    # TODO: Add variables for find by class
    productInStock = html.select('div.product-status-ok')
    productNotInStock = html.select('div.product-status-nok')

    hasProduct = True if productInStock else False
    # hasNoProduct = True if productNotInStock else False

    if hasProduct:
        receivers = ['jackeaik@hotmail.com']
        msg = EmailMessage()
        msg.set_content("The product on your watchlist is now available.")
        msg['Subject'] = 'Product is now back in stock!'
        msg['From'] = 'MMSports - Web Scraping'
        msg['To'] = 'jackeaik@hotmail.com'
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(gmail_user, gmail_password)   
            server.send_message(msg)    
            server.quit()
            print("Successfully sent email")
        except:
            print("Error: unable to send email")
        
    # Quit driver and close browser
    driver.quit()

# Start a scheduler to check for protein powder every 30 minutes
sched.add_job(func=proteinstatus, trigger="interval", minutes=30)
sched.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: sched.shutdown())

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)