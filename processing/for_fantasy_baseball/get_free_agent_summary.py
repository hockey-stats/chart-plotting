import argparse
import logging
from itertools import combinations

import polars as pl
import pybaseball as pb
import yahoo_fantasy_api as yfa
from yahoo_oauth import OAuth2
from unidecode import unidecode

oauth_logger = logging.getLogger('yahoo_oauth')
oauth_logger.disabled = True


# All the abbreviations that differ between the two data sources
TEAM_MAPPING = {
    'SF': 'SFG',
    'SD': 'SDP',
    'TB': 'TBR',
    'CWS': 'CHW',
    'AZ': 'ARI',
    'KC': 'KCR',
    'WSH': 'WSN',
}

# All the positions that we will be collecting data for
POSITIONS = ['1B', '2B', '3B', 'SS', 'C', 'OF', 'SP', 'RP']


def create_session() -> OAuth2:
    """
    Creates the OAuth2 session from a local json. Refreshes token if necessary.

    :return OAuth2: Active OAuth2 session
    """
    sc = OAuth2(None, None, from_file='oauth.json')
    return sc


def standardize_team_names(team: str) -> str:
    """
    Function used to adjust team abbreviations provided by the Yahoo API to match
    those used by pybaseball.

    :param str team: The team name abbreviation provided by the Yahoo API
    :return str: Team name abbreviation used by pybaseball
    """
    return TEAM_MAPPING.get(team, team)


def get_free_agents(position: str, league: yfa.League) -> pl.DataFrame:
    """
    Uses the Yahoo Fantasy API to get a list of all free agents for the given
    position then formats them into a returned DataFrame.

    :param str position: Position for which to pull free agents.
    :param yfa.League league: The League object from the yfa library, representing our league.
    :return pd.DataFrame: DataFrame containing formatted data for free agents.
    """

    players = league.free_agents(position)

    # Get the ID for every returned player, we use these IDs to query more detailed info
    player_ids = [int(player['player_id']) for player in players if player['status'] == '']

    if position in {'1B', '2B', '3B', 'C', 'OF'}:
        df = collect_batter_stats(player_ids, league)
    else:
        df = collect_pitcher_stats(player_ids, league, position)

    return df


def get_players_from_own_team(position: str, league: yfa.League, session: OAuth2) -> pl.DataFrame:
    """
    Pulls from the fantasy API all players of the given position from my own team.

    :param str position: Position for which to pull players.
    :param yfa.League league: The League object from the yfa library, representing our league.
    :param OAuth2 session: OAuth2 session used for authentication.
    :return pl.DataFrame: DataFrame containing the players and their stats.
    """
    # Get all teams and find one owned by the caller of the API
    teams = league.teams()
    for team in teams:
        if teams[team].get('is_owned_by_current_login', False):
            my_team = yfa.Team(session, team)
            break
    else:
        print("Own team not found, exiting...")
        raise ValueError

    # Collect only the players of the given position
    players = []
    for player in my_team.roster():
        # Ignore players on the IL
        if 'IL' in player['status']:
            continue
        if position in player['eligible_positions']:
            players.append(player['player_id'])

    if position in {'1B', '2B', '3B', 'C', 'OF'}:
        df = collect_batter_stats(players, league)
    else:
        df = collect_pitcher_stats(players, league, position)

    return df


def collect_pitcher_stats(player_ids: list, league: yfa.League, position: str) -> pl.DataFrame:
    """
    Given a list of player IDs for pitchers, pull the given stats and organize into a DF.

    :param list(str) player_ids: List of player IDs given as strings.
    :param yfa.League league: The League object to query against.
    :param str position: SP or RP, since we filter the results slightly differently for starters
    :return pl.DataFrame: Details and stats for each player.
    """

    player_details = league.player_details(player_ids)

    # Collect stats across the past week, month, and season
    player_stats_week = league.player_stats(player_ids, 'lastweek')
    player_stats_month = league.player_stats(player_ids, 'lastmonth')
    player_stats_season = league.player_stats(player_ids, 'season')

    p_dict = {
        "name": [],
        "team": [],
        "positions": [],
        "ip": [],
        "era": [],
        "whip": [],
        "k": [],
        "w": [],
        "sv": [],
        "term": []
    }

    for player_stats, term in zip([player_stats_week, player_stats_month, player_stats_season],
                                  ['week', 'month', 'season']):
        for details, stats in zip(player_details, player_stats):
            if stats['IP'] == 0.0 or stats['IP'] == '-':
                # Skip players without any innings pitched
                continue
            p_dict['name'].append(unidecode(details['name']['full']))
            p_dict['team'].append(standardize_team_names(details['editorial_team_abbr']))
            p_dict['positions'].append(','.join([pos['position'] for pos in details['eligible_positions'] \
                                                if pos['position'] != 'P']))
            p_dict['ip'].append(stats['IP'])
            p_dict['era'].append(stats['ERA'])
            p_dict['whip'].append(stats['WHIP'])
            p_dict['k'].append(int(stats['K']))
            p_dict['w'].append(int(stats['W']))
            p_dict['sv'].append(int(stats['SV']))
            p_dict['term'].append(term)

    # Collect yahoo stats into DF
    y_df = pl.DataFrame(p_dict)

    # Now get full-season stats with pybaseball
    p_df = pl.from_pandas(pb.pitching_stats(2025, qual=5)[['Name', 'Team', 'xERA', 'Stuff+', 'G', 'GS']])
    p_df = p_df.rename({"Name": "name", "Team": "team"})

    if position == 'SP':
        # If looking for starters, remove every pitcher with 0 starts
        p_df = p_df.remove(pl.col("GS") == 0)
    else:
        # If looking for relievers, remove every pitcher with as many starts as appearances
        p_df = p_df.remove(pl.col("GS") == pl.col("G"))

    # Remove the games/starts column
    p_df = p_df.drop("G", "GS")

    # Add a last_name column to both dataframes for the join (different sources might have
    # different first names)
    p_df = p_df.with_columns(
        (pl.col("name").str.split(" ").list.slice(1, None).list.join(" ")).alias("last_name")
    )
    y_df = y_df.with_columns(
        (pl.col("name").str.split(" ").list.slice(1, None).list.join(" ")).alias("last_name")
    )

    # Join the two DFs and return
    df = y_df.join(p_df, how='inner', on=['last_name', 'team'])
    df = df.drop("last_name", "name_right")

    return df


def collect_batter_stats(player_ids: list, league: yfa.League) -> pl.DataFrame:
    """
    Given a list of player IDs for batters, pull the given stats and organize into a DF.

    :param list(str) player_ids: List of player IDs given as strings.
    :param yfa.League league: The League object to query against.
    :return pl.DataFrame: Details and stats for each player.
    """

    player_details = league.player_details(player_ids)

    # Collect stats across the past week, month, and season
    player_stats_week = league.player_stats(player_ids, 'lastweek')
    player_stats_month = league.player_stats(player_ids, 'lastmonth')
    player_stats_season = league.player_stats(player_ids, 'season')

    p_dict = {
        "name": [],
        "team": [],
        "positions": [],
        "ab": [],
        "avg": [],
        "hr": [],
        "rbi": [],
        "sb": [],
        "term": []
    }

    for player_stats, term in zip([player_stats_week, player_stats_month, player_stats_season],
                                  ['week', 'month', 'season']):
        for details, stats in zip(player_details, player_stats):
            if stats['AVG'] == '-':
                # Skip players without any at-bats.
                continue
            p_dict['name'].append(unidecode(details['name']['full']))
            p_dict['team'].append(standardize_team_names(details['editorial_team_abbr']))
            p_dict['positions'].append(','.join([pos['position'] \
                                                for pos in details['eligible_positions'] \
                                                if pos['position'] != 'Util']))
            p_dict['ab'].append(int(stats['H/AB'].split('/')[-1]))

            p_dict['avg'].append(stats['AVG'])
            p_dict['hr'].append(int(stats['HR']))
            p_dict['rbi'].append(int(stats['RBI']))
            p_dict['sb'].append(int(stats['SB']))
            p_dict['term'].append(term)

    # Collect yahoo stats into DF
    y_df = pl.DataFrame(p_dict)

    # Now get full-season stats with pybaseball
    p_df = pl.from_pandas(pb.batting_stats(2025, qual=70)[['Name', 'Team', 'wRC+', 'xwOBA']])
    p_df = p_df.rename({"Name": "name", "Team": "team"})

    p_df = p_df.with_columns(pl.col('xwOBA').cast(pl.Decimal(10, 3)))

    # Add a last_name column to both dataframes for the join (different sources might have
    # different versions of first names)
    p_df = p_df.with_columns(
        (pl.col("name").str.split(" ").list.slice(1, None).list.join(" ")).alias("last_name")
    )
    y_df = y_df.with_columns(
        (pl.col("name").str.split(" ").list.slice(1, None).list.join(" ")).alias("last_name")
    )

    # Join the two DFs and return
    df = y_df.join(p_df, how='inner', on=['last_name', 'team'])
    df = df.drop("name_right")
    df = df.drop("last_name")

    return df


def filter_free_agents(fa_df: pl.DataFrame, t_df: pl.DataFrame, position: str) -> pl.DataFrame:
    """
    Given DFs containing stats for both the free agents and players on our team, convert the
    averages for each metric for players on our team and filter out every free agent that
    isn't above-average in at least one category.

    Hitters need to be above average in 2 of the given stats to appear, whereas pitchers need
    3.
    
    These comparisons are done only for stats across the last month.

    :param pl.DataFrame fa_df: DF containing free agent data
    :param pl.DataFrame t_df: DF containing data from players on our team
    :param str position: The position we're comparing
    :return pl.DataFrame: DF containing all players that met the filter conditions, as well 
                          as players on our team.
    """

    if position in {'1B', '2B', '3B', 'C', 'OF'}:
        stats = ['avg', 'rbi', 'hr', 'wRC+', 'xwOBA']
        combo_num = 2
    else:
        stats = ['k', 'era', 'xERA', 'Stuff+']
        combo_num = 3
        if position == 'SP':
            stats.append('w')

    base_fa_df = fa_df.clone()

    # Filter both dataframes to only contain stats from this past month
    t_df = t_df.filter(pl.col('term') == 'month')
    fa_df = fa_df.filter(pl.col('term') == 'month')

    # Get the averages among players on our team
    avg = {}
    for stat in stats:
        avg[stat]= float(t_df.select(pl.mean(stat)).item())

    final_df = pl.DataFrame()
    for stat_combo in list(combinations(stats, combo_num)):
        filtered_df = fa_df.clone()
        for stat in stat_combo:
            if stat in {'era', 'xERA'}:
                filtered_df = filtered_df.filter(pl.col(stat) <= avg[stat])
            else:
                filtered_df = filtered_df.filter(pl.col(stat) >= avg[stat])
        if not final_df.is_empty():
            final_df = pl.concat([final_df, filtered_df])
        else:
            final_df = filtered_df.clone()

    # If looking at relievers, include anyone with a save recently
    if position == 'RP':
        filtered_df = fa_df.clone()
        filtered_df = filtered_df.filter(pl.col('sv') > 2)
        final_df = pl.concat([final_df, filtered_df])

    names_to_include = list(set(final_df['name']))

    final_df = base_fa_df.filter(pl.col('name').is_in(names_to_include))
    final_df = final_df.unique(subset=['name', 'team', 'term'], maintain_order=True)

    return final_df


def main(position: str, output_filename: str = 'fantasy_data.csv') -> None:
    """
    Script used to generate a DataFrame that will be used plot reports comparing Free Agents
    in a Yahoo Fantasy Baseball league to the players on my team.

    Uses the Yahoo Fantasy API to pull data for all free agents and compare their stats to 
    players on my team, then creates a DataFrame with statistics for every player who 
    outperforms those on my team, some from the fantasy API and some from pybaseball.

    :param str position: Player position for which to compare.
    :param str output_filename: Name of the output CSV.
    """

    session = create_session()
    game = yfa.Game(session, 'mlb')
    league = yfa.League(session, game.league_ids()[1])

    t_df = get_players_from_own_team(position, league, session)
    fa_df = get_free_agents(position, league)
    filtered_fa_df = filter_free_agents(fa_df, t_df, position)

    t_df = t_df.with_columns((pl.lit(True)).alias('on_team'))
    filtered_fa_df = filtered_fa_df.with_columns((pl.lit(False)).alias('on_team'))

    final_df = pl.concat([t_df, filtered_fa_df])

    # Rename some columns for presentation purposes
    if position in {'1B', '2B', '3B', 'C', 'OF'}:
        final_df = final_df.rename({
            "name": "Name",
            "team": "Team",
            "positions": "Position(s)",
            "avg": "AVG",
            "ab": "ABs",
            "hr": "HRs",
            "rbi": "RBIs",
            "sb": "SBs"
        })
    else:
        final_df = final_df.rename({
            "name": "Name",
            "team": "Team",
            "positions": "Position(s)",
            "ip": "IP",
            "k": "Ks",
            "w": "Ws",
            "sv": "SVs",
            "era": "ERA",
            "whip": "WHIP",
        })

    final_df.write_csv(output_filename)


def dashboard_main():
    """
    Alternative main function to be called when the script is invoked with the `--for_dashboard`
    flag.

    Prepares data to be used for the corresponding dashboard, so gather data for all positions and
    store separately for use.
    """
    for pos in POSITIONS:
        print(f"Gathering data for {pos}...")
        main(position=pos, output_filename=f'fantasy_data_{pos}.csv')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--position', type=str, default="",
                        choices=POSITIONS,
                        help='Position for which to display free agents.')
    parser.add_argument('-f', '--output_filename', default='fantasy_data.csv')
    parser.add_argument('--for_dashboard', action='store_true', default=False,
                        help="Option for when collecting data for the dashboard. If enabled, \"" \
                             "gathers data for all positions and multiple terms.")
    args = parser.parse_args()

    if args.for_dashboard:
        dashboard_main()
    else:
        main(position=args.position, output_filename=args.output_filename)
