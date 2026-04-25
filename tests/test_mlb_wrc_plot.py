from tqdm import tqdm

from util.get_detailed_batter_stats import get_detailed_batter_stats
from baseball.player_plots.plot_wrc_distribution import main


if __name__ == '__main__':
    teams = list(get_detailed_batter_stats(2026)['Team'])
    teams = set(teams)

    for team in tqdm(teams):
        main(year=2026, qual=20, team=team)

