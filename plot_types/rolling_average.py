import math
import numpy as np
import polars as pl
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
from matplotlib.offsetbox import AnnotationBbox
from scipy.interpolate import make_interp_spline

from plot_types.plot import Plot, FancyAxes
from util.color_maps import label_colors, mlb_label_colors
from util.font_dicts import game_report_label_text_params as label_params


class RollingAveragePlot(Plot):
    """
    Sub-class of Plot to create rolling average line plots.
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
                 y_midpoint=50,
                 size=(10, 8),
                 multiline_key=None,
                 add_team_logos=False,
                 for_multiplot=True):

        super().__init__(filename, title, subtitle, size, sport, data_disclaimer)

        self.df = dataframe
        self.x_col = x_column
        self.y_col = y_column
        self.x_label = x_label
        self.y_label = y_label
        self.sport = sport
        self.y_midpoint = y_midpoint
        self.multiline_key = multiline_key
        self.add_team_logos = add_team_logos
        self.for_multiplot = for_multiplot
        self.data_disclaimer = data_disclaimer

        self.fig = plt.figure(figsize=self.size)
        self.axis = self.fig.add_subplot(111, axes_class=FancyAxes, ar=2.0)
        self.axis.spines[['bottom', 'left', 'right', 'top']].set_visible(False)


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

        self.axis.set_xlabel(self.x_label, fontdict=label_params)
        if not self.for_multiplot:
            self.axis.set_ylabel(self.y_label, fontdict=label_params)

        y_range = self.set_scaling()
        self.add_x_axis()

        if self.for_multiplot:
            self.axis.set_xticks([])
        else:
            x_min = self.df['gameNumber'].min()
            x_max = self.df['gameNumber'].max()
            x_ticks = list(range(x_min, x_max, 5))
            self.axis.set_xticks(x_ticks, labels=x_ticks, fontdict=label_params)
        #y_range = list(range(40, 65, 5))
        self.axis.set_yticks(y_range,
                             labels=[f"{y}%" for y in y_range] if self.sport == 'hockey' else y_range,
                             fontdict=label_params)

        # Make sure x-tick labels are whole numbers
        #self.axis.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))

        if self.for_multiplot:
            self.axis.set_title(self.title,
                                fontdict={
                                    "color": "antiquewhite",
                                    "size": 25.0,
                                    "family": "sans-serif",
                                    "weight": 800,
                                    "path_effects": [PathEffects.withStroke(linewidth=4.5, 
                                                                            foreground='black')]
                                }
            )
        else:
            self.set_title()

        self.save_plot()


    def handle_team_logos(self, df=None, alpha=0.75):
        """
        Add the team logo to the first and last point of each line.
        """
        if df is None:
            df = self.df
        logos = list()
        for team in set(df['team']):
            x_last = list(df.filter(pl.col('team') == team)[self.x_col])[-1]
            y_last = list(df.filter(pl.col('team') == team)[self.y_col])[-1]

            artist_box = AnnotationBbox(self.get_logo_marker(team, alpha=alpha, sport=self.sport),
                                        xy=(x_last, y_last),
                                        frameon=False)
            self.axis.add_artist(artist_box)

            x_first = list(df.filter(pl.col('team') == team)[self.x_col])[0]
            y_first = list(df.filter(pl.col('team') == team)[self.y_col])[0]

            artist_box = AnnotationBbox(self.get_logo_marker(team, alpha=alpha, sport=self.sport),
                                        xy=(x_first, y_first),
                                        frameon=False)
            logo = self.axis.add_artist(artist_box)
            logos.append(logo)
        return logos


    def plot_multilines(self, alpha=1, linewidth=3, df=None):
        """
        Given a multiline_key, for each distinct value in the column corresponding to that key,
        add a single line plot for the dataframe filtered on that value.
        """
        if df is None:
            df = self.df
        keys = set(df[self.multiline_key])
        lines = list()
        for key in keys:
            individual_df = df.filter(pl.col(self.multiline_key) == key)

            # Add a bit of smoothing
            x_col = individual_df[self.x_col]
            y_col = individual_df[self.y_col]
            new_x = np.linspace(x_col.min(), x_col.max(), 300)
            spl = make_interp_spline(x_col, y_col, k=3)
            y_smooth = spl(new_x)

            color = 'black'
            if self.add_team_logos:  # If we're adding team logos, color the lines by team color
                if self.sport == 'hockey':
                    color = label_colors[key]['line']
                elif self.sport == 'baseball':
                    color = mlb_label_colors[key]['line']
            #self.axis.plot(individual_df[self.x_col], individual_df[self.y_col], color=color,
            line = self.axis.plot(new_x, y_smooth, color=color, alpha=alpha,
                                  linewidth=linewidth)
            lines.append(line)

        return lines

    def add_x_axis(self):
        """
        Draws the x-axis at the y-midpoint.
        """
        self.axis.axhline(self.y_midpoint, color='black', label='50%')


    def add_dotted_h_lines(self, y_values: list[int]):
        """
        Given a list of y_values, plot dotted lines at each.
        """
        for y in y_values:
            self.axis.axhline(y, color='grey', linestyle='--', alpha=0.4)


    def set_scaling(self):
        """
        Sets x scaling to correspond to number of games in dataset (default behaviour), 
        and y-scaling to have the maximum and minimum be equal, based on the most 
        extreme y-value.
        """
        y_min = self.df[self.y_col].min()
        y_max = self.df[self.y_col].max()

        y_scale = max(abs(self.y_midpoint - y_max), abs(self.y_midpoint - y_min)) * 1.1

        #y_ticks = list(range(math.floor(y_scale * -1), math.ceil(y_scale + 1)))
        y_ticks = list(range(math.floor(self.y_midpoint - y_scale),
                             math.ceil(self.y_midpoint + y_scale + 1)))


        # When doing plots with big-number ranges that center around 50 (i.e. xGoal%), only
        # take multiples of 5 for the y-tick values
        if self.y_midpoint == 50:
            y_ticks = [y for y in y_ticks if y % 5 == 0] 
            self.axis.set_ylim(self.y_midpoint - y_scale, self.y_midpoint + y_scale)

        return y_ticks
        #self.axis.set_ylim(38, 62)
