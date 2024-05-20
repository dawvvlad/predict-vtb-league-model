import pandas as pd
import requests
from bs4 import BeautifulSoup

from funcs.funcs import get_game_stats

season_ids = [4609, 5196, 5774, 6467, 6955, 7529, 8099, 8777, 327328, 666604]
season_dates = ['2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']


def get_team_stats(season_id, season_date):

    data_dicts = []

    url = f'https://www.sports.ru/basketball/tournament/vtb-league/table/?s={season_id}&table=1&sub=table'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')


    table_rows = soup.select('tr')

    for row in table_rows:
        stats = row.find_all('td')
        names = row.find_all('a', class_='name')

        if stats and names:
            team_stats = {
                'Сезон': season_date,
                'Имя': names[0].get_text(strip=True),
                'Матчей': stats[2].get_text(strip=True),
                'Выиграно': stats[3].get_text(strip=True),
                'Проиграно': stats[4].get_text(strip=True),
                '%побед': stats[5].get_text(strip=True),
                'Забито': stats[6].get_text(strip=True),
                'Пропущено': stats[7].get_text(strip=True),
                'Разница': stats[8].get_text(strip=True),
                'Побед дома': stats[9].get_text(strip=True),
                'Побед в гостях': stats[10].get_text(strip=True),
            }
            data_dicts.append(team_stats)

    return data_dicts


columns = [
    'Сезон', 'Имя', 'Матчей', 'Выиграно', 'Проиграно', '%побед', 'Забито',
    'Пропущено', 'Разница', 'Побед дома', 'Побед в гостях'
]

full_data = []

for i in range(len(season_ids)):
    season_data = get_team_stats(season_ids[i], season_dates[i])
    full_data.extend(season_data)

df = pd.DataFrame(full_data, columns=columns)

df.to_csv("../data/csv/team_stats.csv", index=False)
