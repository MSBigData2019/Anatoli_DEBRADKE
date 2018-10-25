# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
import numpy as np

url_api = "https://www.open-medicaments.fr/api/v1/medicaments?query={}"

def get_medicament_ID(medicament):
    url = url_api.format(medicament)
    res = requests.get(url)
    df = pd.read_json(res.content)
    serie = df["denomination"]
    reg = r'(\D)*(\d+)(.*),([\w\s]*)'
    df = df["denomination"].str.extract(reg)
    df["Multiply"] = 1000
    df["Multiply"] = df["Multiply"].where(df[2].str.strip() == "g", 1)
    df['Dosage'] = df[1].fillna(0).astype(int)*df["Multiply"]
    
    return df

def main():
    medicament = "paracetamol"
    medicament_ID =  get_medicament_ID(medicament)

if __name__ == '__main__':
    main()
