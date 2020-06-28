# app.py
from flask import Flask, request, jsonify
import smtplib, os
# Imports, of course
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from email.message import EmailMessage
from bs4 import BeautifulSoup

app = Flask(__name__)
gmail_user = os.environ.get('GMAIL_USER', None)
gmail_password = os.environ.get('GMAIL_PW', None)

# A welcome message to test our server
@app.route('/proteinstatus')
def index():

    # Initialize a Firefox webdriver
    driver = webdriver.Firefox()

    # TODO: Add parameter for URL
    driver.get('https://www.mmsports.se/Kosttillskott/Protein/Vassleprotein-Whey/Body-Science-Whey-100.html?gclid=CjwKCAjw_-D3BRBIEiwAjVMy7AJaBCisTox5QredRmOFc3ETJLJayGNN-3oqaVqXwOkl3-aiAWsbdRoCwcYQAvD_BwE')

    # TODO: Add parameter for dropdown and dropdown value
    # We use .find_element_by_name here because we know the name
    productDropdown = Select(driver.find_element_by_name("product_options[628]"))
    productDropdown.select_by_value("29815")

    # TODO: Add parameter for choosing between find by name/id
    # We use .find_element_by_id here because we know the id
    # dropdownById = driver.find_element_by_id("id")
    # productDropdown.select_by_value("29815")

    html = BeautifulSoup(driver.page_source, "html.parser")

    # TODO: Implement find by value
    restockInfo = html.select('div.product-stock-status')

    # TODO: Add variables for find by class
    productInStock = html.select('div.product-status-ok')
    productNotInStock = html.select('div.product-status-nok')

    hasProduct = True if productInStock else False
    # hasNoProduct = True if productNotInStock else False

    if not hasProduct:
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

    return "<h1>It is available!!</h1>"


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)