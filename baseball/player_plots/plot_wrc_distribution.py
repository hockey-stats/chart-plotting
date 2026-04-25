import argparse
from datetime import datetime
from typing import Tuple

import pybaseball as pyb
import polars as pl

from plot_types.swarm import SwarmPlot
from util.team_maps import mlb_team_full_names
from util.fix_traded_mlb_players import fix_teams_for_traded_batters
from util.get_detailed_batter_stats import get_detailed_batter_stats

def main(year, qual, team):
    qual = 20
    data = get_detailed_batter_stats(year)
    data = data.rename({"Team": 'team'})

    with pl.Config(tbl_rows=100):
        print(data.filter(pl.col("team") == 'TOR'))

    data = data.filter(pl.col('PA') >= qual)

    #data = fix_teams_for_traded_batters(data)

    team_full_name = mlb_team_full_names[team]

    plot_title = f"{team_full_name} Hitters by wRC+"

    team_wrc, team_rank = get_teamwide_wrc(data, team)

    plot = SwarmPlot(dataframe=data.to_pandas(),
                      filename=f'{team}_wrc.png',
                      column='wRC+',
                      team=team,
                      qualifier='PA',
                      team_level_metric=team_wrc,
                      team_rank=team_rank,
                      y_label='wRC+',
                      table_columns=['PAs', 'AVG', 'HRs', 'OPS', 'xWOBA'],
                      title=plot_title,
                      data_disclaimer='baseballreference',
                      subtitle=f"Plotted against league distribution, min. {qual} PAs\n"\
                                "Shows the team's top 12 hitters by total wRC+")

    plot.make_plot()


def get_teamwide_wrc(df: pl.DataFrame, team_name: str) -> Tuple[int, int]:
    """
    Calculates the aggregate wRC+ for a specific team and their league-wide rank.

    :param pl.DataFrame df: Dataframe containing 'Team', 'PA', and 'wRC+' columns.
    :param str team_name: The name or abbreviation of the team (e.g., 'NYY').
    :return Tuple[int, int]: A tuple containing (team_wrc_plus, rank).
    """
    # 1. Calculate weighted wRC+ for every team in the league
    team_standings = (
        df.group_by("team")
        .agg(
            ((pl.col("wRC+") * pl.col("PA")).sum() / pl.col("PA").sum()).alias("Team_wRC+")
        )
        # 2. Sort descending so the best offense is at the top
        .sort("Team_wRC+", descending=True)
        # 3. Add a rank column (1 is the best)
        .with_columns(
            pl.col("Team_wRC+").rank(method="min", descending=True).cast(pl.Int32).alias("Rank")
        )
    )

    # 4. Extract the specific team's values
    team_data = team_standings.filter(pl.col("team") == team_name)
    
    if team_data.is_empty():
        raise ValueError(f"Team '{team_name}' not found in the dataset.")

    wrc_val = int(round(team_data.get_column("Team_wRC+")[0]))
    rank_val = team_data.get_column("Rank")[0]

    return wrc_val, rank_val


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--year', type=int, default=datetime.now().year,
                        help='Year for which to get data, defaults to current year')
    parser.add_argument('-q', '--qual', default=50, type=int,
                        help='Minimum plate appearances to qualify in query, defaults to 50')
    parser.add_argument('-t', '--team', required=True, type=str,
                        help='Team for which players should be highlighted.')
    args = parser.parse_args()

    main(year=args.year, qual=args.qual, team=args.team)
