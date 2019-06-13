# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

import pandas as pd
from requests import get
from bs4 import BeautifulSoup
import csv
from io import StringIO
import json

# +
url = 'https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=50&type=c%2c3%2c4%2c6%2c36%2c34%2c35%2c37%2c38%2c39%2c41%2c42%2c44%2c45%2c47%2c110%2c206%2c209&season=2019&month=0&season1=2019&ind=0&team=0&rost=0&age=0&filter=&players=0'

def get_page(url):
    response = get(url)
    html = response.content
    soup = BeautifulSoup(html, "html.parser")
    return soup

def get_fg_table(url):
    soup = get_page(url)
    max_page = soup.find('div', {"class": "rgWrap rgInfoPart"}).find_all('strong')[1].text
    pages = list(range(1,int(max_page)+1))
    table = soup.find('table',{"class": "rgMasterTable"})
    headers = []
    headers_website = table.find_all('tr')[1]
    for th in headers_website.find_all('th'):
        headers.append(th.text)
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    for page in pages:
        page_url = url + '&page={}_50'.format(page)
        soup = get_page(page_url)
        table = soup.find('table',{"class": "rgMasterTable"})
        players = table.find_all('tr')[3:]
        for player in players:
            s = []
            for stat in player.find_all('td'):
                s.append(stat.text)
            s_dict = dict(zip(headers,s))
            writer.writerow(s_dict)
    output.seek(0)
    df = pd.read_csv(output)
    return df

fg_df = get_fg_table(url)
fg_df.head()

# +
savant = 'https://baseballsavant.mlb.com/statcast_leaderboard?year=2019&abs=0&player_type=resp_batter_id'

def get_savant_table(url):
    soup = get_page(url)
    data = soup.find_all('script')[9].text
    data_string = data.split("var leaderboard_data = ",1)[1]
    cleaned = data_string.strip()[:-1]
    data_list = json.loads(cleaned)
    columns = list(data_list[0].keys())
    df = pd.DataFrame(data_list)
    df  = df[columns]
    return df

savant_df = get_savant_table(savant)
savant_df.head()


# +
def get_ids():
    csv = get('http://crunchtimebaseball.com/master.csv').content
    df = pd.read_csv(StringIO(csv.decode('latin-1')))
    return df

ids_df = get_ids()
# -

new_fg = fg_df.merge(ids_df[['mlb_id', 'fg_name']], left_on = 'Name', right_on = 'fg_name', how = 'left')

merged = new_fg.merge(savant_df, left_on = 'mlb_id', right_on = 'resp_batter_id', how = 'left')

merged.head()

merged['BB%'] = (merged['BB%'].str.replace('%','').astype(float)) / 100

merged.dtypes


