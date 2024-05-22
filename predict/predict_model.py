import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import TimeSeriesSplit, train_test_split
from sklearn.feature_selection import SequentialFeatureSelector
from sklearn.preprocessing import MinMaxScaler
from data import df, team_stats_by_season
from funcs import get_team_season_stats

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


def back_test(data, model, predictors):
    X = data[predictors]
    y = data['Цель']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)
    score = accuracy_score(model.predict(X_test), y_test)
    return model, score


model, score = back_test(dataset, lr, predictors)


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
    combined = pd.concat([last_10_games_1.reset_index(drop=True),
                          last_10_games_2.reset_index(drop=True)], axis=1)
    return combined.mean().to_frame().T.sort_index(axis=1)


t1 = 'ЦСКА'
t2 = 'Минск'

pr_data = get_team_data(t1, t2)
pr_data = pr_data.loc[:, ~pr_data.columns.duplicated()]

pred = model.predict_proba(pr_data)

lose_probability = pred[0][0]
win_probability = pred[0][1]

if win_probability < 0.6:
    res = f'Вероятность победы в матче команды {t1} низкая: {round(pred[0][1] * 100, 2)}%, возможна победа {t2}'
else:
    res = f'Вероятность победы в матче команды {t1} высокая: {round(pred[0][1] * 100, 2)}%. {t1} побеждает'
if lose_probability > 0.5:
    res = f'Вероятность победы в матче команды {t1} крайне низкая: {round(pred[0][1] * 100, 2)}%. {t2} побеждает'

print("Вероятности (команда 1): \n", f'{pred[0][0]} - шанс проигрыша \n {pred[0][1]} - шанс выигрыша')


