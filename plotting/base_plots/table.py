import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
import seaborn as sns
from blume.table import table

from plotting.base_plots.plot import Plot, FancyAxes
from util.font_dicts import game_report_label_text_params as label_params
from util.helpers import ratio_to_color


TOP_LEFT_X = 2
TOP_LEFT_Y = 4


class TablePlot(Plot):
    """
    Class used to plot tabular data into a basic table.

    Best used for displaying an array of metrics for a couple different players/teams.
    """
    def __init__(self,
                 df,
                 id_column,
                 ignore_columns,
                 filename='',
                 title='',
                 subtitle='',
                 size=(10, 5),
                 data_disclaimer='moneypuck',
                 for_game_report=False,
                 sport='hockey'):

        super().__init__(filename=filename,
                         title=title,
                         subtitle=subtitle,
                         size=size,
                         data_disclaimer=data_disclaimer,
                         for_game_report=for_game_report,
                         sport=sport)

        self.id_column = id_column
        self.ignore_columns = ignore_columns
        self.df = df

        self.fig = plt.figure(figsize=self.size)
        self.axis = self.fig.add_subplot((111), axes_class=FancyAxes)
        self.axis.spines[['bottom', 'left', 'right', 'top']].set_visible(False)
        # Hide the axis elements
        self.axis.set_xticks([])
        self.axis.set_xlabel('')
        self.axis.set_yticks([])
        self.axis.set_ylabel('')

        self.columns = [x for x in list(self.df.columns) if x not in ignore_columns]
        self.num_rows = len(self.df)
        self.font_size = 15
        self.x_offset = 0.05
        self.y_offset = 0.1
        self.top_right = (0, 0)
        self.bottom_left = (0, 0)
        self.bottom_right = (0, 0)


    def make_plot(self):

        #self.draw_table()
        self.add_chart_and_table()
        
        self.save_plot()


    def add_chart_and_table(self):
       # sns.scatterplot(self.df, x='wRC+', y='xwOBA')
        print(self.df)

        df = self.df.copy()
        df = df[df['on_team'] == False]
        names = list(df['Name'])
        del df['on_team']
        del df['Name']

        for stat in ['AVG', 'xwOBA']:
            if stat in list(df.columns):
                df[stat] = df.apply(lambda row: "%.3f" % row[stat], axis=1)

        # Each column has a width of 0.07 by default
        col_widths = [0.08] * len(df.columns)
        # Make the column for position a bit bigger
        col_widths[1] = 0.16

        table_plot = plt.table(cellText=df.values,
                               colWidths=col_widths,
                               colLabels=df.columns,
                               cellLoc='center',
                               colLoc='center',
                               colColours=['antiquewhite'] * len(df.columns),
                               rowLabels=names,
                               rowLoc='left',
                               bbox=(.24, .08, .7, .9),
                               edges='BRLT'
                               )

        table_plot.auto_set_font_size(False)
        table_plot.set_fontsize(10)
        table_plot.auto_set_column_width(col=list(range(len(df.columns))))

        # Set properties for each cell
        cells = table_plot.properties()["celld"]
        for x in range(-1, len(df.columns)):
            for y in range(0, len(df) + 1):
                if y == 0 and x == -1:
                    continue
                cells[y, x].set_edgecolor('gray')
                cells[y, x].set_linewidth(0)
                if y % 2 == 0:
                    cells[y, x].set_facecolor("antiquewhite")
                else:
                    cells[y, x].set_facecolor("powderblue")

                if y == 0 or x == -1:
                    cells[y, x].set_text_props(weight=600)
