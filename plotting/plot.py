import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

from util.team_maps import nst_team_mapping
from util.color_maps import label_colors


def get_logo_marker(team_name, alpha=1):
    """
    Quick function to return the team logo as a matplotlib marker object. 
    """
    return OffsetImage(plt.imread(f'team_logos/{team_name}.png'), alpha=alpha, zoom=1)


def add_team_logo(row, x, y, axis, label=None, opacity_scale=None, opacity_max=None):
    """
    Function used with DataFrame.map() that adds a team logo to an axis object.
    :param pandas.Series row: Row of the dataframe being applied on
    :param str x: Row entry to be used for x-coordinate
    :param str y: Row entry to be used for y-coordinate
    :param matplotlib.pyplot.Axis: Axis object the icon is being added to
    :param str label: Row entry to be used as a label. If not supplied, don't label
    :param str opacity_scal: Row entry used to scale opacity, if desired
    :param int opacity_max: Max value to compare against for opacity scale
    """
    opacity = 0.8  # Default opacity if scaling isn't used 
    if opacity_scale:
        # Gives a value between 0 and 1, so that the opacity of the icon demonstrates
        # the value on this scale (e.g., icetime)
        opacity = row[opacity_scale] / opacity_max

    # Assumes the team value is under row['team']
    artist_box = AnnotationBbox(get_logo_marker(row['team'], alpha=opacity),
                                xy=(row[x], row[y]), frameon=False)
    axis.add_artist(artist_box)

    if label:
        # Split the label entry by ' ' and use last entry. Makes no difference for one-word
        # labels, but for names uses last name only.
        axis.text(row[x], row[y] + 0.06, row[label].split(' ')[-1], horizontalalignment='center',
                  verticalalignment='top', fontsize=10)


class Plot:
    """
    Base class to be used for all plots. Will only ever be called via super() for a base class
    """
    def __init__(self, dataframe, filename, x_column, y_column, title='', x_label='', y_label='', ratio_lines=False, 
                 invert_y=False, plot_x_mean=False, plot_y_mean=False, quadrant_labels=None, size=(10, 8)):
        self.df = dataframe
        self.filename = filename
        self.x_col = x_column
        self.y_col = y_column
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.ratio_lines = ratio_lines
        self.invert_y = invert_y
        self.plot_x_mean = plot_x_mean
        self.plot_y_mean = plot_y_mean
        self.quadrant_labels = quadrant_labels
        self.size = size
        self.fig = None
        self.axis = None




class RatioScatterPlot(Plot):
    """
    Class for plotting ratio values as a scatter plot.
    """
    def __init__(self, dataframe, filename, x_column, y_column, title='', x_label='', y_label='', ratio_lines=False, 
                 invert_y=False, plot_x_mean=False, plot_y_mean=False, quadrant_labels='default', size=(10,8), 
                 break_even_line=True, plot_league_average=0, scale='team'):
        super().__init__(dataframe, filename, x_column, y_column, title, x_label, y_label, ratio_lines, invert_y,
                         plot_x_mean, plot_y_mean, quadrant_labels)
        self.break_even_line = break_even_line
        self.plot_league_average = plot_league_average
        if scale not in {'team', 'player'}:
            raise Exception("'scale' value must be one of 'player' or 'team'")
        self.scale = scale
        self.fig = plt.figure(figsize=self.size)
        self.axis = self.fig.add_subplot(111)


    def make_plot(self):
        # First plot the actual values 
        self.axis.scatter(x=self.df[self.x_col], y=self.df[self.y_col], s=0)

        plt.title(self.title)
        self.axis.set_xlabel(self.x_label)
        self.axis.set_ylabel(self.y_label)
        x_min = self.df[self.x_col].min() - 0.1
        x_max = self.df[self.x_col].max() + 0.1
        y_min = self.df[self.y_col].min() - 0.1
        y_max = self.df[self.y_col].max() + 0.1
        self.axis.set_xlim(x_min, x_max)
        self.axis.set_ylim(y_min, y_max)

        if self.quadrant_labels:
            self.add_quadrant_labels()

        # Code for name labels, TODO: make use of or get rid of
        # For player scale, label each logo with the player's name
        #self.df.apply(lambda row: ax.text(row[self.x_col], row[self.y_col], row['name'].split(' ')[1],
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
            for x in np.arange(0.1, 0.9, 0.01):
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
            avg_x = self.df[self.x_col].mean()
            self.axis.axvline(avg_x, color='k', label='NHL Average')
        if self.plot_y_mean:
            avg_y = self.df[self.y_col].mean()
            self.axis.axhline(avg_y, color='k', label='NHL Average')

        # Add team logos, slightly different based on team- or player-scale
        if self.scale == 'player':
            max_icetime = self.df.icetime.max()
            self.df.apply(lambda row: add_team_logo(row, self.x_col, self.y_col, self.axis, label='name',
                                                    opacity_scale='icetime', opacity_max=max_icetime), 
                         axis=1)

        elif self.scale =='team':
            self.df.apply(lambda row: add_team_logo(row, self.x_col, self.y_col, self.axis), axis=1)

        if self.invert_y:
            self.axis.invert_yaxis()

        # Add data disclaimer
        plt.figtext(0.5, 0.01, "All data from MoneyPuck.com", ha="center", 
                    bbox={"facecolor": "cyan", "alpha" :0.5, "pad": 5})
        plt.savefig(self.filename, dpi=100)


    def add_quadrant_labels(self):
        """
        Method to add labels to each quadrant in a scatter plot. 
        Default behaviour is to add the '+/- OFFENSE/DEFENSE' labels depending on the quadrant.

        If a 2x2 list of strings is provided as 'self.quadrant_labels', then add those labels to 
        the corresponding quadrants.
        """
        offset = 0.08
        if self.quadrant_labels == 'default':
            # Top-left
            self.axis.annotate('- OFFENSE', xy=(0 + offset, 1 - offset), xycoords='axes fraction',  
                               color='red', va='bottom', ha='center', fontweight='bold')                                                 
            self.axis.annotate('+ DEFENSE', xy=(0 + offset, 1 - offset), xycoords='axes fraction',                 
                               color='green', va='top', ha='center', fontweight='bold')                                 
            # Bottom-left
            self.axis.annotate('- OFFENSE', xy=(0 + offset, 0 + offset), xycoords='axes fraction', 
                               color='red', va='bottom', ha='center', fontweight='bold')                                                 
            self.axis.annotate('- DEFENSE', xy=(0 + offset, 0 + offset), xycoords='axes fraction',                 
                               color='red', va='top', ha='center', fontweight='bold')                                     
            # Bottom-right
            self.axis.annotate('+ OFFENSE', xy=(1 - offset, 0 + offset), xycoords='axes fraction',  
                               color='green', va='bottom', ha='center', fontweight='bold')                                               
            self.axis.annotate('- DEFENSE', xy=(1 - offset, 0 + offset), xycoords='axes fraction',                 
                               color='red', va='top', ha='center', fontweight='bold')                                    
            # Top-right
            self.axis.annotate('+ OFFENSE', xy=(1 - offset, 1 - offset), xycoords='axes fraction', 
                               color='green', va='bottom', ha='center', fontweight='bold')                                               
            self.axis.annotate('+ DEFENSE', xy=(1 - offset, 1 - offset), xycoords='axes fraction',                 
                               color='green', va='top', ha='center', fontweight='bold')                                   
            return

        self.axis.annotate(self.quadrant_labels[0][0], xy=(0 + offset, 1 - offset), xycoords='axes fraction',
                           color='black', fontweight='bold', va='center', ha='center')  # Top-left
        self.axis.annotate(self.quadrant_labels[1][0], xy=(0 + offset, 0 + offset), xycoords='axes fraction',
                           color='black', fontweight='bold', va='center', ha='center')  # Bottom-left
        self.axis.annotate(self.quadrant_labels[1][1], xy=(1 - offset, 0 + offset), xycoords='axes fraction',
                           color='black', fontweight='bold', va='center', ha='center')  # Botom-right
        self.axis.annotate(self.quadrant_labels[0][1], xy=(1 - offset, 1 - offset), xycoords='axes fraction',
                           color='black', fontweight='bold', va='center', ha='center')  # Top-right
        return
