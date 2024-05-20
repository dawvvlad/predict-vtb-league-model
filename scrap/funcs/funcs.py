import re

from bs4 import BeautifulSoup
import requests


def get_seasons_data(write_file_path: str):
    season_ids = [4609, 5196, 5774, 6467, 6955, 7529, 8099, 8777, 327328, 666604]
    all_season_urls = []

    for season in season_ids:
        url = f'https://www.sports.ru/basketball/tournament/vtb-league/calendar/?s={season}'
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        el = soup.find('div', class_='months')
        matches_by_months = el.find_all('a')
        for match in matches_by_months:
            all_season_urls.append(match['href'])

    with open(write_file_path, 'w') as f:
        for url in all_season_urls:
            f.write(url + '\n')


def write_all_matches_data(read_file_path: str, write_file_path: str):
    all_matches_urls = []
    with open(read_file_path, 'r') as f:
        for url in f.read().splitlines():
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            el = soup.find_all('a', class_='score')
            for match in el:
                all_matches_urls.append(match.get('href'))

    with open(write_file_path, 'w') as f:
        for url in all_matches_urls:
            f.write(url + '\n')


def get_game_stats(uri):
    arr = []
    r = requests.get(uri)
    soup = BeautifulSoup(r.text, 'html.parser')
    tfoots = soup.find_all('tfoot')

    if tfoots:
        for tfoot in tfoots:
            arr.append(tfoot)
    else:
        print("Не найдены данные для обработки на странице", uri)
        return None

    arr2 = [[], []]

    tds1 = arr[0].find_all('td')
    for td in tds1:
        arr2[0].append(td.get_text())

    tds2 = arr[1].find_all('td')
    for td in tds2:
        arr2[1].append(td.get_text())

    pattern = r'\b\d+(?:/\d+)?\b'

    numbers = [match.group() for item in arr2[0] for match in re.finditer(pattern, item)]
    numbers2 = [match.group() for item in arr2[1] for match in re.finditer(pattern, item)]
    numbers.pop()
    numbers2.pop()

    res = numbers + numbers2

    columns = ['Очки', '2-очк-3/В', '2-очк-%', '3-очк-3/В', '3-очк-%', 'Штрафные-3/В', 'Штрафные-%', 'Подборы',
               'Передачи', 'Фолы', 'Перехваты', 'Потери', 'Блокшоты', 'МИН',
               'Очки прот.', '2-очк-3/В прот.', '2-очк-% прот.', '3-очк-3/В прот.', '3-очк-% прот.',
               'Штрафные-3/В прот.', 'Штрафные-% прот.', 'Подборы прот.', 'Передачи прот.', 'Фолы прот.',
               'Перехваты прот.', 'Потери прот.', 'Блокшоты прот.', 'МИН']

    el = soup.find_all('h2', class_='titleH2')

    data_dict = {col: res[i] for i, col in enumerate(columns)}

    data_dict['Имя'] = el[0].text
    data_dict['Имя прот.'] = el[1].text

    won = data_dict.get('Очки') > data_dict.get('Очки прот.')
    data_dict['Победа'] = '1' if won else '0'

    won_home_team = int(numbers[0]) > int(numbers2[0])
    data_dict['Победа дома'] = '1' if won_home_team else '0'

    return data_dict


url = 'https://www.sports.ru/basketball/match/1229550/#online'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
data = soup.find_all('h1', class_='titleH1')

match = re.search(r'\d+\s\w+\s\d{4}', data[0].text)
print(match.group())


def get_game_stats(uri):
    arr = []

    r = requests.get(uri)
    soup = BeautifulSoup(r.text, 'html.parser')
    tfoots = soup.find_all('tfoot')

    if tfoots:
        for tfoot in tfoots:
            arr.append(tfoot)
    else:
        print("Не найдены данные для обработки на странице", uri)
        return None

    arr2 = [[], []]

    tds1 = arr[0].find_all('td')
    for td in tds1:
        arr2[0].append(td.get_text())

    tds2 = arr[1].find_all('td')
    for td in tds2:
        arr2[1].append(td.get_text())

    pattern = r'\b\d+(?:/\d+)?\b'

    numbers = [match.group() for item in arr2[0] for match in re.finditer(pattern, item)]
    numbers2 = [match.group() for item in arr2[1] for match in re.finditer(pattern, item)]
    numbers.pop()
    numbers2.pop()

    res = numbers + numbers2

    columns = ['Очки', '2-очк-3/В', '2-очк-%', '3-очк-3/В', '3-очк-%', 'Штрафные-3/В', 'Штрафные-%', 'Подборы',
               'Передачи', 'Фолы', 'Перехваты', 'Потери', 'Блокшоты', 'МИН',
               'Очки прот.', '2-очк-3/В прот.', '2-очк-% прот.', '3-очк-3/В прот.', '3-очк-% прот.',
               'Штрафные-3/В прот.', 'Штрафные-% прот.', 'Подборы прот.', 'Передачи прот.', 'Фолы прот.',
               'Перехваты прот.', 'Потери прот.', 'Блокшоты прот.', 'МИН']

    names = soup.find_all('h2', class_='titleH2')
    dates = soup.find_all('h1', class_='titleH1')
    match = re.search(r'\d+\s\w+\s\d{4}', dates[0].text)

    data_dict = {col: res[i] for i, col in enumerate(columns)}

    if names:
        data_dict['Имя'] = names[0].text
        data_dict['Имя прот.'] = names[1].text
    else:
        print("Названия команды нет", uri)
        return None

    won = int(data_dict.get('Очки')) > int(data_dict.get('Очки прот.'))

    data_dict['Победа'] = '1' if won else '0'

    won_home_team = int(numbers[0]) > int(numbers2[0])
    data_dict['Победа дома'] = '1' if won_home_team else '0'

    if dates and match:
        data_dict['Дата'] = match.group()
    else:
        data_dict['Дата'] = 'N/A'

    return data_dict
