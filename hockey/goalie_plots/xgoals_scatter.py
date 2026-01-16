"""
Module for plotting goalie GSAX against xG workload.
"""

import argparse
from datetime import datetime
import numpy as np
import pyhockey as ph
import polars as pl

from plot_types.ratio_scatter import RatioScatterPlot
from util.team_maps import team_full_names


def construct_plot(df: pl.DataFrame, team: str, output_filename: str, plot_title: str,
                   subtitle: str) -> None:

    df = df.with_columns(
        (pl.col('xGoals') - pl.col('goals')).alias('GSAX')
    )

    gsax_plot = RatioScatterPlot(
        dataframe=df,
        filename=output_filename,
        x_column='xGoals',
        y_column='GSAX',
        title=plot_title,
        subtitle=subtitle,
        scale='player',
        x_label='Total Expected Goals Faced',
        y_label='Goals Saved Above Expected',
        team=team,
        quadrant_labels=['WORKLOAD', 'RESULTS'],
        #scale_to_extreme=True,
        plot_y_mean=True
    )

    gsax_plot.make_plot()


def main(team: str, min_xg: int, situation: str, season: int) -> None:
    """
    Main function to create the plot and save as a png fike.

    Args:
        team (str): The team(s) which will have their goalies included.
        min_xg (int): The minimum xG goalies need to have faced to be included.
        situation (str): One of '5on5', '4on5', 5on4', 'other', or 'all'.
        season (int): The season for which to plot data.
    """
    df = ph.goalie_seasons(season=season, situation=situation, team=team)\
            [['name', 'team', 'xGoals', 'goals']]

    # If min_xg provided is -1 (i.e. default), calculate to be 30% of max value
    if min_xg == -1:
        min_xg = int(0.3 * df['xGoals'].max())

    # Apply minimum xG filter
    df = df.filter(pl.col('xGoals') >= min_xg)

    # Format the 'team' string to be used in the title of the plot
    if team == 'ALL':
        display_team = 'All'
    else:
        display_team = team_full_names[team]

    subtitle = f'minimum {min_xg} expected goals faced'
    if situation == 'all':
        subtitle += ', all situations'
    else:
        subtitle += f'{situation} minutes only'

    construct_plot(
        df,
        team,
        output_filename=f'{team}_goalie_gsax_scatter.png',
        plot_title=f'{display_team} Goalies Goals Saved Above Expected with Workload',
        subtitle=subtitle
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--team', type=str, default='ALL',
                        help='Team to get stats for, defaults to ALL.')
    parser.add_argument('-m', '--min_xg', type=int, default=-1,
                        help='Minimum xGoals faced by included goalies.')
    parser.add_argument('-si', '--situation', type=str, default='all', const='all', nargs='?',
                        choices=['5on5', '4on5', '5on4', 'other', 'all'],
                        help='Game state to measure points for. Defaults to 5on5.')
    parser.add_argument('-s', '--season', type=int,
                        default=datetime.now().year - 1 if datetime.now().month < 10 \
                                else datetime.now().year,
                        help='Season for which we pull data')
    args = parser.parse_args()

    main(team=args.team, min_xg=args.min_xg, situation=args.situation,
         season=args.season)
