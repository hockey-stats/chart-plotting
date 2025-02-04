"""
Sub-class of Plot that created a mirrored horizontal bar chart. This was originally created
for showing icetime of players from two teams in a game report chart.
"""

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.ticker import LinearLocator, IndexLocator

from plotting.plot import Plot, get_logo_marker, handle_player_full_names
from util.color_maps import label_colors

class MirroredBarPlot(Plot):
    """
    Sub-class of Plot to create a mirrored bar plot.
    """
    def __init__(self, dataframe_a, dataframe_b, filename, x_column='', y_column='', sort_value='',
                 title='', a_label='', b_label='', x_label='', y_label='', size=(10, 8),
                 figure=None, axis=None, is_subplot=False):

        super().__init__(filename=filename, size=size)

        self.fig = plt.figure(figsize=self.size) if figure is None else figure
        self.axis = self.fig.add_subplot(111) if axis is None else axis
        self.df_a = dataframe_a
        self.df_b = dataframe_b
        self.x_col = [x_column] if not isinstance(x_column, list) else x_column
        self.y_col = y_column
        self.sort_value = sort_value
        self.title = title
        self.a_label = a_label
        self.b_label = b_label
        self.x_label = x_label
        self.y_label = y_label
        self.is_subplot = is_subplot

    def make_plot(self):
        """
        Generate the actual plot object.
        """
        # df_a and df_b correspond to the two sides of the mirrored bar plot.
        if self.sort_value:
            self.df_a = self.df_a.sort_values(by=[self.sort_value], ascending=True)
            self.df_b = self.df_b.sort_values(by=[self.sort_value], ascending=True)

        # Add column for display names
        self.df_a['display_name'] = handle_player_full_names(list(self.df_a['name']))
        self.df_b['display_name'] = handle_player_full_names(list(self.df_b['name']))

        # Set the x-range of the plot based on the largest TOI value from both teams
        x_max = max(list(self.df_a[self.sort_value]) + list(self.df_b[self.sort_value])) + 1
        self.axis.set_xlim(x_max * -1, x_max)

        # The x-values used in df_b will be multiplied by -1 to create the mirror effect.
        for column in self.x_col:
            self.df_b[column] = [value * -1 for value in self.df_b[column]]

        y_range = list(range(0, max(len(self.df_a), len(self.df_b))))

        # Create a twin axis to host the second set of data, and add ticks with labels for
        # each player name
        ax2 = self.axis.twinx()
        self.axis.set_yticks(y_range, labels=list(self.df_b['display_name']))
        ax2.set_yticks(y_range, labels=list(self.df_a['display_name']))

        xticks = list(range(int(x_max)*-1, int(x_max), 5))
        xticks = list(range(0, 27, 5)) + [x * -1 for x in range(0, 27, 5) if x != 0]
        xticks.sort()
        print(xticks)
        xtick_labels = [abs(x) for x in xticks]
        self.axis.set_xticks(xticks, labels=xtick_labels)

        # Mapping of colors to use for PP and PK TOI (Even strength will be team color)
        color_map = {
            'pp': 'fuchsia',
            'pk': 'chartreuse'
        }

        # Mapping of state labels from data to labels for legend
        label_map = {
            'ev': 'Even Strength',
            'pp': 'Power Play',
            'pk': 'Penalty Kill'
        }

        for index, column in enumerate(self.x_col):
            # self.x_col[0] will correspond to the EV TOI, which we start drawing at the y-axis
            if index == 0:
                left_a = 0
                left_b = 0
                self.axis.barh(y_range, self.df_a[column],
                               color=label_colors[self.a_label]['bg'],
                               label=label_map[column],
                               alpha=0.6)
                ax2.barh(y_range, self.df_b[column],
                         color=label_colors[self.b_label]['bg'],
                         label=label_map[column],
                         alpha=0.6)

            # self.x_col[1:2] will correspond to pp and pk time, which we start drawing from
            # the end of the previous bar, to create a stacked effect.
            else:
                prev_column = self.x_col[index - 1]
                left_a += self.df_a[prev_column]
                left_b += self.df_b[prev_column]
                self.axis.barh(y_range, self.df_a[column], left=left_a,
                               color=color_map[column],
                               label=label_map[column],
                               alpha=0.6)
                ax2.barh(y_range, self.df_b[column], left=left_b,
                         color=color_map[column],
                         label=label_map[column],
                         alpha=0.6)

        self.axis.legend(loc='lower right')
        ax2.legend(loc='lower left')

        self.save_plot()
