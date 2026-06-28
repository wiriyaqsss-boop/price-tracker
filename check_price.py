import os
import smtplib
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

URL = "https://tracklabsf.com/products/cannondale-track-frameset-blue-58cm-1"
PRICE_FILE = "last_price.txt"

GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASS = os.environ.get("GMAIL_PASS")
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL")

def get_price():
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(URL, headers=headers, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    price_tag = soup.find("meta", {"property": "product:price:amount"})
    if price_tag:
        return price_tag.get("content", "").strip()
    for sel in [".price", ".product__price", "[class*=\'price\']"]:
        el = soup.select_one(sel)
        if el:
            return el.get_text(strip=True)
    return None

def send_email(old_price, new_price):
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = NOTIFY_EMAIL
    msg["Subject"] = "Price Alert: Cannondale Track Frameset changed!"
    body = f"Price change detected!\n\nProduct: Cannondale Track Frameset Blue 60cm\nURL: {URL}\n\nOld Price: {old_price}\nNew Price: {new_price}\n"
    msg.attach(MIMEText(body, "plain"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, NOTIFY_EMAIL, msg.as_string())
    print(f"Email sent! {old_price} -> {new_price}")

def main():
    current_price = get_price()
    if not current_price:
        print("Could not find price on page.")
        return
    print(f"Current price: {current_price}")
    if os.path.exists(PRICE_FILE):
        with open(PRICE_FILE, "r") as f:
            last_price = f.read().strip()
        if last_price != current_price:
            send_email(last_price, current_price)
    else:
        print("First run - saving price.")
    with open(PRICE_FILE, "w") as f:
        f.write(current_price)

if __name__ == "__main__":
    main()
