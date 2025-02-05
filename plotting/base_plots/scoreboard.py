import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnnotationBbox

from plotting.base_plots.plot import Plot, get_logo_marker
from util.helpers import total_toi_as_timestamp


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
                 size=(10, 8)):

        super().__init__(filename, size)

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
        # Define bbox styles for values corresponding to goals or xgoals.
        g_bbox = {
            "boxstyle": "round",
            "facecolor": "cornflowerblue"
        }
        xg_bbox = {
            "boxstyle": "round,pad=0.15",
            "facecolor": "lightblue"
        }

        # Dict that maps game state to corresponding plot features
        state_map = {
            "total": {"x_pos": TOTAL_X_POS},
            "ev": {"color": "blue", "x_pos": ES_X_POS, 'bbox': {}},
            "pp": {"color": "green", "x_pos": PP_X_POS, 'bbox': {}},
            "pk": {"color": "red", "x_pos": SH_X_POS, 'bbox': {}},
        }

        team_data = self.organize_team_data()

        self.draw_total_goals(state_map, team_data, g_bbox, xg_bbox)

        self.draw_goals_by_state(state_map, team_data, g_bbox, xg_bbox)

        self.draw_team_logos()

        self.axis.set_axis_off()

        self.save_plot()


    def draw_total_goals(self, state_map, team_data, g_bbox, xg_bbox):
        """
        Organizer method to draw values corresponding to total goals and xgoals.
        """
        # "Goals" text box
        self.axis.text(0.5, G_HEIGHT, "Goals",
                       size=25,
                       ha='center',
                       va='center',
                       bbox=g_bbox)

        # "xGoals" text box
        self.axis.text(0.5, XG_HEIGHT, "xGoals",
                       size=25,
                       ha='center',
                       va='center',
                       bbox=xg_bbox)

        total_x_pos = state_map['total']['x_pos']
        for team, x_pos in zip([self.team_a, self.team_b], [total_x_pos, 1 - total_x_pos]):
            self.axis.text(x_pos, G_HEIGHT, team_data[team]['all']['goals'],
                           size=20,
                           ha='center',
                           va='center',
                           bbox=g_bbox)

            self.axis.text(x_pos, XG_HEIGHT, round(team_data[team]['all']['xgoals'], 1),
                           size=20,
                           ha='center',
                           va='center',
                           bbox=xg_bbox)


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


    def draw_goals_by_state(self, state_map, team_data, g_bbox, xg_bbox):
        """
        Organizing method to draw the goal/xgoal total for each state, for each team.
        """
        for state, state_settings in state_map.items():
            if state == 'total':
                continue
            default_x_pos = state_settings['x_pos']
            # One x_pos for team a and team b
            for team, x_pos in zip([self.team_a, self.team_b], [default_x_pos, 1 - default_x_pos]):
                # State label
                timestamp = total_toi_as_timestamp(team_data[team][state]['toi'])
                text = f"{state.upper()}\n({timestamp})"
                self.axis.text(x_pos, STATE_LABEL_HEIGHT, text,
                        size=10,
                        color=state_settings['color'],
                        ha='center',
                        va='center')

                # Goal value
                self.axis.text(x_pos, G_HEIGHT, team_data[team][state]['goals'],
                        size=18,
                        #color=state_settings['color'],
                        bbox=g_bbox,
                        ha='center',
                        va='center')

                # xGoal value
                self.axis.text(x_pos, XG_HEIGHT, round(team_data[team][state]['xgoals'], 1),
                        size=18,
                        #color=state_settings['color'],
                        bbox=xg_bbox,
                        ha='center',
                        va='center')


    def draw_team_logos(self):
        """
        Get and draw team logos
        """
        zoom = 2
        alpha = 0.5
        logo_a = AnnotationBbox(get_logo_marker((self.team_a), alpha=alpha, zoom=zoom),
                                xy=(0.2, 0.9), frameon=False)

        logo_b = AnnotationBbox(get_logo_marker((self.team_b), alpha=alpha, zoom=zoom),
                                xy=(0.8, 0.9), frameon=False)

        self.axis.add_artist(logo_a)
        self.axis.add_artist(logo_b)

        self.save_plot()
