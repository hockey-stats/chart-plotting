import os
import argparse
import pandas as pd

from processing.processing_util import convert_raw_to_ph

"""
Script to read in tables for individual player stats and process them into a table 
to display the following ratios on an individual level:
    xGF/xGA per hour
    GF/GA per hour

These ratios are presented along with the player teams and ice time.
"""

# Disable an annoying warning
pd.options.mode.chained_assignment = None


def read_player_table(path, state='5on5'):
  """
  Read table with all player stats from MP and filter based on parameters,
  returning a dataframe.

  :param string path: Path to CSV file with scraped player stats.
  :param str state: Game state to filter on, defaults to '5on5'
  """
  df = pd.read_csv(os.path.join(path, 'mp_skater_table.csv'),
                   usecols=['name', 'playerId', 'team', 'situation', 'icetime', 
									 					'OnIce_F_flurryScoreVenueAdjustedxGoals', 
														'OnIce_A_flurryScoreVenueAdjustedxGoals',
                            'OnIce_F_goals', 'OnIce_A_goals'])

  df = df[df['situation'] == state].sort_values(by=['playerId'])

  df = df.reset_index()
  del df['index']
  return df


def main(path, state):
  mp_df = read_player_table(path, state)

  df = mp_df[['name', 'playerId', 'team', 'icetime']]

  df['GFph'] = list(mp_df.apply(lambda row: convert_raw_to_ph(row['icetime'] / 60.0, 
                                                              row['OnIce_F_goals']),
                                                              axis=1))
  df['GAph'] = list(mp_df.apply(lambda row: convert_raw_to_ph(row['icetime'] / 60.0, 
                                                              row['OnIce_A_goals']), 
                                                              axis=1))
  df['xGFph'] = list(mp_df.apply(lambda row: convert_raw_to_ph(row['icetime'] / 60.0, 
                                                              row['OnIce_F_flurryScoreVenueAdjustedxGoals']), 
                                                              axis=1))
  df['xGAph'] = list(mp_df.apply(lambda row: convert_raw_to_ph(row['icetime'] / 60.0, 
                                                              row['OnIce_A_flurryScoreVenueAdjustedxGoals']),
                                                              axis=1))

  filename = 'player_ratios.csv'
  df.to_csv(os.path.join(path, filename))


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-p', '--path', default=os.path.join(os.getcwd(), 'data'), 
                      help='Path to base folder of repo')
  parser.add_argument('-s', '--state', type=str, default='5on5', 
                      choices=['4on5', 'all', '5on5', 'other', '5on4'],
                      help='Game state to filter data for, defaults to 5on5')
  args = parser.parse_args()

  main(path=args.path, state=args.state)
