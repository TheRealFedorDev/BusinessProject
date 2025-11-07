import requests
from bs4 import BeautifulSoup

def get_vacancies(keyword):
    url = f"https://hh.ru/search/vacancy?text={keyword}"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    titles = [a.text for a in soup.find_all('a', class_='serp-item__title')]
    return titles[:5]

print(get_vacancies("Python"))
