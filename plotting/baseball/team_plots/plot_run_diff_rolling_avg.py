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
        "American League East": ['TOR', 'BOS', 'NYY', 'TBR', 'BAL'],
        "American League West": ['SEA', 'HOU', 'LAA', 'TEX', 'ATH'],
        "American League Central": ['CLE', 'DET', 'KCR', 'MIN', 'CHW'],
        "National League East": ['MIA', 'WSN', 'ATL', 'NYM', 'PHI'],
        "National League West": ['SDP', 'COL', 'SFG', 'LAD', 'ARI'],
        "National League Central": ['STL', 'MIL', 'CHC', 'CIN', 'PIT']
    }

    output_dfs = []
    print(divisions[division])
    for team in divisions[division]:
        print("querying!!!!:", year, team)
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


def main(division: str, year: int) -> None:
    """
    Main function that pulls the necessary data and calls the RollingAverage
    plotting method. The plot will display a run differential rolling average for all
    teams in a single division.

    :param str division: Name of division for which to generate plot.
    :param int year: Year for which to gather data.
    """
    df = proccess_data(division, year)
    #df = pd.read_csv('test_ra.csv')

    # American League East -> AL East
    division_name_shorthand = f"{division[0]}L {division.split(' ')[-1]}"

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
    parser.add_argument('-d', '--division', type=str, required=True,
                        help="Name of division for which to generate plot.")
    parser.add_argument('-y', '--year', type=int, default=datetime.now().year,
                        help='Year for which to gather data, defaults to current year.')
    args = parser.parse_args()

    main(division=args.division, year=args.year)
