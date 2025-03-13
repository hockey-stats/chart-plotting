import numpy as np
import matplotlib.pyplot as plt

from plotting.base_plots.plot import Plot, FancyAxes
from util.font_dicts import game_report_label_text_params


class LayeredLollipopPlot(Plot):
    """
    Class for plotting two corresponding values as a layered lollipop plot.
    """
    def __init__(self, dataframe, filename, value_a, value_b, title='', x_label='',
                 y_label='', size=(10, 8), figure=None, axis=None,
                 value_a_label='', value_b_label='', legend_loc='upper right'):
        super().__init__(filename=filename,
                         title=title,
                         size=size,
                         figure=figure,
                         axis=axis)

        self.df = dataframe
        self.x_label = x_label
        self.y_label = y_label
        self.value_a = value_a
        self.value_b = value_b
        self.value_a_label = value_a_label
        self.value_b_label = value_b_label
        self.fig = plt.figure(figsize=self.size) if figure is None else figure
        self.axis = self.fig.add_subplot(111, axes_class=FancyAxes) if axis is None else axis
        self.axis.spines[['bottom', 'left', 'right', 'top']].set_visible(False)
        self.legend_loc = legend_loc


    def make_plot(self):
        """
        Creates the plot object.
        """

        self.set_title()
        # First add column denoting the rank of each team in the given dataframe
        self.df['rank'] = np.arange(len(self.df.index))

        # Then create the plot for value b, and then the plot of value a on top of it.
        # Then re-plot the final markers of value b so that they don't have lines going
        # through them.
        self.axis.stem(self.df[self.value_b], linefmt='C1-', label=self.value_b_label)
        self.axis.stem(self.df[self.value_a], linefmt='C0-', label=self.value_a_label)
        self.axis.plot(self.df['rank'], self.df[self.value_b], linestyle='',
                       marker='o', color='C1')

        max_y_value = max(self.df[self.value_a].max(), self.df[self.value_b].max())

        y_range = list(range(2, int(max_y_value + 2), 2))
        self.axis.set_yticks(y_range,
                             labels=y_range,
                             fontdict=game_report_label_text_params)
        self.axis.tick_params(color='antiquewhite')
        self.axis.set_xlabel(self.x_label, fontdict=game_report_label_text_params)
        self.axis.set_ylabel(self.y_label, fontdict=game_report_label_text_params)
        self.axis.set_ybound(0, max_y_value + 2)
        self.axis.legend(loc=self.legend_loc)

        # Remove x-labels and ticks
        plt.tick_params(
            axis='x',
            which='both',
            bottom=False,
            top=False,
            labelbottom=False
        )

        # Add one more column that represents a value slightly higher than max(value_a, value_b)
        # to provide a point for plotting team logos just above the head of the lollipop
        self.df['plot_point'] = [x + 0.6 for x in
                                 list(self.df[[self.value_a, self.value_b]].max(axis=1))]

        self.df.apply(lambda row:
                      self.add_team_logo(row, 'rank', 'plot_point', opacity=0.7, size='tiny'),
                      axis=1)

        self.save_plot()
