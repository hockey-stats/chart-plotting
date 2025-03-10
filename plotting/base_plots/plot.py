import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image


class Plot:
    """
    Base class to be used for all plots. Will only ever be called via super() for a base class
    """
    def __init__(self,
                 filename='',
                 title='',
                 size=(10, 8),
                 figure=None,
                 axis=None,
                 data_disclaimer='moneypuck'):

        self.filename = filename
        self.title = title
        self.size = size
        self.fig = figure
        self.axis = axis
        self.data_disclaimer = data_disclaimer


    def save_plot(self):
        """
        Adds the plot title, the data disclaimer, and saves the plot to a PNG file.
        """
        # Add title
        #plt.title(self.title)

        # Add data disclaimer
        if self.data_disclaimer is not None:
            if self.data_disclaimer == 'nst':
                text = "All data from NaturalStatTrick.com"
                textcolor = 'whitesmoke'
                facecolor = 'maroon'
            else:  # Default is moneypuck
                text = "All data from MoneyPuck.com"
                textcolor = 'black'
                facecolor = 'cyan'
            plt.figtext(0.5, 0.01, text, ha="center", color=textcolor,
                        bbox={"facecolor": facecolor, "alpha": 0.8, "pad": 5})

        #if self.fig:
            #self.fig.suptitle(self.title, size='xx-large', weight='heavy', stretch='expanded')
        # If self.filename is empty, then this is for a multiplot so don't save as a file
        if self.filename:
            plt.savefig(self.filename, dpi=100)


    def add_team_logo(self, row, x, y, label=None, opacity=1, opacity_scale=None, opacity_max=None,
                      size='small'):
        """
        Function used with DataFrame.map() that adds a team logo to an axis object.
        :param pandas.Series row: Row of the dataframe being applied on
        :param str x: Row entry to be used for x-coordinate
        :param str y: Row entry to be used for y-coordinate
        :param matplotlib.pyplot.Axis: Axis object the icon is being added to
        :param str label: Row entry to be used as a label. If not supplied, don't label
        :param int opacity: Default opacity if scaling isn't used, default value is 1.
        :param str opacity_scale: Row entry used to scale opacity, if desired
        :param int opacity_max: Max value to compare against for opacity scale
        :param int zoom: Zoom level on image. Defaults to 1.
        :param str size: Either 'tiny', 'small', or 'big'.
        """
        if opacity_scale:
            # Gives a value between 0 and 1, so that the opacity of the icon demonstrates
            # the value on this scale (e.g., icetime)
            opacity = row[opacity_scale] / opacity_max

        # Assumes the team value is under row['team']
        artist_box = AnnotationBbox(self.get_logo_marker(row['team'], alpha=opacity, size=size),
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
            # Split the label entry by ' ' and use last entry. Makes no difference for one-word
            # labels, but for names uses last name only.
            # If data is from naturalstattrick, the encoding they use has `\xa0` as a whitespace
            # instead of a regular space, so check for that as well.
            if '\xa0' in row[label]:
                name = row[label].split('\xa0')[-1]
            else:
                name = row[label].split(' ')[-1]
            self.axis.text(row[x], row[y] + 0.06, name,
                           horizontalalignment='center',
                           verticalalignment=verticalalignment,
                           fontsize=10)

    def get_logo_marker(self, team_name, alpha=1, size='small'):
        """
        Quick function to return the team logo as a matplotlib marker object.

        Size can be one of 'tiny', 'big', or 'small'.
        """
        img = Image.open(f'team_logos/{size}/{team_name}.png')

        #return OffsetImage(plt.imread(f'team_logos/{team_name}.png'), alpha=1, zoom=72./self.fig.dpi)
        return OffsetImage(img, alpha=alpha, zoom=72./self.fig.dpi)