"""
Get company list from Website
"""

import requests
from bs4 import BeautifulSoup
import json
from DataPoint import companyData
import pandas as pd

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def getCompanyList():
    companyList = set()
    url = 'https://tosdr.org/index.html#'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    for div in soup.find_all('a', {"class": "modal-link"}):
        companyName = div.get('data-service-name').lower()
        if isEnglish(companyName) and companyName.isalpha() :
            companyList.add(companyName)
    return companyList

def main():
    url = 'https://tosdr.org/api/1/service/{companyName}.json'
    companyList = getCompanyList()
    dataList = []
    #companyName = 'twitter'
    for companyName in companyList:
        newUrl = url.replace("{companyName}", companyName)
        print(companyName, '-- start')
        response = requests.get(newUrl)
        response = json.loads(response.content)
        print(companyName, '-- end')
        if response.get('pointsData') is not None:
            for point in response.get('pointsData').values():
                if point.get('tosdr') is not None and point.get('quoteText') is not None and point.get('quoteDoc') is not None:
                    data = companyData(companyName, point.get('tosdr').get('point'), point.get('quoteText'),
                                       point.get('quoteDoc'))
                    dataList.append(data)

    COLUMN_NAMES = ['CompanyName', 'Point', 'QuoteText', 'quoteDoc']
    df = pd.DataFrame(columns=COLUMN_NAMES)
    for data in dataList:
        df = df.append({'CompanyName': data.companyName,
                        'Point': data.point,
                        'QuoteText': data.quoteText,
                        'quoteDoc': data.quoteDoc},
                       ignore_index=True)
    df.to_csv(r'../datapoint.csv', index=False, encoding="utf-8-sig")
    print(len(dataList))

if __name__ == "__main__":
    main()
