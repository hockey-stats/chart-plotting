import argparse
from datetime import datetime

import pandas as pd
from pybaseball import schedule_and_record

from plotting.base_plots.rolling_average import RollingAveragePlot
from util.color_maps import mlb_label_colors


# Number of games over which to compute the rolling average
WINDOW = 15
# Number of games to include in plot
NUM_GAMES = 25


def proccess_data(teams: list[str], year: int) -> pd.DataFrame:
    """
    Pulls the requisite data from pybaseball for teams in the given division and processes
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
    # Rename team column
    final_output.to_csv('test_ra.csv')
    return final_output


def main(division: str, year: int) -> None:
    """
    Main function that pulls the necessary data and calls the RollingAverage
    plotting method. The plot will display a run differential rolling average for all
    teams in a single division.

    :param str division: Name of division for which to generate plot.
    :param int year: Year for which to gather data.
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
    df = proccess_data(divisions[division]['teams'], year)
    #df = pd.read_csv('test_ra.csv')
    
    division_name = divisions[division]['name']
    # American League East -> AL East
    division_name_shorthand = f"{division_name[0]}L {division_name.split(' ')[-1]}"

    plot_title = f"{division_name_shorthand} - Run Differential "\
                 f"{WINDOW}-Game Rolling Average"
    subtitle = f"Over the last {NUM_GAMES} games"

    plot = RollingAveragePlot(dataframe=df, filename="run_diff_rolling_avg.png",
                              x_column='gameNumber',
                              y_column='RDRollingAvg',
                              title=plot_title, subtitle=subtitle,
                              y_label='Run Diff. Rolling Avg',
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
    parser.add_argument('-y', '--year', type=int, default=datetime.now().year,
                        help='Year for which to gather data, defaults to current year.')
    args = parser.parse_args()

    main(division=args.division, year=args.year)
