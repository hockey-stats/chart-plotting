import argparse

import pandas as pd

from plotting.base_plots.rolling_average import RollingAveragePlot


# Number of games over which to compute the rolling average
WINDOW = 20
# Number of games to include in plot
NUM_GAMES = 40


def proccess_data(teams: list[str]) -> pd.DataFrame:
    """
    Loads scraped data for teams in the given division and processes
    data to be fit for rolling average chart.

    :param list[str] teams: List of teams to process.
    :param int year: Year for which to gather data.
    :return pd.DataFrame: DataFrame fit for rolling average plot.
    """
    base_df = pd.read_csv('data/team_records.csv')
    output_dfs = []

    for team in teams:
        df = base_df[base_df['team'] == team]
        # Add run differential column
        df['RD'] = df.apply(lambda row: row['runs_for'] - row['runs_against'], 1)
        # Add rolling average column
        df['RDRollingAvg'] = df['RD'].rolling(WINDOW).mean()
        df = df[['game_number', 'team', 'RDRollingAvg']]
        output_dfs.append(df.tail(NUM_GAMES))

    final_output = pd.concat(output_dfs)

    # Rename game_num column
    final_output['gameNumber'] = final_output['game_number']
    del final_output['game_number']

    final_output.to_csv('test_ra.csv')
    return final_output


def main(division: int) -> None:
    """
    Main function that pulls the necessary data and calls the RollingAverage
    plotting method. The plot will display a run differential rolling average for all
    teams in a single division.

    :param int division: Integer corresponding to division for which to generate plot.
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

    df = proccess_data(divisions[division]['teams'])

    division_name = divisions[division]['name']
    # American League East -> AL East
    division_name_shorthand = f"{division_name[0]}L {division_name.split(' ')[-1]}"

    plot_title = f"{division_name_shorthand} Run Differential - Rolling Averages"
    subtitle = f"Over the last {NUM_GAMES} games"

    plot = RollingAveragePlot(dataframe=df, filename="run_diff_rolling_avg.png",
                              x_column='gameNumber',
                              y_column='RDRollingAvg',
                              title=plot_title, subtitle=subtitle,
                              y_label=f'{WINDOW}-Game Rolling Average',
                              x_label='Game #',
                              multiline_key='team',
                              sport='baseball',
                              y_midpoint=0,
                              add_team_logos=True,
                              for_multiplot=False,
                              data_disclaimer='baseballreference')

    plot.make_plot()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--division', type=int, required=True,
                        help="Name of division for which to generate plot.")
    args = parser.parse_args()

    main(division=args.division)
