"""
Module for plotting points against ice-time for skaters.
"""

import os
import argparse
import numpy as np
import pandas as pd

from plotting.base_plots.ratio_scatter import RatioScatterPlot


def construct_plot(df, team, output_filename, plot_title, subtitle):
    """
    Given the dataframe, create the skater points ratio plot with the given
    output filename.
    """

    # Calculate the percentiles for points per hour
    pph_percentiles = []
    for percentile in [25, 50, 75]:
        pph_percentiles.append(np.percentile(df['pointsPerHour'], percentile))

    max_pph = max(df['pointsPerHour']) + 0.2

    #if team != "ALL":
    #    df = df[df['team'] == team]

    pph_plot = RatioScatterPlot(dataframe=df,
                                filename=output_filename,
                                x_column='avgTOI',
                                y_column='pointsPerHour',
                                title=plot_title,
                                subtitle=subtitle,
                                scale='player',
                                x_label='Average Time on Ice per Game',
                                y_label='Points per Hour',
                                team=team,
                                show_league_context=True,
                                percentiles={'horizontal': pph_percentiles},
                                quadrant_labels=['OPPORTUNITY', 'PRODUCTION'],
                                plot_x_mean=False,
                                plot_y_mean=False,
                                y_min_max=(0, max_pph))
    pph_plot.make_plot()


def main(team, min_icetime_minutes, situation):
    """
    Main function to create the plot and save as a png file.
    """

    df = pd.read_csv(os.path.join('data', 'skater_individual_stats.csv'),
                          usecols=['season', 'name', 'team', 'position', 'situation',
                                   'games_played', 'icetime', 'I_F_points'])

    df = df[(df['icetime'] >= (min_icetime_minutes * 60)) & \
            (df['situation'] == situation)]

    # Generate columns for points per hour and average TOI
    df['pointsPerHour'] = df.apply(lambda row:
                                   round(row['I_F_points'] / (row['icetime'] / 3600), 3),
                                   axis=1)
    df['avgTOI'] = df.apply(lambda row:
                            round(row['icetime'] / (row['games_played'] * 60), 3),
                            axis=1)

    # Create separate DataFrames for forwards and defensemen
    df_f = df[df['position'].isin({'C', 'R', 'L'})]
    df_d = df[df['position'] == 'D']
    del df

    construct_plot(df_f, team,
                   output_filename=f'{team}_F_{situation}_scoring_rates.png',
                   plot_title=f'{team} Forward Scoring Rates ({situation.replace("on", "v")})',
                   subtitle=f'min. {min_icetime_minutes} minutes')

    construct_plot(df_d, team,
                   output_filename=f'{team}_D_{situation}_scoring_rates.png',
                   plot_title=f'{team} Defenseman Scoring Rates ({situation.replace("on", "v")})',
                   subtitle=f'min. {min_icetime_minutes} minutes)')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--team', type=str, default='ALL',
                        help='Team to get stats for, defaults to ALL.')
    parser.add_argument('-i', '--min_icetime', type=int, default=0,
                        help='Minimum icetime, in minutes cuttoff for players (defaults to 0')
    parser.add_argument('-s', '--situation', type=str, default='5on5', const='5on5', nargs='?',
                        choices=['5on5', '4on5', '5on4', 'other'],
                        help='Game state to measure points for. Defaults to 5on5.')
    args = parser.parse_args()

    main(team=args.team, min_icetime_minutes=args.min_icetime, situation=args.situation)
