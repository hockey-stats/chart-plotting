"""
Script used to plot things like xG%, Corsi%, and G% at the team-wide level on a 2D scatterplot.
"""

from datetime import datetime
import argparse

import pyhockey as ph

from plot_types.ratio_scatter import RatioScatterPlot


def make_plots(base_df):
    """
    Given DataFrame, create ratio scatter plots for 5on5 xG and G, and save as image files.
    """

    # Calculate league averages for plot
    league_avg_xg = base_df['xGoalsForPerHour'].mean()
    league_avg_g = base_df['goalsForPerHour'].mean()

    xg_plot = RatioScatterPlot(dataframe=base_df, filename='xg_ratios.png',
                               x_column='xGoalsForPerHour', y_column='xGoalsAgainstPerHour',
                               title='Team Expected Goal Rates',
                               subtitle='    5v5, flurry-, score-, and venue-adjusted',
                               scale='team',
                               x_label='Expected Goals For per hour',
    						   y_label='Expected Goals Against per hour (inverted)',
                               ratio_lines=True, invert_y=True,
                               plot_x_mean=False, plot_y_mean=False,
                               scale_to_extreme=True, plot_league_average=league_avg_xg)
    xg_plot.make_plot()

    # Plot Team Goal ratios
    g_plot = RatioScatterPlot(dataframe=base_df, filename='g_ratios.png',
                              x_column='goalsForPerHour', y_column='goalsAgainstPerHour',
                              title='Team Goal Rates (5v5)', scale='team',
                              x_label='Goals For per hour',
                              y_label='Goals Against per hour (inverted)',
                              ratio_lines=True, invert_y=True,
                              plot_x_mean=False, plot_y_mean=False,
                              scale_to_extreme=True, plot_league_average=league_avg_g)
    g_plot.make_plot()


def main(situation, season):
    """
    Main function which disambiguates and calls appropriate plotting function based on provided
    situation.
    """
    base_df = ph.team_summary(season=season, situation=situation)

    make_plots(base_df)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-si', '--situation', default='5on5',
                        help='Given game state for which to process table.')
    parser.add_argument('-s', '--season', type=int,
                        default=datetime.now().year - 1 if datetime.now().month < 10 \
                                else datetime.now().year,
                        help='Season for which we pull data')

    args = parser.parse_args()

    main(situation=args.situation, season=args.season)
