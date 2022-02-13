from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import concurrent.futures
import pandas as pd

urls = []
product_details = []


def get_links():
    """ This is a get_links function which scrape all product urls"""
    with sync_playwright() as p:
        url = "https://www.amazon.com/s?k=python+books"
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()
        page.goto(url)
        html = page.inner_html('div.s-main-slot')
        # Using BeautifulSoup to get all links based on HTML code
        soup = BeautifulSoup(html, 'html.parser')
        for item in soup.find_all('div', {'class': 'sg-col-4-of-12'}):
            urls.append(f"https://www.amazon.com/{item.find('a', {'class': 'a-link-normal'})['href']}") ## Saving them to list
        browser.close()
        print("Got all product links!")
    return urls


def get_details(url):
    with sync_playwright() as p:
        # Laungching a Chrome browser
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()
        # Using timeout features to not get any error while sending requests
        page.set_default_navigation_timeout(300000)
        page.set_default_timeout(300000)
        page.goto(url)
        html = page.inner_html('div#dp-container')
        soup = BeautifulSoup(html, 'html.parser')
        # Starting scrape product details
        title = soup.find('span', {"id": "productTitle"}).text.strip()
        authors_list = []
        # List was created to save authors in case if there two or more authors
        for author in soup.find_all('span', {'class': 'author'}):
            authors_list.append(author.find('a', {'class':'a-link-normal'}).text.strip())
        # converting list values to variable using join operator
        authors = ', '.join(authors_list)
        rating_product = soup.find('span', {'id': 'acrPopover'}).find('span', {'class': 'a-icon-alt'}).text.replace(
            'stars', '').strip()
        rating_amount = soup.find('span', {'id': 'acrCustomerReviewText'}).text.replace('ratings', '').strip()
        # using ("Try Except") to get no errors
        try:
            cover_image = soup.find('img', {'id': 'main-image'})['src']
        except:
            cover_image = soup.find('img', {'class': 'a-dynamic-image'})['src']
        try:
            price = soup.find("ul", {'class': "a-unordered-list"}).find_all("li", {'class': "swatchElement"})[-1]
            paperback_price = price.find('span', {'class': 'a-button-inner'}).text.split("$")[-1].strip()
        except:
            paperback_price = soup.find("li", {'id': 'mediaTab_heading_1'}).find('span',
                                                                                 {'class': 'a-size-base'}).text.replace(
                '$', '').strip()

        items = {
            "title": title,
            "paperback_price": paperback_price,
            "cover_image": cover_image,
            "authors": authors,
            "rating_product": rating_product,
            "rating_amount": rating_amount
        }
        # Saving all information to a list to convert later to CSV file
        product_details.append(items)
        browser.close()
    return product_details

# Running a functions
urls = get_links()
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(get_details, urls) ## going through the urls

"""Used 'max_workers = 4', because of the capabilities of my laptop"""

# Saving product details to CSV file
df = pd.DataFrame(product_details)
df.to_csv('Amazon_books.csv', index=False)
print('Complete.')
