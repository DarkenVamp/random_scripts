import requests
from bs4 import BeautifulSoup as Soup
import os

COOKIE = os.getenv('HI10_COOKIE')
assert COOKIE, "Set Cookie in 'HI10_COOKIE' environment variable"

header = {'Cookie': COOKIE, 'User-Agent': 'Mozilla/5.0'}
jtoken = '121308a2bd'

name = input("Enter search query: ").lower()
r = requests.get('https://hi10anime.com/?s=' + '+'.join(name.split()))
soup = Soup(r.content, 'lxml')
post = soup.article.h1.a
print("Found post with title :", post.text)
url = post['href']

ddl = []
r = requests.get(url, headers=header)
soup = Soup(r.content, 'lxml')


def new():
    lnks_tbl = soup.find('div', {'class': 'episodes'})
    for row in lnks_tbl.find_all('span', {'class': 'ddl'}):
        data = row.find_all('a')
        ouo = filter(lambda x: x['href'].startswith('https://ouo.io/'), data)
        ddl.append(next(ouo)['href'])


def old():
    lnks_tbl = soup.find('table', {'class': 'showLinksTable'}).tbody
    for row in lnks_tbl.find_all('tr'):
        data = row.find_all('td')[2:]
        ouo = filter(lambda x: x.a['href'].startswith('https://ouo.io/'), data)
        ddl.append(next(ouo).a['href'])


try:
    new()
except AttributeError:
    old()

ddl = list(map(lambda x: x.split('s=')[1] + f'?{jtoken=!s}', ddl))
print(*ddl, sep='\n')
