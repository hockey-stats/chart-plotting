"""
Script used to plot on-ice ratios for individual players.
"""

import argparse
from datetime import datetime
import pyhockey as ph

from plot_types.ratio_scatter import RatioScatterPlot
from util.team_maps import team_full_names

def main(team, min_icetime, season):
    """
    Main function to create the plot and save as a png file.
    """

    base_df = ph.skater_seasons(season=season, situation='5on5', min_icetime=min_icetime)

    # Calculate league averages for plot
    league_avg_xg = base_df['xGoalsForPerHour'].mean()
    league_avg_g = base_df['goalsForPerHour'].mean()

    # Format the 'team' string to be used in the title of the plot
    if team == 'ALL':
        display_team = 'All'
    else:
        display_team = team_full_names[team]

    xg_plot = RatioScatterPlot(dataframe=base_df,
                               filename=f'{team}_skater_xg_ratios.png',
                               x_column='xGoalsForPerHour', y_column='xGoalsAgainstPerHour',
                               title=f'{display_team} Expected Goal Rates',
                               subtitle=f'5v5, flurry-,score- and venue-adjusted\n'\
                                        f'min. {min_icetime} minutes',
                               scale='player', x_label='Expected Goals For per hour',
                               y_label='Expected Goals Against per hour (inverted)',
                               team=team,
                               ratio_lines=True,
                               invert_y=True,
                               plot_x_mean=False,
                               plot_y_mean=False,
                               scale_to_extreme=True,
                               plot_league_average=league_avg_xg)
    xg_plot.make_plot()

    g_plot = RatioScatterPlot(dataframe=base_df,
                              filename=f'{team}_skater_g_ratios.png',
                              x_column='goalsForPerHour',
                              y_column='goalsAgainstPerHour',
                              title=f'{team} Player G Rates(5v5)\nmin. {min_icetime} minutes',
                              scale='player',
                              x_label='Goals For per hour',
                              y_label='Goals Against per hour (inverted)',
                              team=team,
                              show_league_context=True,
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
    parser.add_argument('-s', '--season', type=int,
                        default=datetime.now().year - 1 if datetime.now().month < 10 \
                                else datetime.now().year,
                        help='Season for which we pull data')
    args = parser.parse_args()

    main(team=args.team, min_icetime=args.min_icetime, season=args.season)
