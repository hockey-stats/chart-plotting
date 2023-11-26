import os
import argparse
import pandas as pd

from plotting.plot import Plot


class RollingAveragePlot(Plot):
    """
    Sub-class of Plot to create rolling average line plots.
    """
    def __init__(self, dataframe, filename, x_column, y_column, title='', x_label='',
                 y__label='', ratio_lines=False, )