"""
Script used to plot on-ice ratios for individual players.
"""

import os
import argparse
import pandas as pd

from plotting.base_plots.ratio_scatter import RatioScatterPlot
from util.team_maps import team_full_names

def main(team, min_icetime):
    """
    Main function to create the plot and save as a png file.
    """

    base_df = pd.read_csv(os.path.join('data', 'player_ratios.csv'))

    # Apply minimum icetime
    base_df = base_df[base_df['icetime'] >= (min_icetime * 60)]

    # Calculate league averages for plot
    league_avg_xg = base_df['xGFph'].mean()
    league_avg_g = base_df['GFph'].mean()

    if team != "ALL":
        base_df = base_df[base_df['team'] == team]

    # Format the 'team' string to be used in the title of the plot
    if team == 'ALL':
        display_team = 'All'
    else:
        display_team = team_full_names[team]

    print(team)

    xg_plot = RatioScatterPlot(dataframe=base_df,
                               filename=f'{team}_skater_xg_ratios.png',
                               x_column='xGFph', y_column='xGAph',
                               title=f'{display_team} Expected Goal Rates',
                               subtitle=f'5v5, flurry-,score- and venue-adjusted\n'\
                                        f'min. {min_icetime} minutes',
                               scale='player', x_label='Expected Goals For per hour',
                               y_label='Expected Goals Against per hour (inverted)',
                               ratio_lines=True,
                               invert_y=True,
                               plot_x_mean=False,
                               plot_y_mean=False,
                               scale_to_extreme=True,
                               plot_league_average=league_avg_xg)
    xg_plot.make_plot()

    g_plot = RatioScatterPlot(dataframe=base_df,
                              filename=f'{team}_skater_g_ratios.png',
                              x_column='GFph',
                              y_column='GAph',
                              title=f'{team} Player G Rates(5v5)\nmin. {min_icetime} minutes',
                              scale='player',
                              x_label='Goals For per hour',
                              y_label='Goals Against per hour (inverted)',
                              ratio_lines=True,
                              invert_y=True,
                              plot_x_mean=False,
                              plot_y_mean=False,
                              scale_to_extreme=True,
                              plot_league_average=league_avg_g)
    g_plot.make_plot()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--team', type=str, default='ALL',
                        help='Team to get stats for, defaults to ALL.')
    parser.add_argument('-i', '--min_icetime', type=int, default=0,
                        help='Minimum icetime, in minutes cuttoff for players (defaults to 0')
    args = parser.parse_args()

    main(team=args.team, min_icetime=args.min_icetime)
