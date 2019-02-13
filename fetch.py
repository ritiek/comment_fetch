import requests
from bs4 import BeautifulSoup

response = requests.get('https://github.com/search?q=commenter%3Aritiek')
soup = BeautifulSoup(response.text, 'html.parser')
tags = soup.find_all('h3',{'text-normal flex-auto pb-1'})

for tag in tags:
	a = tag.find('a')
	print('https://github.com' + a['href'])

