import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib import axes
from matplotlib import patches
from PIL import Image

from util.font_dicts import title_params, subtitle_params, multiplot_subtitle_params


class StaticColorAxisBbox(patches.FancyBboxPatch):
    """
    Class extension of FancyBboxPatch that allows us to create axes' with
    rounded corners (i.e. FancyAxes)
    """
    def set_edgecolor(self, color):
        if hasattr(self, "_original_edgecolor"):
            return
        self._original_edgecolor = color
        self._set_edgecolor(color)

    def set_linewidth(self, w=1.5):
        super().set_linewidth(w)


class FancyAxes(axes.Axes):
    """
    Class extension of axes.Axes that, when used, draws axes' with rounded corners.
    """
    name = 'fancy_box_axes'
    _edgecolor: str

    def __init__(self, *args, **kwargs):
        self._edgecolor = kwargs.pop("edgecolor", None)
        self.aspect_ratio = kwargs.pop("ar", 1.0)
        super().__init__(*args, **kwargs)

    def _gen_axes_patch(self):
        return StaticColorAxisBbox(
            (0, 0),
            1.0,
            1.0,
            boxstyle='round, rounding_size=0.06, pad=0',
            mutation_aspect=self.aspect_ratio,
            edgecolor=self._edgecolor,
            linewidth=5
        )


class Plot:
    """
    Base class to be used for all plots. Will only ever be called via super() for a base class
    """
    def __init__(self,
                 filename='',
                 title='',
                 subtitle='',
                 size=(10, 8),
                 figure=None,
                 axis=None,
                 data_disclaimer='moneypuck',
                 for_game_report=False,
                 fantasy_mode=False,
                 sport='hockey'):

        self.filename = filename
        self.title = title
        self.subtitle = subtitle
        self.size = size
        self.fig = figure
        self.axis = axis
        self.data_disclaimer = data_disclaimer
        self.for_game_report = for_game_report
        self.fantasy_mode = fantasy_mode
        self.sport = sport


    def set_title(self):
        """
        Set the title of the plot.
        """
        if self.subtitle:
            #self.title += '\n\n'
            #plt.suptitle(self.subtitle, y=0.95, **subtitle_params)
            plt.figtext(0.08, 0.92, self.subtitle, fontdict=subtitle_params)
        if self.for_game_report:
            plt.title(self.title, fontdict=multiplot_subtitle_params)
        else:
            plt.figtext(0.08, 0.95, self.title, fontdict=title_params)


    def set_styling(self):
        """
        Sets some styling options around colors, borders, etc..
        """
        #self.fig.patch.set_edgecolor('cornflowerblue')
        #self.fig.patch.set_linewidth(100)
        if self.axis:
            self.axis.set_facecolor('antiquewhite')
        self.fig.set_facecolor('steelblue')


    def add_data_disclaimer(self):
        """
        Adds a disclaimer indicating the source of the data being used in the plot.
        """
        if self.data_disclaimer is None:
            return
        if self.data_disclaimer == 'nst':
            text = "All data from NaturalStatTrick.com"
            textcolor = 'whitesmoke'
            facecolor = 'maroon'
        elif self.data_disclaimer == 'fangraphs':
            text = "All data from fangraphs.com"
            textcolor = 'black'
            facecolor = 'limegreen'
        elif self.data_disclaimer == 'baseballreference':
            text = "All data from baseballreference.com"
            textcolor = 'whitesmoke'
            facecolor = 'maroon'
        else:  # Default is moneypuck
            text = "All data from MoneyPuck.com"
            textcolor = 'black'
            facecolor = 'cyan'

        size = 20 if self.for_game_report else 10
        plt.figtext(0.995, 0.01, text, ha="right", color=textcolor, size=size,
                    bbox={"facecolor": facecolor, "alpha": 0.8, "pad": 5})


    def save_plot(self):
        """
        Performs the following before saving the plot as a PNG file:
           i. add styling (colors, frames, etc.)
          ii. adds the data disclaimer
        """

        self.set_styling()

        # Add data disclaimer
        self.add_data_disclaimer()

        # If self.filename is empty, then this is for a multiplot so don't save as a file
        if self.filename:
            plt.savefig(self.filename, dpi=100)


    def add_team_logo(self, row, x, y, label=None, opacity=1, opacity_scale=None, opacity_max=None,
                      teams_to_fade=None, size='small', label_bbox=None):
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
        :param set(str) teams_to_fade: For playoffs, set of eliminated teams to fade their logos
        :param str size: Either 'tiny', 'small', or 'big'.
        :param dict label_bbox: If given, styling options for label bbox.
        """
        if opacity_scale:
            # Gives a value between 0 and 1, so that the opacity of the icon demonstrates
            # the value on this scale (e.g., icetime)
            opacity = row[opacity_scale] / opacity_max

        if teams_to_fade:
            if row['team'] in teams_to_fade:
                opacity = 0.2

        # Assumes the team value is under row['team']
        artist_box = AnnotationBbox(self.get_logo_marker(row['team'], alpha=opacity, size=size,
                                                         sport=self.sport),
                                    xy=(row[x], row[y]), frameon=False)
        self.axis.add_artist(artist_box)

        if label:
            self.add_label_to_logo(row, x, y, label, label_bbox)

      
    def add_label_to_logo(self, row, x, y, label, label_bbox):
        """ Adds a text label to a logo in a plot, slightly under the logo

        Args:
            row (pd.Series): The row of the DataFrame passed to the logo-adding method
            x (str): The name of the column corresponding to the x-value in the data
            y (str): The name of the column corresponding to the y-value in the data
            label (str): The name of the column in the DataFrame corresponding to the label value
            label_bbox (dict[str, str]): Dict object with styling parameters for the label textbox
        """
        # Check if plot is using an inverted y-axis. If so, add label to top of logo.
        # Else, add label to the bottom.
        try:
            verticalalignment = 'top' if self.invert_y else 'bottom'
        except AttributeError:
            # AttributeError here implies that the plot doesn't have the 'invert_y' attribute,
            # i.e. it isn't a plot type that would ever invert the y-axis, so set vertical
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
            # If the last word is Jr., add the 2nd-last word as well
            if name == 'Jr.':
                name = f"{row[label].split(' ')[-2]} {name}"

        # Convert the x,y-coords of the logo from corresponding to the data to corresponding
        # to the axis space, and then place the logos slightly below them
        x_coord, y_coord = self.axis.transLimits.transform((row[x], row[y]))

        # Get the inverse of the y_coord if we're dealing with an inverted y-axis
        if verticalalignment == 'top':
            y_coord = 1 - y_coord

        # Set the offset for the logo label based on the vertical alignment of the chart,
        # with different values if it's for a game report chart
        if verticalalignment == 'top':
            if self.for_game_report:
                # This affects the label placement for the xG scatter on the game report
                y_coord -= 0.04
            else:
                y_coord -= 0.04
        else:
            y_coord -= 0.06

        self.axis.text(x_coord, y_coord,
                        name,
                        horizontalalignment='center',
                        verticalalignment=verticalalignment,
                        fontsize=10,
                        bbox=label_bbox,
                        transform=self.axis.transAxes)


    def get_logo_marker(self, team_name, alpha=1, size='small', sport='hockey'):
        """
        Quick function to return the team logo as a matplotlib marker object.

        Size can be one of 'tiny', 'big', or 'small'.
        Sport can be 'hockey' or 'baseball'.
        """
        img = Image.open(f'team_logos/{sport}/{size}/{team_name}.png')

        # The zoom value here is how we get the native resolution of the image
        # relative to the DPI of the figure
        return OffsetImage(img, alpha=alpha, zoom=72./self.fig.dpi)
