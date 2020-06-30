def load_firefox_driver():

    options = Options()

    options.binary_location = os.environ.get('FIREFOX_BIN')

    options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-smh-usage')
    options.add_argument('--no-sandbox')

    return webdriver.Firefox(executable_path=str(os.environ.get('GECKODRIVER_PATH')), firefox_options=options)

def send_restock_email(toEmail):
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