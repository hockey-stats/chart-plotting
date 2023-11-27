import matplotlib.pyplot as plt
from numpy import array
import pandas as pd
from plotting.rolling_average_plot import RollingAveragePlot

class MultiPlot:
    """
    Wrapper class to take a 2D matrix of Plot objects and put them together into a multi-
    plot.
    """
    def __init__(self, plot_matrix, filename, title='', figsize=(14, 14)):
        self.plot_matrix = plot_matrix
        self.filename = filename
        self.title = title
        self.figsize = figsize
    
    def make_multiplot(self):
        """
        Generate the actual multiplot.
        """
        fig, axs = plt.subplots(nrows=self.plot_matrix.shape[0],
                                ncols=self.plot_matrix.shape[1],
                                figsize=self.figsize)
        
        for x in range(0, self.plot_matrix.shape[0]):
            for y in range(0, self.plot_matrix.shape[1]):
                self.plot_matrix[x][y].fig = fig
                self.plot_matrix[x][y].axis = axs[x, y]
                self.plot_matrix[x][y].make_plot()

        fig.suptitle(self.title, size='xx-large', weight='heavy')
        plt.savefig(self.filename)
