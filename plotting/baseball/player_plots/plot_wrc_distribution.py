import argparse
from datetime import datetime

import pybaseball as pyb

from plotting.base_plots.swarm import SwarmPlot
from util.team_maps import mlb_team_full_names
from util.fix_traded_mlb_players import fix_teams_for_traded_batters

def main(year, qual, team):
    data = pyb.batting_stats(year, qual=qual)[['Team', 'Name', 'PA', 'wRC+', 'AVG',
                                               'WAR', 'HR', 'OPS', 'Barrel%', 'maxEV']]
    data['team'] = data['Team']
    del data['Team']

    data = fix_teams_for_traded_batters(data)

    team_full_name = mlb_team_full_names[team]

    plot_title = f"{team_full_name} Hitters by wRC+"

    team_rank, team_wrc = get_teamwide_wrc(year, team)

    plot = SwarmPlot(dataframe=data,
                      filename=f'{team}_wrc.png',
                      column='wRC+',
                      team=team,
                      qualifier='PA',
                      team_level_metric=team_wrc,
                      team_rank=team_rank,
                      y_label='wRC+',
                      table_columns=['PAs', 'AVG', 'HRs', 'OPS', 'WAR'],
                      title=plot_title,
                      data_disclaimer='fangraphs',
                      subtitle=f"Plotted against league distribution, min. {qual} PAs\n"\
                                "Shows the team's top 12 hitters by total PAs")

    plot.make_plot()


def get_teamwide_wrc(year, team):
    """
    Gets the team-level batting data and finds the team-wide wRC+ and rank to include in the plot.
    :param int year: Year of the season in question.
    :param str team: 3-letter acronym of team in question.
    """
    df = pyb.team_batting(year)[['Team', 'wRC+']]
    df = df.sort_values(by='wRC+', ascending=False).reset_index()
    rank = int(df[df['Team'] == team].index[0]) + 1
    wrc = int(df[df['Team'] == team]['wRC+'].iloc[0])

    return rank, wrc


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--year', type=int, default=datetime.now().year,
                        help='Year for which to get data, defaults to current year')
    parser.add_argument('-q', '--qual', default=50, type=int,
                        help='Minimum plate appearances to qualify in query, defaults to 50')
    parser.add_argument('-t', '--team', required=True, type=str,
                        help='Team for which players should be highlighted.')
    args = parser.parse_args()

    main(year=args.year, qual=args.qual, team=args.team)
