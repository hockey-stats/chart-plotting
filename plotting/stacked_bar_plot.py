"""
Sub-class of Plot for creating stacked bar plots.
"""

import pandas as pd
import matplotlib.pyplot as plt

from plotting.plot import Plot

class StackedBarPlot(Plot):
    def __init__(self, dataframe, filename, x_column, y_column, title='', )