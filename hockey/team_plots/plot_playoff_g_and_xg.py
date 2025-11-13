"""
Script used to plot things like xG%, Corsi%, and G% at the team-wide level on a 2D scatterplot.
"""

import os
import pandas as pd

from plot_types.ratio_scatter import RatioScatterPlot
from plot_types.multiplot import MultiPlot


def make_plots(base_df):
    """
    Given DataFrame, create ratio scatter plots for 5on5 xG and G, and save as image files.
    """

    # Calculate league averages for plot
    league_avg_xg = base_df['xGoalsForPerHour'].mean()
    league_avg_g = base_df['goalsForPerHour'].mean()

    xg_plot = RatioScatterPlot(dataframe=base_df, filename='xg_ratios.png',
                               x_column='xGoalsForPerHour', y_column='xGoalsAgainstPerHour',
                               title='\n\nExpected Goal Rates (5v5)',
                               scale='team',
                               x_label='Expected Goals For per hour',
    						   y_label='Expected Goals Against per hour (inverted)',
                               ratio_lines=True, invert_y=True,
                               plot_x_mean=False, plot_y_mean=False,
                               fade_non_playoffs=True,
                               scale_to_extreme=True, plot_league_average=league_avg_xg)

    g_plot = RatioScatterPlot(dataframe=base_df, filename='g_ratios.png',
                              x_column='goalsForPerHour', y_column='goalsAgainstPerHour',
                              title='\n\nActual Goal Rates (5v5)', scale='team',
                              x_label='Goals For per hour',
                              y_label='Goals Against per hour (inverted)\n\n',
                              ratio_lines=True, invert_y=True,
                              plot_x_mean=False, plot_y_mean=False,
                               fade_non_playoffs=True,
                              scale_to_extreme=True, plot_league_average=league_avg_g)
    
    return xg_plot, g_plot


def assemble_multiplot(xg_plot, g_plot):
    """
    Given plots for expected and actual goals, assemble them in a 2x1 multiplot object and
    save.

    :param Plot xg_plot: Scatter plot for expected goals.
    :param Plot g_plot: Scatter plot for actual goals.
    """

    arrangement = {
        "dimensions": (1, 2),
        "plots": [
            {
                "plot": xg_plot,
                "y_pos": 0,
                "start": 0,
                "end": 1
            },
            {
                "plot": g_plot,
                "y_pos": 0,
                "start": 1,
                "end": 2
            },
        ],
        "wspace": 0.1,
        "hspace": 0.05
    }

    multiplot = MultiPlot(arrangement=arrangement, filename="playoff_xg_and_g",
                          figsize=(24, 12),
                          title="Playoff Team 5v5 Expected and Actual Goal Rates")

    multiplot.make_multiplot()


def main():
    """
    Main function which disambiguates and calls appropriate plotting function based on provided
    situation.
    """
    base_df = pd.read_csv(os.path.join('data', 'team_ratios.csv'))

    xg_plot, g_plot = make_plots(base_df)

    assemble_multiplot(xg_plot, g_plot)


if __name__ == '__main__':
    main()
