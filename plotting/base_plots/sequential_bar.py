"""
Sub-class for plot that consists of sequential bars demonstrating a single value in sequence over
a period of time. 

Originally designed for goalie GSaX results from game-to-game.
"""

import polars as pl
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnnotationBbox

from plotting.base_plots.plot import Plot, FancyAxes
from util.font_dicts import game_report_label_text_params as label_params

COLORS = ['blue', 'orange', 'green', 'red', 'purple']

class SequentialBarPlot(Plot):
    """ Sub-class of plots for bar charts representing values over a time sequence. """

    def __init__(
            self,
            df,
            filename,
            team,
            x_column='',
            y_column='',
            y_max=0,
            show_average=False,
            selector_column='',
            sort_value='',
            title='',
            y_label='',
            x_label='',
            size=(12, 8),
            figure=None,
            axis=None,
            data_disclaimer='nst'):

        super().__init__(title=title, filename=filename, size=size, data_disclaimer=data_disclaimer)

        self.fig = plt.figure(figsize=self.size) if figure is None else figure
        self.axis = self.fig.add_subplot(111, axes_class=FancyAxes) if axis is None else axis
        self.axis.spines[['bottom', 'top', 'left', 'right']].set_visible(False)
        self.df = df
        self.team = team
        self.x_col = x_column
        self.y_col = y_column
        self.y_max = y_max
        self.show_average = show_average
        self.selector_col = selector_column
        self.sort_value = sort_value
        self.title = title
        self.x_label = x_label
        self.y_label = y_label

    def make_plot(self):
        """Generate the actual plot object."""

        self.set_title()

        # Gets a list of colors that will be used to color the bars in the proper sequence
        color_list = self.get_color_sequence()

        # Get information for the total value for each name
        totals = {}
        for x in set(self.df[self.selector_col]):
            total = self.df.filter(pl.col(self.selector_col) == x)[self.y_col].sum()
            totals[x] = round(total, 2)

        # Add the total value to the label which will be used in the legend
        bar_labels = [f"{name} (Total: {totals[name]})" for name in self.df[self.selector_col]]

        if self.y_max == 0:
            # If no y_max provided, set the y-range based on the most extreme value in the
            # y-column, plus a little more
            y_max = max([abs(y) for y in self.df[self.y_col]]) * 1.1
            self.axis.set_ylim(y_max * -1, y_max)
        else:
            # Otherwise use the provided value
            self.axis.set_ylim(self.y_max * -1, self.y_max)

        self.axis.set_ylabel(self.y_label, fontdict=label_params)

        # Set the x-range to be +/-1 the values of the x-column (this will usually be something
        # like game #)
        self.axis.set_xlim(min(self.df[self.x_col]) - 1, max(self.df[self.x_col]) + 1)
        self.axis.set_xticks(list(range(min(self.df[self.x_col]), max(self.df[self.x_col]) + 1)))
        self.axis.set_xlabel(self.x_label, fontdict=label_params)

        self.axis.tick_params(colors='antiquewhite', which='both')

        self.axis.bar(self.df[self.x_col], self.df[self.y_col], color=color_list,
                      alpha=0.6, label=bar_labels)

        self.axis.axhline(color='black')

        if self.show_average:
            average = self.df[self.y_col].mean()
            self.axis.axhline(average, label='Season Average')


        self.legend_without_duplicates()

        # Add huge logo as background piece
        team_logo = self.get_logo_marker(self.team, sport='hockey', size='huge', alpha=0.1)
        self.axis.add_artist(AnnotationBbox(team_logo, xy=(0.9, 0.5),
                                            frameon=False,
                                            box_alignment=(1, 0.5),
                                            xycoords='axes fraction', zorder=-10))

        self.save_plot()


    def get_color_sequence(self):
        """ Creates a list of colors for the bars corresponding to each row, where the color is 
        determined by the value in the selector column.

        If project_to_x is set, also add a unique color for season averages.
        """
        entities = list(set(self.df[self.selector_col]))
        entities.sort()

        color_map = {}
        for i, x in enumerate(entities):
            color_map[x] = COLORS[i]

        color_list = [color_map[x] for x in list(self.df[self.selector_col])]

        return color_list


    def legend_without_duplicates(self):
        """ Creates a legend box without duplicate values for labels that appear more than once """
        handles, labels = self.axis.get_legend_handles_labels()
        unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
        num_labels = len(unique)
        max_length = 0
        for x in set(labels):
            max_length = max(max_length, len(x))

        self.axis.legend(*zip(*unique),
                         bbox_to_anchor=(0.2 + 0.012 * max_length, 0.08 + 0.06 * num_labels),
                         bbox_transform=self.axis.transAxes,
                         prop={'size': 18})
