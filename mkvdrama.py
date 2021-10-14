import requests
from bs4 import BeautifulSoup as Soup

# Example
# lenk = 'https://mkvdrama.com/download-a-love-so-beautiful-korean-drama/'
# lenk = 'https://mkvdrama.com/download-dark-hole-korean-drama/'

lenk = input("Enter mkvdrama link: ")

q = {'1': '540', '2': '720', '3': '1080'}
choice = '0'
while choice not in q:
    print("Resolutions: ")
    for x, res in q.items():
        print(x, ':', res+'p')
    choice = input("Enter choice: ")
print()


def getLenks(lnk, res_ch):
    soup = Soup(requests.get(lnk).content, 'lxml')
    table = soup.table
    for episodes in table.find_all('tr'):
        ep, res, ddl = episodes.find_all('td')[:3]
        try:
            index = res.text.split('p').index(res_ch)
        except ValueError:
            continue
        jmp = ddl.text.count('|') // res.text.count('p') + 1
        for dl_lnk in ddl.find_all('a')[index * jmp:(index + 1) * jmp]:
            if dl_lnk.text in ('Mega', 'MG'):
                break
        print(ep.text, ':', dl_lnk.text, '-', dl_lnk['href'])


getLenks(lenk, q[choice])
