import numpy as np
import matplotlib.pyplot as plt

from plotting.base_plots.plot import Plot, FancyAxes
from util.font_dicts import game_report_label_text_params as label_params
from util.helpers import ratio_to_color


class RatioScatterPlot(Plot):
    """
    Class for plotting ratio values as a scatter plot.
    """
    def __init__(self,
                 dataframe,
                 filename,
                 x_column,
                 y_column,
                 title='',
                 subtitle='',
                 x_label='',
                 y_label='',
                 ratio_lines=False,
                 invert_y=False,
                 plot_x_mean=False,
                 plot_y_mean=False,
                 quadrant_labels='default',
                 size=(10,8),
                 percentiles=None,
                 break_even_line=True,
                 plot_league_average=0,
                 show_league_context=False,
                 team='ALL',
                 scale='team',
                 scale_to_extreme=False,
                 y_min_max=None,
                 for_game_report=False,
                 data_disclaimer='moneypuck',
                 fade_non_playoffs=False,
                 sport='hockey'):

        super().__init__(filename, title, subtitle, size, data_disclaimer=data_disclaimer,
                         sport=sport)

        self.df = dataframe
        self.x_col = x_column
        self.y_col = y_column
        self.x_label = x_label
        self.y_label = y_label
        self.percentiles = percentiles
        self.break_even_line = break_even_line
        self.plot_league_average = plot_league_average
        if scale not in {'team', 'player'}:
            raise ValueError("'scale' value must be one of 'player' or 'team'")
        self.scale = scale
        self.ratio_lines = ratio_lines
        self.invert_y = invert_y
        self.plot_x_mean = plot_x_mean
        self.plot_y_mean = plot_y_mean
        self.quadrant_labels = quadrant_labels
        self.show_league_context = show_league_context
        self.team = team
        self.scale_to_extreme = scale_to_extreme
        self.for_game_report = for_game_report
        self.y_min_max = y_min_max
        self.fig = plt.figure(figsize=self.size)
        self.axis = self.fig.add_subplot(111, axes_class=FancyAxes, ar=2.0)
        self.axis.spines[['bottom', 'left', 'right', 'top']].set_visible(False)

        # Filter Dataframe if looking at a specific team
        if not self.show_league_context and self.team != 'ALL':
            self.df = self.df[self.df['team'] == self.team]

        # Setting specific to playoffs, fades the logos of non-playoff teams
        self.fade_non_playoffs = fade_non_playoffs


    def make_plot(self):
        """
        Method to assemble the plot object.
        """

        self.set_title()

        self.axis.set_xlabel(self.x_label, fontdict=label_params)

        # Have the y-axis labels on the right in the game report
        if self.for_game_report:
            self.axis.yaxis.set_label_position("right")
            self.axis.yaxis.tick_right()

        self.axis.set_ylabel(self.y_label, fontdict=label_params)
        if self.for_game_report:
            self.axis.set_xticks([])
            self.axis.set_yticks([])

        self.axis.tick_params(colors='antiquewhite', which='both')

        # Set the scaling of the plot
        x_min, x_max, _, y_max = self.set_scaling()

        if self.quadrant_labels:
            self.add_quadrant_labels()

        if self.percentiles:
            self.add_percentiles(x_min=x_min)

        if self.break_even_line:
            # Plot the line to display break-even
            self.axis.axline((2, 2),
                             slope=1,
                             color='black' if self.for_game_report else 'red',
                             alpha=0.5)

        if self.plot_league_average:
            start = 0.1
            end = 0.9
            self.axis.axvline(self.plot_league_average, color='k', label='NHL Average',
                       ymin=start, ymax=end)
            self.axis.axhline(self.plot_league_average, color='k', label='NHL Average',
                       xmin=start, xmax=end)
            self.axis.text(x=self.plot_league_average, y=self.plot_league_average, s="NHL\nAvg",
                    backgroundcolor='red', color='white', ha='center', va='center',
                    size='small', weight='bold')

        if self.ratio_lines:
            # Plot diagonal lines to show each percentage breakpoint
            for x in np.arange(0.0001, 1, 0.01):
                if round(x ,3) == 0.50:  # Already have a line indicating 50%, so skip here
                    continue
                # p1 and p2 are the endpoints of the diagonal
                p1 = (2, 2 * ((1 - x) / x))
                p2 = (2.5, 2.5 * ((1 - x) / x))
                color = '0.88'
                if round(x * 100, 0) % 5 == 0:  # Emphasize lines at 40, 45, 55, 60, etc.
                    #color = '0.6'
                    color = ratio_to_color(x) if self.for_game_report else '0.6'
                    text_xy = (y_max * (x / (1 - x)), y_max - 0.02)
                    if text_xy[0] > x_max or text_xy[0] < x_min:
                        text_xy = (x_max - 0.1, x_max * ((1 - x) / x))
                    self.axis.annotate(f'{str(round(x, 3) * 100)[:2]}%', xy=text_xy, color=color)

                # If this is for the game report, we only want the big lines at 40, 45 etc.
                if not self.for_game_report or  round(x* 100, 0) % 5 == 0:
                    self.axis.axline(p1, p2, color=color)

        # Calculate and plot the average for each value
        if self.plot_x_mean:
            x_mean = self.df[self.x_col].mean()
            self.axis.axvline(x_mean, color='k', label='NHL Average')
        if self.plot_y_mean:
            y_mean = self.df[self.y_col].mean()
            self.axis.axhline(y_mean, color='k', label='NHL Average')

        # Add team logos, slightly different based on team- or player-scale
        if self.scale == 'player':
            self.self_add_player_data()

        elif self.scale =='team':
            bad_teams = set()
            if self.fade_non_playoffs:
                bad_teams = {'OTT', 'STL', 'TB', 'TBL', 'MTL', 'NJD', 'NJ', 'LAK', 'LA',
                             'MIN', 'COL'}
            self.df.apply(lambda row:
                          self.add_team_logo(row, self.x_col, self.y_col, opacity=0.7, 
                                             teams_to_fade=bad_teams), axis=1)

        if self.invert_y:
            self.axis.invert_yaxis()

        self.save_plot()


    def self_add_player_data(self):
        """
        Method to add the logos for each player in the plot. 
        
        If `self.team` is not 'ALL' and `self.show_league_context` is True, then show players from
        all teams with severely reduced opacity and no labels.
        """
        if self.team != 'ALL' and self.show_league_context:
            # DataFrame for every player excluding the target team
            remaining_df = self.df[self.df['team'] != self.team]
            remaining_df.apply(lambda row: self.add_team_logo(row, self.x_col, self.y_col,
                                                              opacity=0.08),
                               axis=1)

        max_icetime = self.df.icetime.max()
        # Now add the desired players for the given team, with scaled opacity and name labels
        team_df = self.df[self.df['team'] == self.team] if self.team != 'ALL' else self.df
        team_df.apply(lambda row: self.add_team_logo(row, self.x_col, self.y_col, label='name',
                                                     opacity_scale='icetime',
                                                     opacity_max=max_icetime),
                      axis=1)


    def set_scaling(self):
        """
        Method to set the xy-scaling of a scatter plot.

        If self.set_scale_to_extreme is True, the x-scale will equal the y-scale, and the scale will
        correspond to whichever of the x-ranges or y-ranges is larger.

        If self.x_min_max or self.y_min_max are provided, those will override these values.

        If neither are set, the x- and y-scale will be set independently of each-
        other, both being set to just contain there corresponding extrema.

        Returns the max/min x-,y-values to be used,
        """

        x_min = self.df[self.x_col].min() / 1.04
        x_max = self.df[self.x_col].max() * 1.04
        y_min = self.df[self.y_col].min() / 1.04
        y_max = self.df[self.y_col].max() * 1.04
       # x_min = self.df[self.x_col].min() - 0.1
       # x_max = self.df[self.x_col].max() + 0.1
       # y_min = self.df[self.y_col].min() - 0.1
       # y_max = self.df[self.y_col].max() + 0.1

        if self.scale_to_extreme:
            if not self.plot_league_average:
                # Need the average value for one of the axes to use as the midpoint
                raise AttributeError("self.scale_to_extreme set to True but "\
                                     "self.plot_league_average not provided.")
            max_diff = 0
            for val in [x_min, x_max, y_min, y_max]:
                max_diff = max(max_diff, abs(self.plot_league_average - val))

            x_max = self.plot_league_average + max_diff
            y_max = x_max
            x_min = self.plot_league_average - max_diff
            y_min = x_min

        else:
            #if self.x_min_max:
            #    x_min = self.x_min_max[0]
            #    x_max = self.x_min_max[1]
            # Nothing uses this yet
            if self.y_min_max:
                y_min = self.y_min_max[0]
                y_max = self.y_min_max[1]

        if self.for_game_report:
            # Since the game reports deal with more extreme values, we want to start at 0
            self.axis.set_xlim(0, x_max)
            self.axis.set_ylim(0, y_max)
        else:
            self.axis.set_xlim(x_min, x_max)
            self.axis.set_ylim(y_min, y_max)

        return x_min, x_max, y_min, y_max


    def add_percentiles(self, x_min):
        """
        Method to label percentiles in a scatter plot.
        Argument is to be given in the dict format, looking like the following:
        {
            "vertical": [a, b, c],
            "horizontal": [x, y, z]
        },
        where vertical/horizontal will determine what orientation the percentile label will have,
        and the value will be a list of floats denoting the breakpoint for each percentile. Thus,
        the number of percentiles to label will be the length of the list + 1. E.g, to label 
        quarter-percentiles, 3 values will be given which denote the 25th, 50th, and 75th 
        percentile cut-offs respectively.
        """

        if self.percentiles.get('vertical', None):
            iterator = int(100.0 / (len(self.percentiles['vertical']) + 1))
            for index, value in enumerate(self.percentiles['vertical']):
                self.axis.axvline(value, color='k',
                                  label=f'{iterator * (index + 1)}th Percentile')

        if self.percentiles.get('horizontal', None):
            iterator = int(100.0 / (len(self.percentiles['horizontal']) + 1))
            span_start = 0
            for index, value in enumerate(self.percentiles['horizontal']):
                label_xy = (x_min * 1.01, value - 0.05)
                self.axis.axhspan(span_start, value, alpha=0.1 * (index + 1))
                self.axis.annotate(f'{iterator * (index + 1)}th Percentile',
                                   xy=label_xy, color='royalblue')
                span_start = value
            self.axis.axhspan(span_start, 100, alpha=0.4)


    def add_quadrant_labels(self):
        """
        Method to add labels to each quadrant in a scatter plot.
        Default behaviour is to add the '+/- OFFENSE/DEFENSE' labels depending on the quadrant.

        If a 2x2 list of strings is provided as 'self.quadrant_labels', then add those labels to
        the corresponding quadrants.

        If a list of just two strings was provided, then add them in alternating +/- modes in the
        style of the default OFFENSE/DEFENSE quadrant labels.
        """
        ofs = 0.1  # Offset value for labels (distance between label and axis)
        if self.quadrant_labels == 'default' or np.array(self.quadrant_labels).shape == (2,):
            label_a = 'OFFENSE' if self.quadrant_labels == 'default' else self.quadrant_labels[0]
            label_b = 'DEFENSE' if self.quadrant_labels == 'default' else self.quadrant_labels[1]

            # Make sure both labels are the same length, for neatness
            if len(label_a) > len(label_b):
                label_b += ' ' * (len(label_a) - len(label_b))
            elif len(label_a) < len(label_b):
                label_a += ' ' * (len(label_b) - len(label_a))

            # Define colors for 'good' and 'bad'
            good = 'royalblue'
            bad = 'red'

            # Combinations to zip and iterator over
            label_sign_combinations = [('-', '+'), ('-', '-'), ('+', '-'), ('+', '+')]
            color_combinations = [(bad, good), (bad, bad), (good, bad), (good, good)]
            offset_combinations = [(ofs, 1-ofs), (ofs, ofs), (1-ofs, ofs), (1-ofs, 1-ofs)]

            for xy, color, sign in zip(offset_combinations,
                                       color_combinations,
                                       label_sign_combinations):
                self.axis.annotate(f'{sign[0]} {label_a}', xy=xy,
                                   xycoords='axes fraction',
                                   color=color[0], va='bottom', ha='center', fontweight='bold')
                self.axis.annotate(f'{sign[1]} {label_b}', xy=xy,
                                   xycoords='axes fraction',
                                   color=color[1], va='top', ha='center', fontweight='bold')

        if np.array(self.quadrant_labels).shape == (2, 2):
            self.axis.annotate(self.quadrant_labels[0][0],  # Top-left
                            xy=(0 + ofs, 1 - ofs), xycoords='axes fraction',
                            color='black', fontweight='bold', va='center', ha='center')
            self.axis.annotate(self.quadrant_labels[1][0],  # Bottom-left
                            xy=(0 + ofs, 0 + ofs), xycoords='axes fraction',
                            color='black', fontweight='bold', va='center', ha='center')
            self.axis.annotate(self.quadrant_labels[1][1],  # Bottom-right
                            xy=(1 - ofs, 0 + ofs), xycoords='axes fraction',
                            color='black', fontweight='bold', va='center', ha='center')
            self.axis.annotate(self.quadrant_labels[0][1],  # Top-right
                            xy=(1 - ofs, 1 - ofs), xycoords='axes fraction',
                            color='black', fontweight='bold', va='center', ha='center')
