"""
Script used to plot things like xG%, Corsi%, and G% at the team-wide level on a 2D scatterplot.
"""

import os
import argparse
import pandas as pd

from plotting.base_plots.ratio_scatter import RatioScatterPlot


def make_5on5_plots(base_df):
    """
    Given DataFrame, create ratio scatter plots for 5on5 xG and G, and save as image files.
    """

    # Calculate league averages for plot
    league_avg_xg = base_df['xGFph'].mean()
    league_avg_g = base_df['GFph'].mean()

    xg_plot = RatioScatterPlot(dataframe=base_df, filename='xg_ratios.png',
                               x_column='xGFph', y_column='xGAph',
                               title='Team Expected Goal Rates',
                               subtitle='    5v5, flurry-, score-, and venue-adjusted',
                               scale='team',
                               x_label='Expected Goals For per hour',
    						   y_label='Expected Goals Against per hour (inverted)',
                               ratio_lines=True, invert_y=True, plot_x_mean=True, plot_y_mean=True,
                               scale_to_extreme=True, plot_league_average=league_avg_xg)
    xg_plot.make_plot()

    # Plot Team Goal ratios
    g_plot = RatioScatterPlot(dataframe=base_df, filename='g_ratios.png',
                              x_column='GFph', y_column='GAph',
                              title='Team Goal Rates (5v5)', scale='team',
                              x_label='Goals For per hour',
                              y_label='Goals Against per hour (inverted)',
                              ratio_lines=True, invert_y=True, plot_x_mean=True, plot_y_mean=True,
                              scale_to_extreme=True, plot_league_average=league_avg_g)
    g_plot.make_plot()


def main(situation):
    """
    Main function which disambiguates and calls appropriate plotting function based on provided
    situation.
    """
    base_df = pd.read_csv(os.path.join('data', 'team_ratios.csv'))

    if situation == '5on5':
        make_5on5_plots(base_df)

    else:
        raise NotImplementedError('Unsupported situation provided. Options are "5on5", "5on4",'\
                                  'or 4on5')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--situation', default='5on5',
                        help='Given game state for which to process table.')
    args = parser.parse_args()

    main(situation=args.situation)
