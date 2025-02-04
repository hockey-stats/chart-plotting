import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnnotationBbox

from plotting.base_plots.plot import Plot, get_logo_marker


G_HEIGHT = 0.75
XG_HEIGHT = 0.65
STATE_LABEL_HEIGHT = 0.55

TOTAL_X_POS = 0.34
ES_X_POS = 0.23
PP_X_POS = 0.16
SH_X_POS = 0.09


def total_toi_as_timestamp(toi):
    """
    Given the total TOI as a float representing the number of minutes played,
    return a string representing the timestamp in the form MM:SS.

    :param float toi: Total time on ice, in minutes.
    """

    minutes = int(toi)
    seconds = int(60 * (toi - minutes))
    minutes = str(minutes) if minutes >= 10 else '0' + str(minutes)
    seconds = str(seconds) if seconds >= 10 else '0' + str(seconds)
    timestamp = f"{minutes}:{seconds}"
    return timestamp


class ScoreBoardPlot(Plot):
    """
    Special type of plot that is only used in game reports. Creates a scoreboard showing
    general team-level statistics for a game.
    """
    def __init__(self,
                 filename,
                 skater_df,
                 goalie_df):

        super().__init__(filename)

        self.df = skater_df
        self.g_df = goalie_df
        self.fig = plt.figure(figsize=self.size)
        self.axis = self.fig.add_subplot(111)


    def make_plot(self):
        """
        Assembles the Plot object.
        """
        # Get the names of the two teams in the game
        team_a, team_b = set(self.df['team'])

        # Assemble a dict object containing details and stats for each team, namely
        # goal and xgoal totals for each game state per team as well as ToI.
        team_data = {}
        for team in [team_a, team_b]:
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

        # Dict that maps game state to corresponding plot features
        state_map = {
            "total": {"x_pos": TOTAL_X_POS},
            "ev": {"color": "blue", "x_pos": ES_X_POS, 'bbox': {}},
            "pp": {"color": "green", "x_pos": PP_X_POS, 'bbox': {}},
            "pk": {"color": "red", "x_pos": SH_X_POS, 'bbox': {}},
        }

        g_bbox = {
            "boxstyle": "round",
            "facecolor": "cornflowerblue"
        }
        xg_bbox = {
            "boxstyle": "round,pad=0.15",
            "facecolor": "lightblue"
        }

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
        for team, x_pos in zip([team_a, team_b], [total_x_pos, 1 - total_x_pos]):
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

        for state, state_settings in state_map.items():
            if state == 'total':
                continue
            default_x_pos = state_settings['x_pos']
            # One x_pos for team a and team b
            for team, x_pos in zip([team_a, team_b], [default_x_pos, 1 - default_x_pos]):
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

        logo_a = AnnotationBbox(get_logo_marker((team_a), alpha=0.8, zoom=2),
                                xy=(0.2, 0.9), frameon=False)

        logo_b = AnnotationBbox(get_logo_marker((team_b), alpha=0.8, zoom=2),
                                xy=(0.8, 0.9), frameon=False)

        self.axis.add_artist(logo_a)
        self.axis.add_artist(logo_b)

        self.save_plot()
    