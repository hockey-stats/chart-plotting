import matplotlib.pyplot as plt

from plot_types.plot import Plot, FancyAxes
from util.font_dicts import multiplot_title_params


class MultiPlot(Plot):
    """
    Wrapper class to take a 2D matrix of Plot objects and put them together into a multi-
    plot.
    
    self.arrangement will be a dict object which contains all the plots to be included as
    well as information on how they should be arranged. The format should look like:

    {
        "dimensions": (2, 2)  \\The raw dimensions of the multiplot
        "plots": [
            {  \\ Positioning details for each plot
                "plot": <Plot Object>,
                "y_pos": 0,
                "start": 1,
                "end": 2
            },
            ...
        ],
        \\ Height and width spacing between the plots
        "hspace": 0.1,
        "wspace": 0.1
    }
    """
    def __init__(self,
                 arrangement,
                 filename,
                 title='',
                 subtitle='',
                 figsize=(16, 14),
                 data_disclaimer='moneypuck'):
        self.arrangement = arrangement
        self.filename = filename
        self.title = title
        self.subtitle = subtitle
        self.figsize = figsize
        self.fig = plt.figure(layout='constrained', figsize=self.figsize)
        super().__init__(title=self.title,
                         subtitle=self.subtitle,
                         filename=self.filename,
                         data_disclaimer=data_disclaimer,
                         figure=self.fig)

    def make_multiplot(self):
        """
        Generate the actual multiplot.
        """

        dimensions = self.arrangement['dimensions']
        gs = self.fig.add_gridspec(dimensions[0], dimensions[1],
                                   hspace=self.arrangement.get('hspace', 0),
                                   wspace=self.arrangement.get('wspace', 0))


        for plot in self.arrangement['plots']:
            if 'start' in plot.keys():
                ax = self.fig.add_subplot(gs[plot['y_pos'], plot['start']:plot['end']],
                                          axes_class=FancyAxes)
            else:
                # If no start is provided, assume the plot spans the whole row.
                ax = self.fig.add_subplot(gs[plot['y_pos'], :],
                                          axes_class=FancyAxes)
            ax.spines[['bottom', 'left', 'right', 'top']].set_visible(False)
            plot["plot"].axis = ax
            plot["plot"].make_plot()

        self.fig.suptitle(self.title, **multiplot_title_params)
        self.save_plot()
