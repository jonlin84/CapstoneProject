import time
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient


#returns basketball-refrence.com/teams/{teamname}/{year}_games.html
def box_score_url_creator(team:str,year:str,baseurl:str)->list:
    return [baseurl + '/teams/' + team + '/' + year + '_games.html']


#returns big dictionary of teams:{'year'{year:[html]}}
#team name, 'year' dictornary with year# key and list of string value
#example {'HOU':{'year':{1994:[www.worldchampions.com]}}}
def url_list_generator(teams:list,years:list):
    biglist = {}
    baseurl = 'https://www.basketball-reference.com'
    for team in teams:
        biglist[team] = {}
        biglist[team]['year'] = {}
        for year in years:
            biglist[team]['year'][int(year)] = box_score_url_creator(team,year,baseurl)
    return biglist

#taking big list and making containers
def soup_maker(dct:dict):
    boxscores = {}
    for team in dct.keys():
        boxscores[team] = {}
        for year in dct[team]['year'].keys():
            boxscores[team]['year'] = {}
            url = dct[team]['year'][year][0]
            r = requests.get(url)
            soup = BeautifulSoup(r.content,'html.parser')
            boxscores[team]['year'][int(year)] = get_box_score_url(soup)
            time.sleep(3)

#returns a list of urls extensions to boxscores from a team for a particular year
#soup should be the parsed content from a team/year's url
def get_box_score_url(soup):
    container = []
    for link in soup.find_all('a'):
        k = str(link.get('href'))
        if k.startswith('/boxscores/20'):
            container.append(k)
    return container[:82]

#second attempt to make soup, this did not work as intended...DEBUG <---
def soup_maker(dct:dict):
    boxscores = {}
    for team in dct.keys():
        boxscores[team] = {}
        for year in dct[team]['year'].keys():
            boxscores[team]['year'] = {}
            url = dct[team]['year'][int(year)][0]
            r = requests.get(url)
            soup = BeautifulSoup(r.content,'html.parser')
            boxscores[team]['year'][int(year)] = get_box_score_url(soup)
            time.sleep(3)
    return boxscores

#Write a function that extracts data and stores it in proper dictionaries
#Basica box score stats for each team and also information on officals
#assume first official is HEAD OFFICIAL?

#html = r.content, returns dictionary of box score totals
def scrape_stats_from_page(html,team:str):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select(f'#box_{team.lower()}_basic tfoot tr td')
    return {item.attrs.get('data-stat'): item.text for item in items}

#--------------------------------------------------------------
#all relevant functions I used

#code to create dictionary with
#probably bad practice but
# iterates over each row and populates a dictionary 
#returns dictionary
def create_dct_content_spread(df):
    biglist = {}
    for i in range(len(df.content)):
        if df.team[i] not in biglist.keys():
            biglist[df.team[i]] = {}
        if df.year[i] not in biglist[df.team[i]].keys():
            biglist[df.team[i]][df.year[i]] = {}
        soup = BeautifulSoup(df.content[i], 'html.parser')
        for count,items in enumerate(soup.select('tbody tr'),1):
            biglist[df.team[i]][spreads_df.year[i]][count] = []
            temp = []
            for item in items.select('td'):
                temp.append(item.get_text())
            biglist[df.team[i]][df.year[i]][count] += temp
    return biglist

'''
list of variables to use for iterations

teams    =    ['ATL','BOS','BRK','CHI','CHO','CLE','DAL','DEN','DET','GSW','HOU','IND','LAC','LAL','MEM','MIA','MIL','MIN','NOP','NYK',\
              'OKC','ORL', 'PHI','PHO','POR','SAC','SAS','TOR','UTA','WAS']

years    =    ['2014','2015','2016','2017','2018']

team_dic = {  'Dallas':'DAL','Boston':'BOS','Toronto':'TOR','Denver':'DEN','Philadelphia':'PHI'\
            , 'New York':'NYK','Orlando':'ORL','Cleveland':'CLE','Detroit':'DET'\
            , 'Miami':'MIA','Charlotte':'CHO','Houston':'HOU','San Antonio':'SAS','LA Clippers':'LAC','Washington':'WAS'\
            , 'Oklahoma City':'OKC', 'Milwaukee':'MIL','Phoenix':'PHO','Sacramento':'SAC','New Orleans':'NOP'\
            , 'Indiana':'IND','Portland':'POR','Brooklyn':'BRK', 'Golden State':'GSW','Chicago':'CHI'\
            , 'LA Lakers':'LAL','Memphis':'MEM','Atlanta':'ATL','Utah':'UTA','Minnesota':'MIN'}
'''

#function to change the string in opponent to 3 letter abbreviation consistent for search
def switch_to_key(x):
    for k,v in team_dic.items():
        if k in x:
            return v

#takes dataframe and list of teams('strings') 
def dataframe_separator(df,teams:list):
    lst = []
    for team in teams:
        lst.append(copy.deepcopy(df[df.team == f'{team}']))
    return dict(zip(teams,lst))
