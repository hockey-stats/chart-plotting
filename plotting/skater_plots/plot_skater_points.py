"""
Module for plotting points against ice-time for skaters.
"""

import os
import argparse
import pandas as pd

from plotting.plot import RatioScatterPlot

##############################################
########## TODO: This ain't done #############
##############################################

def main(team, min_icetime_minutes):
    """
    Main function to create the plot and save as a png file.
    """

    df = pd.read_csv(os.path.join('data', 'skater_individual_stats.csv'),
                          usecols=['season', 'name', 'team', 'position', 'situation',
                                   'games_played', 'icetime', 'I_F_points'])

    # Apply minimum icetime, which is given in seconds, as well as
    # non-5on5 scoring
    df.drop(df[(df.icetime >= (min_icetime_minutes * 60)) & \
               (df.situation != '5on5')])

    df.rename(column={'I_F_points': 'points'})


    df['pointsPerHour'] = df.apply(lambda row:
                                   row['points'] / (row['icetime'] * 60 * 60))


    ##############################################
    ########## TODO: Stopped around here #########
    ##############################################

    # Calculate league averages for plot
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
    args = parser.parse_args()

    main(team=args.team, min_icetime_minutes=args.min_icetime)
