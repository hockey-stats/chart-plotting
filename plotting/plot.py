import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

from util.team_maps import nst_team_mapping


def get_logo_marker(team_name):
    """ Quick function to return the team logo as a matplotlib marker object. """
    return OffsetImage(plt.imread(f'team_logos/{team_name}.png'), alpha=0.8)


class Plot:
    """
    Base class to be used for all plots. Will only ever be called via super() for a base class
    """
    def __init__(self, dataframe, filename, x_column, y_column, title='', x_label='', y_label='', ratio_lines=False, 
                 invert_y=False, plot_x_mean=False, plot_y_mean=False, quadrant_labels=None, size=(10, 8)):
        self.df = dataframe
        self.filename = filename
        self.x_col = x_column
        self.y_col = y_column
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.ratio_lines = ratio_lines
        self.invert_y = invert_y
        self.plot_x_mean = plot_x_mean
        self.plot_y_mean = plot_y_mean
        self.quadrant_labels = quadrant_labels
        self.size = size


class TeamPlot(Plot):
    """
    Class for plotting values for each team in the league against each other.
    """
    def __init__(self, dataframe, filename, x_column, y_column, title='', x_label='', y_label='', ratio_lines=False, 
                 invert_y=False, plot_x_mean=False, plot_y_mean=False, quadrant_labels=None, size=(10,8), 
                 break_even_line=True):
        super().__init__(dataframe, filename, x_column, y_column, title, x_label, y_label, ratio_lines, invert_y,
                         plot_x_mean, plot_y_mean, quadrant_labels)
        self.break_even_line = break_even_line

    def make_plot(self):
        fig = plt.figure(figsize=self.size)
        ax = fig.add_subplot(111)

        # First plot the actual values for each team
        ax.scatter(x=self.df[self.x_col], y=self.df[self.y_col], s=0)

        plt.title(self.title)
        ax.set_xlabel(self.x_label)
        ax.set_ylabel(self.y_label)
        x_min = self.df[self.x_col].min() - 0.1
        x_max = self.df[self.x_col].max() + 0.1
        y_min = self.df[self.y_col].min() - 0.1
        y_max = self.df[self.y_col].max() + 0.1
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

        # Replace each blank marker with the team logos
        for team in list(self.df['team']):
            team_df = self.df[self.df['team'] == team]
            ab = AnnotationBbox(get_logo_marker(team), (team_df[self.x_col], team_df[self.y_col]), frameon=False)
            ax.add_artist(ab)

        if self.break_even_line:
            # Plot the line to display break-even
            ax.axline((2, 2), slope=1, color='r')

        if self.ratio_lines:
            # Plot diagonal lines to show each percentage breakpoint
            for x in np.arange(0.3, 0.8, 0.01):
                if round(x ,3) == 0.50:
                    continue
                p1 = (2, 2 * ((1 - x) / x))
                p2 = (2.5, 2.5 * ((1 - x) / x))
                color = '0.95'
                if round(x * 100, 0) % 5 == 0:
                    color = '0.8'
                    text_xy = (y_max * (x / (1 - x)), y_max - 0.02)
                    if text_xy[0] > x_max or text_xy[0] < x_min:
                        text_xy = (x_max - 0.1, x_max * ((1 - x) / x))
                    ax.annotate(f'{str(round(x, 3) * 100)[:2]}%', xy=text_xy, color=color)
                ax.axline(p1, p2, color=color)

        # Calculate and plot the average for each value
        if self.plot_x_mean:
            avg_x = self.df[self.x_col].mean()
            ax.axvline(avg_x, color='k', label='NHL Average')
        if self.plot_y_mean:
            avg_y = self.df[self.y_col].mean()
            ax.axhline(avg_y, color='k', label='NHL Average')

        if self.quadrant_labels:
            # Add quadrant labels
            offset = 0.15
            ax.annotate(self.quadrant_labels[0][0], xy=(x_min + offset, y_min + offset), color='k')  # Top-left
            ax.annotate(self.quadrant_labels[1][0], xy=(x_min + offset, y_max - offset), color='k')  # Bottom-left
            ax.annotate(self.quadrant_labels[1][1], xy=(x_max - offset, y_max - offset), color='k')  # Bottom-right
            ax.annotate(self.quadrant_labels[0][1], xy=(x_max - offset, y_min + offset), color='k')  # Top-right

        if self.invert_y:
            ax.invert_yaxis()
        plt.savefig(self.filename, dpi=100)


