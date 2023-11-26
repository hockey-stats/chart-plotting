import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

from plotting.plot import Plot, get_logo_marker


class RollingAveragePlot(Plot):
    """
    Sub-class of Plot to create rolling average line plots.
    """
    def __init__(self, dataframe, filename, x_column, y_column, title='', x_label='',
                 y_label='', y_midpoint=50, size=(10, 8), multiline_key=None,
                 add_team_logos=False):

        super().__init__(dataframe, filename, x_column, y_column, title, x_label, y_label,
                         size)

        self.fig = plt.figure(figsize=self.size)
        self.axis = self.fig.add_subplot(111)
        self.y_midpoint = y_midpoint
        self.multiline_key = multiline_key
        self.add_team_logos = add_team_logos

    def make_plot(self):
        """
        Generate the actual plot object.
        """
        # If multiline_key parameter is not empty, plot a line for every distinct
        # value in dataframe[multiline_key], e.g. one line for each team.
        if self.multiline_key:
            self.plot_multilines()
        else:
            self.axis.plot(self.df[self.x_col], self.df[self.y_col])

        if self.add_team_logos:
            self.handle_team_logos()

        plt.title(self.title)
        self.axis.set_xlabel(self.x_label)
        self.axis.set_ylabel(self.y_label)

        self.set_scaling()
        self.add_x_axis()

        self.save_plot()


    def handle_team_logos(self):
        """
        Add the team logo to the last point of each line.
        """
        for team in set(self.df['team']):
            x_last = list(self.df[self.df['team'] == team][self.x_col])[-1]
            y_last = list(self.df[self.df['team'] == team][self.y_col])[-1]

            artist_box = AnnotationBbox(get_logo_marker(team),
                                        xy=(x_last, y_last), frameon=False)
            self.axis.add_artist(artist_box)



    def plot_multilines(self):
        """
        Give a multiline_key, for each distinct value in the column corresponding to that key,
        add a single line plot for the dataframe filtered on that value.
        """
        keys = set(self.df[self.multiline_key])
        for key in keys:
            individual_df = self.df[self.df[self.multiline_key] == key]
            self.axis.plot(individual_df[self.x_col], individual_df[self.y_col])


    def add_x_axis(self):
        """
        Draws the x-axis at the y-midpoint.
        """
        self.axis.axhline(self.y_midpoint, color='black', label='50%')


    def set_scaling(self):
        """
        Sets x scaling to correspond to number of games in dataset (default behaviour), 
        and y-scaling to have the maximum and minimum be equal, based on the most 
        extreme y-value.
        """
        y_min = self.df[self.y_col].min()
        y_max = self.df[self.y_col].max()

        y_scale = max(abs(self.y_midpoint - y_max), abs(self.y_midpoint - y_min)) * 1.1

        self.axis.set_ylim(self.y_midpoint - y_scale, self.y_midpoint + y_scale)


if __name__ == '__main__':
    df = pd.read_csv('data/xGoalsPercentage_rolling_avg.csv')
    tor_df = df[df['team'].isin(['TOR', 'BOS', 'VAN'])]
    tor_df['xGoalsPercentageRollingAvg'] = tor_df.apply(lambda row: round(row['xGoalsPercentageRollingAvg'] * 100, 2), 1)

    plot = RollingAveragePlot(tor_df, 'x.png', 'gameNumber', 'xGoalsPercentageRollingAvg',
                              '10-game rolling xG% avg', x_label='Game #', y_label='10-game avg xg%',
                              multiline_key='team', add_team_logos=True)
    plot.make_plot()