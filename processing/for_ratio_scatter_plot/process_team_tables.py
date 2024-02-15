import os
import argparse
import pandas as pd

from processing.processing_util import convert_raw_to_ph

"""
Script to read in the three team tables and compile them all into a single table 
containing averages (when applicable) for each of:
  xGF/xGA per hour
  GF/GA per hour
"""

# Disable an annoying warning
pd.options.mode.chained_assignment = None


def read_mp_table(path):
  df = pd.read_csv(os.path.join(path, 'mp_team_table.csv'), 
                  usecols=['team', 'situation', 'iceTime', 'goalsFor', 
                           'goalsAgainst', 'flurryScoreVenueAdjustedxGoalsFor', 'flurryScoreVenueAdjustedxGoalsAgainst'])
  df = df[df['situation'] == '5on5'].sort_values(by=['team'])
  df.index = df.team
  return df


def main(path):
  mp_df = read_mp_table(path)

  df = mp_df[['team', 'iceTime']]
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

  df.to_csv(os.path.join(path, 'team_ratios.csv'), columns=['team', 'GFph', 'GAph', 'xGFph', 'xGAph'])


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-p', '--path', default=os.path.join(os.getcwd(), 'data'), 
                      help='Path to base folder of repo')
  args = parser.parse_args()
  
  main(path=args.path)
