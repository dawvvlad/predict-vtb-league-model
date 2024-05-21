import pandas as pd
from matplotlib import pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import TimeSeriesSplit, train_test_split, cross_val_score
from sklearn.feature_selection import SequentialFeatureSelector
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score
import seaborn as sns
from funcs import get_team_season_stats
from data import df, team_stats_by_season

result_data = get_team_season_stats('ЦСКА')

dataset = pd.merge(df, team_stats_by_season, on=['Имя', 'Сезон'], how='left')

team_stats_by_season_prot = team_stats_by_season.rename(columns=lambda x: x + ' прот.' if x not in ['Сезон', 'Имя'] else x)

# Объединение данных по имени противника
dataset = pd.merge(dataset, team_stats_by_season_prot, left_on=['Имя прот.', 'Сезон'], right_on=['Имя', 'Сезон'], how='left')

# Целевой признак
def add_target(team):
    team['Цель'] = team['Победа'].shift(-1)
    return team


dataset = dataset.groupby('Имя_x', group_keys=False).apply(add_target).copy().dropna().reset_index(drop=True)
dataset['Цель'] = dataset['Цель'].astype(int, errors='ignore')

dataset.rename(columns={'Имя_x': 'Имя'}, inplace=True)
dataset.drop(columns=['Имя_y'], inplace=True)

lr = LogisticRegression()
split = TimeSeriesSplit(n_splits=3)
sfs = SequentialFeatureSelector(lr, n_features_to_select=30, direction='forward', cv=split)

removed_cols = ['Сезон', 'Дата', 'Цель', 'Победа', 'Имя', 'Имя прот.', 'Победа дома']
selected_cols = dataset.columns[~dataset.columns.isin(removed_cols)]

scaler = MinMaxScaler()
dataset[selected_cols] = scaler.fit_transform(dataset[selected_cols])

sfs.fit(dataset[selected_cols], dataset['Цель'])
predictors = list(selected_cols[sfs.get_support()])

args = ['Блокшоты', 'Забито', 'Перехваты', 'Пропущено', 'Разница']
for i in args:
    predictors.append(i)
predictors.sort()


def back_test(data, model, predictors, start=2, step=1):
    seasons = sorted(data['Сезон'].unique())
    for i in range(start, len(seasons), step):
        season = seasons[i]
        train = data[data['Сезон'] < season]
        model.fit(train[predictors], train['Цель'])
    return model


model = back_test(dataset, lr, predictors)


def get_team_data(team, team_2):

    team_1_df = dataset[(dataset['Имя'] == team)]
    team_2_df = dataset[(dataset['Имя'] == team_2)]

    team_1_df['Сезон'] = pd.to_numeric(team_1_df['Сезон'])
    team_2_df['Сезон'] = pd.to_numeric(team_2_df['Сезон'])

    team_1_sorted = (team_1_df.sort_values(by='Сезон'))
    team_2_sorted = team_2_df.sort_values(by='Сезон')

    last_10_games_1 = team_1_sorted[predictors].tail(10).filter(regex='^(?!.*прот).*$')
    last_10_games_2 = team_2_sorted[predictors].tail(10).filter(regex='^(?!.*прот).*$').rename(
        columns=lambda x: f"{x} прот.")
    last_10_games_2.drop(columns=['МИН прот.', 'Потери прот.', 'Фолы прот.'], inplace=True)
    combined = pd.concat([last_10_games_1.reset_index(drop=True), last_10_games_2.reset_index(drop=True)], axis=1)
    return combined.mean().to_frame().T.sort_index(axis=1)

t2 = 'Автодор'
t1 = 'ЦСКА'
pr_data = get_team_data(t1, t2)
pr_data = pr_data.loc[:, ~pr_data.columns.duplicated()]

pred = model.predict_proba(pr_data)
print(f'Вероятность победы в матче: {t1 if pred[0][0] < pred[0][1] else t2} побеждает')
print(pred)


