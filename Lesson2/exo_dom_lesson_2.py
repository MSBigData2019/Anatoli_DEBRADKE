# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import pandas as pd

url_prefix = "https://www.reuters.com/finance/stocks/financial-highlights/"


def build_soup_from_url(url):
    page = requests.get(url)
    html = page.text
    soup = BeautifulSoup(html,"html.parser")
    return soup


def get_all_performance(society_list):
    df = pd.DataFrame(columns = \
            ["Society","Stock_Sales","Stock_Price","Stock_Variation", \
                "Shares_Owned","DY_Company","DY_Sector","DY_Industry"])
    i_society = 0
    for society in society_list:
        url = url_prefix + society
        soup = build_soup_from_url(url)
        stock_sales = get_stock_sales(soup)
        stock_price = get_stock_price(soup)
        stock_variation = get_stock_variation(soup)
        shares_owned = get_shares_Owned(soup)
        dividend_yield = get_dividend_yield(soup)
        performance_list = [society, stock_sales, stock_price, \
                                stock_variation, shares_owned, dividend_yield[0], \
                                    dividend_yield[1], dividend_yield[2]]
        df.loc[i_society] = performance_list
        i_society += 1
    df.set_index("Society")
    return df


def get_stock_price(soup):
    stock_price = soup.find(class_ = "sectionQuoteDetail")\
                    .findAll("span")[1].text.strip()
    return stock_price


def get_stock_sales(soup):
    stock_sales = soup.find_all(class_  = "module")[2]\
                    .find_all(class_ = "stripe")[0]\
                        .find_all(class_ = "data")[1].text.strip()
    return stock_sales


def get_stock_variation(soup):
    stock_variation = soup.find(class_ = "valueContentPercent")\
                        .find(class_ = "neg").text.strip()
    return stock_variation


def get_shares_Owned(soup):
    shares_owned = soup.find_all(class_ = "dataSmall")[2]\
                    .findAll(class_ = "data")[0].text.strip()
    return shares_owned


def get_dividend_yield(soup):
    dividend_yield_company  = soup.find_all(class_ = "module")[4]\
                                .find_all(class_ = "data")[3].text.strip()
    dividend_yield_sector   = soup.find_all(class_ = "module")[4]\
                                .find_all(class_ = "data")[4].text.strip()
    dividend_yield_industry = soup.find_all(class_ = "module")[4]\
                                .find_all(class_ = "data")[5].text.strip()
    return [dividend_yield_company, dividend_yield_sector, dividend_yield_industry]


def main():
    society_list = ["LVMH.PA", "AIR.PA", "DANO.PA"]
    performance = get_all_performance(society_list)
    print(performance)

if __name__ == '__main__':
    main()
