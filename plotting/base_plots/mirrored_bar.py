"""
Sub-class of Plot that created a mirrored horizontal bar chart. This was originally created
for showing icetime of players from two teams in a game report chart.
"""

import matplotlib.pyplot as plt

from plotting.base_plots.plot import Plot
from util.color_maps import label_colors
from util.helpers import handle_player_full_names

class MirroredBarPlot(Plot):
    """
    Sub-class of Plot to create a mirrored bar plot. Built with the goal of creating
    an icetime plot for the game report, but could be extended elsewhere.
    """
    def __init__(self,
                 dataframe_a,
                 dataframe_b,
                 filename,
                 x_column='',
                 y_column='',
                 sort_value='',
                 title='',
                 a_label='',
                 b_label='',
                 x_label='',
                 y_label='',
                 size=(10, 8),
                 figure=None,
                 axis=None,
                 data_disclaimer='moneypuck'):

        super().__init__(title=title, filename=filename, size=size, data_disclaimer=data_disclaimer)

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

    def make_plot(self):
        """
        Generate the actual plot object.
        """

        # Set title
        plt.title(self.title)

        # df_a and df_b correspond to the two sides of the mirrored bar plot.
        if self.sort_value:
            self.df_a = self.df_a.sort_values(by=[self.sort_value], ascending=True)
            self.df_b = self.df_b.sort_values(by=[self.sort_value], ascending=True)

        # Add column for display names
        self.df_a['display_name'] = handle_player_full_names(self.df_a)
        self.df_b['display_name'] = handle_player_full_names(self.df_b)

        # Set the x-range of the plot based on the largest TOI value from both teams
        x_max = max(list(self.df_a[self.sort_value]) + list(self.df_b[self.sort_value])) + 1
        self.axis.set_xlim(x_max * -1, x_max)

        # The x-values used in df_a will be multiplied by -1 to create the mirror effect.
        for column in self.x_col:
            self.df_a[column] = [value * -1 for value in self.df_a[column]]

        y_range = list(range(0, max(len(self.df_a), len(self.df_b))))

        # Create a twin axis to host the second set of data, and add ticks with labels for
        # each player name
        ax2 = self.axis.twinx()
        self.axis.set_yticks(y_range, labels=list(self.df_a['display_name']))
        ax2.set_yticks(y_range, labels=list(self.df_b['display_name']))

        xticks = list(range(0, 27, 5)) + [x * -1 for x in range(0, 27, 5) if x != 0]
        xticks.sort()
        xtick_labels = [abs(x) for x in xticks]
        self.axis.set_xticks(xticks, labels=xtick_labels)

        # Mapping of colors to use for PP and PK TOI (Even strength will be team color)
        color_map = {
            'pp': 'fuchsia',
            'pk': 'chartreuse'
        }

        # Mapping of state labels from data to labels for legend
        label_map = {
            #'ev': 'Even Strength',
            'pp': 'Power Play',
            'pk': 'Penalty Kill'
        }

        bar_pp, bar_pk = (None, None)
        zorder = 0
        for index, column in enumerate(self.x_col):
            # self.x_col[0] will correspond to the EV TOI, which we start drawing at the y-axis
            if index == 0:
                left_a = 0
                left_b = 0
                self.axis.barh(y_range, self.df_b[column],
                               color=label_colors[self.b_label]['bg'],
                               #label='Even Strength',
                               zorder=zorder,
                               alpha=0.5)
                ax2.barh(y_range, self.df_a[column],
                         color=label_colors[self.a_label]['bg'],
                         #label='Even Strength',
                         zorder=zorder,
                         alpha=0.5)

            # self.x_col[1:2] will correspond to pp and pk time, which we start drawing from
            # the end of the previous bar, to create a stacked effect.
            else:
                prev_column = self.x_col[index - 1]
                left_b += self.df_b[prev_column]
                left_a += self.df_a[prev_column]

                # Have to assign specific portions for pp/pk bars to specific variables for
                # creating the legend with just these two elements.
                if index == 1:
                    bar_pp = self.axis.barh(y_range, self.df_b[column], left=left_b,
                                            color=color_map[column],
                                            label=label_map[column],
                                            zorder=zorder,
                                            alpha=0.5)
                else:
                    bar_pk = self.axis.barh(y_range, self.df_b[column], left=left_b,
                                            color=color_map[column],
                                            label=label_map[column],
                                            alpha=0.5)

                ax2.barh(y_range, self.df_a[column], left=left_a,
                         color=color_map[column],
                         label=label_map[column],
                         zorder=zorder,
                         alpha=0.5)

        self.add_scoring_summary(ax2)

        # Add a vertical line separating the two teams
        plt.axvline(x=0, color='black')

        # Add further dashed vertical lines indicating every 5-min increment of icetime
        for x in xticks:
            if x == 0:
                continue
            plt.axvline(x=x, color='grey', linestyle='--', alpha=0.2)

        # Legend will only show the colors for PP/PK, hopefully Even-Strength is intuitive enough
        self.axis.legend(handles=[bar_pp, bar_pk],
                         labels=['Power Play', 'Penalty Kill'],
                         loc='lower right')

        # Add label for x-axis
        if self.x_label:
            self.axis.set_xlabel(self.x_label)

        self.save_plot()


    def add_scoring_summary(self, ax2):
        """
        Method that will draw indicators for players who have scored any goals or assists,
        by drawing a small symbol on their icetime bar for each goal/assist.

        :param Axis ax2: The secondary axis which the elements for the second team should be drawn.
        """

        # Define bbox styles for goal and assist indicators
        g_bbox = {
            "boxstyle": "circle",
            "edgecolor": "white",
            "facecolor": "slateblue"
        }
        a_bbox = {
            "boxstyle": "circle",
            "edgecolor": "white",
            "facecolor": "darkgoldenrod"
        }

        # Global font settings
        fontsize = 9
        fontweight = 1000
        fontcolor = "mintcream"

        zorder = 10

        vertical_offset = 0.13
        horizontal_offset_increment = 1.7
        horizontal_offset_start = 1
        for i, df in enumerate([self.df_b, self.df_a]):
            for index, (_, row) in enumerate(df.iterrows()):
                horizontal_offset = horizontal_offset_start
                for _ in range(0, row['g']):
                    if i == 0:
                        self.axis.text(horizontal_offset, index - vertical_offset,
                                    "G",
                                    size=fontsize,
                                    weight=fontweight,
                                    color=fontcolor,
                                    zorder=zorder,
                                    bbox=g_bbox)
                    else:
                        ax2.text(horizontal_offset, index - vertical_offset,
                                    "G",
                                    size=fontsize,
                                    weight=fontweight,
                                    color=fontcolor,
                                    zorder=zorder,
                                    bbox=g_bbox)

                    horizontal_offset += horizontal_offset_increment
                for _ in range(0, row['a1'] + row['a2']):
                    if i == 0:
                        self.axis.text(horizontal_offset, index - vertical_offset,
                                    "A",
                                    size=fontsize,
                                    weight=fontweight,
                                    color=fontcolor,
                                    zorder=zorder,
                                    bbox=a_bbox)
                    else:
                        ax2.text(horizontal_offset, index - vertical_offset,
                                    "A",
                                    size=fontsize,
                                    weight=fontweight,
                                    color=fontcolor,
                                    zorder=zorder,
                                    bbox=a_bbox)
                    horizontal_offset += horizontal_offset_increment
            # When switching to team b, mirror the values for horizontal incrementation
            horizontal_offset_start = -1.4
            horizontal_offset_increment = -1 * horizontal_offset_increment
