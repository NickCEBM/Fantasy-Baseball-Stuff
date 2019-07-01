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
from datetime import date


# +
def get_page(url):
    response = get(url)
    html = response.content
    soup = BeautifulSoup(html, "html.parser")
    return soup

base_ff_url = 'https://www.fleaflicker.com/mlb/leagues/'
league_ids = ['21579', '21581', '21580', '21582', '21583', '21584', '21585', '21586', '21587', '21588', '21589', 
              '21590', '21591', '21592', '21593', '21594', '21595', '21596']

all_teams = []
for l in league_ids:
    url = base_ff_url + l
    soup = get_page(url)
    trs = soup.find_all('tr')
    raw_headers = trs[1].find_all('th')
    player_data = trs[2:]
    headers = []
    for header in raw_headers:
        if header.text:
            headers.append(header.text)
    exp_headers = headers + ['league_id', 'league_name', 'team_id']   
    league_name = soup.find_all('li', {'class': 'active'})[1].text.strip()
    for row in player_data:
        d_dict = dict.fromkeys(exp_headers)
        d_dict['league_id'] = l
        d_dict['league_name'] = league_name
        d_dict['Team'] = row.find('td', {'class': 'left'}).text
        d_dict['Owner'] = row.find('td', {'class': 'right'}).text
        d_dict['team_id'] = row.find('a', href=True).get('href')[-6:]
        try:
            d_dict['Rank'] = row.find_all('td', {'class': 'right text-center'})[-1].text
        except IndexError:
            d_dict['Rank'] = row.find_all('td', {'class': 'bottom right text-center'})[-1].text
        heads = ['HR', 'R','RBI','SB','OBP','OPS','SO','SV','HD','ERA','WHP','QS']
        if d_dict['Owner'] == 'Take Over':
            stats = row.find_all('span', {'class': 'nowrap'})
        else:
            stats = row.find_all('span', {'class': 'nowrap'})[1:]
        for h, s in zip(heads, stats):
            d_dict[h] = s.text
        all_teams.append(d_dict)
# -

all_df = pd.DataFrame(all_teams, columns=exp_headers)
all_df.HR = all_df.HR.str.replace(",","").astype(int)
all_df.R = all_df.R.str.replace(",","").astype(int)
all_df.RBI = all_df.RBI.str.replace(",","").astype(int)
all_df.SB = all_df.SB.astype(int)
all_df.OBP = all_df.OBP.astype(float)
all_df.OPS = all_df.OPS.astype(float)
all_df.SO = all_df.SO.str.replace(",","").astype(int)
all_df.SV = all_df.SV.astype(int)
all_df.HD = all_df.HD.astype(int)
all_df.ERA = all_df.ERA.astype(float)
all_df.WHP = all_df.WHP.astype(float)
all_df.QS = all_df.QS.astype(int)

rank_headers = ['HR', 'R','RBI','SB','OBP','OPS','SO','SV','HD','ERA','WHP','QS']
for r in rank_headers:
    if r in ['ERA', 'WHP']:
        all_df[r+'_Points'] = all_df[r].rank(ascending=False)
    else:
        all_df[r+'_Points'] = all_df[r].rank()

all_df['Total_Points'] = all_df.iloc[:,-12:].sum(axis=1)
all_df['Overall_Rank'] = all_df.Total_Points.rank(ascending=False)

all_df.head()

t_date = str(date.today())
all_df.to_csv('current_rankings_'+t_date+'.csv')


