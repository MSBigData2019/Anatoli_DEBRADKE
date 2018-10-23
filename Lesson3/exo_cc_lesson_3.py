import requests
from bs4 import BeautifulSoup
import pandas as pd
import json


def build_soup_from_url(url):
    page = requests.get(url)
    html = page.text
    soup = BeautifulSoup(html,"html.parser")
    return soup

def build_city_list(list_size):
    url = "https://fr.wikipedia.org/wiki/Liste_des_communes_de_France_les_plus_peupl%C3%A9es"
    soup = build_soup_from_url(url)
    city_list = []
    table = soup.find('table').find_all('tr')
    for index in range(1, min(len(table),list_size + 1)):
        city_list.append(table[index].find('a').getText())
    return city_list


def build_matrix_dist(city_list):
    url = "https://fr.distance24.org/route.json?stops={}|{}"
    df = pd.DataFrame(columns = city_list,index = city_list)
    for city_1 in city_list:
        dist = []
        for city_2 in city_list:
            res = requests.get(url.format(city_1, city_2))
            reponse_object = json.loads(res.text)
            dist.append(reponse_object["distances"])
        df.loc[city_1] = dist
    return df


def main():
    city_list = build_city_list(50)
    df = build_matrix_dist(city_list)
    print(df)

if __name__ == '__main__':
    main()
