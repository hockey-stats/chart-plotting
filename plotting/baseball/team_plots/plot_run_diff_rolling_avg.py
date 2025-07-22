import argparse

import pandas as pd
from datetime import datetime
from pybaseball import schedule_and_record

from plotting.base_plots.animated_rolling_average import AnimatedRollingAveragePlot

# Disable annoying warning
pd.options.mode.chained_assignment = None

# Number of games over which to compute the rolling average
WINDOW = 20
# Number of games to include in plot
NUM_GAMES = 50


def proccess_data(teams: list[str]) -> pd.DataFrame:
    """
    Queries standings data from pybaseball for each provided teams and adds columns for run
    differential and run differential rolling averages, returning a DataFrame with these data
    for every provided team.

    :param list[str] teams: List of teams to query.
    :return pd.DataFrame: Final DataFrame with all combined data.
    """
    output_dfs = []
    year = datetime.now().year

    for team in teams:
        # Pull the schedule record data for each individual team, to process and save in a list
        df = schedule_and_record(year, team).fillna(0)

        # Filter out games that haven't been played yet
        df = df[df['Win'] != 0]

        # Add run differential column
        df['RD'] = df.apply(lambda row: row['R'] - row['RA'], 1)

        df['RD'] = df.apply(lambda row: row['RF'] - row['RA'], 1)

        # Add rolling average column
        df['RDRollingAvg'] = df['RD'].rolling(WINDOW).mean()
        df['gameNumber'] = df.apply(lambda row: int(row.name), 1)

        # Filter DataFrame to only columns we need for plotting
        df = df[['gameNumber', 'Tm', 'RDRollingAvg']]
        output_dfs.append(df.tail(NUM_GAMES))

    final_output = pd.concat(output_dfs)

    # Rename team column
    final_output['team'] = final_output['Tm']
    del final_output['Tm']
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

    plot_title = f"{division_name_shorthand} Run Differential - Rolling Averages (Last {NUM_GAMES} Games)"
    subtitle = f"Over the last {NUM_GAMES} games"

    plot = AnimatedRollingAveragePlot(dataframe=df, filename="run_diff_rolling_avg.png",
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

    plot.make_plot_gif()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--division', type=int, required=True,
                        help="Name of division for which to generate plot.")

    args = parser.parse_args()

    main(division=args.division)
