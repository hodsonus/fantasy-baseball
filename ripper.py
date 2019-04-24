import mechanize
from bs4 import BeautifulSoup
import time
import re
import pandas as pd
from pandas import ExcelWriter
import config

username = config.credentials['yahoo_email']
password = config.credentials['yahoo_password']
league_id = config.credentials['yahoo_league_id']

player_info = []

br = mechanize.Browser()
br.set_handle_robots(False)
br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6')]

url = 'https://login.yahoo.com/config/login;_ylt=AwrGB7pqzTxUF9oAigC3cJ8u?.src=fantasy&.intl=us&.lang=en-US&.done=http://baseball.fantasysports.yahoo.com/b1/'+str(league_id)+'/players'
br.open(url)
time.sleep(1)

br.select_form(nr=0)
br.form["username"] = username
br.form["passwd"] = password
response = br.submit()
time.sleep(1)

br.select_form(nr = 0)
br.form["password"] = password
response = br.submit()
time.sleep(1)

# i=0
while (True): # rip player data until we hit the break statement

    html_scrape = response.read()
    soup = BeautifulSoup(html_scrape, "lxml")

    # with open("out"+str(i)+".html", "w") as text_file:
    #     text_file.write(str(soup))
    # i+=1

    players = soup.find_all('div', {'class':'ysf-player-name Nowrap Grid-u Relative Lh-xs Ta-start'})
    for player in players:
        name = player.find('a').get_text()
        team_pos_str = player.find('span').get_text()
        team_pos_lis = re.split(' - ',team_pos_str)
        team = team_pos_lis[0]
        pos = team_pos_lis[1]
        player_info+=[(name,team,pos)]

    links = br.links(text_regex='Next 25')
    link = next(links,None)
    if (link == None):
            break
    response = br.follow_link(link)
    time.sleep(1)

df = pd.DataFrame(player_info, columns=['PLAYER', 'TEAM', 'POS'])

print(df)
writer = ExcelWriter('Players.xlsx')
df.to_excel(writer,'Sheet',index=False)
writer.save()