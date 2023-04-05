import requests
from bs4 import BeautifulSoup
import json
#from fake_headers import Headers
#не получилось установить библиотеку fake_headers - pip выполняется успешно, а в списке пакетов она не появляется (?)

HEADERS = {
    'User-Agent': 'Firefox/99.0'
}
HOST = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'

def find_keywords_in_description(link) ->bool :
    '''проверка на вхождение в текст описания ключевых слов'''
    description = requests.get(link, headers=HEADERS)
    if description.status_code == 404:
        return False
    soup = BeautifulSoup(description.text, 'lxml')
    tag_content = soup.find(class_='vacancy-description-print')
    if tag_content:
        text = tag_content.text.lower()
        if 'django' in text or 'flask' in text:
            return True
    return False

def parse_all_vacancies(page_text, res):
    '''просмотр вакансий на текущем листе'''
    soup = BeautifulSoup(page_text, 'lxml')
    vacancies = soup.find_all('div', class_='serp-item', limit=50)
    qty = len(vacancies) - 1
    for ind, vacancy in enumerate(vacancies):
        # fill = round(20 * ind / qty)
        # print(f'\r  {(100 * ind / qty):3.0f}% {("▒" * fill).ljust(20)}', end='')
        link_tag = vacancy.find("a", class_='serp-item__title')
        link = link_tag['href']
        title = link_tag.text
        salary = vacancy.find('span', class_='bloko-header-section-3')
        if salary:
            salary = vacancy.find('span', class_='bloko-header-section-3').text
        else:
            salary = 'оплата труда по договоренности'
        company = vacancy.find('a', class_='bloko-link bloko-link_kind-tertiary').text
        dop = vacancy.find('div', class_='vacancy-serp-item__info')
        city = dop.find_all('div', class_='bloko-text')[1].text
        datadict = {
                    'title': title,
                    'salary': salary,
                    'company': company,
                    'city': city,
                    'link': link
                    }
        if find_keywords_in_description(link):
            res.append(datadict)
        fill = round(20 * ind / qty)
        print(f'\r  {(100 * ind / qty):3.0f}% {("▒" * fill).ljust(20)}', end='')
    print()

def create_vacancies_list() -> list:
    '''формируем список вакансий'''
    res_list = []
    page_num = 0
    while page_num < 2: #чтобы не заблокировали из-за кол-ва запросов
        url = f'{HOST}&page={page_num}'
        print(f'page {page_num}')
        page = requests.get(url, headers=HEADERS)
        if page.status_code != 404:
            parse_all_vacancies(page.text, res_list)
            page_num += 1
        else:
            break
    return res_list

def main():
    data = create_vacancies_list()
    if data:
        with open('vacancies.json', 'w', encoding='utf-8') as fout:
            json.dump(data, fout, indent=3, ensure_ascii=False)
        print(json.dumps(data, indent=3, ensure_ascii=False))

if __name__ == '__main__':
    main()

