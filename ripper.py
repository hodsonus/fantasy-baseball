import mechanize
import time
import re
import pandas as pd
import config
import bs4

username = config.credentials['yahoo_email']
password = config.credentials['yahoo_password']
league_id = config.credentials['yahoo_league_id']
sport = config.credentials['sport']
sport_prefix = sport[0]

player_info = []

br = mechanize.Browser()
br.set_handle_robots(False)
br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6')]

print('Logging in.')
url = f'https://login.yahoo.com/config/login;_ylt=AwrGB7pqzTxUF9oAigC3cJ8u?.src=fantasy&.intl=us&.lang=en-US&.done=http://{sport}.fantasysports.yahoo.com/{sport_prefix}1/{league_id}/players'
br.open(url)
time.sleep(.5)

br.select_form(nr=0)
br.form["username"] = username
br.form["passwd"] = password
response = br.submit()
time.sleep(.5)

br.select_form(nr = 0)
br.form["password"] = password
response = br.submit()
time.sleep(.5)
print('Logged in!')

i=1
while (True): # rip player data until we hit the break statement

    html_scrape = response.read()
    soup = bs4.BeautifulSoup(html_scrape, "lxml")

    # with open("out"+str(i)+".html", "w") as text_file:
    #     text_file.write(str(soup))

    print('Processing page ',i,'.',sep="")
    i+=1

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
    time.sleep(.5)

print('Creating dataframe.')
df = pd.DataFrame(player_info, columns=['PLAYER', 'TEAM', 'POS'])

# print(df)

print('Writing the dataframe to an excel spreadsheet.')
writer = pd.ExcelWriter('Players.xlsx')
df.to_excel(writer,'Sheet',index=False)
writer.save()
print('Done! Check the working directory for the completed spreadsheet.')