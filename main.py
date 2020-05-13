"""
Website used as reference:
https://realpython.com/beautiful-soup-web-scraper-python/
https://www.youtube.com/watch?v=Bg9r_yLk7VY
"""
import requests
from bs4 import BeautifulSoup

from re import sub
from decimal import Decimal

import smtplib
import os
from dotenv import load_dotenv


def main():
    load_dotenv()

    USER_AGENT = os.getenv('USER_AGENT')
    URL = 'https://www.costco.ca/CatalogSearch?dept=All&keyword=lg+gram'
    MAXIMUM_ACCEPTABLE_PRICE = 1400

    headers = {
        'User-Agent': USER_AGENT
    }

    page = requests.get(URL, headers=headers)
    print(f'HTTP STATUS CODE: {page.status_code}')
    soup = BeautifulSoup(page.content, 'html.parser')

    price_string = soup.find(id='price-100540466')
    if price_string is None:
        print('Product Not Found (May be Out of Stock)')
        return
    else:
        price_string = price_string.get_text().strip()

    # Adapted from https://stackoverflow.com/questions/8421922/how-do-i-convert-a-currency-string-to-a-floating-point-number-in-python
    price_value = Decimal(sub(r'[^\d.]', '', price_string))

    if price_value < MAXIMUM_ACCEPTABLE_PRICE:
        send_mail(price_value, URL)


def send_mail(price, url):
    load_dotenv()

    USERNAME = os.getenv('USERNAME')
    PASSWORD = os.getenv('PASSWORD')
    SEND_TO = os.getenv('SEND_TO')
    SUBJECT = 'Price drop alert'
    BODY = f'Price dropped to * ${price} * at:\n\n{url}'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(USERNAME, PASSWORD)

    msg = f'Subject: {SUBJECT}\n\n{BODY}'

    server.sendmail(USERNAME, SEND_TO, msg)

    print('Email has been sent successfully!')

    server.quit()


if __name__ == '__main__':
    main()
