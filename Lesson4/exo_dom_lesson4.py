import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

url_lacentrale = "https://www.lacentrale.fr"
url_prefix = "https://www.lacentrale.fr/listing?makesModelsCommercialNames={}%3A{}&regions={}&page={}"
url_argus = "https://www.lacentrale.fr/cote-auto-{}-{}-{}-{}.html"

# Build soup from URL
def build_soup_from_url(url):
    page = requests.get(url)
    html = page.text
    soup = BeautifulSoup(html,"html.parser")
    return soup

# Get Argus for a specific model
def get_argus(brand, model, version, fieldYear):
    # Build url
    url = url_argus.format(brand.lower(), model.lower(), version.lower().replace(" ", "+"), fieldYear)
    # Buid soup
    soup = build_soup_from_url(url)
    # get argus
    argus = soup.find("span", class_ = "jsRefinedQuot")
    # Check if argus is available
    if argus is None:
        argus = 0
    else:
        argus = argus.getText().replace(" ", "").replace("€","")
    # return argus
    return argus


# Get number total of annonce available for specific model
def get_number_annonce(brand, model, region):
    # Build url
    url = url_prefix.format(brand, model, region, 1)
    # Buid soup
    soup = build_soup_from_url(url)
    # Get Number total of annonce
    numAnn = soup.find("span", class_ = "numAnn").getText()
    # Return result
    return int(numAnn)


# Get Phone number of a i_annonce
def get_phone_number(soup, i_annonce):
    # Get url link to the annonce
    url = url_lacentrale +\
            soup.find_all("div", class_ = "adContainer")[i_annonce]\
                .find("a", class_ ="linkAd")['href']
    # Build soup
    soup_annonce = build_soup_from_url(url)
    # Get phone number
    phone = soup_annonce.find("div", class_ = "phoneNumber1").find("span", class_ = "bold")\
                .getText().strip().replace("\xa0", "-").split()[0]
    # Return phone
    return phone


# Build a DF containing occasion informations
def get_occasion_informations(brand, model, region):
    # Initialize DataFrame
    informations_list = ["BRAND","MODEL", "VERSION", "YEAR", "KM", "PRICE", "ARGUS", "SELLER", "REGION","PHONE"]
    df = pd.DataFrame(columns = informations_list)
    # Get Number total of annonce
    numAnn = get_number_annonce(brand, model, region)
    # Initialize index page & annonce
    i_page = 1
    i_annonce = 0
    while (i_annonce < numAnn):
        # Build url
        url = url_prefix.format(brand, model, region, i_page)
        # Buid soup
        soup = build_soup_from_url(url)
        # Get all container on all pages
        container_list = soup.find_all("div", class_ = "subContRight")
        for i in range(len(container_list)):
            # Get version
            version = container_list[i].find("span", class_ = "version").getText()
            # Get fieldYear
            fieldYear = container_list[i].find("div", class_ = "fieldYear").getText()
            # Get fieldMileage
            fieldMileage = container_list[i].find("div", class_ = "fieldMileage").getText()\
                                                                    .replace("\xa0", "").replace("km","")
            # Get fieldPrice
            fieldPrice = container_list[i].find("div", class_ = "fieldPrice").getText()\
                                                                    .replace("\xa0", "").replace("€","")
            # Get typeSeller
            typeSeller = container_list[i].find("p", class_ = "typeSeller").getText()
            # Get argus
            argus = get_argus(brand, model, version, fieldYear)
            # get Phone number
            phone = get_phone_number(soup, i)
            # Add informations to DataFrame
            df.loc[i_annonce] = [brand, model, version, fieldYear, fieldMileage, fieldPrice, argus, typeSeller, region, phone]
            # Iterate annonce
            i_annonce += 1
        # Iterate page
        i_page += 1
    # Cast columns to correct format
    df[['YEAR','KM', 'PRICE', 'ARGUS']] = df[['YEAR','KM', 'PRICE','ARGUS']]\
                                            .apply(pd.to_numeric, errors='coerce')
    # Compare price to argus
    df.insert(7,'COMPARE', np.where(df['PRICE'] > df['ARGUS'], '+', '-'))
    # Return DataFrame
    return df

def main():
    # Region List
    region_list = ["FR-IDF", "FR-NAQ", "FR-PAC"]
    # Brand List
    brand_list = ["RENAULT"]
    # Model List
    model_list = ["ZOE"]
    # Build all Data Frame
    df_list = []
    for brand in brand_list:
        for model in model_list:
            for region in region_list:
                df_list.append(get_occasion_informations(brand, model, region))
    # Concatenate all DataFrame
    df = pd.concat(df_list, ignore_index = True)
    # Export DataFrame to csv
    df.to_csv("/Users/anatoli_debradke/Desktop/lacentrale.csv", sep=';', index=False)
    # print DataFrame
    print(df)

if __name__ == '__main__':
    main()
