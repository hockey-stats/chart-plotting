import polars as pl
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
from matplotlib.offsetbox import AnnotationBbox
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from plotting.base_plots.plot import Plot
from util.helpers import total_toi_as_timestamp, ratio_to_color
from util.color_maps import label_colors


# Dimensions for the boxes holding the goal/xgoal values
BOX_WIDTH = 0.08
BOX_HEIGHT = 0.15
# Non-total boxes will be slightly smaller, define mult here
SMALL_BOX_MULT = 0.8
BOX_EDGE_COLOR = 'navy'

# Positional constants
LOGO_HEIGHT = 0.86
G_HEIGHT = 0.63
XG_HEIGHT = 0.45
situation_LABEL_HEIGHT = 0.30

LOGO_XPOS = 0.35
TOTAL_X_POS = 0.39
ES_X_POS = TOTAL_X_POS - (BOX_WIDTH * SMALL_BOX_MULT)
PP_X_POS = ES_X_POS - (BOX_WIDTH * SMALL_BOX_MULT)
SH_X_POS = PP_X_POS - (BOX_WIDTH * SMALL_BOX_MULT)

# Path effect gives a white outline to text, used many times
PATH_EFFECT = [PathEffects.withStroke(linewidth=2.2, foreground='w')]


class ScoreBoardPlot(Plot):
    """
    Special type of plot that is only used in game reports. Creates a scoreboard showing
    general team-level statistics for a game.
    """
    def __init__(self,
                 filename,
                 skater_df,
                 goalie_df,
                 title='',
                 size=(28, 8),
                 data_disclaimer='moneypuck'):

        super().__init__(title=title,
                         filename=filename,
                         size=size,
                         data_disclaimer=data_disclaimer)

        self.df = skater_df
        self.g_df = goalie_df
        # Set the two team names from the skater df
        self.team_a, self.team_b = set(self.df['team'])
        self.fig = plt.figure(figsize=self.size)
        self.axis = self.fig.add_subplot(111)

    def make_plot(self):
        """
        Assembles the Plot object.
        """
        # Dict that maps game situation to corresponding plot features
        situation_map = {
            "total": {"x_pos": TOTAL_X_POS},
            "ev": {"color": "blue", "x_pos": ES_X_POS, 'bbox': {}},
            "pp": {"color": "green", "x_pos": PP_X_POS, 'bbox': {}},
            "pk": {"color": "red", "x_pos": SH_X_POS, 'bbox': {}},
        }

        team_data = self.organize_team_data()

        self.draw_total_goals(situation_map, team_data)

        self.draw_goals_by_situation(situation_map, team_data)

        self.draw_icetime_distribution()

        #self.axis.set_axis_off()
        self.axis.set_yticks([])
        self.axis.set_xticks([])

        self.draw_team_logos()

        self.draw_goalie_summary()

        self.save_plot()


    def draw_total_goals(self, situation_map, team_data):
        """
        Organizer method to draw values corresponding to total goals and xgoals.
        """

        fontdict = {
            "size": 45,
            "weight": 700,
            "path_effects": PATH_EFFECT
        }

        label_fontdict = {
            "size": 45,
            "weight": 700,
            "color": "steelblue"
        }

        # Draw bounding box for all the goal/xgoal values in the scoreboard
        boundingbox_x = 0.868 * PP_X_POS
        boundingbox_y = 0.80 * XG_HEIGHT
        self.axis.add_patch(
            Rectangle(xy=(boundingbox_x, boundingbox_y),
                      width=0.545,
                      height=0.357,
                      facecolor='antiquewhite',
                      edgecolor='steelblue',
                      linewidth=4)
        )

        # "Goals" text box
        self.axis.text(0.5, G_HEIGHT, "Goals",
                       ha='center',
                       va='center',
                       **label_fontdict)


        # "xGoals" text box
        self.axis.text(0.5, XG_HEIGHT, "xGoals",
                       ha='center',
                       va='center',
                       **label_fontdict)

        total_x_pos = situation_map['total']['x_pos']

        gcolor_a, gcolor_b = self.get_ratio_colors_for_teams(team_data, 'all', 'goals')
        xgcolor_a, xgcolor_b = self.get_ratio_colors_for_teams(team_data, 'all', 'xgoals')


        for team, x_pos, g_color, xg_color in zip([self.team_a, self.team_b],
                                                  [total_x_pos, 1 - total_x_pos],
                                                  [gcolor_a, gcolor_b],
                                                  [xgcolor_a, xgcolor_b]):
            self.axis.text(x_pos, G_HEIGHT, f"  {team_data[team]['all']['goals']}  ",
                           ha='center',
                           va='center',
                           **fontdict)

            self.axis.add_patch(
                Rectangle(xy=(x_pos - 0.5*BOX_WIDTH, G_HEIGHT - 0.5*BOX_HEIGHT),
                          width=BOX_WIDTH,
                          height=BOX_HEIGHT,
                          #edgecolor=BOX_EDGE_COLOR,
                          facecolor=g_color)
            )

            self.axis.text(x_pos, XG_HEIGHT, round(team_data[team]['all']['xgoals'], 1),
                           ha='center',
                           va='center',
                           **fontdict)

            self.axis.add_patch(
                Rectangle(xy=(x_pos - 0.5*BOX_WIDTH, XG_HEIGHT - 0.5*BOX_HEIGHT),
                          width=BOX_WIDTH,
                          height=BOX_HEIGHT,
                          #edgecolor=BOX_EDGE_COLOR,
                          facecolor=xg_color, )
            )

    def organize_team_data(self):
        """
        Assemble a dict object containing details and stats for each team, namely
        goal and xgoal totals for each game situation per team as well as ToI.
        """
        team_data = {}
        for team in [self.team_a, self.team_b]:
            team_data[team] = {}
            for situation in ['all', 'ev', 'pp', 'pk']:
                skater_df = self.df.filter((pl.col('team') == team) & (pl.col('situation') == situation))
                goalie_df = self.g_df.filter((pl.col('team') == team) & (pl.col('situation') == situation))
                goals = skater_df['goals'].sum()
                xgoals = skater_df['individualxGoals'].sum()
                # Can get the total ToI of each situation by checking the goalie icetime.
                toi = goalie_df['iceTime'].sum()
                team_data[team][situation] = {
                    'goals': goals, 
                    'xgoals': xgoals, 
                    'toi': toi
                }

        return team_data


    def draw_goals_by_situation(self, situation_map, team_data):
        """
        Organizing method to draw the goal/xgoal total for each situation, for each team.
        """

        fontdict = {
            "size": 30,
            "weight": 700,
            "path_effects": PATH_EFFECT
        }

        label_fontdict = {
            "size": 30,
            "weight": 700,
            "color": "steelblue"
        }

        # Use a slightly smaller box width for the non-total values
        box_width = SMALL_BOX_MULT * BOX_WIDTH

        for situation, situation_settings in situation_map.items():
            # Gonna skip PK for now, seems low-value as the values are always very low
            if situation == 'total' or situation == 'pk':
                continue
            default_x_pos = situation_settings['x_pos']

            gcolor_a, gcolor_b = self.get_ratio_colors_for_teams(team_data, situation, 'goals')
            xgcolor_a, xgcolor_b = self.get_ratio_colors_for_teams(team_data, situation, 'xgoals')

            # One x_pos for team a and team b
            for team, x_pos, g_color, xg_color in zip([self.team_a, self.team_b],
                                                      [default_x_pos, 1 - default_x_pos],
                                                      [gcolor_a, gcolor_b],
                                                      [xgcolor_a, xgcolor_b]):
                # situation label
                text = f"{situation.upper()}"
                self.axis.text(x_pos, situation_LABEL_HEIGHT, text,
                               ha='center',
                               va='center',
                               **label_fontdict)

                # Goal value
                self.axis.text(x_pos, G_HEIGHT, team_data[team][situation]['goals'],
                               ha='center',
                               va='center',
                               **fontdict)

                self.axis.add_patch(
                    Rectangle(xy=(x_pos - 0.5*box_width, G_HEIGHT - 0.5*BOX_HEIGHT),
                              width=box_width,
                              height=BOX_HEIGHT,
                              #edgecolor=BOX_EDGE_COLOR,
                              facecolor=g_color, )
                )

                # xGoal value
                self.axis.text(x_pos, XG_HEIGHT, round(team_data[team][situation]['xgoals'], 1),
                               ha='center',
                               va='center',
                               **fontdict)

                self.axis.add_patch(
                    Rectangle(xy=(x_pos - 0.5*box_width, XG_HEIGHT - 0.5*BOX_HEIGHT),
                              width=box_width,
                              height=BOX_HEIGHT,
                              #edgecolor=BOX_EDGE_COLOR,
                              facecolor=xg_color, )
                )


    def draw_team_logos(self):
        """
        Get and draw team logos
        """
        alpha = 1
        logo_a = AnnotationBbox(self.get_logo_marker((self.team_a), alpha=alpha, size='big'),
                                xy=(LOGO_XPOS, LOGO_HEIGHT), frameon=False)

        logo_b = AnnotationBbox(self.get_logo_marker((self.team_b), alpha=alpha, size='big'),
                                xy=(1-LOGO_XPOS, LOGO_HEIGHT), frameon=False)

        self.axis.add_artist(logo_a)
        self.axis.add_artist(logo_b)

        self.save_plot()

    def draw_icetime_distribution(self):
        """
        Method to embed a pie chart in the scoreboard showing the icetime breakdown by game situation.
        """
        g = self.g_df  # Easy alias
        print(g)
        team_a, team_b = set(g['team'])
        team_a_pp_toi = g.filter((pl.col('team') == team_a) & (pl.col('situation') == 'pp'))\
            ['iceTime'].sum()
        team_b_pp_toi = g.filter((pl.col('team') == team_b) & (pl.col('situation') == 'pp'))\
            ['iceTime'].sum()

        # Start the value/label lists as only containing ES info, and only add the PP toi
        # for either team if that toi is > 0
        values = []
        labels = []

        # Check that the toi > 0 before adding to the pie chart
        for team, toi_value in zip([team_a, team_b], [team_a_pp_toi, team_b_pp_toi]):
            if toi_value == 0:
                continue
            values.append(toi_value)
            label = f"{team} PP\n{total_toi_as_timestamp(toi_value)}"
            labels.append(label)

        # Text settings for pie chart labels
        textprops = {
            'fontsize': 15,
            'weight': 'heavy',
            'color': 'white',
            'path_effects': [PathEffects.withStroke(linewidth=2, foreground='black')]
        }

        # Add the chart as an inset axis.
        inset_ax = inset_axes(self.axis, width="15%", height="45%", loc='lower right')
        inset_ax.pie(values, labels=labels, radius=1, textprops=textprops,
                     colors=[label_colors[team_a]['bg'], label_colors[team_b]['bg']],
                     labeldistance=0.3,
                     wedgeprops={"alpha": 0.5},
                     explode=(0.05,) * len(values),  # Either (0.05,) or (0.05, 0.05)
                     shadow=False)

        self.axis.text(0.99, 0.455, "Power Play Time\nDistribution", ha='right',
                       fontdict={
                           "color": "steelblue",
                           "fontsize": 20,
                           "family": "sans-serif",
                           "fontweight": 700,
                       })

    def draw_goalie_summary(self):
        """
        Draw text boxes indicating goalie goals saved above expected for each goalie in the game.
        """
        # Filtered DataFrame with just all-strength goalies stats
        g = self.g_df.filter(pl.col('situation') == 'all').sort(by='team')

        # List of goalies in the game
        goalies = list(g['name'])

        # Initial y-position for goalie text boxes
        y_pos = 0.12

        # x-pos for name and GSAX text boxes
        name_x_pos = 0.015
        gsax_x_pos = 0.15

        # Font settings
        fontsize = 20
        fontweight = 700
        va = 'center'

        # Height of summary should scale with the amount of goalies in the game
        height = 0.12 * len(goalies)

        # Draw a little box for this section
        self.axis.add_patch(
            Rectangle(xy=(0.003, y_pos-0.07), width=0.2, height=height,
                      facecolor='antiquewhite',
                      edgecolor='steelblue',
            )
        )

        # Give our little box a title
        self.axis.text(x=0.005, y=(y_pos + height) * 0.9,
                       s="Goals Saved Above\nExpected",
                       color='steelblue',
                       size=fontsize,
                       weight=fontweight)

        for goalie in goalies:
            ga = float(g.filter(pl.col('name') == goalie)['goalsAgainst'].item(0))
            xga = float(g.filter(pl.col('name') == goalie)['xGoalsAgainst'].item(0))
            gsax = round(xga - ga, 1)

            # Determine color of the GSAX text box based on how high/low the gsax value is.
            # Anything >= 2 will be cornflowerblue, <= 2 will be red, and anything in between 
            # scaled accordingly
            if gsax >= 2:
                ratio = 1
            elif gsax <= -2:
                ratio = 0
            else:
                ratio = 0.25 * gsax + 0.5
            gsax_color = ratio_to_color(ratio)

            # Want the last name only
            name = goalie.split()[-1]

            # Add spacing for positive values to align with negative
            if gsax > 0:
                gsax = f" {gsax}"

            team = str(g.filter(pl.col('name') == goalie)['team'].item(0))

            # Goalie name
            self.axis.text(name_x_pos, y_pos, name,
                           size=fontsize,
                           weight=fontweight,
                           ha='left', va=va,
                           bbox={
                               "boxstyle": "square",
                               "facecolor": label_colors[team]['bg'],
                               "alpha": 0.3
                           },
                           path_effects=PATH_EFFECT)

            # GSAX value
            self.axis.text(gsax_x_pos, y_pos, gsax,
                           size=fontsize, weight=fontweight,
                           bbox={
                               "boxstyle": "round",
                               "facecolor": gsax_color
                           },
                           ha='left', va=va,
                           path_effects=PATH_EFFECT)

            y_pos += 0.1


    def get_ratio_colors_for_teams(self, team_data, situation, value):
        """
        Given a value to compare for two teams, e.g. xgoals or goals, as well as a situation to compare 
        for determine the ratio and appropriate colors to use for representing the two values.

        :param dict team_data: Dict containing the stats for each team
        :param string situation: The situation to look for, e.g. all, ev, pp, pk
        :param string value: The value we're comparing, e.g. goals, xgoals, etc.
        """
        value_a = team_data[self.team_a][situation][value]
        value_b = team_data[self.team_b][situation][value]

        if value_a + value_b == 0:
            ratio = 0.5
        else:
            ratio = float(value_a) / (float(value_b) + float(value_a))

        color_a = ratio_to_color(ratio)
        color_b = ratio_to_color(1.0 - ratio)

        return color_a, color_b
