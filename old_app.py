# app.py
from flask import Flask, request, jsonify
import bs4, requests, smtplib

app = Flask(__name__)

# A welcome message to test our server
@app.route('/')
def index():

    getPage = requests.get('https://www.mmsports.se/Kosttillskott/Protein/Vassleprotein-Whey/Body-Science-Whey-100.html?gclid=CjwKCAjw_-D3BRBIEiwAjVMy7AJaBCisTox5QredRmOFc3ETJLJayGNN-3oqaVqXwOkl3-aiAWsbdRoCwcYQAvD_BwE')

    # This will display an error message if something goes wrong, and stops your script.
    getPage.raise_for_status()

    # Parse raw data
    html = bs4.BeautifulSoup(getPage.text, 'html.parser')

    # Identifier

    restockInfo = html.select('div.product-status-ok')

    # https://www.mmsports.se/Kosttillskott/Protein/Vassleprotein-Whey/Body-Science-Whey-100.html?gclid=CjwKCAjw_-D3BRBIEiwAjVMy7AJaBCisTox5QredRmOFc3ETJLJayGNN-3oqaVqXwOkl3-aiAWsbdRoCwcYQAvD_BwE

    # https://www.mmsports.se/Kosttillskott/Protein/Vassleprotein-Whey/Body-Science-Whey-100.html?gclid=CjwKCAjw_-D3BRBIEiwAjVMy7AJaBCisTox5QredRmOFc3ETJLJayGNN-3oqaVqXwOkl3-aiAWsbdRoCwcYQAvD_BwE

    # product-status-ok product-status-nok
    print(restockInfo)

    hasProduct = False
    for restockElement in restockInfo:
        print("Another loop")
        if restockElement.has_attr('class'):
            print(restockElement['class'][0])
            if restockElement['class'][0] == 'product-status-nok':
                hasProduct = True

    print(hasProduct)

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