import requests
from bs4 import BeautifulSoup as Soup
from dotenv import dotenv_values

env = dotenv_values()
USERNAME, PASSWORD = env.get('HI10_USERNAME'), env.get('HI10_PASSWORD')
assert USERNAME and PASSWORD, "HI10_USERNAME or HI10_PASSWORD not set in .env file"

header = {'User-Agent': 'Mozilla/5.0'}
jtoken = '121308a2bd'


def login_session() -> requests.Session:
    data = {
        'log': USERNAME,
        'pwd': PASSWORD,
        'rememberme': "forever"
    }
    sess = requests.Session()
    sess.post('https://hi10anime.com/wp-login.php', headers=header, data=data)
    return sess


def search_post(search_term: str) -> str:
    r = sess.get('https://hi10anime.com/?s=' + '+'.join(search_term.split()))
    soup = Soup(r.content, 'lxml')
    post = soup.article.h1.a
    print("Found post with title :", post.text)
    return post['href']


sess = login_session()

search_term = input("Enter search query: ").lower()
url = search_post(search_term)

ddl = []
r = sess.get(url, headers=header)
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
    old()
except AttributeError:
    new()

ddl = list(map(lambda x: x.split('s=')[1] + f'?{jtoken=!s}', ddl))
print(*ddl, sep='\n')
