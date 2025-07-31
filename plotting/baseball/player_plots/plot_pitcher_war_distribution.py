import argparse
from datetime import datetime

import pandas as pd
import pybaseball as pyb

from plotting.base_plots.swarm import SwarmPlot
from util.team_maps import mlb_team_full_names


def fix_teams_for_traded_players(df: pd.DataFrame) -> pd.DataFrame:
    """
    For players who have played on multiple teams, fangraphs returns their 'Team' value as
    '- - -'. Replace these values with the actual current team.
    """
    traded_players = list(df[df['team'] == '- - -']['Name'])
    traded_db = {
        'Jordan Hicks': 'BOS',
        'Sean Newcomb': 'ATH',
        'Tyler Alexander': 'CHW',
        'Aaron Civale': 'CHW',
        'Bryan Baker': 'TBR',
        'Joey Wentz': 'ATL',
        'Carlos Hernandez': 'DET',
        'Jorge Alcala': 'BOS',
        'Lou Trivino': 'LAD',
        'Scott Blewett': 'BAL',
        'Luis Garcia': 'LAA',
        'Andrew Chafin': 'LAA',
        'Jake Eder': 'WSN',
        'Tyler Kinley': 'ATL',
        'Austin Smith': 'COL',
        'Gage Ziehl': 'CWS',
        'Seranthony Dominguez': 'TOR',
        'Carlos Carrasco': 'ATL',
        'Chris Paddack': 'DET',
        'Randy Dobnak': 'DET',
        'Amed Rosario': 'NYY',
        'Randal Grichuk': 'KCR',
        "Ke'Byran Hayes": "CIN",
        "Mason Miller": "SDP",
        "JP Sears": "SDP",
        "Shane Bieber": "TOR",
        "Steven Matz": "BOS",
        "Andrew Kittredge": "CHI",
        "Zack Litell": "CIN",
        "Rafael Montero": "DET",
        "Michael Soroka": "CHI",
        "Ryan Helsley": "NYM",
        "Jhoan Duran": "PHI",
        "Mick Abel": "MIN",
        "Caleb Ferguson": "SEA",
        "Tyler Rogers": "NYM",
        "Taylor Rogers": "PIT",

        
    }
    for name in traded_players:
        if name in traded_db:
            index = df[df['Name'] == name].index
            df.loc[index, 'team'] = traded_db[name]

    return df


def get_teamwide_stuff(year: int, team: str) -> None:
    """
    Gets the team-level pitching data and finds the team-wide Stuff+ and rank to include in the
    plot.
    :param int year: Season in question
    :param str team: Team in question
    """
    df = pyb.team_pitching(year)[['Team', 'WAR']]
    df = df.sort_values(by='WAR', ascending=False).reset_index()
    rank = int(df[df['Team'] == team].index[0]) + 1
    stuff = float(df[df['Team'] == team]['WAR'].iloc[0])

    return rank, stuff


def main(year: int, qual: int, team: str) -> None:
    """
    Queries team-level pitching data from pybaseball and calls the plotting method.

    :param int year: Season for which to query
    :param int qual: Minimum inning-pitched to apply to query
    :param str team: Team for which to query
    """

    data = pyb.pitching_stats(year, qual=qual)[['Team', 'Name', 'IP', 'G', 'GS', 'Stuff+',
                                                'ERA', 'xERA', 'K-BB%', 'WAR']]

    data['team'] = data['Team']
    del data['Team']

    # Scale K-BB% up to 1-100%
    data['K-BB%'] = data.apply(lambda x: x['K-BB%'] * 100, axis=1)

    team_full_name = mlb_team_full_names[team]

    plot_title = f"{team_full_name} Pitchers by WAR"

    team_rank, team_stuff = get_teamwide_stuff(year, team)

    data['is_starter'] = data.apply(lambda x: True if x['GS'] >= 0.5 * x['G'] else False,
                                    axis=1)

    subtitle = f"Plotted against league distribution, min {qual} IPs\n"\
               f"Shows top-5 starters and top-7 relievers by IP"

    plot = SwarmPlot(dataframe=data,
                     filename=f'{team}_pitcher_war.png',
                     column='WAR',
                     team=team,
                     qualifier='IP',
                     team_level_metric=team_stuff,
                     team_rank=team_rank,
                     y_label='WAR',
                     table_columns=['IP', 'ERA', 'K-BB%', 'Stuff+'],
                     title=plot_title,
                     category_column='is_starter',
                     data_disclaimer='fangraphs',
                     subtitle=subtitle
                     )
    
    plot.make_plot()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--year', type=int, default=datetime.now().year,
                        help='Year for which to get data, defaults to current year')
    parser.add_argument('-q', '--qual', default=10, type=int,
                        help='Minimum innings pitched to qualify in query, defaults to 30')
    parser.add_argument('-t', '--team', required=True, type=str,
                        help='Team for which players should be highlighted.')
    args = parser.parse_args()
    main(year=args.year, qual=args.qual, team=args.team)
#    import os
#    for x in os.listdir(path='team_logos/baseball/svg'):
#        team = x.split('.')[0]
#        main(year=2025, qual=10, team=team)
#