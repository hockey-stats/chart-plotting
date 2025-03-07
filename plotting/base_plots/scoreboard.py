import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
from matplotlib.offsetbox import AnnotationBbox
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from plotting.base_plots.plot import Plot
from util.helpers import total_toi_as_timestamp, ratio_to_color
from util.color_maps import label_colors


G_HEIGHT = 0.73
XG_HEIGHT = 0.61
STATE_LABEL_HEIGHT = 0.51

TOTAL_X_POS = 0.40
ES_X_POS = 0.33
PP_X_POS = 0.28
SH_X_POS = 0.19
LOGO_XPOS = 0.35

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
        # Dict that maps game state to corresponding plot features
        state_map = {
            "total": {"x_pos": TOTAL_X_POS},
            "ev": {"color": "blue", "x_pos": ES_X_POS, 'bbox': {}},
            "pp": {"color": "green", "x_pos": PP_X_POS, 'bbox': {}},
            "pk": {"color": "red", "x_pos": SH_X_POS, 'bbox': {}},
        }

        team_data = self.organize_team_data()

        self.draw_total_goals(state_map, team_data)

        self.draw_goals_by_state(state_map, team_data)

        self.draw_icetime_distribution()

        self.axis.set_axis_off()

        self.draw_team_logos()

        self.draw_goalie_summary()

        self.save_plot()


    def draw_total_goals(self, state_map, team_data):
        """
        Organizer method to draw values corresponding to total goals and xgoals.
        """
        fontsize = 25
        fontweight = 700
        # "Goals" text box
        self.axis.text(0.5, G_HEIGHT, "Goals",
                       size=fontsize,
                       weight=fontweight,
                       ha='center',
                       va='center',
                       path_effects=PATH_EFFECT)

        # "xGoals" text box
        self.axis.text(0.5, XG_HEIGHT, "xGoals",
                       size=fontsize,
                       weight=fontweight,
                       ha='center',
                       va='center',
                       path_effects=PATH_EFFECT)

        total_x_pos = state_map['total']['x_pos']

        gcolor_a, gcolor_b = self.get_ratio_colors_for_teams(team_data, 'all', 'goals')
        xgcolor_a, xgcolor_b = self.get_ratio_colors_for_teams(team_data, 'all', 'xgoals')

        for team, x_pos, g_color, xg_color in zip([self.team_a, self.team_b],
                                                  [total_x_pos, 1 - total_x_pos],
                                                  [gcolor_a, gcolor_b],
                                                  [xgcolor_a, xgcolor_b]):
            self.axis.text(x_pos, G_HEIGHT, team_data[team]['all']['goals'],
                           size=fontsize,
                           weight=fontweight,
                           ha='center',
                           va='center',
                           bbox={
                             "boxstyle": "round",
                             "facecolor": g_color
                           },
                           path_effects=PATH_EFFECT)

            self.axis.text(x_pos, XG_HEIGHT, round(team_data[team]['all']['xgoals'], 1),
                           size=fontsize,
                           weight=fontweight,
                           ha='center',
                           va='center',
                           bbox={
                             "boxstyle": "round",
                             "facecolor": xg_color
                           },
                           path_effects=PATH_EFFECT)


    def organize_team_data(self):
        """
        Assemble a dict object containing details and stats for each team, namely
        goal and xgoal totals for each game state per team as well as ToI.
        """
        team_data = {}
        for team in [self.team_a, self.team_b]:
            team_data[team] = {}
            for state in ['all', 'ev', 'pp', 'pk']:
                skater_df = self.df[(self.df['team'] == team) & (self.df['state'] == state)]
                goalie_df = self.g_df[(self.g_df['team'] == team) & (self.g_df['state'] == state)]
                goals = skater_df['goals'].sum()
                xgoals = skater_df['ixG'].sum()
                # Can get the total ToI of each state by checking the goalie icetime.
                toi = goalie_df['icetime'].sum()
                team_data[team][state] = {
                    'goals': goals, 
                    'xgoals': xgoals, 
                    'toi': toi
                }

        return team_data


    def draw_goals_by_state(self, state_map, team_data):
        """
        Organizing method to draw the goal/xgoal total for each state, for each team.
        """
        for state, state_settings in state_map.items():
            # Gonna skip PK for now, seems low-value as the values are always very low
            if state == 'total' or state == 'pk':
                continue
            default_x_pos = state_settings['x_pos']

            fontsize = 20
            fontweight = 700

            gcolor_a, gcolor_b = self.get_ratio_colors_for_teams(team_data, state, 'goals')
            xgcolor_a, xgcolor_b = self.get_ratio_colors_for_teams(team_data, state, 'xgoals')

            # One x_pos for team a and team b
            for team, x_pos, g_color, xg_color in zip([self.team_a, self.team_b],
                                                      [default_x_pos, 1 - default_x_pos],
                                                      [gcolor_a, gcolor_b],
                                                      [xgcolor_a, xgcolor_b]):
                # State label
                text = f"{state.upper()}"
                self.axis.text(x_pos, STATE_LABEL_HEIGHT, text,
                               size=fontsize,
                               weight=fontweight,
                               ha='center',
                               va='center',
                               path_effects=PATH_EFFECT)

                # Goal value
                self.axis.text(x_pos, G_HEIGHT, team_data[team][state]['goals'],
                               size=fontsize,
                               weight=fontweight,
                               bbox={
                                   "boxstyle": "round",
                                   "facecolor": g_color
                               },
                               ha='center',
                               va='center',
                               path_effects=PATH_EFFECT)

                # xGoal value
                self.axis.text(x_pos, XG_HEIGHT, round(team_data[team][state]['xgoals'], 1),
                               size=fontsize,
                               weight=fontweight,
                               bbox={
                                   "boxstyle": "round",
                                   "facecolor": xg_color
                               },
                               ha='center',
                               va='center',
                               path_effects=PATH_EFFECT)


    def draw_team_logos(self):
        """
        Get and draw team logos
        """
        alpha = 1
        logo_a = AnnotationBbox(self.get_logo_marker((self.team_a), alpha=alpha, big=True),
                                xy=(LOGO_XPOS, 0.9), frameon=False)

        logo_b = AnnotationBbox(self.get_logo_marker((self.team_b), alpha=alpha, big=True),
                                xy=(1-LOGO_XPOS, 0.9), frameon=False)

        self.axis.add_artist(logo_a)
        self.axis.add_artist(logo_b)

        self.save_plot()

    def draw_icetime_distribution(self):
        """
        Method to embed a pie chart in the scoreboard showing the icetime breakdown by game state.
        """
        g = self.g_df  # Easy alias
        team_a, team_b = set(g['team'])
        team_a_pp_toi = g[(g['team'] == team_a) & (g['state'] == 'pp')]['icetime'].sum()
        team_b_pp_toi = g[(g['team'] == team_b) & (g['state'] == 'pp')]['icetime'].sum()

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
            'path_effects': [PathEffects.withStroke(linewidth=2, foreground='w')]
        }

        # Add the chart as an inset axis.
        inset_ax = inset_axes(self.axis, width="60%", height="50%", loc="lower center")
        inset_ax.pie(values, labels=labels, radius=1, textprops=textprops,
                     colors=[label_colors[team_a]['bg'], label_colors[team_b]['bg']],
                     labeldistance=0.3,
                     wedgeprops={"alpha": 0.5})

        self.axis.text(0.5, 0.03, "Power Play Time Distribution", ha='center')

    def draw_goalie_summary(self):
        """
        Draw text boxes indicating goalie goals saved above expected for each goalie in the game.
        """
        # Filtered DataFrame with just all-strength goalies tats
        g = self.g_df[self.g_df['state'] == 'all'].sort_values(by='team')

        # List of goalies in the game
        goalies = list(g['name'])

        # Initial y-position for goalie text boxes
        y_pos = 0.59

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
            Rectangle(xy=(0.001, 0.52), width=0.2, height=height,
                      facecolor='gainsboro',
                      alpha=0.8
            )
        )

        # Give our little box a title
        self.axis.text(x=0.005, y=0.55 + height,
                       s="Goals Saved Above\nExpected",
                       size=fontsize,
                       weight=fontweight)

        for goalie in goalies:
            ga = float(g[g['name'] == goalie]['GA'].iloc[0])
            xga = float(g[g['name'] == goalie]['xGA'].iloc[0])
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

            team = str(g[g['name'] == goalie]['team'].iloc[0])

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


    def get_ratio_colors_for_teams(self, team_data, state, value):
        """
        Given a value to compare for two teams, e.g. xgoals or goals, as well as a state to compare 
        for determine the ratio and appropriate colors to use for representing the two values.

        :param dict team_data: Dict containing the stats for each team
        :param string state: The state to look for, e.g. all, ev, pp, pk
        :param string value: The value we're comparing, e.g. goals, xgoals, etc.
        """
        value_a = team_data[self.team_a][state][value]
        value_b = team_data[self.team_b][state][value]

        if value_a + value_b == 0:
            ratio = 0.5
        else:
            ratio = float(value_a) / (float(value_b) + float(value_a))

        color_a = ratio_to_color(ratio)
        color_b = ratio_to_color(1.0 - ratio)

        return color_a, color_b
