"""
Module for plotting points against ice-time for skaters.
"""

import os
import argparse
import numpy as np
import pandas as pd

from plotting.plot import RatioScatterPlot

##############################################
########## TODO: This ain't done #############
##############################################


def construct_plot(df, team, min_icetime_minutes, output_filename):
    """
    Given the dataframe, create the skater points ratio plot with the given
    output filename.
    """

    # Calculate the percentiles for points per hour
    pph_percentiles = []
    for percentile in [25, 50, 75]:
        pph_percentiles.append(np.percentile(df['pointsPerHour'], percentile))

    if team != "ALL":
        df = df[df['team'] == team]

    #TODO: Got to about here, working on percentile method for RatioScatterPlot
    xg_plot = RatioScatterPlot(dataframe=df,
                               filename=f'{team}_skater_xg_ratios.png',
                               x_column='xGFph', y_column='xGAph',
                               title=f'{team} Player xG Rates (5v5, minimum {min_icetime_minutes} minutes)',
                               scale='player', x_label='Expected Goals For per hour',
                               y_label='Expected Goals Against per hour (inverted)',
                               ratio_lines=True,
                               invert_y=True,
                               plot_x_mean=False,
                               plot_y_mean=False,
                               plot_league_average=league_avg_xg)
    xg_plot.make_plot()


def main(team, min_icetime_minutes, situation):
    """
    Main function to create the plot and save as a png file.
    """

    df = pd.read_csv(os.path.join('data', 'skater_individual_stats.csv'),
                          usecols=['season', 'name', 'team', 'position', 'situation',
                                   'games_played', 'icetime', 'I_F_points'])

    df = df[(df['icetime'] >= (min_icetime_minutes * 60)) & \
            (df['situation'] == situation)]

    df['pointsPerHour'] = df.apply(lambda row:
                                   row['I_F_points'] / (row['icetime'] * 60 * 60), axis=1)

    # Create separate DataFrames for forwards and defensemen
    df_f = df[df['position'].isin({'C', 'R', 'L'})]
    df_d = df[df['position'] == 'D']
    del df

    # Calculate league averages for plot
    avg_pph_f = df_f['pointsPerHour'].mean()
    league_avg_xg = df['xGFph'].mean()
    league_avg_g = df['GFph'].mean()

    if team != "ALL":
        df = df[df['team'] == team]

    xg_plot = RatioScatterPlot(dataframe=df,
                               ilename=f'{team}_skater_xg_ratios.png',
                               x_column='xGFph', y_column='xGAph',
                               title=f'{team} Player xG Rates (5v5, minimum {min_icetime_minutes} minutes)',
                               scale='player', x_label='Expected Goals For per hour',
                               y_label='Expected Goals Against per hour (inverted)',
                               ratio_lines=True,
                               invert_y=True,
                               plot_x_mean=False,
                               plot_y_mean=False,
                               plot_league_average=league_avg_xg)
    xg_plot.make_plot()

    g_plot = RatioScatterPlot(dataframe=df,
                              filename=f'{team}_skater_g_ratios.png',
                              x_column='GFph',
                              y_column='GAph',
                              title=f'{team} Player G Rates (5v5, minimum {min_icetime_minutes} minutes)',
                              scale='player',
                              x_label='Goals For per hour',
                              y_label='Goals Against per hour (inverted)',
                              ratio_lines=True,
                              invert_y=True,
                              plot_x_mean=False,
                              plot_y_mean=False,
                              plot_league_average=league_avg_g)
    g_plot.make_plot()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--team', type=str, default='ALL',
                        help='Team to get stats for, defaults to ALL.')
    parser.add_argument('-i', '--min_icetime', type=int, default=0,
                        help='Minimum icetime, in minutes cuttoff for players (defaults to 0')
    parser.add_argument('-s', '--situation', type=str, default='5on5', const='5on5', nargs='?',
                        choices=['5on5', '4on5', '5on4', 'other'],
                        help='Game state to measure points for.')  #TODO: Add support for 'ALL'
    args = parser.parse_args()

    main(team=args.team, min_icetime_minutes=args.min_icetime, situation=args.situation)
