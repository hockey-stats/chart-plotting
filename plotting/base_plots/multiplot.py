import matplotlib.pyplot as plt

from plotting.base_plots.plot import Plot

class MultiPlot(Plot):
    """
    Wrapper class to take a 2D matrix of Plot objects and put them together into a multi-
    plot.
    
    self.arrangement will be a dict object which contains all the plots to be included as
    well as information on how they should be arranged. The format should look like:

    {
        "dimensions": (2, 2)  \\The raw dimensions of the multiplot
        "plots": [
            {
                "plot": <Plot Object>,
                "position": (0, 0),
                "colspan": 1,
                "rowspan": 2
            },
            ...
        ]
    }
    """
    def __init__(self, arrangement, filename, title='', figsize=(14, 14), data_disclaimer='moneypuck'):
        self.arrangement = arrangement
        self.filename = filename
        self.title = title
        self.figsize = figsize
        super().__init__(title=self.title,
                         filename=self.filename,
                         data_disclaimer=data_disclaimer)

    def make_multiplot(self):
        """
        Generate the actual multiplot.
        """
        fig = plt.figure(layout='constrained', figsize=self.figsize)
        dimensions = self.arrangement['dimensions']
        for plot in self.arrangement['plots']:
            ax = plt.subplot2grid(dimensions,
                                  plot["position"],
                                  colspan=plot.get("colspan", 1),
                                  rowspan=plot.get("rowspan", 1))
            plot["plot"].axis = ax
            plot["plot"].make_plot()

        fig.suptitle(self.title, size='xx-large', weight='heavy', stretch='expanded')
        self.save_plot()
