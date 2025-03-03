import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
from matplotlib.offsetbox import AnnotationBbox
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from plotting.base_plots.plot import Plot, get_logo_marker
from util.helpers import total_toi_as_timestamp
from util.color_maps import label_colors


G_HEIGHT = 0.75
XG_HEIGHT = 0.65
STATE_LABEL_HEIGHT = 0.55

TOTAL_X_POS = 0.34
ES_X_POS = 0.23
PP_X_POS = 0.16
SH_X_POS = 0.09


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
                 size=(14, 8),
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
        # Define bbox styles for values corresponding to goals, xgoals or state labels.
        bboxes = {
            "g": {
                "boxstyle": "round",
                "facecolor": "cornflowerblue"
            },
            "xg": {
                "boxstyle": "round",
                "facecolor": "lightblue"
            },
            "state": {
                "boxstyle": "round",
                "facecolor": "gainsboro"
            }
        }

        # Dict that maps game state to corresponding plot features
        state_map = {
            "total": {"x_pos": TOTAL_X_POS},
            "ev": {"color": "blue", "x_pos": ES_X_POS, 'bbox': {}},
            "pp": {"color": "green", "x_pos": PP_X_POS, 'bbox': {}},
            "pk": {"color": "red", "x_pos": SH_X_POS, 'bbox': {}},
        }

        team_data = self.organize_team_data()

        self.draw_total_goals(state_map, team_data, bboxes)

        self.draw_goals_by_state(state_map, team_data, bboxes)

        self.draw_team_logos()

        self.draw_icetime_distribution()

        self.axis.set_axis_off()

        self.save_plot()


    def draw_total_goals(self, state_map, team_data, bboxes):
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
                       bbox=bboxes["g"],
                       path_effects=[PathEffects.withStroke(linewidth=3, foreground='w')])

        # "xGoals" text box
        self.axis.text(0.5, XG_HEIGHT, "xGoals",
                       size=fontsize,
                       weight=fontweight,
                       ha='center',
                       va='center',
                       bbox=bboxes["xg"],
                       path_effects=[PathEffects.withStroke(linewidth=3, foreground='w')])

        total_x_pos = state_map['total']['x_pos']
        for team, x_pos in zip([self.team_a, self.team_b], [total_x_pos, 1 - total_x_pos]):
            self.axis.text(x_pos, G_HEIGHT, team_data[team]['all']['goals'],
                           size=fontsize,
                           weight=fontweight,
                           ha='center',
                           va='center',
                           bbox=bboxes["g"],
                           path_effects=[PathEffects.withStroke(linewidth=3, foreground='w')])

            self.axis.text(x_pos, XG_HEIGHT, round(team_data[team]['all']['xgoals'], 1),
                           size=fontsize,
                           weight=fontweight,
                           ha='center',
                           va='center',
                           bbox=bboxes["xg"],
                           path_effects=[PathEffects.withStroke(linewidth=3, foreground='w')])


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


    def draw_goals_by_state(self, state_map, team_data, bboxes):
        """
        Organizing method to draw the goal/xgoal total for each state, for each team.
        """
        for state, state_settings in state_map.items():
            if state == 'total':
                continue
            default_x_pos = state_settings['x_pos']

            fontsize = 20
            fontweight = 700

            # One x_pos for team a and team b
            for team, x_pos in zip([self.team_a, self.team_b], [default_x_pos, 1 - default_x_pos]):
                # State label
                text = f"{state.upper()}"
                self.axis.text(x_pos, STATE_LABEL_HEIGHT, text,
                               size=fontsize,
                               weight=fontweight,
                               bbox=bboxes["state"],
                               ha='center',
                               va='center',
                               path_effects=[PathEffects.withStroke(linewidth=3, foreground='w')])

                # Goal value
                self.axis.text(x_pos, G_HEIGHT, team_data[team][state]['goals'],
                               size=fontsize,
                               weight=fontweight,
                               bbox=bboxes["g"],
                               ha='center',
                               va='center',
                               path_effects=[PathEffects.withStroke(linewidth=3, foreground='w')])

                # xGoal value
                self.axis.text(x_pos, XG_HEIGHT, round(team_data[team][state]['xgoals'], 1),
                               size=fontsize,
                               weight=fontweight,
                               bbox=bboxes["xg"],
                               ha='center',
                               va='center',
                               path_effects=[PathEffects.withStroke(linewidth=3, foreground='w')])


    def draw_team_logos(self):
        """
        Get and draw team logos
        """
        zoom = 3
        alpha = 0.8
        logo_a = AnnotationBbox(get_logo_marker((self.team_a), alpha=alpha, zoom=zoom),
                                xy=(0.2, 0.9), frameon=False)

        logo_b = AnnotationBbox(get_logo_marker((self.team_b), alpha=alpha, zoom=zoom),
                                xy=(0.8, 0.9), frameon=False)

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
        #es_toi = 60 - float(team_a_pp_toi) - float(team_b_pp_toi)

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

