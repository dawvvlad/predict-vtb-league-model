import pandas as pd
from funcs.funcs import get_game_stats


def read_data_from_urls():
    with open("../data/urls/all_matches_urls.txt", "r") as f:
        urls = f.read().splitlines()
        csv_games = "../data/csv/games_data_2.csv"
        dicts = []
        for url in urls:
            data = get_game_stats(url)
            if data is not None:
                dicts.append(data)

        df = pd.DataFrame(dicts)
        df.to_csv(csv_games, index=False)


read_data_from_urls()
