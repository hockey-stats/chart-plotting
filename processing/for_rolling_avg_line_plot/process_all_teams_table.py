import os
import argparse

from datetime import datetime

import pandas as pd

def main(path, year, window, column, num_games):
    """
    Processing CSV containing game-level data for every game from 2008-onwards from MoneyPuck. 

    Output will be a csv containing rolling averages for every team in the desired season, on 
    the desired column, saved to the data/ directory.

    For each team:
      filter input data to just that team
      sort by game id
      calculate rolling averages, add as new column
      also add column for game number
      use dropna() method to get rid of games before our window starts
      add resulting dataframe to a list
    and finally concat every dataframe in list to our output, containing the rolling averages 
    for each team, by game.

    :param path: Directory containing input csv 'mp_all_team_games.csv'
    :param year: Year to calculate for.
    :param window: Size of the window to calculate rolling averages for.
    :param column: Column on which to calculate rolling averages.
    :param num_games: Number of games to include in output.
    """
    df = pd.read_csv(os.path.join(path, 'mp_all_team_games.csv'))
    df = df[(df['season'] == year) & (df['situation'] == '5on5')][['team', 'gameId', column]]

    output_dfs = []
    for team in set(df['team']):
        team_df = df[df['team'] == team].sort_values(by='gameId').reset_index()
        del team_df['index']
        team_df[f'{column}RollingAvg'] = team_df[column].rolling(window).mean()
        team_df['gameNumber'] = team_df.apply(lambda row: int(row.name) + 1, 1)
        team_df = team_df.dropna()

        if num_games > 0:
            team_df = team_df.tail(num_games)

        output_dfs.append(team_df)

    final_output = pd.concat(output_dfs)
    final_output.to_csv(os.path.join(path, f'{column}_rolling_avg.csv'), index=False,
                        columns=['team', 'gameNumber', f'{column}RollingAvg'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', default=os.path.join(os.getcwd(), 'data'),
                        help='Path to base folder of repo')
    parser.add_argument('-y', '--year', default=datetime.now().year, type=int,
                        help='Year of data to analyze, defaults to current year.')
    parser.add_argument('-w', '--window', default=10, type=int,
                        help='Size of window to calculate rolling averages, defaults to 10')
    parser.add_argument('-c', '--column', default='xGoalsPercentage',
                        help='Column to calculate rolling average for, defaults to'\
                             'xGoalsPercentage.')
    parser.add_argument('-n', '--num_games', default=0, type=int,
                        help='`n` for last n games for which to include in plot, e.g. n=25 would'\
                             'mean only include the last 25 games in the output.')

    args = parser.parse_args()

    main(path=args.path, year=args.year, window=args.window, column=args.column, num_games=args.num_games)
