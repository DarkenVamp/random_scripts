import requests
from bs4 import BeautifulSoup as Soup

# Example
# lenk = 'https://mkvdrama.com/download-a-love-so-beautiful-korean-drama/'
# lenk = 'https://mkvdrama.com/download-dark-hole-korean-drama/'

lenk = input("Enter mkvdrama link: ")


def getLenks(lnk):
    soup = Soup(requests.get(lnk).content, 'lxml')
    table = soup.table
    for episodes in table.find_all('tr'):
        ep, res, ddl = episodes.find_all('td')[:3]
        try:
            index = res.text.split('p').index('720')
        except ValueError:
            continue
        jmp = ddl.text.count('|') // res.text.count('p') + 1
        for dl_lnk in ddl.find_all('a')[index * jmp:(index + 1) * jmp]:
            if dl_lnk.text in ('Mega', 'MG'):
                break
        print(ep.text, ':', dl_lnk.text, '-', dl_lnk['href'])


getLenks(lenk)
