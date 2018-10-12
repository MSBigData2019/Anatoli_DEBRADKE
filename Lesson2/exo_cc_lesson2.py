# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup

url_prefix = "https://www.darty.com/nav/recherche/"

def build_soup_from_url(url):
    page = requests.get(url)
    html = page.text
    soup = BeautifulSoup(html,"html.parser")
    return soup

def get_all_discount_sales(computer):
    url = url_prefix + computer
    soup = build_soup_from_url(url)
    discount_sales = soup.find_all("p", class_ = "darty_prix_barre_remise")
    return len(discount_sales)

def main():
    computer_list = ["acer.html", "dell.html"]
    for computer in computer_list:
        discount_sales = get_all_discount_sales(computer)
        print("Nombre d article soldés pour {} = {}".format(computer,discount_sales))

if __name__ == '__main__':
    main()
