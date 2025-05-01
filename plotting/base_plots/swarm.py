import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
from matplotlib.offsetbox import AnnotationBbox
import seaborn as sns
import pandas as pd

from plotting.base_plots.plot import Plot, FancyAxes
from util.font_dicts import game_report_label_text_params as label_params


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
                 y_label,
                 title='',
                 subtitle='',
                 size=(10, 8),
                 data_disclaimer='',
                 sport='baseball'):

        super().__init__(filename, title, subtitle, size, data_disclaimer, sport)

        self.df = dataframe
        self.team = team
        self.column = column
        self.y_label = y_label
        self.fig = plt.figure(figsize=self.size)
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

        # Now plot every batter in the full sample
        self.axis = sns.swarmplot(y='wRC+', x='day', data=self.df, color='silver')

        # Then plot top-12 hitters (by # of PAs) of specific team
        team_df = self.df[self.df['team'] == self.team]
        team_df = team_df.sort_values(by=['AB'], ascending=False)[0:12]
        team_df = team_df.sort_values(by=['wRC+'], ascending=False)
        team_points = sns.swarmplot(y='wRC+', x='day', data=team_df, color='blue')

        # Get the xy-coords of the point for every player on the team
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
        x_pos = 0.55
        y_pos = 225

        # Get logo marker for team in question
        team_logo = self.get_logo_marker(self.team, sport='baseball')

        # Define style dicts for the label Bbox
        label_dict = {
            'size': 15,
            'weight': 600,
            'color': 'white',
            'path_effects': [PathEffects.withStroke(linewidth=1.2, foreground='black')],
            'bbox': {
                'facecolor': 'blue',
                'alpha': 0.6,
                'boxstyle': 'round'
            }
        }

        for name, ab, wrc, coord in zip(team_df['Name'], team_df['AB'], team_df['wRC+'],
                                        team_coords):
            # Draw the logos
            self.axis.add_artist(AnnotationBbox(team_logo, xy=(x_pos, y_pos), frameon=False,
                                                zorder=11))

            # Draw a line connect logo to the point in the swarmplot
            plt.plot([x_pos, coord[0]], [y_pos, coord[1]], color='blue', zorder=10, alpha=0.2)

            # Pad the wRC+ value if it is only 2-digits
            if 10 < int(wrc) < 100:
                wrc = f" {wrc} "

            # Draw the wRC+ text box
            self.axis.text(x=x_pos*1.2, y=y_pos-4, s=wrc,
                           **label_dict)

            # Format name as {FirstInitial}. {LastName}, e.g. Bo Bichette -> B. Bichette
            name = f"{name.split(' ')[0][0]}. {' '.join(name.split(' ')[1:])}"

            # Draw the text box with player info
            self.axis.text(x=x_pos*1.55, y=y_pos-4,
                           s=f'{name} ({ab} PAs)',
                           **label_dict)

            # Increment the y_pos
            y_pos -= 25


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
