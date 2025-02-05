from plotting.base_plots.plot import Plot


class PiePlot(Plot):
    """
    Plot subclass for basic pie charts.
    `values` and `labels` will be lists of equal size, with each item in
    `values` having its corresponding label in `labels.
    """
    def __init__(self,
                 filename,
                 values,
                 labels,
                 radius=1):
        super().__init__(filename)

        self.values = values
        self.labels = labels
        self.radius = radius

    def make_plot(self):
        """
        Draw the pie chart.
        """
        self.axis.pie(self.values, labels=self.labels, radius=self.radius)
