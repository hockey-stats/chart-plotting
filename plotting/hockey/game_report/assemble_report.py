"""
Script that will call methods to generate plots for a post-game report visualization.
The report will consist of many plots assembed into a multi-plot, including:
 - A scatter plot showing each skaters on-ice xG results
 - A bar plot showing TOI for each skater
 - A (?) plot comparing each teams goals and xgoals
 - A scoring summary
 - A goaltending breakdown
 - and we'll see what else, it's a WIP
"""

import os
import glob
import argparse
import pandas as pd

from plotting.base_plots.ratio_scatter import RatioScatterPlot
from plotting.base_plots.mirrored_bar import MirroredBarPlot
from plotting.base_plots.scoreboard import ScoreBoardPlot
from plotting.base_plots.multiplot import MultiPlot
from util.team_maps import team_full_names

# Disable an annoying warning
pd.options.mode.chained_assignment = None


def make_xg_ratio_plot(skater_df):
    """
    Function for creating scatter plot showing 5v5 on-ice xG ratios.
    :param DataFrame skater_df: DataFrame containing information for all skaters in the game.
    """
    # DataFrame contains info for all states, so filter to 5v5
    df = skater_df[skater_df['state'] == 'ev']

    xg_plot = RatioScatterPlot(dataframe=df,
                               filename='',
                               x_column='xGF', y_column='xGA',
                               title='Even-Strength xGoal Share', scale='player',
                               x_label='Expected Goals For',
                               # The newlines are a hack-y way to make the spacing align with
                               # the y-axis labels of the icetime plot i'm sorry
                               y_label='Expected Goals Against (inverted)\n\n\n\n',
                               ratio_lines=True, invert_y=True,
                               plot_x_mean=False,
                               plot_y_mean=False,
                               scale_to_extreme=False,
                               for_game_report=True,
                               data_disclaimer=None)

    return xg_plot


def make_icetime_plot(skater_df):
    """
    Function for creating mirrored bar plot showing icetime for both teams.
    Requires creating two new dataframes, one for each team, with the columns showing:
        name | team | position | es_toi | pp_toi | pk_toi
    :param DataFrame skater_df: DataFrame containing information for all skaters in the game.
    """
    # Pivot skater_df to have one df showing icetime broken down by state
    icetime_df = pd.pivot_table(skater_df, values='icetime', index=['name', 'team', 'position'],
                                columns=['state'])
    icetime_df.reset_index(inplace=True)
    teams = list(set(icetime_df['team']))
    df_a = icetime_df[icetime_df['team'] == teams[0]]
    df_b = icetime_df[icetime_df['team'] == teams[1]]

    # Add column for total icetime, to have a value to sort the tables by
    for df in df_a, df_b:
        df['total_toi'] = df.apply(lambda row: row['ev'] + row['pp'] + row['pk'], axis=1)

    # Add columns for total goals and assists
    df_a_scoring = skater_df[(skater_df['team'] == teams[0]) & (skater_df['state'] == 'all')]\
                   [['name', 'goals', 'primary_assists', 'secondary_assists']]
    df_b_scoring = skater_df[(skater_df['team'] == teams[1]) & (skater_df['state'] == 'all')]\
                   [['name', 'goals', 'primary_assists', 'secondary_assists']]

    # Merge dataframe with scoring stats into icetime dataframe
    df_a = df_a.merge(df_a_scoring, on='name')\
            .rename(columns={'goals': 'g', 'primary_assists': 'a1', 'secondary_assists': 'a2'})
    df_b = df_b.merge(df_b_scoring, on='name')\
            .rename(columns={'goals': 'g', 'primary_assists': 'a1', 'secondary_assists': 'a2'})

    df_a.drop_duplicates(subset=['name', 'position'], inplace=True)
    df_b.drop_duplicates(subset=['name', 'position'], inplace=True)

    icetime_plot = MirroredBarPlot(dataframe_a=df_a,
                                   dataframe_b=df_b,
                                   x_column=['ev', 'pp', 'pk'],
                                   a_label=teams[0], b_label=teams[1],
                                   sort_value='total_toi',
                                   title='Icetime and Scoring Breakdown',
                                   # Similar hack-y thing with the newline here to give us a bit of
                                   # padding on the bottom of the report i'm still sorry
                                   x_label="Icetime in Minutes\n",
                                   filename='',
                                   data_disclaimer=None)

    return icetime_plot


def make_scoreboard_plot(df, g_df):
    """
    Draw scoreboard plot based on skater/goalie dataframes.
    """
    plot = ScoreBoardPlot(filename='', skater_df=df, goalie_df=g_df, data_disclaimer=None)
    return plot


def assemble_multiplot(icetime, xg_scatter, scoreboard, team_a, team_b, date, filename):
    """
    Function which takes the various plots which constitute the game report and assembles them
    into a single multiplot.
    """
    arrangement = {
        "dimensions": (2, 2),
        "plots": [
            {
                "plot": scoreboard,
                "y_pos": 0,
            },
            {
                "plot": icetime,
                "y_pos": 1,
                "start": 0,
                "end": 1,
            },
            {
                "plot": xg_scatter,
                "y_pos": 1,
                "start": 1,
                "end": 2,
            }
        ],
        "hspace": 0.1,
        "wspace": 0
    }

    game_report_title, default_filename = construct_title(team_a, team_b, date)

    if filename is None:
        filename = default_filename

    game_report = MultiPlot(arrangement=arrangement,
                            figsize=(25, 16),
                            filename=filename,
                            title=game_report_title,
                            data_disclaimer='nst')

    game_report.make_multiplot()


def construct_title(team_a, team_b, date):
    """
    Construct the string which will be used for the game report title, as well as a 
    default filename for the output if a specific filename was not given.
    :param str team_a: Acronym of team A 
    :param str team_b: Acronym of team B
    :param str date: Date of the game given in YYYY-MM-DD format
    """
    year, month, day = date.split('-')

    # Get full names for teams
    a = team_full_names[team_a]
    b = team_full_names[team_b]

    title = f"Game Report\n{a} vs {b}\n{day}-{month}-{year}"
    filename=f'{team_a}_{team_b}_{year}-{month}-{day}.png'

    return title, filename


def main(game_id, filename):
    """
    Given a GameID (corresponding to a game on NST), find CSVs corresponding to that game ID 
    and create the Game Report plot.
    """

    try:
        skater_csv = glob.glob(os.path.join('data', f'*{game_id}_skaters.csv'))[0]
        goalie_csv = glob.glob(os.path.join('data', f'*{game_id}_goalies.csv'))[0]
    except IndexError as e:
        print(f"One or more CSVs for game ID {game_id} are missing. Contents of data directory"\
              f" are {os.listdir('data')}")
        raise e

    skater_df = pd.read_csv(skater_csv, encoding='utf-8-sig')
    goalie_df = pd.read_csv(goalie_csv, encoding='utf-8-sig')

    # Get the date of the game from the CSV file handle.
    if '/' in skater_csv:
        date = skater_csv.split('_')[0].split('/')[1]
    else:
        date = skater_csv.split('_')[0].split('\\')[1]

    xg_scatter_plot = make_xg_ratio_plot(skater_df)

    icetime_plot = make_icetime_plot(skater_df)

    scoreboard_plot = make_scoreboard_plot(skater_df, goalie_df)

    team_a, team_b = set(skater_df['team'])

    assemble_multiplot(icetime=icetime_plot, xg_scatter=xg_scatter_plot, scoreboard=scoreboard_plot,
                       team_a=team_a, team_b=team_b, date=date, filename=filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--game_id',
                        help="Game ID (via NST) to create a game report for.")
    parser.add_argument('-f', '--filename', default=None,
                        help='Specify filename for output image. Defaults to team/date format')
    args = parser.parse_args()

    main(args.game_id, args.filename)
