# app.py
from flask import Flask, request, jsonify
import smtplib, os, atexit
import re
from functions import load_firefox_driver, send_restock_email
# Imports, of course
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler

app = Flask(__name__)

def run_selenium(restock_url, restock_email, dropdown_name, dropdown_id, dropdown_value, 
        track_container, track_value, track_class):
    # Initialize a Firefox webdriver
    driver = load_firefox_driver()
    driver.get(restock_url)

    if dropdown_id is not None or dropdown_name is not None:
        productDropdown = None
        if dropdown_id is not None:
            productDropdown = Select(driver.find_element_by_id(dropdown_id))
        if dropdown_name is not None:
            productDropdown = Select(driver.find_element_by_id(dropdown_name))
        if productDropdown is not None and dropdown_value is not None:
            productDropdown.select_by_value(dropdown_value)
    
    html = BeautifulSoup(driver.page_source, "html.parser")

    hasProduct = False

    if track_container is not None:
        # ResultSet will only contain one element since we know there is only one such tag, so we take the first
        restockElement = html.select(track_container)[0] # Use css selector (can use find/findall too)
        print(restockElement)
        if track_value is not None:
            # Use regex to find elements that contains the value string
            if restockElement.find(string=re.compile(track_value)):
                hasProduct = True
        if track_class is not None:
            # Check if the class exists anywhere in current element tree or if it is present in the classlist of the current element
            if restockElement.find_all(_class=track_class) or track_class in restockElement.get("class"):
                hasProduct = True

    if hasProduct:
        send_restock_email(restock_email)

    driver.quit()
    
@app.route('/checkrestock', methods=['GET'])
def check_restock():
    # Retrieve parameters
    restock_url = request.args.get("restock_url", None)
    restock_email = request.args.get("restock_email", None)

    # If we need to choose a value from a dropdown (i.e. colour, taste for the current product etc.)
    dropdown_name = request.args.get("dropdown_name", None)
    dropdown_id = request.args.get("dropdown_id", None)
    dropdown_value = request.args.get("dropdown_value", None)

    # Set this parameter to search for a value within a given html tag
    track_container = request.args.get("track_valueContainer", None)
    # Set this parameter to search for an element with a specific class, i.e. div.product-status-ok
    track_value = request.args.get("track_value", None)
    track_class = request.args.get("track_class", None)

    if restock_url is None:
        return f'The parameter restock_url is mandatory'
    
    if (track_container is None or track_value is None) and track_class is None:
        return f'You have to search either by value (track_value & track_valueContainer) or class (track_class)'

    run_selenium(restock_url, restock_email, dropdown_name, dropdown_id, dropdown_value, 
        track_container, track_value, track_class)

    # scheduler = BlockingScheduler()

    # # Start a scheduler
    # scheduler.add_job(func=lambda: restockCheck(restock_url, restock_email, dropdown_name, dropdown_id, dropdown_value, 
    #     track_container, track_value, track_class), trigger="interval", minutes=30)
    # scheduler.start()

    # # Shut down the scheduler when exiting the app
    # atexit.register(lambda: sched.shutdown())

@app.route('/test', methods=['GET'])
def test():
    scrape_url = 'https://www.mmsports.se/Kosttillskott/Protein/Vassleprotein-Whey/Body-Science-Whey-100.html?gclid=CjwKCAjw_-D3BRBIEiwAjVMy7AJaBCisTox5QredRmOFc3ETJLJayGNN-3oqaVqXwOkl3-aiAWsbdRoCwcYQAvD_BwE'
    restock_email = 'jackeaik@hotmail.com'
    dropdown_name = None
    dropdown_id = None
    dropdown_value = None
    track_container = 'div.product-stock-status'
    track_value = 'I lager'
    track_class = 'product-status-ok'
    
    # test_url = (
    #     f'/checkrestock?restock_url={scrape_url}&restock_email={restock_email}&dropdown_name={dropdown_name}'
    #     f'&dropdown_id={dropdown_id}&dropdown_value={dropdown_value}&track_container={track_container}'
    #     f'&track_value={track_value}&track_class={track_class}'
    # )

    run_selenium(scrape_url, restock_email, dropdown_name, dropdown_id, dropdown_value, 
        track_container, track_value, track_class)

    return '<h1>Just testing</h1>'

    
    

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
