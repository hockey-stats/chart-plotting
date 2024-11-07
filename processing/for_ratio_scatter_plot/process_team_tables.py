"""
Script to read in the three team tables and compile them all into a single table 
containing averages (when applicable) for each of:
  xGF/xGA per hour
  GF/GA per hour
"""
import os
import argparse
import pandas as pd

from processing.processing_util import convert_raw_to_ph


# Disable an annoying warning
pd.options.mode.chained_assignment = None

def read_mp_table(path, situation='5on5'):
    """
    Function to read MoneyPuck team table and return a DataFrame with only relevant
    columns.
    :param string path: Filepath pointing to CSV file containing table data.
    :param string situation: In-game situation for which table will be processed. Currently 
                             supported options are '5on5', '5on4', or '4on5'. Defaults to '5on5'.
    """
    if situation == '5on5':
        df = pd.read_csv(os.path.join(path, 'mp_team_table.csv'),
                        usecols=['team', 'situation', 'iceTime', 'goalsFor',
                                 'goalsAgainst', 'flurryScoreVenueAdjustedxGoalsFor',
                                 'flurryScoreVenueAdjustedxGoalsAgainst'])
        df = df[df['situation'] == '5on5'].sort_values(by=['team'])
        df.index = df.team

    elif situation == '5on4':
        df = pd.read_csv(os.path.join(path, 'mp_team_table.csv'),
                        usecols=['team', 'situation', 'iceTime', 'goalsFor',
                                 'flurryScoreVenueAdjustedxGoalsFor'])
        df = df[df['situation'] == '5on4'].sort_values(by=['team'])
        df.index = df.team

    elif situation == '4on5':
        df = pd.read_csv(os.path.join(path, 'mp_team_table.csv'),
                        usecols=['team', 'situation', 'iceTime', 'goalsAgainst',
                                 'flurryScoreVenueAdjustedxGoalsAgainst'])
        df = df[df['situation'] == '4on5'].sort_values(by=['team'])
        df.index = df.team

    else:
        raise NotImplementedError('Unsupported situation provided. Options are "5on5", "5on4",'\
                                  'or 4on5')

    return df


def main(path, situation='5on5'):
    """
    Main function that takes filepath and given situation and processes data into an output CSV.
    """
    mp_df = read_mp_table(path, situation)

    df = mp_df[['team', 'iceTime']]
    # Convert given total stats into rate stats per hour.
    df['GFph'] = list(mp_df.apply(lambda row: convert_raw_to_ph(row['iceTime'] / 60.0,
                                                                row['goalsFor']),
                                                                axis=1))
    df['GAph'] = list(mp_df.apply(lambda row: convert_raw_to_ph(row['iceTime'] / 60.0,
                                                                row['goalsAgainst']),
                                                                axis=1))
    df['xGFph'] = list(mp_df.apply(lambda row: convert_raw_to_ph(row['iceTime'] / 60.0,
                                                                 row['flurryScoreVenueAdjustedxGoalsFor']),
                                                                 axis=1))
    df['xGAph'] = list(mp_df.apply(lambda row: convert_raw_to_ph(row['iceTime'] / 60.0,
                                                                 row['flurryScoreVenueAdjustedxGoalsAgainst']),
                                                                 axis=1))

    df.to_csv(os.path.join(path, 'team_ratios.csv'), columns=['team', 'GFph', 'GAph', 
                                                              'xGFph', 'xGAph'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', default=os.path.join(os.getcwd(), 'data'),
                        help='Path to base folder of repo')
    parser.add_argument('-s', '--situation', default='5on5',
                        help='Given game state for which to process table.')
    args = parser.parse_args()

    main(path=args.path, situation=args.situation)
