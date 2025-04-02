import matplotlib.pyplot as plt

from plotting.base_plots.plot import Plot, FancyAxes
from util.font_dicts import game_report_label_text_params as label_params


class ViolinPlot(Plot):
    """
    Class for violin plots best suited for indicating distributions of a single metric, while
    highlighting players from a provided team.
    """
    def __init__(self,
                 dataframe,
                 filename,
                 column,
                 team,
                 y_label,
                 title='',
                 subtitle='',
                 size=(10, 8),
                 data_disclaimer='',
                 sport='baseball'):

        super().__init__(filename, title, subtitle, size, data_disclaimer, sport)

        self.df = dataframe
        self.team = team
        self.column = column
        self.y_label = y_label
        self.fig = plt.figure(figsize=self.size)
        self.axis = self.fig.add_subplot(111, axes_class=FancyAxes, ar=2.0)
        self.axis.spines[['bottom', 'left', 'right', 'top']].set_visible(False)


    def make_plot(self):
        """
        Method to assemble the plot object.
        """

        self.set_title()
        self.axis.set_ylabel(self.y_label, fontdict=label_params)

        self.axis.violinplot(self.df['wRC+'])
        self.save_plot()
