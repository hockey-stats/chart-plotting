import sys
import matplotlib
import matplotlib.patheffects as PathEffects
from matplotlib.animation import FuncAnimation, FFMpegWriter

from plotting.base_plots.plot import FancyAxes
from plotting.base_plots.rolling_average import RollingAveragePlot
from util.font_dicts import game_report_label_text_params as label_params
from util.font_dicts import multiplot_title_params


if sys.platform == 'win32':
    matplotlib.rcParams['animation.ffmpeg_path'] = r'C:\\Users\\sohra\\Downloads\\ffmpeg-7.1.1-essentials_build\\ffmpeg-7.1.1-essentials_build\\bin\\ffmpeg.exe'


class AnimatedRollingAveragePlot(RollingAveragePlot):
    """
    Creates a GIF version of the Rolling Average plot where each line is highlighted individually
    sequentially. 
    """
    def __init__(self,
                 filename,
                 dataframe,
                 sport='hockey',
                 data_disclaimer='moneypuck',
                 x_column='',
                 y_column='',
                 title='',
                 subtitle='',
                 x_label='',
                 y_label='',
                 y_midpoint=50,
                 size=(10, 8),
                 add_team_logos=False,
                 multiline_key='',
                 for_multiplot=True):

        super().__init__(filename=filename,
                         dataframe=dataframe,
                         title=title,
                         subtitle=subtitle,
                         size=size,
                         sport=sport,
                         data_disclaimer=data_disclaimer,
                         x_column=x_column,
                         y_column=y_column,
                         x_label=x_label,
                         y_label=y_label,
                         y_midpoint=y_midpoint,
                         add_team_logos=add_team_logos,
                         multiline_key=multiline_key,
                         for_multiplot=for_multiplot)

        self.axis = self.fig.add_subplot(111, axes_class=FancyAxes, ar=2.0)
        self.axis.spines[['bottom', 'left', 'right', 'top']].set_visible(False)
        #plt.axis('off')

    def make_plot_gif(self):
        """
        Generates each frame of the plot and saves it as a GIF.
        """

        x_min = self.df['gameNumber'].min()
        x_max = self.df['gameNumber'].max()
        x_ticks = list(range(x_min, x_max, 5))
        y_range = self.set_scaling()

        def animate(i: int):
            self.axis.clear()

            self.axis.set_xticks([], [])
            self.axis.set_xticks(x_ticks, labels=x_ticks, fontdict=label_params)
            self.axis.set_xlabel(self.x_label, fontdict=label_params)

            self.axis.set_yticks([], [])
            self.axis.set_yticks(y_range,
                                labels=[f"{y}%" for y in y_range] if self.sport == 'hockey' else y_range,
                                fontdict=label_params)
            self.axis.set_ylabel(self.y_label, fontdict=label_params)

            teams = list(set(self.df['team']))
            team = teams[i % 5]
            team_df = self.df[self.df['team'] == team]
            else_df = self.df[self.df['team'] != team]

            team_line = self.plot_multilines(alpha=1, linewidth=3, df=team_df)
            else_lines = self.plot_multilines(alpha=0.2, linewidth=1, df=else_df)
            team_logo = self.handle_team_logos(df=team_df, alpha=1)
            else_logos = self.handle_team_logos(df=else_df, alpha=0.1)

            self.add_x_axis()
            self.add_dotted_h_lines(y_values=[5, 4, 3, 2, 1, -1, -2, -3, 4, 5])

            return team_line + else_lines, team_logo, else_logos
       

        ani = FuncAnimation(self.fig, animate,
                            frames=5,
                            blit=False,
                            repeat=True)

        self.add_data_disclaimer()
        self.set_styling()
        self.set_title()
        title_params = {
            "color": "antiquewhite",
            "size": 20.0,
            "family": "sans-serif",
            "weight": 800,
            "path_effects": [PathEffects.withStroke(linewidth=4.5, foreground='black')]
        }
        self.fig.suptitle(self.title, **title_params)

        self.fig.set_facecolor('#000d1a')

        videowriter = FFMpegWriter(fps=0.5)
        ani.save('run_diff_rolling_avg.mp4', dpi=300, writer=videowriter)
