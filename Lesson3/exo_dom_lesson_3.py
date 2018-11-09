# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

userID = "Anatoli-deBRADKE"
token = "9cd4072eb166d1b41a0bac0f4a0dc9908641f2f6"

def build_soup_from_url(url):
    page = requests.get(url)
    html = page.text
    soup = BeautifulSoup(html,"html.parser")
    return soup

def get_top_contributor():
    url = "https://gist.github.com/paulmillr/2657075"
    soup = build_soup_from_url(url)
    top_contributor = []
    table = soup.find('table').find_all('tr')
    for index in range(1,len(table)):
        contributor_pseudo = table[index].find('a').getText()
        top_contributor.append(contributor_pseudo)
    return top_contributor


def get_contributor_stars(contrib):
    url = "https://api.github.com/users/" + contrib + "/repos"
    res = requests.get(url, auth = (userID,token))
    reponse_object = json.loads(res.text)
    star_count = 0
    for repo in reponse_object:
        star_count += int(repo['stargazers_count'])
    if (len(reponse_object) == 0):
        return 0
    else:
        return round(star_count/len(reponse_object), 2)

def get_best_contributor():
    top_contributor = get_top_contributor()
    best_contributor = {}
    for contributor in top_contributor:
        best_contributor[contributor] = get_contributor_stars(contributor)
    sorted_best_contributor = sorted(best_contributor.items(), key = lambda kv: kv[1], reverse = True)
    return sorted_best_contributor

print(get_best_contributor())
