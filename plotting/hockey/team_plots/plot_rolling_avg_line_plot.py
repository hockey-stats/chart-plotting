import argparse
from datetime import datetime

import duckdb
import polars as pl

from plotting.base_plots.animated_rolling_average import AnimatedRollingAveragePlot


def get_xg_data(season: int, window: int, num_games: int) -> pl.DataFrame:
    """
    For a given season, query the relevant team data from the team_games
    table and calculate the rolling xG%, returning the results in a 
    polars DataFrame.

    :param int season: Season for which to query data
    :param int window: Window size for computing rolling average
    :param int num_games: Number of games to include in dataset (i.e. last 'n' games)
    :return pl.DataFrame: Results of the query + rolling data
    """

    conn = duckdb.connect(database='hockey-stats.db', read_only=True)

    query = f"""
        SELECT
            team,
            gameId,
            xGoalsPercentage
        FROM team_games
        WHERE
            season={season} AND
            situation='5on5';
    """

    df = conn.execute(query).pl()

    output_dfs = []

    for team in set(df['team']):
        team_df = df.filter(pl.col('team') == team).sort(by='gameId')
        team_df = team_df.with_columns(
            gameNumber=pl.col('gameId').rank('ordinal', descending=False),
            xGoalsRollingAvg=pl.col('xGoalsPercentage').rolling_mean(window_size=window) * 100
        ).drop_nulls()

        if num_games > 0:
            team_df = team_df.tail(num_games)

        output_dfs.append(team_df)

    final_df = pl.concat(output_dfs)

    return final_df


def xg_by_division_multiplot(season: int, div: int, window: int, num_games: int):
    """
    Plot each teams rolling 10-game average, in a 2x2 plot where each plot shows
    all the teams in one division.
    """

    divisions = {
    0: {'teams': {'TOR', 'TBL', 'BOS', 'DET', 'MTL', 'OTT', 'FLA', 'BUF'},
        'name': 'Atlantic'},
    1: {'teams': {'NYR', 'NYI', 'NJD', 'CAR', 'CBJ', 'PIT', 'WSH', 'PHI'},
        'name': 'Metropolitan'},
    2: {'teams': {'VAN', 'CGY', 'EDM', 'ANA', 'VGK', 'SJS', 'LAK', 'SEA'},
        'name': 'Pacific'},
    3: {'teams': {'COL', 'DAL', 'WPG', 'STL', 'ARI', 'MIN', 'CHI', 'NSH'},
        'name': 'Central'}
    }

    df = get_xg_data(season, window, num_games)

    df = df.filter(pl.col('team').is_in(divisions[div]['teams']))

    plot_title = f'{divisions[div]['name']} Division xG% Rolling Averages'
    subtitle = f"Over the last {num_games} games"

    plot = AnimatedRollingAveragePlot(dataframe=df,
                                      filename="xg_rolling_avg.mp4",
                                      x_column='gameNumber',
                                      x_label='Game #',
                                      y_column='xGoalsRollingAvg',
                                      y_label=f'{window}-Game Rolling Average',
                                      title=plot_title,
                                      sport='hockey',
                                      y_midpoint=50,
                                      add_team_logos=True,
                                      for_multiplot=False,
                                      multiline_key='team',
                                      subtitle=subtitle)

    plot.make_plot_gif()


def main(plot_type: str, season: int, div, window: int, num_games: int):
    """
    Main function which disambiguates the stat to be plotted, calls the plotting methods
    and saves the output.
    """
    if plot_type == 'xg_by_division':
        xg_by_division_multiplot(season, div, window, num_games)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--plot_type', default='xg_by_division',
                        const='xg_by_division',
                        nargs='?',
                        choices=['xg_by_division'])
    parser.add_argument('-s', '--season', type=int,
                        default=datetime.now().year - 1 if datetime.now().month < 10 \
                                else datetime.now().year)
    parser.add_argument('-d', '--div', type=int, required=True,
                        help="Integer corresponding to division for which to generate plot. \n"\
                             "0 - Atlantic\n1 - Metropolitan\n2 - Pacific\n3 - Central")
    parser.add_argument('-w', '--window', default=10, type=int,
                        help='Size of window to calculate rolling averages, defaults to 10')
    parser.add_argument('-n', '--num_games', default=0, type=int,
                        help='`n` for last n games for which to include in plot, e.g. n=25 would '\
                             'mean only include the last 25 games in the output.')
    args = parser.parse_args()

    main(args.plot_type, args.season, args.div, window=args.window, num_games=args.num_games)
