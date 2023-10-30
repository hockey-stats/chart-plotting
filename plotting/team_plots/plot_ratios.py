import pandas as pd

from plotting.plot import RatioScatterPlot


"""
Script used to plot things like xG%, Corsi%, and G% at the team-wide level on a 2D scatterplot.
"""

def main():
    base_df = pd.read_csv('data/team_ratios.csv')
    # Plot Team xG ratios
    xg_plot = RatioScatterPlot(dataframe=base_df, filename='xg_ratios.png', x_column='xGFph', y_column='xGAph', 
                       title='Team xG Rates', 
                       x_label='Expected Goals For per hour (5v5)', y_label='Expected Goals Against per hour (inverted)',
                       ratio_lines=True, invert_y=True, plot_x_mean=True, plot_y_mean=True, 
                       quadrant_labels=(('DULL', 'GOOD'), ('BAD', 'FUN')))
    xg_plot.make_plot()

    # Plot Team Goal ratios
    g_plot = RatioScatterPlot(dataframe=base_df, filename='g_ratios.png', x_column='GFph', y_column='GAph', 
                      title='Team Goal Rates (5v5)',
                      x_label='Goals For per hour', y_label='Goals Against per hour (inverted)',
                      ratio_lines=True, invert_y=True, plot_x_mean=True, plot_y_mean=True, 
                      quadrant_labels=(('DULL', 'GOOD'), ('BAD', 'FUN')))
    g_plot.make_plot()


if __name__ == '__main__':
    main()
