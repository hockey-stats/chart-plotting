import argparse
from datetime import datetime

import pandas as pd
from pybaseball import schedule_and_record

from plotting.base_plots.rolling_average import RollingAveragePlot
from util.color_maps import mlb_label_colors


# Number of games over which to compute the rolling average
WINDOW = 10
# Number of games to include in plot
NUM_GAMES = 25


def proccess_data(division: int, year: int) -> pd.DataFrame:
    """
    Pulls the requisite data from pybaseball for teams in the given division and processes
    data to be fit for rolling average chart.

    :param int division: Integer corresponding to division.
    :param int year: Year for which to gather data.
    :return pd.DataFrame: DataFrame fit for rolling average plot.
    """
    divisions = {
        1: ['TOR', 'BOS', 'NYY', 'TBR', 'BAL'],
        2: ['SEA', 'HOU', 'LAA', 'TEX', 'ATH'],
        3: ['CLE', 'DET', 'KCR', 'MIN', 'CHW'],
        4: ['MIA', 'WSN', 'ATL', 'NYM', 'PHI'],
        5: ['SDP', 'COL', 'SFG', 'LAD', 'ARI'],
        6: ['STL', 'MIL', 'CHC', 'CIN', 'PIT']
    }

    output_dfs = []
    for team in divisions[division]:
        # Pull the schedule record data for each individual team, to process and save in a list
        df = schedule_and_record(year, team).fillna(0)
        # Filter out games that haven't been played yet
        df = df[df['Win'] != 0]
        # Add run differential column
        df['RD'] = df.apply(lambda row: row['R'] - row['RA'], 1)
        # Add rolling average column
        df['RDRollingAvg'] = df['RD'].rolling(WINDOW).mean()
        df['gameNumber'] = df.apply(lambda row: int(row.name), 1)
        df = df[['gameNumber', 'Tm', 'RDRollingAvg']]
        output_dfs.append(df.tail(NUM_GAMES))

    final_output = pd.concat(output_dfs)
    # Rename team column
    final_output['team'] = final_output['Tm']
    del final_output['Tm']
    final_output.to_csv('test_ra.csv')
    return final_output


def main(division: int, year: int) -> None:
    """
    Main function that pulls the necessary data and calls the RollingAverage
    plotting method. The plot will display a run differential rolling average for all
    teams in a single division.

    :param int division: Integer which corresponds to the different MLB divisions.
                          0 - AL East
                          1 - AL West
                          2 - AL Central
                          3 - NL East
                          4 - NL West
                          5 - NL Central
    :param int year: Year for which to gather data.
    """
    df = proccess_data(division, year)
    #df = pd.read_csv('test_ra.csv')

    division_map = {
        0: "AL East",
        1: "AL West",
        2: "AL Central",
        3: "NL East",
        4: "NL West",
        5: "NL Central",
    }

    plot_title = f"{division_map[division]} - Run Differential "\
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
                        help="Integer corresponding to the different MLB divisions to create the " \
                             "rolling average plot.")
    parser.add_argument('-y', '--year', type=int, default=datetime.now().year,
                        help='Year for which to gather data, defaults to current year.')
    args = parser.parse_args()

    main(division=args.division, year=args.year)
