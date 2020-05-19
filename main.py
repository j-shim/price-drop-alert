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

import time


def price_drop_alert():
    load_dotenv()

    USER_AGENT = os.getenv('USER_AGENT')
    URL = 'https://www.costco.ca/CatalogSearch?dept=All&keyword=lg+gram'
    MAXIMUM_ACCEPTABLE_PRICE = 1400

    headers = {
        'User-Agent': USER_AGENT
    }

    try:
        page = requests.get(URL, headers=headers, timeout=50)
        page.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
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
        subj = 'Price drop alert'
        body = f'Price dropped to * ${price_value} * at:\n\n{URL}'
        send_mail(subj, body)


def stock_alert():
    load_dotenv()

    USER_AGENT = os.getenv('USER_AGENT')
    URL = 'https://www.lenovo.com/ca/en/laptops/ideapad/ideapad-500-series/IdeaPad-5-14ARE05/p/88IPS501392'

    headers = {
        'User-Agent': USER_AGENT
    }

    try:
        page = requests.get(URL, headers=headers, timeout=50)
        page.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    soup = BeautifulSoup(page.content, 'html.parser')

    soup_item = soup.find(id='addWishlistForm81YM0002US')
    if soup_item is None:
        print('Product Not Found (May be Out of Stock)')
        return
    else:
        button = soup_item.find_previous_sibling().find('button')

    if 'out-of-stock' in button['class']:
        print(f'OUT OF STOCK AT: {time.ctime()}')
    else:
        subj = 'Stock alert'
        body = f'In Stock at:\n\n{URL}'
        send_mail(subj, body)


def send_mail(subj, body):
    load_dotenv()

    USERNAME = os.getenv('USERNAME')
    PASSWORD = os.getenv('PASSWORD')
    SEND_TO = os.getenv('SEND_TO')
    SUBJECT = subj
    BODY = body

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
    stock_alert()
