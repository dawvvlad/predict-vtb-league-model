import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.metrics import accuracy_score

from predict_model import dataset, lr, predictors, t1, t2

# График важности признаков
importance = pd.Series(lr.coef_[0], index=predictors).sort_values(ascending=False)

plt.figure(figsize=(10, 8))
importance.plot(kind='bar')
plt.title('Важность признаков')
plt.xlabel('Признаки')
plt.ylabel('Значение коэффициента')
plt.show()

# Производительность модели по сезонам
season_accuracy = []

seasons = sorted(dataset['Сезон'].unique())
for season in seasons:
    train = dataset[dataset['Сезон'] < season]
    test = dataset[dataset['Сезон'] == season]

    # Проверяем, что у нас есть достаточно данных для обучения и тестирования
    if len(train) == 0 or len(test) == 0:
        print(f"Недостаточно данных для сезона {season}. Пропускаем этот сезон.")
        continue

    lr.fit(train[predictors], train['Цель'])
    predictions = lr.predict(test[predictors])
    accuracy = accuracy_score(test['Цель'], predictions)
    season_accuracy.append((season, accuracy))

season_accuracy_df = pd.DataFrame(season_accuracy, columns=['Сезон', 'Точность'])

plt.figure(figsize=(10, 6))
sns.lineplot(x='Сезон', y='Точность', data=season_accuracy_df)
plt.title('Точность модели по сезонам')
plt.xlabel('Сезон')
plt.ylabel('Точность')
plt.show()

# Сравнение производительности команд
team_1_data = dataset[dataset['Имя'] == t1].tail(10)
team_2_data = dataset[dataset['Имя'] == t2].tail(10)

team_1_avg = team_1_data[predictors].mean()
team_2_avg = team_2_data[predictors].mean()

comparison_df = pd.DataFrame({'Команда 1': team_1_avg, 'Команда 2': team_2_avg})
comparison_df.plot(kind='bar', figsize=(14, 8))
plt.title(f'Сравнение производительности за последние 10 игр: {t1} vs {t2}')
plt.xlabel('Признаки')
plt.ylabel('Среднее значение')
plt.show()
