import pandas as pd
from data import df, team_stats_by_season


def get_team_season_stats(team_name: str):
    # Объединение данных, где команда упоминается как "Имя" и как "Имя противника"
    team_stats = df[(df['Имя'] == team_name)].copy()

    # Упрощение данных для работы
    team_stats['Имя'] = team_stats.apply(lambda row: team_name, axis=1)

    # Агрегирование данных по сезонам и командам
    grouped = team_stats.groupby(['Сезон', 'Имя'])

    team_season_stats = grouped.agg({
        '2-очк-%': 'mean',
        '3-очк-%': 'mean',
        'Штрафные-%': 'mean',
        'Подборы': 'mean',
        'Передачи': 'mean',
        'Фолы': 'mean',
        'Перехваты': 'mean',
        'Потери': 'mean',
        'Блокшоты': 'mean',
    }).reset_index()

    # Преобразуем тип данных столбца "Сезон" в строковый
    team_season_stats['Сезон'] = team_season_stats['Сезон'].astype(str)
    team_stats_by_season['Сезон'] = team_stats_by_season['Сезон'].astype(str)

    # Добавляем данные из таблицы team_stats_by_season
    team_season_stats = pd.merge(team_season_stats, team_stats_by_season, how='inner', on=['Сезон', 'Имя'])

    return team_season_stats
