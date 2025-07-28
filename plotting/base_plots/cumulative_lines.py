import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnnotationBbox

from plotting.base_plots.plot import Plot, FancyAxes
from util.color_maps import mlb_label_colors
from util.font_dicts import game_report_label_text_params as label_params


class CumulativeLinePlot(Plot):
    """
    Sub-class of Plot to create line plots in the vein of MoneyPucks standings plot.
    """
    def __init__(self,
                 filename,
                 dataframe,
                 sport='hockey',
                 data_disclaimer='moneypuck',
                 x_column='',
                 y_column='',
                 title='',
                 subtitle='',
                 x_label='',
                 y_label='',
                 size=(10, 8)):

        super().__init__(filename, title, subtitle, size, sport, data_disclaimer)

        self.df = dataframe
        self.x_col = x_column
        self.y_col = y_column
        self.x_label = x_label
        self.y_label = y_label
        self.sport = sport
        self.data_disclaimer = data_disclaimer

        self.fig = plt.figure(figsize=self.size)
        self.axis = self.fig.add_subplot(111, axes_class=FancyAxes, ar=2.0)
        self.axis.spines[['bottom', 'left', 'right', 'top']].set_visible(False)


    def make_plot(self):
        """
        Assemble the plot object.
        """
        self.plot_lines()
        y_min, y_max = self.add_horizontal_lines()

        self.axis.set_xlabel(self.x_label, fontdict=label_params)
        self.axis.set_ylabel(self.y_label, fontdict=label_params)

        x_ticks = list(range(0, self.df['game_number'].max(), 10))
        self.axis.set_xticks(x_ticks, labels=x_ticks, fontdict=label_params)

        y_ticks = list(range(y_min, y_max))
        y_ticks = [y for y in y_ticks if y % 2 == 0]
        self.axis.set_yticks(y_ticks, labels=y_ticks, fontdict=label_params)

        self.axis.tick_params(colors='antiquewhite', which='both')

        self.handle_team_logos()

        self.set_title()

        self.save_plot()


    def add_horizontal_lines(self):
        """
        Adds horizontal lines to denote break-points in y-axis.
        """
        y_min = int(self.df[self.y_col].min())
        y_max = int(self.df[self.y_col].max())

        if abs(y_min) != abs(y_max):
            y_min = -1 * y_max if abs(y_max) > abs(y_min) else y_min
            y_max = -1 * y_min if abs(y_min) > abs(y_max) else y_max

        for y in range(y_min, y_max + 1):
            if y == 0:
                color = 'black'
                linestyle = '-'
            else:
                color = 'grey'
                linestyle = '--'

            self.axis.hlines(y=y, xmin=0, xmax=self.df['game_number'].max(), alpha=0.4,
                            colors=color, linestyles=linestyle, zorder=-10)

        return y_min, y_max


    
    def plot_lines(self):
        """
        Adds a line plot for each team in the dataframe.
        """
        for team in set(self.df['team']):
            team_df = self.df[self.df['team'] == team]

            if self.sport == 'baseball':
                color = mlb_label_colors[team]['line']
            else:
                color = 'black'

            self.axis.plot(team_df[self.x_col], team_df[self.y_col],
                           color, marker='o', markersize=2, linestyle='dashed')



    def handle_team_logos(self):
        """
        Add the team logo to the last point of each line.
        """
        for team in set(self.df['team']):
            x_last = list(self.df[self.df['team'] == team][self.x_col])[-1]
            y_last = list(self.df[self.df['team'] == team][self.y_col])[-1]

            artist_box = AnnotationBbox(self.get_logo_marker(team, alpha=0.6, sport=self.sport),
                                        xy=(x_last, y_last),
                                        frameon=False)
            self.axis.add_artist(artist_box)
