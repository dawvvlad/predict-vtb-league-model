import pandas as pd

df = pd.read_csv('../data/csv/games_data_2.csv')
team_stats_by_season = pd.read_csv('../data/csv/team_stats.csv')

# Статистика каждой команды в сезоне
team_stats_by_season['% Побед дома'] = team_stats_by_season['Побед дома'].apply(
    lambda x: round(int(x.split('-')[0]) / int(x.split('-')[1]) if int(x.split('-')[1]) != 0 else int(x.split('-')[0]),
                    2)).copy()
team_stats_by_season['% Побед в гостях'] = team_stats_by_season['Побед в гостях'].apply(
    lambda x: round(int(x.split('-')[0]) / int(x.split('-')[1]) if int(x.split('-')[1]) != 0 else int(x.split('-')[0]),
                    2)).copy()
team_stats_by_season.drop(columns=['Побед дома'], inplace=True)
team_stats_by_season.drop(columns=['Побед в гостях'], inplace=True)

# Выборка нечисловых значений
float_fields = [x for x in df.keys() if x.endswith('3/В') or x.endswith('В прот.')]
percent_fields = [x for x in df.keys() if x.endswith('%') or x.endswith('% прот.')]

# Представление нечисловых значений в процентах
for fl in float_fields:
    df[fl] = df[fl].apply(lambda x: int(x.split('/')[0]) / int(x.split('/')[1]) if '/' in x else 0)

for per in percent_fields:
    df[per] = df[per].apply(lambda x: int(x) / 100 if x > 0 else 0)

df = df.dropna(axis=0, how='any')


# Создание столбца Сезон
def get_season(date_str):
    year = int(date_str.split()[-1])
    if year == 2024:
        return 2024
    return f"{year + 1}"


df['Сезон'] = df['Дата'].apply(get_season)
