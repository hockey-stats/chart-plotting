"""
Script to read in raw team table from MoneyPuck and proccess it into a DataFrame
suitable for creating layered lollipop plots for special teams tables.
"""
import os
import argparse
import pandas as pd

from processing.processing_util import convert_raw_to_ph


# Disable annoying warning
pd.options.mode.chained_assignment = None

def read_mp_table(path, situation='5on4'):
    """
    Function to read MoneyPuck team table and return a DataFrame with relevant columns
    and transformations for the provided situation.
    :param string path: Filepath pointing to CSV file containing table data.
    :param string situation: In-game situation for which table will be processed. Currently
                             supported options are '5on4', '4on5'. Defaults to '5on4'.
    """
    if situation == '5on4':
        df = pd.read_csv(os.path.join(path, 'mp_team_table.csv'),
                         usecols=['team', 'situation', 'iceTime', 'goalsFor',
                                  'flurryScoreVenueAdjustedxGoalsFor'])
        df = df[df['situation'] == '5on4']
        df.index = df.team

        df['GFph'] = list(df.apply(lambda row: convert_raw_to_ph(row['iceTime'] / 60.0,
                                                                 row['goalsFor']),
                                                                 axis=1))
        df['xGFph'] = list(df.apply(lambda row: convert_raw_to_ph(row['iceTime'] / 60.0,
                                                                  row['flurryScoreVenueAdjustedxGoalsFor']),
                                                                  axis=1))

        df = df.sort_values(by='GFph', ascending=False)

    elif situation == '4on5':
        df = pd.read_csv(os.path.join(path, 'mp_team_table.csv'),
                         usecols=['team', 'situation', 'iceTime', 'goalsAgainst',
                                  'flurryScoreVenueAdjustedxGoalsAgainst'])
        df = df[df['situation'] == '4on5']
        df.index = df.team

        df['GAph'] = list(df.apply(lambda row: convert_raw_to_ph(row['iceTime'] / 60.0,
                                                                 row['goalsAgainst']),
                                                                 axis=1))
        df['xGAph'] = list(df.apply(lambda row: convert_raw_to_ph(row['iceTime'] / 60.0,
                                                                  row['flurryScoreVenueAdjustedxGoalsAgainst']),
                                                                  axis=1))

        df = df.sort_values(by='GAph', ascending=True)

    return df


def main(path, situation):
    """
    Main function that takes filepath and given situation, processes data, and saves to an output
    CSV.
    """
    if situation not in ['5on4', '4on5']:
        raise NotImplementedError('Unsupported situation provided. Options are "5on4" or "4on5".')

    mp_df = read_mp_table(path, situation)

    if situation == '5on4':
        columns = ['team', 'GFph', 'xGFph']

    else:
        columns = ['team', 'GAph', 'xGAph']

    mp_df.to_csv(os.path.join(path, 'special_teams_ratios.csv'), columns=columns)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', default=os.path.join(os.getcwd(), 'data'),
                        help='Path to base folder of repo')
    parser.add_argument('-s', '--situation', default='5on4',
                        help='Given game state for which to process table. Defaults to "5on4".')
    args = parser.parse_args()

    main(path=args.path, situation=args.situation)
