import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
from matplotlib.offsetbox import AnnotationBbox
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter

from plotting.base_plots.plot import FancyAxes
from plotting.base_plots.rolling_average import RollingAveragePlot
from util.color_maps import label_colors, mlb_label_colors
from util.font_dicts import game_report_label_text_params as label_params


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

    def make_plot_gif(self):
        """
        Generates each frame of the plot and saves it as a GIF.
        """

        def animate(i: int):
            self.axis.clear()
            print(i)
            teams = list(set(self.df['team']))
            team = teams[i % 5]
            team_df = self.df[self.df['team'] == team]
            else_df = self.df[self.df['team'] != team]
            team_line = self.plot_multilines(alpha=1, linewidth=3, df=team_df)
            else_lines = self.plot_multilines(alpha=0.2, linewidth=1, df=else_df)
            logos = self.handle_team_logos()
            return team_line + else_lines, logos
        

        

        ani = FuncAnimation(self.fig, animate,
                            #frames=len(set(self.df['team'])),
                            frames=30,
                            #interval=20,
                            blit=False,
                            repeat=True,
                            save_count=1500)

        self.add_data_disclaimer()
        x_min = self.df['gameNumber'].min()
        x_max = self.df['gameNumber'].max()
        x_ticks = list(range(x_min, x_max, 5))
        self.axis.set_xticks(x_ticks, labels=x_ticks, fontdict=label_params)
        y_range = self.set_scaling()
        self.axis.set_yticks(y_range,
                            labels=[f"{y}%" for y in y_range] if self.sport == 'hockey' else y_range,
                            fontdict=label_params)
        self.set_styling()
        
        videowriter = FFMpegWriter(fps=1)
        ani.save('test.mp4', dpi=300, writer=videowriter)
        

            


