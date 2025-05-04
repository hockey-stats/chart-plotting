import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
from matplotlib.offsetbox import AnnotationBbox
import seaborn as sns
import pandas as pd
import pybaseball

from plotting.base_plots.plot import Plot, FancyAxes
from util.font_dicts import game_report_label_text_params as label_params
from util.helpers import ratio_to_color
from util.color_maps import mlb_label_colors


class SwarmPlot(Plot):
    """
    Class for swarm plots best suited for indicating distributions of a single metric, while
    highlighting players from a provided team.
    """
    def __init__(self,
                 dataframe,
                 filename,
                 column,
                 team,
                 qualifier,
                 y_label,
                 team_level_metric=None,
                 team_rank=None,
                 title='',
                 subtitle='',
                 size=(10, 8),
                 data_disclaimer='',
                 sport='baseball'):

        super().__init__(filename, title, subtitle, size, data_disclaimer, sport)

        self.df = dataframe
        self.team = team
        self.column = column
        # 'qualifier' is the value used to determine/sort if/how a player qualifies for inclusion,
        # e.g. at-bats for hitters and pitches/innings for pitchers
        self.qualifier = qualifier
        self.y_label = y_label
        self.team_level_metric = team_level_metric
        self.team_rank = team_rank
        self.fig = plt.figure(figsize=self.size)
        self.data_disclaimer = data_disclaimer
        self.axis = self.fig.add_subplot(111, axes_class=FancyAxes, ar=2.0)
        self.axis.spines[['bottom', 'left', 'right', 'top']].set_visible(False)
        # Hide the x-axis ticks and label
        self.axis.set_xticks([])
        self.axis.set_xlabel('')


    def make_plot(self):
        """
        Method to assemble the plot object.
        """

        # Basic styling
        self.set_title()
        self.axis.set_ylabel(self.y_label, fontdict=label_params)
        self.axis.tick_params(colors='antiquewhite', which='both')

        # Introduce fake categories for formatting purposes
        self.make_dummy_categorical_data()

        # Now plot every player in the full sample
        self.axis = sns.swarmplot(y=self.column, x='day', data=self.df, color='silver')

        # Add a line denoting league average
        self.draw_average_line()

        # Then plot top-12 qualified players
        team_df = self.df[self.df['team'] == self.team]
        team_df = team_df.sort_values(by=[self.qualifier], ascending=False)[0:12]

        # And re-sort by the desired metric
        team_df = team_df.sort_values(by=[self.column], ascending=False)

        team_points = sns.swarmplot(y=self.column, x='day', data=team_df,
                                    color=mlb_label_colors[self.team]["line"],
                                    zorder=9)

        # Get the xy-coords of the point for every player on the team
        # team_points.collections refers to a list of the collections of objects in
        # the axis, the last one (i.e. index -1) will be the team-specific swarm points
        team_coords = team_points.collections[-1].get_offsets()

        # Add labels for every player on team
        self.label_team_players(team_df, team_coords)

        self.save_plot()


    def label_team_players(self, team_df, team_coords):
        """
        Method that adds a logo and text box to label the point in the swarmplot for every player
        on the desired team.

        :param DataFrame team_df: DataFrame containing data for just the team in question.
        :param list((float, float)) team_coords: List of float 2-tuple for the coordinates of each
                                                 player's point in the plot.
        """
        # Define starting x- and y-pos.
        y_pos = 225
        logo_x_pos = 0.50
        wrc_x_pos = 0.62
        name_x_pos = 0.82

        # Get logo marker for team in question
        team_logo = self.get_logo_marker(self.team, sport='baseball', size='tiny')

        # Define style dicts for the label Bbox
        base_dict = {
            'size': 15,
            'weight': 600,
            'color': 'white',
            'path_effects': [PathEffects.withStroke(linewidth=1.2, foreground='black')],
            'bbox': {
                'alpha': 0.6,
                'boxstyle': 'round'
            }
        }

        for name, qual, metric, coord in zip(team_df['Name'], team_df[self.qualifier],
                                             team_df[self.column], team_coords):
            # Draw the logos
            self.axis.add_artist(AnnotationBbox(team_logo, xy=(logo_x_pos, y_pos), frameon=False,
                                                zorder=11))

            # Get the appropriate colors for the team
            line_color = mlb_label_colors[self.team]["line"]
            box_color = mlb_label_colors[self.team]["bg"]

            # Draw a line connect logo to the point in the swarmplot
            plt.plot([logo_x_pos, coord[0]], [y_pos, coord[1]], color=line_color,
                     linewidth=3, zorder=10, alpha=0.2)

            # Pad the metric value if it is only 2-digits
            if 10 < int(metric) < 100:
                metric = f" {metric} "

            # Determine the color of the metric text box based on the value
            ratio = float(metric) / 200.0 if float(metric) > 0.0 else 0.0
            metric_color = ratio_to_color(min(ratio, 1.0))
            metric_dict = base_dict
            metric_dict['bbox']['facecolor'] = metric_color

            # Draw the metric text box
            self.axis.text(x=wrc_x_pos, y=y_pos-4, s=metric,
                           **metric_dict)

            # Format name as {FirstInitial}. {LastName}, e.g. Bo Bichette -> B. Bichette
            name = f"{name.split(' ')[0][0]}. {' '.join(name.split(' ')[1:])}"

            label_dict = base_dict
            base_dict['bbox']['facecolor'] = box_color

            # Draw the text box with player info
            self.axis.text(x=name_x_pos, y=y_pos-4,
                           s=f'{name} ({qual} PAs)',
                           **label_dict)

            # Increment the y_pos
            y_pos -= 25

        if self.team_rank is not None:
            self.add_team_rank(base_dict)


    def make_dummy_categorical_data(self):
        """
        To achieve the affect of the swarmplot being on the left-hand side of the axis, create
        a dummy column called 'day' to hold a catergorical value, where all the values in our
        sample will belong to one category, and create dummy values for each of the other
        categories. When these categories are passed into the swarmplot function, each category
        will get their own 'column' in the axis, but all columns except for the first will be
        empty, creating the desired affect of all the relevant values being on the left.
        """
        self.df['day'] = 0
        dummy_rows = {
            'Team': [self.team] * 2, 
            'Name': [''] * 2, 
            'AB': [0] * 2, 
            'wRC+': [0] * 2, 
            'day': list(range(1, 3))
        }
        df = pd.DataFrame(dummy_rows)
        dummy_df = pd.concat([self.df, df]).fillna(0)

        # First plot every value, including the dummy values, but without any color.
        self.axis = sns.swarmplot(y='wRC+', x='day', data=dummy_df, color='antiquewhite')


    def draw_average_line(self, avg_value=100, league_name='MLB'):
        """
        Draws a horizontal line representing the league average value for whichever metric
        is being plotted.

        :param int avg_value: The average value of the metric, defaults to 100.
        :param str league_name: Name of the league, for label.
        """
        self.axis.axhline(y=avg_value, xmin=0.06, xmax=0.28, color='black', alpha=0.3, zorder=8)
        self.axis.text(x=0.04, y=0.45, s=f"{league_name}\nAverage", size=9, color='black',
                       transform=self.axis.transAxes, ha='center', va='center')


    def add_team_rank(self, base_dict):
        """
        Add text box for the entire team's metric value as well as their leaguewide rank.
        """
        metric_ratio = min(1.0, float(self.team_level_metric) / 200.0)
        metric_color = ratio_to_color(metric_ratio)

        base_dict['size'] = 20

        metric_dict = base_dict
        label_dict = base_dict

        x = 0.4
        y = 0.9

        label_dict['bbox']['facecolor'] = mlb_label_colors[self.team]['bg']
        self.axis.text(x, y, s=f'Team {self.column}', **label_dict,
                       transform=self.axis.transAxes)

        metric_text = str(self.team_level_metric)
        if 0 < self.team_level_metric < 100:
            metric_text = f' {metric_text} '

        metric_dict['bbox']['facecolor'] = metric_color
        self.axis.text(x + 0.27, y, s=metric_text, **metric_dict,
                       transform=self.axis.transAxes)

        rank_text = str(self.team_rank)
        a = self.team_rank % 10
        if a == 1:
            rank_text += 'st'
        elif a == 2:
            rank_text += 'nd'
        elif a == 3:
            rank_text += 'rd'
        else:
            rank_text += 'th'

        self.axis.text(x + 0.28, y - 0.05, s=f"({rank_text})", color='black', size=10,
                       transform=self.axis.transAxes)
