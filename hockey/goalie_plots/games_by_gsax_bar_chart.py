"""
Module for generate sequential bar chart showing goalie GSaX on a game-by-game basis for a team.
"""

import argparse
from datetime import datetime
import polars as pl
import pyhockey as ph

from plot_types.sequential_bar import SequentialBarPlot
from util.team_maps import team_full_names


def main(team: str, season: int) -> None:
    """ Calls plotting methods on goalie data from pyhockey.

    Args:
        team (str): Team to generate plot for
        season (int): Season for which to gather data
    """

    df = ph.goalie_games(season=season, team=team, situation='all').with_row_index()

    df = df.sort(by=pl.col('gameDate'))

    # Add columns for GSaX and game #
    df = df.with_columns(
        (pl.col('xGoalsAgainst') - pl.col('goalsAgainst')).alias('goalsSavedAboveExpected'),
        (pl.col('index') + 1).alias('gameNumber')
    )

    # Save only the columns used in the plot
    df = df[['name', 'gameNumber', 'goalsSavedAboveExpected']]

    team_name = team_full_names[team]

    gsax_plot = SequentialBarPlot(df=df,
                                  filename=f'{team}_gsax.png',
                                  x_column='gameNumber',
                                  y_column='goalsSavedAboveExpected',
                                  selector_column='name',
                                  team=team,
                                  y_max=6,
                                  x_label='Game #',
                                  y_label='Goals Saved Above Expected',
                                  title=f'Game-by-Game Goals Saved Above Expected\n for '\
                                        f'{team_name} Goalies',
                                  data_disclaimer='nst')

    gsax_plot.make_plot()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--team', type=str, required=True,
                        help='Team to create plot for')
    parser.add_argument('-s', '--season', type=int,
                        default=datetime.now().year - 1 if datetime.now().month < 10 \
                                else datetime.now().year,
                        help='Season for which we pull data')
    args = parser.parse_args()

    main(team=args.team, season=args.season)
