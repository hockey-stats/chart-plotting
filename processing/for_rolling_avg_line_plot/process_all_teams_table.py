import os
import argparse
import pandas as pd

from datetime import datetime
from processing.processing_util import convert_raw_to_ph


def main(path, year, window, column):
  df = pd.read_csv(os.path.join(path, 'mp_all_team_games.csv'))
  df = df[(df['season'] == year) & (df['situation'] == '5on5')][['team', 'gameId', 'xGoalsPercentage']]

  output_dfs = list()
  for team in set(df['team']):
    team_df = df[df['team'] == team].sort_values(by='gameId').reset_index()
    del team_df['index']



if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-p', '--path', default=os.path.join(os.getcwd(), 'data'), 
                      help='Path to base folder of repo')
  parser.add_argument('-y', '--year', default=datetime.now().year,
                      help='Year of data to analyze, defaults to current year.')
  parser.add_argument('-w', '--window', default=10,
                      help='Size of window to calculate rolling averages, defaults to 10')
  parser.add_argument('-c', '--column', default='xGoalsPercentage',
                      help='Column to calculate rolling average for, defaults to xGoalsPercentage.')
  
  args = parser.parse_args()
  
  main(path=args.path, year=args.year, window=args.window, column=args.column)

  