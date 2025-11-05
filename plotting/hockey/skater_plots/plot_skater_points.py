"""
Module for plotting points against ice-time for skaters.
"""

import argparse
from datetime import datetime
import numpy as np
import pyhockey as ph
import polars as pl

from plotting.base_plots.ratio_scatter import RatioScatterPlot
from util.team_maps import team_full_names


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

    pph_plot = RatioScatterPlot(dataframe=df,
                                filename=output_filename,
                                x_column='averageIceTime',
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


def main(team, min_icetime_minutes, situation, season):
    """
    Main function to create the plot and save as a png file.
    """
    df = ph.skater_summary(season=season, situation=situation, min_icetime=min_icetime_minutes)
    df = df[['season', 'name', 'team', 'position', 'iceTime', 'averageIceTime', 'pointsPerHour']]

    # Create separate DataFrames for forwards and defensemen
    df_f = df.filter(pl.col('position').is_in({'C', 'R', 'L'})) 
    df_d = df.filter(pl.col('position') == 'D')
    del df

    # Format the 'team' string to be used in the title of the plot
    if team == 'ALL':
        display_team = 'All'
    else:
        display_team = team_full_names[team]

    construct_plot(df_f, team,
                   output_filename=f'{team}_F_{situation}_scoring_rates.png',
                   plot_title=f'{display_team} Forward Scoring Rates ({situation.replace("on", "v")})',
                   subtitle=f'min. {min_icetime_minutes} minutes')

    construct_plot(df_d, team,
                   output_filename=f'{team}_D_{situation}_scoring_rates.png',
                   plot_title=f'{display_team} Defenseman Scoring Rates ({situation.replace("on", "v")})',
                   subtitle=f'min. {min_icetime_minutes} minutes)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--team', type=str, default='ALL',
                        help='Team to get stats for, defaults to ALL.')
    parser.add_argument('-i', '--min_icetime', type=int, default=0,
                        help='Minimum icetime, in minutes cuttoff for players (defaults to 0')
    parser.add_argument('-si', '--situation', type=str, default='5on5', const='5on5', nargs='?',
                        choices=['5on5', '4on5', '5on4', 'other', 'all'],
                        help='Game state to measure points for. Defaults to 5on5.')
    parser.add_argument('-s', '--season', type=int,
                        default=datetime.now().year - 1 if datetime.now().month < 10 \
                                else datetime.now().year,
                        help='Season for which we pull data')
    args = parser.parse_args()

    main(team=args.team, min_icetime_minutes=args.min_icetime, situation=args.situation,
         season=args.season)
