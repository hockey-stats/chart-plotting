"""
Sub-class of Plot that created a mirrored horizontal bar chart. This was originally created
for showing icetime of players from two teams in a game report chart.
"""

import matplotlib.pyplot as plt
import numpy as np

from plotting.plot import Plot, get_logo_marker
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
        # df_a and df_b correspond to the two sides of the mirrored bar plot. The x-values used in
        # df_b will be multiplied by -1 to create the mirror effect.
        if self.sort_value:
            self.df_a = self.df_a.sort_values(by=[self.sort_value], ascending=True)
            self.df_b = self.df_b.sort_values(by=[self.sort_value], ascending=True)

        print(self.df_a)
        print(self.df_b)

        for column in self.x_col:
            self.df_b[column] = [value * -1 for value in self.df_b[column]]

        y_range = list(range(0, max(len(self.df_a), len(self.df_b))))

        hatch_patterns = ['', 'x', 'o']
        for index, column in enumerate(self.x_col):
            if index == 0:
                left_a = 0
                left_b = 0
                self.axis.barh(y_range, self.df_a[column], color=label_colors[self.a_label]['bg'])
                self.axis.barh(y_range, self.df_b[column], color=label_colors[self.b_label]['bg'])
            else:
                prev_column = self.x_col[index - 1]
                left_a += self.df_a[prev_column]
                left_b += self.df_b[prev_column]
                self.axis.barh(y_range, self.df_a[column], left=left_a,
                               hatch=hatch_patterns[index])
                #mirrored_prev_column = [x + y for x, y in zip(self.df_b[column], self.df_b[prev_column])]
                self.axis.barh(y_range, self.df_b[column], left=left_b,
                               hatch=hatch_patterns[index])

        self.save_plot()


