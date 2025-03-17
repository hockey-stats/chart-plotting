"""
Script to read in raw game data from NaturalStatTrick and process into two CSVs, one
for skaters and one for goalies.
"""

import os
import glob
import csv
import argparse
import pandas as pd


def process_skater_data(path, game_id):
    """
    Processes raw data for skaters into a single DataFrame containing all the columns
    needed to create the post-game report. For each team there will be 8 CSVs, one for
    each of all strengths, 5v5, PP, and PK statistics in both individual and on-ice formats.

    Output DataFrame will have information from all 8, with each player having four rows
    for each game state that includes both the invididual and on-ice metrics.

    :param str path: Filepath to folder containing raw CSVs.
    :param str game_id: Game ID
    """

    # Initialize empty dicts to hold data from the CSVs, each dict taking all the data
    # from all situations.
    indiv_data = {
        "name": [],
        "team": [],
        "position": [],
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
        "position": [],
        "state": [],
        "CF": [],
        "CA": [],
        "GF": [],
        "GA": [],
        "xGF": [],
        "xGA": [],
    }

    for filename in glob.glob(os.path.join(path, f'*{game_id}*st.csv')):
        # Filename will be in the format
        #   date_gameID_team_state_(oi/st).csv
        # We only want the team name and state from this for the dataframe,
        # and then also get the date to use for the output filename.
        date, _, team, state, _ = os.path.basename(filename).split('_')

        with open(filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                indiv_data['name'].append(row['Player'])
                indiv_data['team'].append(team)
                indiv_data['state'].append(state)
                indiv_data['position'].append(row['Position'])
                indiv_data['icetime'].append(row['TOI'])
                indiv_data['goals'].append(row['Goals'])
                indiv_data['primary_assists'].append(row['First Assists'])
                indiv_data['secondary_assists'].append(row['Second Assists'])
                indiv_data['shots'].append(row['Shots'])
                indiv_data['ixG'].append(row['ixG'])

    for filename in glob.glob(os.path.join(path, f'*{game_id}*oi.csv')):
        _, _, team, state, _ = os.path.basename(filename).split('_')
        with open(filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                onice_data['name'].append(row['Player'])
                onice_data['team'].append(team)
                onice_data['state'].append(state)
                onice_data['position'].append(row['Position'])
                onice_data['CF'].append(row['CF'])
                onice_data['CA'].append(row['CA'])
                onice_data['GF'].append(row['GF'])
                onice_data['GA'].append(row['GA'])
                onice_data['xGF'].append(row['xGF'])
                onice_data['xGA'].append(row['xGA'])

    indiv_df = pd.DataFrame(data=indiv_data)
    onice_df = pd.DataFrame(data=onice_data)

    # Do a right join on the two DataFrames to get output DataFrame
    df = pd.merge(indiv_df, onice_df, left_on=['name', 'state', 'team', 'position'],
                  right_on=['name', 'state', 'team', 'position'], how='right')\
            .sort_values(by=['name'], ascending=True)

    df.fillna(0, inplace=True)

    # Check for and handle an error with the data source where xG values are all given as 0
    x = [float(a) for a in df['ixG']]
    col_sum = 0
    for a in x:
        col_sum += a
    if col_sum == 0:
        raise ValueError("Expected Goal values sum to 0, issue with data source, exiting...")

    return df, date

def process_goalie_data(path, game_id):
    """
    Raw goalie data is provided as one CSV for each game state, per team. Combines all 8
    into one DataFrame and return it.

    :param str path: Filepath to folder containing raw CSVs.
    :param str game_id: Game ID
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

    for filename in glob.glob(os.path.join(path, f'*{game_id}*goalies.csv')):
        print(os.path.basename(filename))
        _, _, team, state, _ = os.path.basename(filename).split('_')
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


def main(path, game_id):
    """
    Opens the CSV files containing raw game data from NaturalStatTrick, combines into two 
    dataframes (one for skaters, one for goalies), and saves them to CSVs to be used
    for plotting.
    :param str path: Path to directory containing raw CSV files.
    :param str game_id: ID for game that will be processed.
    """
    skater_df, date = process_skater_data(path, game_id)
    goalie_df = process_goalie_data(path, game_id)

    if not os.path.isdir('data'):
        os.makedirs('data')

    skater_df.to_csv(os.path.join('data', f'{date}_{game_id}_skaters.csv'), index=False)
    goalie_df.to_csv(os.path.join('data', f'{date}_{game_id}_goalies.csv'), index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', default=os.path.join(os.getcwd(), 'data'),
                        help='Path to folder containing CSV data.')
    parser.add_argument('-g', '--game_id', required=True,
                        help='Game ID for which tables should be processed.')
    args = parser.parse_args()

    main(path=args.path, game_id=args.game_id)
