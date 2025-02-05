import matplotlib.pyplot as plt

class MultiPlot:
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
    def __init__(self, arrangement, filename, title='', figsize=(14, 14)):
        self.arrangement = arrangement
        self.filename = filename
        self.title = title
        self.figsize = figsize

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

        #fig.suptitle(self.title, size='xx-large', weight='heavy')

        #fig, axs = plt.subplots(nrows=self.plot_matrix.shape[0],
        #                        ncols=self.plot_matrix.shape[1],
        #                        figsize=self.figsize)

        #for x in range(0, self.plot_matrix.shape[0]):
        #    for y in range(0, self.plot_matrix.shape[1]):
        #        print(x, y)
        #        self.plot_matrix[x][y].fig = fig
        #        if self.plot_matrix.shape[0] == 1:
        #            self.plot_matrix[x][y].axis = axs[y]
        #        else:
        #            self.plot_matrix[x][y].axis = axs[x, y]
        #        self.plot_matrix[x][y].make_plot()

        fig.suptitle(self.title, size='xx-large', weight='heavy')
        plt.savefig(self.filename)

