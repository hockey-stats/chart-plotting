"""
Script used to plot things like xG%, Corsi%, and G% at the team-wide level on a 2D scatterplot.
"""

import argparse
import duckdb

from plotting.base_plots.ratio_scatter import RatioScatterPlot


def make_plots(base_df):
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
                               ratio_lines=True, invert_y=True,
                               plot_x_mean=False, plot_y_mean=False,
                               scale_to_extreme=True, plot_league_average=league_avg_xg)
    xg_plot.make_plot()

    # Plot Team Goal ratios
    g_plot = RatioScatterPlot(dataframe=base_df, filename='g_ratios.png',
                              x_column='GFph', y_column='GAph',
                              title='Team Goal Rates (5v5)', scale='team',
                              x_label='Goals For per hour',
                              y_label='Goals Against per hour (inverted)',
                              ratio_lines=True, invert_y=True,
                              plot_x_mean=False, plot_y_mean=False,
                              scale_to_extreme=True, plot_league_average=league_avg_g)
    g_plot.make_plot()


def main(situation):
    """
    Main function which disambiguates and calls appropriate plotting function based on provided
    situation.
    """
    conn = duckdb.connect('hockey-stats.db', read_only=True)

    query = f"""
        SELECT
            team,
            xGFph,
            xGAph,
            GFph,
            GAph
        FROM teams
        WHERE situation='{situation}';
    """

    base_df = conn.execute(query).pl()

    make_plots(base_df)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--situation', default='5on5',
                        help='Given game state for which to process table.')
    args = parser.parse_args()

    main(situation=args.situation)
