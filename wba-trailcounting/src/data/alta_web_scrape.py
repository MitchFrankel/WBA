"""
Webscrape annual snowfall from Alta's webage
"""

# Imports
import requests
import bs4
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime


# Initializations
curr_season = [2019, 2020]
past_seasons = 16


# Set up Alta's webpage
headers = {'Accept': '*/*',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'en-US,en;q=0.9',
           'Connection': 'keep-alive',
           'Content-Length': '55',
           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
           'Cookie': '_ga=GA1.2.715602370.1568149005; _fbp=fb.1.1568149006234.629873357; _gid=GA1.2.364080449.1574268539; _cookie_token=4e15d76f7dfb5a321d20e9b6f6597921; bz_session=7fNWm%2B2BJpxSXDpEQuFVFyUFOgTWXvHIn%2ByjFX1DAIVNopdRq5u2R%2Fton5rXDjIvSG%2FxSLdFEaq1s2Ii7vc6vEyU3A0PDAtUKcCevTNgVA80HR6QHpl%2BtFkM4i6qIdq4GbvikD%2BKOH0hARINjFknGu0KowP6x97KthsEJ6AgYdppQIIah7vNETjbX2CIwz7qCLRDwUnF2%2B7RFaBIQb%2FhPhGJDNULSrGZ5kJrU5dJBy6YKaC7INB%2B3PBvCCXFHRQ1MMsQnSRhQGncZUvBt0h2z%2FRWB5afR2lutR0ODBrGi3FpsiEUX%2FNn4ulHRqxSJdk5ygGZUef8ErbXWpzIIeBNasKLMQ58ClzFCp%2BERGcEHx6hFeWPB776XQT5isO4uM7nLDuS2ONDkRdjTU66AKE3SWMikCwJ5lFS5bXR04lp7WV59VO0R%2B09%2F%2F6zRsN97gbxMf5%2BOZFY%2FY25bgDw6uSuHQ%3D%3D9bb1d0108774c5ecbb16d5b7e63ee1928378f45e',
           'DNT': '1',
           'Host': 'www.alta.com',
           'Origin': 'https://www.alta.com',
           'Referer': 'https://www.alta.com/conditions/weather-observations/snowfall-history',
           'Sec-Fetch-Mode': 'cors',
           'Sec-Fetch-Site': 'same-origin',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
           'X-Requested-With': 'XMLHttpRequest'}
url = 'https://www.alta.com/conditions/weather-observations/snowfall-history'

# Pull current years data
curr_year = "".join(str(x) for x in curr_season)
form_data = {'_token': '4e15d76f7dfb5a321d20e9b6f6597921', 'season': curr_year}
response = requests.post(url, data=form_data, headers=headers)

# Get table headers
soup = BeautifulSoup(response.text, 'lxml')
snowfall_table = soup.find('table', {'class': 'table table-striped'})
table_headers = []
for th in snowfall_table.find_all('th'):
    th_str = " ".join(x for x in th.contents if type(x) != bs4.element.Tag)
    if th_str not in table_headers:
        table_headers.append(th_str)

# Loop through all desired seasons and append to dataframe
df = pd.DataFrame(columns=['season'] + table_headers)
for i in range(past_seasons):

    season = "-".join(str(x - i) for x in curr_season)
    form_data = {'_token': '4e15d76f7dfb5a321d20e9b6f6597921', 'season': season.replace("-", "")}
    response = requests.post(url, data=form_data, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    snowfall_table = soup.find('table', {'class': 'table table-striped'})
    all_data_rows = snowfall_table.find('tbody').find_all('tr')

    for row in all_data_rows:
        df.loc[len(df)] = [season] + [x.contents[0].strip() for x in row.find_all('td')]

# Remove "Trace" or "Trac" of "NA" rows
for th in table_headers[1:]:
    df = df[df[th] != 'Trace']
    df = df[df[th] != 'Trac']
    df = df[df[th] != 'N/A']

# Convert data to datetime and floats
df[table_headers[0]] = df[table_headers[0]].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
for th in table_headers[1:]:
    df[th] = df[th].apply(lambda x: float(x[:-1]))

file_path = os.path.abspath(os.path.join(os.getcwd(), "..", "..", "data", "raw", "alta_snowfall.csv"))
df.to_csv(file_path, index=False)

