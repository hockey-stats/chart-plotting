import argparse

import pandas as pd

from plotting.base_plots.cumulative_lines import CumulativeLinePlot

# Disable annoying warning
pd.options.mode.chained_assignment = None

"""
Inspired by MoneyPuck's graphical standings plot, creates a line plot for each divsion
showing the team's cumulative records above/below .500.
"""


def calculate_wins(team_df: pd.DataFrame, row: pd.Series) -> tuple[int, int]:
    """
    To be used with pandas.apply(), given a DataFrame contaings runs for/against on a per-game
    basis, adds columns for total wins and wins above average (i.e. games above .500).

    :param pd.DataFrame team_df: DataFrame containing runs for/against on a per-game basis.
    :param pd.Series row: The row of the DataFrame being applied to.
    :return tuple[int, int]: The total wins and wins above .500 at the given row.
    """
    df_to_date = team_df[team_df['game_number'] <= row['game_number']]
    row['wins'] = df_to_date['w'].sum()
    row['waa'] = row['wins'] - int(row['game_number'] / 2)
    return row



def process_data(teams: list[str]) -> pd.DataFrame:
    """
    Loads the DataFrame containing runs for/against for all teams in the division and
    adds columns for total wins and wins above average.

    :param list[str] teams: List of teams in the division.
    :return pd.DataFrame: DataFrame containing all the columns needed for the plot.
    """
    base_df = pd.read_csv('data/team_records.csv')
    team_dfs = []

    for team in teams:
        df = base_df[base_df['team'] == team]

        # Add a column denoting if a game was a win or not
        df.loc[:, 'w'] = df.apply(lambda row: 1 if row['runs_for'] > row['runs_against'] else 0,
                                  axis=1)

        df = df.apply(lambda row: calculate_wins(df, row), axis=1)

        team_dfs.append(df)

    final_df = pd.concat(team_dfs)
    return final_df


def main(division: int) -> None:
    """
    Main function which takes an integers denoting the division and creates the plot.
    """
    divisions = {
        0: { "name": "American League East",
             "teams": ['TOR', 'BOS', 'NYY', 'TBR', 'BAL'] },
        1: { "name": "American League West",
             "teams": ['SEA', 'HOU', 'LAA', 'TEX', 'ATH'] },
        2: { "name": "American League Central",
             "teams": ['CLE', 'DET', 'KCR', 'MIN', 'CHW'] },
        3: { "name": "National League East",
             "teams": ['MIA', 'WSN', 'ATL', 'NYM', 'PHI'] },
        4: { "name": "National League West",
             "teams": ['SDP', 'COL', 'SFG', 'LAD', 'ARI'] },
        5: { "name": "National League Central",
             "teams": ['STL', 'MIL', 'CHC', 'CIN', 'PIT'] }
    }

    df = process_data(divisions[division]['teams'])

    plot = CumulativeLinePlot(filename='test.png',
                              dataframe=df,
                              sport='baseball',
                              data_disclaimer='baseballreference',
                              title=f'Graphical Standings for {divisions[division]["name"]}',
                              y_column='waa',
                              y_label='Games Above .500',
                              x_column='game_number',
                              x_label='Game Number')

    plot.make_plot()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--division', type=int, required=True,
                        help="Name of division for which to generate plot.")
    args = parser.parse_args()

    main(division=args.division)
