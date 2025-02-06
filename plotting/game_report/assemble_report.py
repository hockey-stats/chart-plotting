"""
Script that will call methods to generate plots for a post-game report visualization.
The report will consist of many plots assembed into a multi-plot, including:
 - A scatter plot showing each skaters on-ice xG results
 - A bar plot showing TOI for each skater
 - A (?) plot comparing each teams goals and xgoals
 - A scoring summary
 - A goaltending breakdown
 - and we'll see what else, it's a WIP
"""

import os
import argparse
import pandas as pd
from numpy import array

from plotting.base_plots.ratio_scatter import RatioScatterPlot
from plotting.base_plots.mirrored_bar import MirroredBarPlot
from plotting.base_plots.scoreboard import ScoreBoardPlot
from plotting.base_plots.multiplot import MultiPlot
from plotting.base_plots.pie import PiePlot
from util.helpers import total_toi_as_timestamp

# Disable an annoying warning
pd.options.mode.chained_assignment = None


def make_xg_ratio_plot(skater_df):
    """
    Function for creating scatter plot showing 5v5 on-ice xG ratios.
    :param DataFrame skater_df: DataFrame containing information for all skaters in the game.
    """
    # DataFrame contains info for all states, so filter to 5v5
    df = skater_df[skater_df['state'] == 'ev']

    xg_plot = RatioScatterPlot(dataframe=df,
                               filename='',
                               x_column='xGF', y_column='xGA',
                               title='Even-Strength On-Ice xGoals', scale='player',
                               x_label='Expected Goals For',
                               y_label='Expected Goals Against (inverted)',
                               ratio_lines=True, invert_y=True,
                               plot_x_mean=False,
                               plot_y_mean=False,
                               scale_to_extreme=False,
                               data_disclaimer=None)

    return xg_plot


def make_icetime_plot(skater_df):
    """
    Function for creating mirrored bar plot showing icetime for both teams.
    Requires creating two new dataframes, one for each team, with the columns showing:
        name | team | position | es_toi | pp_toi | pk_toi
    :param DataFrame skater_df: DataFrame containing information for all skaters in the game.
    """
    # Pivot skater_df to have one df showing icetime broken down by state
    icetime_df = pd.pivot_table(skater_df, values='icetime', index=['name', 'team'],
                                columns=['state'])
    icetime_df.reset_index(inplace=True)
    teams = list(set(icetime_df['team']))
    df_a = icetime_df[icetime_df['team'] == teams[0]]
    df_b = icetime_df[icetime_df['team'] == teams[1]]

    # Add column for total icetime, to have a value to sort the tables by
    for df in df_a, df_b:
        df['total_toi'] = df.apply(lambda row: row['ev'] + row['pp'] + row['pk'], axis=1)

    # Add columns for total goals and assists
    df_a_scoring = skater_df[(skater_df['team'] == teams[0]) & (skater_df['state'] == 'all')]\
                   [['name', 'goals', 'primary_assists', 'secondary_assists']]
    df_b_scoring = skater_df[(skater_df['team'] == teams[1]) & (skater_df['state'] == 'all')]\
                   [['name', 'goals', 'primary_assists', 'secondary_assists']]

    # Merge dataframe with scoring stats into icetime dataframe
    df_a = df_a.merge(df_a_scoring, on='name')\
            .rename(columns={'goals': 'g', 'primary_assists': 'a1', 'secondary_assists': 'a2'})
    df_b = df_b.merge(df_b_scoring, on='name')\
            .rename(columns={'goals': 'g', 'primary_assists': 'a1', 'secondary_assists': 'a2'})

    icetime_plot = MirroredBarPlot(dataframe_a=df_a,
                                   dataframe_b=df_b,
                                   x_column=['ev', 'pp', 'pk'],
                                   a_label=teams[0], b_label=teams[1],
                                   sort_value='total_toi',
                                   title='Icetime Breakdownsss by Team',
                                   filename='',
                                   data_disclaimer=None)

    return icetime_plot


def make_scoreboard_plot(df, g_df):
    """
    Draw scoreboard plot based on skater/goalie dataframes.
    """
    plot = ScoreBoardPlot(filename='', skater_df=df, goalie_df=g_df, data_disclaimer=None)
    return plot


def assemble_multiplot(icetime, xg_scatter, scoreboard):
    """
    Function which takes the various plots which constitute the game report and assembles them
    into a single multiplot.
    """


def main():
    """
    Main function that reads the CSV files into DataFrames and calls the appropriate plotting
    methods.
    """

    skater_df = pd.read_csv(os.path.join('data', '20844_skaters.csv'), encoding='utf-8-sig')
    goalie_df = pd.read_csv(os.path.join('data', '20844_goalies.csv'), encoding='utf-8-sig')
    xg_scatter_plot = make_xg_ratio_plot(skater_df)

    icetime_plot = make_icetime_plot(skater_df)

    scoreboard_plot = make_scoreboard_plot(skater_df, goalie_df)

    team_a, team_b = set(skater_df['team'])

    arrangement = {
        "dimensions": (13, 6),
        "plots": [
            {
                "plot": scoreboard_plot,
                "position": (0, 1),
                "colspan": 4,
                "rowspan": 6
            },
            {
                "plot": icetime_plot,
                "position": (6, 0),
                "colspan": 3,
                "rowspan": 6
            },
            {
                "plot": xg_scatter_plot,
                "position": (6, 3),
                "colspan": 3,
                "rowspan": 6
            }
        ]
    }

    game_report = MultiPlot(arrangement=arrangement,
                            figsize=(20, 14),
                            filename='game_report.png',
                            title=f'Game Report - {team_a} vs {team_b}',
                            data_disclaimer='nst')

    game_report.make_multiplot()


if __name__ == '__main__':
    main()
