import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

from util.team_maps import nst_team_mapping
from util.color_maps import label_colors


def get_logo_marker(team_name, alpha=1, zoom=1):
    """
    Quick function to return the team logo as a matplotlib marker object.
    """
    return OffsetImage(plt.imread(f'team_logos/{team_name}.png'), alpha=alpha, zoom=zoom)


def handle_player_full_names(names):
    """
    Generally skater names will be displayed as just their last names. This function will be
    called in the event that multiple skaters share a last name, and will adjust their last names
    to also show their first initials (e.g. Nylander -> W. Nylander and A. Nylander).

    :param list names: List of full names.
    """
    last_names = [name.split()[-1] for name in names]
    seen = set()
    dupes = [name for name in last_names if name in seen or seen.add(name)]
    final_names = []
    for name in names:
        last_name = name.split()[-1]
        if last_name in dupes:
            initial = name.split()[0][0]
            display_name = f'{initial}. {last_name}'
            final_names.append(display_name)
        else:
            final_names.append(last_name)
    return final_names



class Plot:
    """
    Base class to be used for all plots. Will only ever be called via super() for a base class
    """
    def __init__(self, dataframe=None, filename='', x_column=None, y_column=None,
                 title='', x_label='', y_label='', size=(10, 8), figure=None, axis=None):

        self.df = dataframe
        self.filename = filename
        self.x_col = x_column
        self.y_col = y_column
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.size = size
        self.fig = figure
        self.axis = axis

    def save_plot(self):
        plt.title(self.title)
        # Add data disclaimer
        plt.figtext(0.5, 0.01, "All data from MoneyPuck.com", ha="center",
                    bbox={"facecolor": "cyan", "alpha" :0.5, "pad": 5})
        # If self.filename is empty, then this is for a multiplot so don't save as a file
        if self.filename:
            plt.savefig(self.filename, dpi=100)

    def add_team_logo(self, row, x, y, label=None, opacity_scale=None, opacity_max=None, zoom=1):
        """
        Function used with DataFrame.map() that adds a team logo to an axis object.
        :param pandas.Series row: Row of the dataframe being applied on
        :param str x: Row entry to be used for x-coordinate
        :param str y: Row entry to be used for y-coordinate
        :param matplotlib.pyplot.Axis: Axis object the icon is being added to
        :param str label: Row entry to be used as a label. If not supplied, don't label
        :param str opacity_scal: Row entry used to scale opacity, if desired
        :param int opacity_max: Max value to compare against for opacity scale
        :param int zoom: Zoom level on image. Defaults to 1.
        """
        opacity = 0.6  # Default opacity if scaling isn't used
        if opacity_scale:
            # Gives a value between 0 and 1, so that the opacity of the icon demonstrates
            # the value on this scale (e.g., icetime)
            opacity = row[opacity_scale] / opacity_max

        # Assumes the team value is under row['team']
        artist_box = AnnotationBbox(get_logo_marker(row['team'], alpha=opacity, zoom=zoom),
                                    xy=(row[x], row[y]), frameon=False)
        self.axis.add_artist(artist_box)

        if label:
            # Check if plot is using an inverted y-axis. If so, add label to top of logo.
            # Else, add label to the bottom.
            try:
                verticalalignment = 'top' if self.invert_y else 'bottom'
            except AttributeError:
                # AttributeError here implies that the plot doesn't have the 'invert_y' attribute,
                # i.e. it isn't a plot type that would every invert the y-axis, so set vertical
                # alignment to be 'bottom'
                verticalalignment = 'bottom'
            self.axis.text(row[x], row[y] + 0.06, row[label],
                           horizontalalignment='center',
                           verticalalignment=verticalalignment,
                           fontsize=10)


class LayeredLollipopPlot(Plot):
    """
    Class for plotting two corresponding values as a layered lollipop plot.
    """
    def __init__(self, dataframe, filename, value_a, value_b, title='', x_label='',
                 y_label='', size=(10, 8), figure=None, axis=None,
                 value_a_label='', value_b_label=''):
        super().__init__(dataframe, filename, value_a, value_b, title, x_label, y_label,
                         size, figure, axis)
        self.value_a = value_a
        self.value_b = value_b
        self.value_a_label = value_a_label
        self.value_b_label = value_b_label
        self.fig = plt.figure(figsize=self.size) if figure is None else figure
        self.axis = self.fig.add_subplot(111) if axis is None else axis


    def make_plot(self):
        # First add column denoting the rank of each team in the given dataframe
        self.df['rank'] = np.arange(len(self.df.index))

        # Then create the plot for value b, and then the plot of value a on top of it.
        # Then re-plot the final markers of value b sp that they don't have lines going 
        # through them.
        stem = self.axis.stem(self.df[self.value_b], linefmt='C1-', label=self.value_b_label)
        #stem[1].set_linewidth(1)
        stem = self.axis.stem(self.df[self.value_a], linefmt='C0-', label=self.value_a_label)
        #stem[1].set_linewidth(1)
        self.axis.plot(self.df['rank'], self.df[self.value_b], linestyle='',
                       marker='o', color='C1')

        self.axis.set_xlabel(self.x_label)
        self.axis.set_ylabel(self.y_label)
        self.axis.legend()

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
        self.df['plot_point'] = [x + 0.5 for x in 
                                 list(self.df[[self.value_a, self.value_b]].max(axis=1))]

        self.df.apply(lambda row: self.add_team_logo(row, 'rank', 'plot_point', zoom=0.4), axis=1)

        self.save_plot()


class RatioScatterPlot(Plot):
    """
    Class for plotting ratio values as a scatter plot.
    """
    def __init__(self, dataframe, filename, x_column, y_column, title='', x_label='',
                 y_label='', ratio_lines=False, invert_y=False, plot_x_mean=False,
                 plot_y_mean=False, quadrant_labels='default', size=(10,8),
                 percentiles=None, break_even_line=True, plot_league_average=0, scale='team',
                 scale_to_extreme=False, figure=None, axis=None):

        super().__init__(dataframe, filename, x_column, y_column, title, x_label, y_label,
                         size, figure, axis)

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
        self.fig = plt.figure(figsize=self.size) if figure is None else figure
        self.axis = self.fig.add_subplot(111) if axis is None else axis
        self.scale_to_extreme = scale_to_extreme


    def make_plot(self):
        # First plot the actual values
        self.axis.scatter(x=self.df[self.x_col], y=self.df[self.y_col], s=0)

        self.axis.set_xlabel(self.x_label)
        self.axis.set_ylabel(self.y_label)

        # Set the scaling of the plot
        x_min, x_max, y_min, y_max = self.set_scaling()

        if self.quadrant_labels:
            self.add_quadrant_labels()

        if self.percentiles:
            self.add_percentiles(x_min=x_min)

        # Code for name labels, TODO: make use of or get rid of
        # For player scale, label each logo with the player's name
        # self.df.apply(lambda row: ax.text(row[self.x_col], row[self.y_col], row['name'].split(' ')[1],
        #                                  horizontalalignment='center', fontsize=10,
        #                                  backgroundcolor=label_colors[row['team']]['bg'],
        #                                  color=label_colors[row['team']]['text'],
        #                                  verticalalignment='center'), axis=1)

        if self.break_even_line:
            # Plot the line to display break-even
            self.axis.axline((2, 2), slope=1, color='r')

        if self.plot_league_average and self.x_col == 'xGFph':
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
            for x in np.arange(0.01, 1.0, 0.01):
                if round(x ,3) == 0.50:  # Already have a line indicating 50%, so skip here
                    continue
                # p1 and p2 are the endpoints of the diagonal
                p1 = (2, 2 * ((1 - x) / x))
                p2 = (2.5, 2.5 * ((1 - x) / x))
                color = '0.95'
                if round(x * 100, 0) % 5 == 0:  # Emphasize lines at 40, 45, 55, 60, etc.
                    color = '0.8'
                    text_xy = (y_max * (x / (1 - x)), y_max - 0.02)
                    if text_xy[0] > x_max or text_xy[0] < x_min:
                        text_xy = (x_max - 0.1, x_max * ((1 - x) / x))
                    self.axis.annotate(f'{str(round(x, 3) * 100)[:2]}%', xy=text_xy, color=color)
                self.axis.axline(p1, p2, color=color)

        # Calculate and plot the average for each value
        if self.plot_x_mean:
            self.axis.axvline(self.plot_league_average, color='k', label='NHL Average')
        if self.plot_y_mean:
            self.axis.axhline(self.plot_league_average, color='k', label='NHL Average')

        # Add team logos, slightly different based on team- or player-scale
        if self.scale == 'player':
            # Convert full names to just last names, adding first initial in the case of duplicates
            adjusted_names = handle_player_full_names(list(self.df['name']))
            self.df['display_name'] = adjusted_names
            max_icetime = self.df.icetime.max()
            self.df.apply(lambda row: self.add_team_logo(row, self.x_col, self.y_col, 
                                                         label='display_name',
                                                         opacity_scale='icetime',
                                                         opacity_max=max_icetime),
                         axis=1)

        elif self.scale =='team':
            self.df.apply(lambda row: self.add_team_logo(row, self.x_col, self.y_col), axis=1)

        if self.invert_y:
            self.axis.invert_yaxis()

        self.save_plot()


    def set_scaling(self):
        """
        Method to set the xy-scaling of a scatter plot.

        If self.set_scale_to_extreme is True, the x-scale will equal the y-scale, and the scale will
        correspond to whichever of the x-ranges or y-ranges is larger.

        If self.set_scale_to_extreme is False, the x- and y-scale will be set independently of each-
        other, both being set to just contain there corresponding extrema.

        Returns the max/min x-,y-values to be used,
        """
        x_min = self.df[self.x_col].min() - 0.1
        x_max = self.df[self.x_col].max() + 0.1
        y_min = self.df[self.y_col].min() - 0.1
        y_max = self.df[self.y_col].max() + 0.1

        if self.scale_to_extreme:
            x_max = max(x_max, y_max)
            y_max = x_max
            x_min = min(x_min, y_min)
            y_min = x_min
            #if not self.plot_league_average:
            #    raise AttributeError("self.scale_to_extreme set to True but "\
            #                         "self.plot_league_average not provided.")
            #max_diff = 0
            #for val in [x_min, x_max, y_min, y_max]:
            #    if abs(self.plot_league_average - val) > max_diff:
            #        max_diff = abs(self.plot_league_average - val)

            #x_max = self.plot_league_average + max_diff
            #y_max = x_max
            #x_min = self.plot_league_average - max_diff
            #y_min = x_min

        self.axis.set_xlim(0, x_max)
        self.axis.set_ylim(0, y_max)

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
        offset = 0.08
        if self.quadrant_labels == 'default' or np.array(self.quadrant_labels).shape == (2,):
            label_a = 'OFFENSE' if self.quadrant_labels == 'default' else self.quadrant_labels[0]
            label_b = 'DEFENSE' if self.quadrant_labels == 'default' else self.quadrant_labels[1]

            # Make sure both labels are the same length, for neatness
            if len(label_a) > len(label_b):
                label_b += ' ' * (len(label_a) - len(label_b))
            elif len(label_a) < len(label_b):
                label_a += ' ' * (len(label_b) - len(label_a))

            # Top-left
            self.axis.annotate(f'- {label_a}', xy=(0 + offset, 1 - offset), xycoords='axes fraction',
                               color='red', va='bottom', ha='center', fontweight='bold')
            self.axis.annotate(f'+ {label_b}', xy=(0 + offset, 1 - offset), xycoords='axes fraction',
                               color='green', va='top', ha='center', fontweight='bold')
            # Bottom-left
            self.axis.annotate(f'- {label_a}', xy=(0 + offset, 0 + offset), xycoords='axes fraction',
                               color='red', va='bottom', ha='center', fontweight='bold')
            self.axis.annotate(f'- {label_b}', xy=(0 + offset, 0 + offset), xycoords='axes fraction',
                               color='red', va='top', ha='center', fontweight='bold')
            # Bottom-right
            self.axis.annotate(f'+ {label_a}', xy=(1 - offset, 0 + offset), xycoords='axes fraction',
                               color='green', va='bottom', ha='center', fontweight='bold')
            self.axis.annotate(f'- {label_b}', xy=(1 - offset, 0 + offset), xycoords='axes fraction',
                               color='red', va='top', ha='center', fontweight='bold')
            # Top-right
            self.axis.annotate(f'+ {label_a}', xy=(1 - offset, 1 - offset), xycoords='axes fraction',
                               color='green', va='bottom', ha='center', fontweight='bold')
            self.axis.annotate(f'+ {label_b}', xy=(1 - offset, 1 - offset), xycoords='axes fraction',
                               color='green', va='top', ha='center', fontweight='bold')
            return None

        if np.array(self.quadrant_labels).shape == (2, 2):
            self.axis.annotate(self.quadrant_labels[0][0],  # Top-left
                            xy=(0 + offset, 1 - offset), xycoords='axes fraction',
                            color='black', fontweight='bold', va='center', ha='center')
            self.axis.annotate(self.quadrant_labels[1][0],  # Bottom-left
                            xy=(0 + offset, 0 + offset), xycoords='axes fraction',
                            color='black', fontweight='bold', va='center', ha='center')
            self.axis.annotate(self.quadrant_labels[1][1],  # Bottom-right
                            xy=(1 - offset, 0 + offset), xycoords='axes fraction',
                            color='black', fontweight='bold', va='center', ha='center')
            self.axis.annotate(self.quadrant_labels[0][1],  # Top-right
                            xy=(1 - offset, 1 - offset), xycoords='axes fraction',
                            color='black', fontweight='bold', va='center', ha='center')
            return None
