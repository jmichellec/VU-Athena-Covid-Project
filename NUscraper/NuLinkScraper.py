import os
from bs4 import BeautifulSoup
import requests
import Build_Sqlite_Database

currentpath = os.getcwd()

# Start a Selenium driver
#chromedriver = currentpath + '/chromedriver.exe'

#driver = webdriver.Chrome(chromedriver)

nucategories = ['https://www.nu.nl/rss/coronavirus', 'https://www.nu.nl/rss/binnenland', 'https://www.nu.nl/rss/buitenland', 'https://www.nu.nl/rss/algemeen', 'https://www.nu.nl/rss/politiek', 'https://www.nu.nl/rss/klimaat', 'https://www.nu.nl/rss/dvn', 'https://www.nu.nl/rss/weer', 'https://www.nu.nl/rss/weekend', 'https://www.nu.nl/rss/economie', 'https://www.nu.nl/rss/geldzaken', 'https://www.nu.nl/rss/werk', 'https://www.nu.nl/rss/ondernemen', 'https://www.nu.nl/rss/brexit', 'https://www.nu.nl/rss/auto', 'https://www.nu.nl/rss/aandelen', 'https://www.nu.nl/rss/verkeer', 'https://www.nu.nl/rss/sport', 'https://www.nu.nl/rss/voetbal', 'https://www.nu.nl/rss/formule-1', 'https://www.nu.nl/rss/live/voetbal', 'https://www.nu.nl/rss/spellen', 'https://www.nu.nl/rss/tech', 'https://www.nu.nl/rss/games', 'https://www.nu.nl/rss/reviews', 'https://www.nu.nl/rss/tech-achtergrond', 'https://www.nu.nl/rss/entertainment', 'https://www.nu.nl/rss/film', 'https://www.nu.nl/rss/muziek', 'https://www.nu.nl/rss/cultuur-overig', 'https://www.nu.nl/rss/media', 'https://www.nu.nl/rss/achterklap', 'https://www.nu.nl/rss/tvgids', 'https://www.nu.nl/rss/overig', 'https://www.nu.nl/rss/dieren', 'https://www.nu.nl/rss/eten-en-drinken', 'https://www.nu.nl/rss/gezondheid', 'https://www.nu.nl/rss/nucheckt', 'https://www.nu.nl/rss/opmerkelijk', 'https://www.nu.nl/rss/uit', 'https://www.nu.nl/rss/vakantie', 'https://www.nu.nl/rss/wetenschap', 'https://www.nu.nl/rss/wonen', 'https://www.nu.nl/rss/regio', 'https://www.nu.nl/rss/alphen-aan-den-rijn', 'https://www.nu.nl/rss/amsterdam', 'https://www.nu.nl/rss/breda', 'https://www.nu.nl/rss/den-haag', 'https://www.nu.nl/rss/eindhoven', 'https://www.nu.nl/rss/groningen', 'https://www.nu.nl/rss/haarlem', 'https://www.nu.nl/rss/leiden', 'https://www.nu.nl/rss/walcheren-en-beveland', 'https://www.nu.nl/rss/rotterdam', 'https://www.nu.nl/rss/utrecht', 'https://www.nu.nl/rss/west-brabant', 'https://www.nu.nl/rss/zwolle']

for category in nucategories:
    # Reach the Nu.nl RSS website
    r = requests.get(category)
    # Get the source html in xml format
    soup = BeautifulSoup(r.content, "lxml")

    itemlinks = soup.find_all('item')

    allitems = []

    for item in itemlinks:
        title = item.find('title').text
        link = item.find('link')
        linktext = link.next_sibling
        description = item.find('description').text
        pubdate = item.find('pubdate').text
        guid = item.find('guid').text
        try:
            enclosure = item.find('enclosure')['url']
        except AttributeError:
            enclosure = ''
        categorylist = item.find_all('category')
        emptycategories = [''] * (9 - len(categorylist))
        newcategorylist = []
        for cat in categorylist:
            newcategorylist.append(cat.text)
        newcategorylist += emptycategories
        try:
            creator = item.find('dc:creator').text
        except AttributeError:
            creator = ''
        try:
            rights = item.find('dc:rights').text
        except AttributeError:
            rights = ''

        itemlist = [title, linktext, description, pubdate, guid, enclosure] + newcategorylist + [creator, rights, category, '']
        findurl = Build_Sqlite_Database.database_search_links(currentpath + '/URLlist.db', guid)
        if findurl == 'notFound':
            allitems.append(itemlist)


    for itemlist in allitems:
        Build_Sqlite_Database.database_main(currentpath + '/URLlist.db', itemlist)