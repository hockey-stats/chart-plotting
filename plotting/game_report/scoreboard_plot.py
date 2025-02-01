import os 
import pandas as pd 
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

from plotting.plot import Plot, get_logo_marker


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


def main(df, g_df):
    team_a, team_b = set(df['team'])

    team_data = {}
    for team in [team_a, team_b]:
        team_data[team] = {}
        team_data[team]['total'] = {
            'goals': 0,
            'xgoals': 0,
        }
        for state in ['es', 'pp', 'pk']:
            goals = df[(df['team'] == team) & (df['state'] == state)]['goals'].sum()
            xgoals = df[(df['team'] == team) & (df['state'] == state)]['ixG'].sum()
            toi = g_df[(g_df['team'] == team) & (g_df['state'] == state)]['icetime'].sum()
            team_data[team][state] = {
                'goals': goals, 
                'xgoals': xgoals, 
                'toi': toi
            }
            team_data[team]['total']['goals'] += goals
            team_data[team]['total']['xgoals'] += xgoals

    print(team_data)

    state_map = {
        "total": {"x_pos": TOTAL_X_POS},
        "es": {"color": "blue", "x_pos": ES_X_POS, 'bbox': {}},
        "pp": {"color": "green", "x_pos": PP_X_POS, 'bbox': {}},
        "pk": {"color": "red", "x_pos": SH_X_POS, 'bbox': {}},
    }

    plot = Plot(filename='test.png')
    _, ax = plot.fig, plot.axis

    g_bbox = {
        "boxstyle": "round",
        "facecolor": "royalblue"
    }
    xg_bbox = {
        "boxstyle": "round",
        "facecolor": "lightblue"
    }

    # "Goals" text box
    ax.text(0.5, G_HEIGHT, "Goals",
            size=25,
            ha='center',
            va='center',
            bbox=g_bbox)

    # "xGoals" text box
    ax.text(0.5, XG_HEIGHT, "xGoals",
            size=25,
            ha='center',
            va='center',
            bbox=xg_bbox)

    total_x_pos = state_map['total']['x_pos']
    for team, x_pos in zip([team_a, team_b], [total_x_pos, 1 - total_x_pos]):
        ax.text(x_pos, G_HEIGHT, team_data[team]['total']['goals'],
                size=20,
                ha='center',
                va='center',
                bbox=g_bbox)

        ax.text(x_pos, XG_HEIGHT, team_data[team]['total']['xgoals'],
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
            ax.text(x_pos, STATE_LABEL_HEIGHT, text,
                    size=10,
                    color=state_settings['color'],
                    ha='center',
                    va='center')

            # Goal value
            ax.text(x_pos, G_HEIGHT, team_data[team][state]['goals'],
                    size=20,
                    #color=state_settings['color'],
                    bbox=g_bbox,
                    ha='center',
                    va='center')
        
            # xGoal value
            ax.text(x_pos, XG_HEIGHT, round(team_data[team][state]['xgoals'], 1),
                    size=20,
                    #color=state_settings['color'],
                    bbox=xg_bbox,
                    ha='center',
                    va='center')

    logo_a = AnnotationBbox(get_logo_marker((team_a), alpha=0.8, zoom=2),
                            xy=(0.2, 0.9), frameon=False)

    logo_b = AnnotationBbox(get_logo_marker((team_b), alpha=0.8, zoom=2),
                            xy=(0.8, 0.9), frameon=False)

    ax.add_artist(logo_a)
    ax.add_artist(logo_b)

    plot.save_plot()




if __name__ == '__main__':
    skater_df = pd.read_csv(os.path.join('data', 'skaters.csv'), encoding='utf-8-sig')
    goalie_df = pd.read_csv(os.path.join('data', 'goalies.csv'), encoding='utf-8-sig')

    main(skater_df, goalie_df)
