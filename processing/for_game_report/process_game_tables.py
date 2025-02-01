"""
Script to read in raw game data from NaturalStatTrick and process into two CSVs, one
for skaters and one for goalies.
"""

import os
import glob
import csv
import argparse
import pandas as pd


def process_skater_data(path):
    """
    Processes raw data for skaters into a single DataFrame containing all the columns
    needed to create the post-game report. For each team there will be 8 CSVs, one for
    each of all strengths, 5v5, PP, and PK statistics in both individual and on-ice formats.

    Output DataFrame will have information from all 8, with each player having four rows
    for each game state that includes both the invididual and on-ice metrics.

    :param str path: Filepath to folder containing raw CSVs.
    """

    # Initialize empty dicts to hold data from the CSVs, each dict taking all the data
    # from all situations.
    indiv_data = {
        "name": [],
        "team": [],
        "state": [],
        "icetime": [],
        "goals": [],
        "primary_assists": [],
        "secondary_assists": [],
        "shots": [],
        "ixG": [],
    }

    onice_data = {
        "name": [],
        "team": [],
        "state": [],
        "CF": [],
        "CA": [],
        "GF": [],
        "GA": [],
        "xGF": [],
        "xGA": [],
    }

    for filename in glob.glob(os.path.join(path, '*st.csv')):
        # Filename will be in the format
        #   gameID_team_state_(oi/st).csv
        # We only want the team name and state from this for the dataframe,
        # and then also get the game_id to use for the output filename.
        game_id, team, state, _ = os.path.basename(filename).split('_')
        with open(filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                indiv_data['name'].append(row['Player'])
                indiv_data['team'].append(team)
                indiv_data['state'].append(state)
                indiv_data['icetime'].append(row['TOI'])
                indiv_data['goals'].append(row['Goals'])
                indiv_data['primary_assists'].append(row['First Assists'])
                indiv_data['secondary_assists'].append(row['Second Assists'])
                indiv_data['shots'].append(row['Shots'])
                indiv_data['ixG'].append(row['ixG'])

    for filename in glob.glob(os.path.join(path, '*oi.csv')):
        _, team, state, _ = os.path.basename(filename).split('_')
        with open(filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                onice_data['name'].append(row['Player'])
                onice_data['team'].append(team)
                onice_data['state'].append(state)
                onice_data['CF'].append(row['CF'])
                onice_data['CA'].append(row['CA'])
                onice_data['GF'].append(row['GF'])
                onice_data['GA'].append(row['GA'])
                onice_data['xGF'].append(row['xGF'])
                onice_data['xGA'].append(row['xGA'])

    indiv_df = pd.DataFrame(data=indiv_data)
    onice_df = pd.DataFrame(data=onice_data)

    # Do a right join on the two DataFrames to get output DataFrame
    df = pd.merge(indiv_df, onice_df, left_on=['name', 'state', 'team'],
                  right_on=['name', 'state', 'team'], how='right')\
            .sort_values(by=['name'], ascending=True)
       
    df.fillna(0, inplace=True)

    return df, game_id

def process_goalie_data(path):
    """
    Raw goalie data is provided as one CSV for each game state, per team. Combines all 8
    into one DataFrame and return it.

    :param str path: Filepath to folder containing raw CSVs.
    """
    goalie_data = {
        'name': [],
        'team': [],
        'icetime': [],
        'state': [],
        'SA': [],
        'GA': [],
        'xGA': []
    }

    for filename in glob.glob(os.path.join(path, '*goalies.csv')):
        _, team, state, _ = os.path.basename(filename).split('_')
        print(os.path.basename(filename))
        with open(filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                goalie_data['name'].append(row['Player'])
                goalie_data['team'].append(team)
                goalie_data['icetime'].append(row['TOI'])
                goalie_data['state'].append(state)
                goalie_data['SA'].append(row['Shots Against'])
                goalie_data['GA'].append(row['Goals Against'])
                goalie_data['xGA'].append(row['Expected Goals Against'])

    df = pd.DataFrame(data=goalie_data)

    return df


def main(path):
    """
    Opens the CSV files containing raw game data from NaturalStatTrick, combines into two 
    dataframes (one for skaters, one for goalies), and saves them to CSVs to be used
    for plotting.
    :param str path: Path to directory containing raw CSV files.
    """
    skater_df, game_id = process_skater_data(path)
    goalie_df = process_goalie_data(path)

    skater_df.to_csv(os.path.join(path, f'{game_id}_skaters.csv'), index=False)
    goalie_df.to_csv(os.path.join(path, f'{game_id}_goalies.csv'), index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', default=os.path.join(os.getcwd(), 'data'),
                        help='Path to folder containing CSV data.')
    args = parser.parse_args()

    main(path=args.path)
