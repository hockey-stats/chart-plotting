import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
import matplotlib.transforms as transforms
from matplotlib.offsetbox import AnnotationBbox
from matplotlib.patches import Rectangle
import seaborn as sns
import pandas as pd

from plotting.base_plots.plot import Plot, FancyAxes
from util.font_dicts import game_report_label_text_params as label_params
from util.helpers import ratio_to_color
from util.color_maps import mlb_label_colors

PRIMARY_COLOR = '#cccccc'
SECONDARY_COLOR = '#999999'

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
                 table_columns=None,
                 team_level_metric=None,
                 team_rank=None,
                 category_column=None,
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
        # List of columns to be included in the companion table to the plot
        self.table_columns = table_columns
        # If not None, category_column will refer to a boolean column which denotes whether a row
        # member belongs to a certain category or not, for coloring the swarms differently.
        # E.g.,  is_starter for the pitcher stuff+ plot.
        self.category_column = category_column
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

        if self.column == 'WAR':
            self.axis.set_yticks(list(range(-1, 6, 1)))
            self.axis.set_ylim(bottom=-2, top=6)

        if self.column == 'Stuff+':
            self.axis.set_yticks(list(range(80, 120, 10)))
            self.axis.set_ylim(bottom=70, top=140)

        # Add huge logo as background piece
        team_logo = self.get_logo_marker(self.team, sport='baseball', size='huge', alpha=0.2)
        self.axis.add_artist(AnnotationBbox(team_logo, xy=(1, 0.5),
                                            frameon=False,
                                            box_alignment=(1, 0.5),
                                            xycoords='axes fraction', zorder=-11))

        # Now plot every player in the full sample
        self.axis = sns.swarmplot(y=self.column, x='day', data=self.df, color=PRIMARY_COLOR,
                                  size=4.5)

        # If dealing with a second category of points, call a seperate method to handle
        # the bulk of the plotting.
        if self.category_column:
            self.plot_categorically()
            self.save_plot()
            return

        # Add a line denoting league average
        self.draw_average_line()

        # Then plot top-12 qualified players
        team_df = self.df[self.df['team'] == self.team]
        #team_df = team_df.sort_values(by=[self.column], ascending=False)[0:12]
        team_df = team_df.sort_values(by=[self.qualifier], ascending=False)[0:12]

        # And re-sort by the desired metric
        team_df = team_df.sort_values(by=[self.column], ascending=False)

        team_points = sns.swarmplot(y=self.column, x='day', data=team_df,
                                    color='steelblue',
                                    zorder=9)

        # Get the xy-coords of the point for every player on the team
        # team_points.collections refers to a list of the collections of objects in
        # the axis, the last one (i.e. index -1) will be the team-specific swarm points
        team_coords = team_points.collections[-1].get_offsets()

        # Add labels for every player on team
        self.label_team_players(team_df, team_coords)

       # if self.table_columns is not None:
       #     self.add_table(team_df)

        self.save_plot()


    def plot_categorically(self) -> None:
        """
        Method used to generate the plot when dealing with an additional category for the players
        in the dataset that want to be marked differently, e.g. starters and relievers.

        Players in the alternate category have a different color by default in the swarm plot and
        their labels will be presented separately.
        """
        # df_a will contain every player in the sample set for which the category column is True
        df_a = self.df[self.df[self.category_column]]\
                    .sort_values(by=[self.column], ascending=False).reset_index()

        # df_b will be the same but where the category column is False
        df_b = self.df[~(self.df[self.category_column])]\
                    .sort_values(by=[self.column], ascending=False).reset_index()

        # Add columns for rank within their cohort
        df_a['rank'] = df_a.apply(lambda row: row.name, axis=1)
        df_b['rank'] = df_b.apply(lambda row: row.name, axis=1)

        # Add all players in league from df_a to swarm plot with slightly different color
        self.axis = sns.swarmplot(y=self.column, x='day', data=df_a, color=SECONDARY_COLOR,
                                  size=4.5)

        # Add two lines denoting the averages for each category
        self.draw_average_line(label='Starter\nAverage', avg_value=df_a[self.column].mean())
        self.draw_average_line(label='Reliever\nAverage', avg_value=df_b[self.column].mean())

        combined_dfs = []

        for i, df in enumerate([df_a, df_b]):
            # Show 5 players for the first category, 7 for the second
            num_players = 5 + (i * 2)

            # Filter df_a and df_b to only contain players from our team
            team_df = df[df['team'] == self.team]\
                           .sort_values(by=[self.qualifier], ascending=False)[0:num_players]

            # Then re-sort by metric
            team_df = team_df.sort_values(by=[self.column], ascending=False)

            # And add to plot
            team_points = sns.swarmplot(y=self.column, x='day', data=team_df,
                                        color='steelblue',
                                        #color=mlb_label_colors[self.team]['line'],
                                        zorder=9)
            team_coords = team_points.collections[-1].get_offsets()

            # Then add labels
            self.label_team_players(team_df, team_coords, vert_offset=0.3*i)

            # And save to list for creating combined table
            combined_dfs.append(team_df)

        # Add labels for starters and relievers in table
        pos_label_params = label_params.copy()
        pos_label_params['fontsize'] = 13
        line_a = plt.plot([1.02, 1.02], [0.77, 0.48], color='white', linewidth=2,
                          solid_capstyle='butt',
                          transform=self.axis.transAxes)
        line_a_start = plt.plot([1.016, 1.024], [0.77, 0.77], color='white', linewidth=2,
                                transform=self.axis.transAxes)
        line_a_end = plt.plot([1.016, 1.024], [0.48, 0.48], color='white', linewidth=2,
                                transform=self.axis.transAxes)
        label_a = self.axis.text(1.03, 0.55, s='Starters',
                                 transform=self.axis.transAxes,
                                 rotation=270,
                                 **pos_label_params)

        line_b = plt.plot([1.02, 1.02], [0.46, 0.07], color='white', linewidth=2,
                          solid_capstyle='butt',
                          transform=self.axis.transAxes)
        line_b_start = plt.plot([1.016, 1.024], [0.46, 0.46], color='white', linewidth=2,
                                transform=self.axis.transAxes)
        line_b_end = plt.plot([1.016, 1.024], [0.07, 0.07], color='white', linewidth=2,
                                transform=self.axis.transAxes)
        label_b = self.axis.text(1.03, 0.2, s='Relievers',
                                 transform=self.axis.transAxes,
                                 rotation=270,
                                 **pos_label_params)

        for thing in [line_a[0], line_a_start[0], line_a_end[0], label_a,
                      line_b[0], line_b_start[0], line_b_end[0] ,label_b]:
            thing.set_clip_on(False)

        if self.table_columns is not None:
            team_df = pd.concat(combined_dfs)
            self.add_table(team_df)

        # Add legend for different categories
        legend_x = 0.03
        legend_y = 0.94

        self.axis.add_patch(
            Rectangle(xy=(legend_x-0.01, legend_y-0.05),
                      height=0.07,
                      width=0.13,
                      edgecolor='steelblue',
                      facecolor='antiquewhite',
                      transform=self.axis.transAxes)
        )

        self.axis.plot([legend_x], [legend_y], color=SECONDARY_COLOR,
                       marker='o', markersize=4.5,
                       transform=self.axis.transAxes)
        self.axis.text(legend_x + 0.02, legend_y, s='Starters',
                       va='center', color='steelblue', weight='bold',
                       transform=self.axis.transAxes)
        self.axis.plot([legend_x], [legend_y-0.03], color=PRIMARY_COLOR,
                       marker='o', markersize=4.5,
                       transform=self.axis.transAxes)
        self.axis.text(legend_x + 0.02, legend_y-0.03, s='Relievers',
                       va='center', color='steelblue', weight='bold',
                       transform=self.axis.transAxes)

    def label_team_players(self, team_df, team_coords, vert_offset=0):
        """
        Method that adds a logo and text box to label the point in the swarmplot for every player
        on the desired team.

        :param DataFrame team_df: DataFrame containing data for just the team in question.
        :param list((float, float)) team_coords: List of float 2-tuple for the coordinates of each
                                                 player's point in the plot.
        :param float vert_offset: How much to vertically offset the start of the labels. Used mostly
                                  in categorical mode.
        """
        # Define starting x- and y-pos.
        y_pos = 0.73 - vert_offset
        logo_x_pos = 3

        # Get logo marker for team in question
        #team_logo = self.get_logo_marker(self.team, sport='baseball', size='tiny')

        # Define style dicts for the label and metric Bbox
        metric_dict = {
            'size': 14,
            'weight': 600,
            'color': 'antiquewhite',
            'path_effects': [PathEffects.withStroke(linewidth=1.3, foreground='black')],
            'bbox': {
                'alpha': 1,
                'boxstyle': 'round'
            }
        }
        label_dict = {
            'size': 14,
            'weight': 600,
            'color': 'antiquewhite',
            'path_effects': [PathEffects.withStroke(linewidth=1.2, foreground='black')],
            'bbox': {
                'alpha': 0.85,
                'color': 'steelblue',
                'boxstyle': 'round'
            }
        }

        for name, metric, coord in zip(team_df['Name'], team_df[self.column], team_coords):

            # Our logo x-/y-pos are in Axes coordinates, we want them in data coordinates
            # to be able to draw the line connecting them to the points in the swarm plot
            axis_to_data = self.axis.transAxes + self.axis.transData.inverted()
            x, y = axis_to_data.transform((logo_x_pos, y_pos))

            # Not exactly sure why the x-coordinate gets inverted in the transformation process,
            # but it does
            x = -1 * x

            # Offset value to place the player label, may differ based on metric value
            x_offset = 1.55

            # Draw a line connecting the metric value to the point in the swarmplot
            #print(coord)
            plt.plot([x, coord[0]], [y, coord[1]], color='steelblue',
                     linewidth=2, zorder=10, alpha=0.7)

            # Additional formatting conditions for wRC+/Stuff+ etc.
            if '+' in self.column:
                # Pad the metric value if it is only 2-digits
                if 9 < int(metric) < 100:
                    metric = f" {metric} "

            # Additional formatting conditions for WAR
            if self.column == 'WAR':
                if len(str(metric)) < 4:
                    metric = f" {metric}"
                x_offset = 1.6

            # Determine the color of the metric text box based on the value
            if self.category_column:
                category_value = list(team_df[self.category_column])[0]
                max_rank = float(len(self.df[self.df[self.category_column] == category_value]))
                rank = list(team_df[team_df['Name'] == name]['rank'])[0]
                ratio = 1.0 - (float(rank) / float(max_rank))
            else:
                ratio = float(metric) / 200.0 if float(metric) > 0.0 else 0.0
            metric_color = ratio_to_color(min(ratio, 1.0))
            metric_dict['bbox']['color'] = metric_color

            # Draw the metric text box
            self.axis.text(x=x*1.05, y=y, s=metric,
                           transform=self.axis.transData,
                           **metric_dict)

            # Format name as {FirstInitial}. {LastName}, e.g. Bo Bichette -> B. Bichette
            #name = f"{name.split(' ')[0][0]}. {' '.join(name.split(' ')[1:])}"
            name = f"{' '.join(name.split(' ')[1:])}"

            # Draw the text box with player info
            self.axis.text(x=x*x_offset, y=y, s=f'{name}',
                           transform=self.axis.transData,
                           **label_dict)

            # Increment the y_pos
            y_pos -= 0.06

        if self.team_rank is not None:
            self.add_team_rank(label_dict, metric_dict)



    def make_dummy_categorical_data(self):
        """
        To achieve the affect of the swarmplot being on the left-hand side of the axis, create
        a dummy column called 'day' to hold a categorical value, where all the values in our
        sample will belong to one category, and create dummy values for each of the other
        categories. When these categories are passed into the swarmplot function, each category
        will get their own 'column' in the axis, but all columns except for the first will be
        empty, creating the desired affect of all the relevant values being on the left, and the
        plot being empty otherwise.
        """
        self.df['day'] = 0
        dummy_rows = {
            'Team': [self.team] * 2, 
            'Name': [''] * 2, 
            self.qualifier: [0] * 2,
            self.column: [0] * 2,
            'day': list(range(1, 3))
        }
        df = pd.DataFrame(dummy_rows)
        dummy_df = pd.concat([self.df, df]).fillna(0)

        # First plot every value, including the dummy values, but without any color.
        self.axis = sns.swarmplot(y=self.column, x='day', data=dummy_df, color='antiquewhite')


    def draw_average_line(self, league_name='MLB', label=None, avg_value=None):
        """
        Draws a horizontal line representing the league average value for whichever metric
        is being plotted.

        :param str league_name: Name of the league, for label.
        :param str label: Label to add to the line.
        :param int avg_value: The y-value to plot the line at.
        """
        if avg_value is None:
            if '+' in self.column:  # e.g. wRC+ or Stuff+
                avg_value = 100

            else:
                avg_value = self.df[self.column].mean()

        self.axis.axhline(y=avg_value, xmin=0.02, xmax=0.25, color='steelblue', alpha=1, zorder=8)

        if label is None:
            label = f"{league_name}\nAverage"

        # Create custom transform to have x-coordinates correspond to the Axes and y-coordinates
        # correspond to the data
        trans = transforms.blended_transform_factory(self.axis.transAxes, self.axis.transData)
        self.axis.text(x=0.04, y=avg_value*0.98, s=label, size=9, color='steelblue',
                       weight='bold',
                       transform=trans, ha='center', va='top')


    def add_team_rank(self, label_dict, metric_dict):
        """
        Adds text boxes displaying the entire team's rank in the metric.

        :param dict label_dict: Config info for the labels text box.
        :param dict metric_dict: Config info for the metrics text box.
        """

        #metric_ratio = min(1.0, float(self.team_level_metric) / 200.0)
        metric_ratio = 1 - (float(self.team_rank) / 30.0)
        metric_color = ratio_to_color(metric_ratio)

        # Increase text size
        label_dict['size'] = 20
        metric_dict['size'] = 20

        x = 0.4
        y = 0.94

        self.axis.text(x, y, s=f'Team {self.column}', **label_dict,
                       transform=self.axis.transAxes)

        metric_text = str(self.team_level_metric)
        if 0 < self.team_level_metric < 100:
            metric_text = f' {metric_text} '

        metric_dict['bbox']['color'] = metric_color
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


    def add_table(self, team_df: pd.DataFrame) -> None:
        """
        Adds a table to the right of the swarm plot showing some basic hitting metrics

        :param pd.DataFrame team_df: DataFrame containing stats for players on the team.
        """
        # Work with a copy of the DataFrame to avoid silly issues
        df = team_df.copy()

        # Format some columns with specific decimal place points
        for col in ['AB', 'HR', 'PA']:
            try:
                df[f'{col}s'] = df.apply(lambda row: "%.0f" % row[col], axis=1)
            except KeyError:
                continue

        for col in ['K-BB%', 'WAR']:
            try:
                df[f'{col}'] = df.apply(lambda row: "%.1f" % row[col], axis=1)
            except KeyError:
                continue

        for col in ['ERA', 'xERA']:
            try:
                df[f'{col}'] = df.apply(lambda row: "%.2f" % row[col], axis=1)
            except KeyError:
                continue

        for col in ['AVG', 'OPS']:
            try:
                df[col] = df.apply(lambda row: "%.3f" % row[col], axis=1)
            except KeyError:
                continue

        # Isolate only the columns we want, in the order we want
        df = df[self.table_columns]

        table = plt.table(cellText=df.values,
                          colLabels=df.columns,
                          cellLoc='center',
                          colLoc='center',
                          rowLoc='left',
                          bbox=(0.65, 0.05, 0.35, 0.785),
                          edges='B'
                          )

        table.set_fontsize(12)

        # Apply some specific formatting to the cells
        cells = table.properties()['celld']
        for x in range(0, len(df.columns)):
            for y in range(0, len(df) + 1):
                # Set the edge color and width between rows
                cells[y, x].set_edgecolor('steelblue')
                cells[y, x].set_linewidth(2)

                # Don't draw an edge under the last row
                if y == len(df):
                    cells[y, x].set_linewidth(0)

                # Column headers are bolded, other values less so
                if y == 0:
                    cells[y, x].set_text_props(weight=900)
                else:
                    cells[y, x].set_text_props(weight=600)

                cells[y, x].set_text_props(color='steelblue',
                                           path_effects=[PathEffects.withStroke(linewidth=0.2,
                                                                                foreground='antiquewhite')])