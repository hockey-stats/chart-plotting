import pybaseball as pyb
import polars as pl
from unidecode import unidecode

def get_park_factor(team):

    mapping= {
        'Angels': 101.23049020767212,
        'Astros': 99.48140382766724,
        'Athletics': 102.86766290664673,
        'Blue Jays': 99.45313930511475,
        'Braves': 100.12708902359009,
        'Brewers': 98.89779090881348,
        'Cardinals': 97.5001335144043,
        'Cubs': 97.8569507598877,
        'Diamondbacks': 100.64197778701782,
        'Dodgers': 99.1439938545227,
        'Giants': 97.25400805473328,
        'Guardians': 98.87371063232422,
        'Mariners': 93.54020357131958,
        'Marlins': 100.99986791610718,
        'Mets': 96.34352326393127,
        'Nationals': 99.63456988334656,
        'Orioles': 98.61453771591187,
        'Padres': 95.90458273887634,
        'Phillies': 101.27016305923462,
        'Pirates': 101.54402256011963,
        'Rangers': 98.6534059047699,
        'Rays': 100.93531608581543,
        'Red Sox': 104.24087047576904,
        'Reds': 104.54981327056885,
        'Rockies': 113.34958076477051,
        'Royals': 103.06445360183716,
        'Tigers': 100.30543804168701,
        'Twins': 100.81133842468262,
        'White Sox': 100.31185150146484,
        'Yankees': 98.9298939704895
    }

    return mapping[team] / 100


def get_team_name(lev, tm):
    # Handle multi-team strings like 'Chicago,Houston' by taking the final team
    current_city = tm.split(',')[-1].strip()

    mapping = {
        ("Maj-AL", "Chicago"): "White Sox",
        ("Maj-NL", "Chicago"): "Cubs",
        ("Maj-AL", "New York"): "Yankees",
        ("Maj-NL", "New York"): "Mets",
        ("Maj-AL", "Los Angeles"): "Angels",
        ("Maj-NL", "Los Angeles"): "Dodgers",
        # Standard City -> Nickname mappings
        ("Maj-AL", "Houston"): "Astros",
        ("Maj-AL", "Detroit"): "Tigers",
        ("Maj-NL", "Philadelphia"): "Phillies",
        ("Maj-AL", "Baltimore"): "Orioles",
        ("Maj-AL", "Toronto"): "Blue Jays",
        ("Maj-NL", "Atlanta"): "Braves",
        ("Maj-NL", "Arizona"): "Diamondbacks",
        ("Maj-AL", "Tampa Bay"): "Rays",
        ("Maj-NL", "Pittsburgh"): "Pirates",
        ("Maj-AL", "Seattle"): "Mariners",
        ("Maj-NL", "San Francisco"): "Giants",
        ("Maj-AL", "Athletics"): "Athletics",
        ("Maj-AL", "Cleveland"): "Guardians",
        ("Maj-NL", "San Diego"): "Padres",
        ("Maj-AL", "Boston"): "Red Sox",
        ("Maj-NL", "Milwaukee"): "Brewers",
        ("Maj-AL", "Minnesota"): "Twins",
        ("Maj-AL", "Kansas City"): "Royals",
        ("Maj-NL", "Cincinnati"): "Reds",
        ("Maj-NL", "Miami"): "Marlins",
        ("Maj-NL", "Colorado"): "Rockies",
        ("Maj-AL", "Texas"): "Rangers",
        ("Maj-NL", "Washington"): "Nationals",
        ("Maj-NL", "St. Louis"): "Cardinals",
    }

    # Return the mapped name, or the city name if no mapping exists
    return mapping.get((lev, current_city), current_city)


def get_fg_abbreviation(row):
    """
    Maps Baseball-Reference 'Lev' and 'Tm' to FanGraphs 3-letter abbreviations.
    Handles multi-team cities using the League (Lev) as a differentiator.
    """
    # Clean the team name (handles 'Chicago,Houston' by taking the last team)
    city = row['Tm'].split(',')[-1].strip()

    mapping = {
        # Multi-team Cities
        ("Maj-AL", "Chicago"): "CHW",
        ("Maj-NL", "Chicago"): "CHC",
        ("Maj-AL", "New York"): "NYY",
        ("Maj-NL", "New York"): "NYM",
        ("Maj-AL", "Los Angeles"): "LAA",
        ("Maj-NL", "Los Angeles"): "LAD",
        
        # Standard American League
        ("Maj-AL", "Baltimore"): "BAL",
        ("Maj-AL", "Boston"): "BOS",
        ("Maj-AL", "Cleveland"): "CLE",
        ("Maj-AL", "Detroit"): "DET",
        ("Maj-AL", "Houston"): "HOU",
        ("Maj-AL", "Kansas City"): "KCR",
        ("Maj-AL", "Minnesota"): "MIN",
        ("Maj-AL", "Oakland"): "OAK",
        ("Maj-AL", "Athletics"): "OAK",
        ("Maj-AL", "Seattle"): "SEA",
        ("Maj-AL", "Tampa Bay"): "TBR",
        ("Maj-AL", "Texas"): "TEX",
        ("Maj-AL", "Toronto"): "TOR",
        
        # Standard National League
        ("Maj-NL", "Arizona"): "ARI",
        ("Maj-NL", "Atlanta"): "ATL",
        ("Maj-NL", "Cincinnati"): "CIN",
        ("Maj-NL", "Colorado"): "COL",
        ("Maj-NL", "Miami"): "MIA",
        ("Maj-NL", "Milwaukee"): "MIL",
        ("Maj-NL", "Philadelphia"): "PHI",
        ("Maj-NL", "Pittsburgh"): "PIT",
        ("Maj-NL", "San Diego"): "SDP",
        ("Maj-NL", "San Francisco"): "SFG",
        ("Maj-NL", "St. Louis"): "STL",
        ("Maj-NL", "Washington"): "WSN"
    }

    # Return the 3-letter code, or the original city name if not found
    return mapping.get((row['Lev'], city), city)


def calculate_woba(row):
    ubb = row['BB'] - row['IBB']
    singles = row['H'] - row['2B'] - row['3B'] - row['HR']
    
    # Constants
    wBB = 0.709
    wHBP = 0.740
    w1B = 0.904
    w2B = 1.281
    w3B = 1.620
    wHR = 2.080

    wOBA = ((wBB * ubb) + (wHBP * row['HBP']) + (w1B * singles) + (w2B * row['2B']) + \
            (w3B * row['3B']) + (wHR * row['HR'])) / (row['AB'] + ubb + row['SF'] + row['HBP'])

    return wOBA


def calculate_wrcplus(row: pl.DataFrame.row) -> float:
    """
    Row-wise function which caulculates wRC+ for each hitter. 

    :param pl.DataFrame.row row: Each row of the DataFrame containing hitter info
    :return float: The calculated wRC+.
    """

    # Constants supplied from Fangraphs Guts
    wOBAScale = 1.275
    avgwOBA = 0.320
    runsPerPA = 0.118
    runsPerWin = 9.851

    wRAA = ((row['wOBA'] - avgwOBA) / wOBAScale) * row['PA']

    player_team = get_team_name(row['Lev'], row['Tm'])
    parkFactor = get_park_factor(player_team)

    wRC = wRAA + (runsPerPA * row['PA'])

    wRC_p = (((wRC / row['PA']) / runsPerPA) / parkFactor * 100)

    return wRC_p



def get_detailed_batter_stats(year: int) -> pl.DataFrame:
    """
    Gets basic hitting stats from bref and calculates wRC+, also adds xWOBA from statcast.
    
    :param int year: The year for which to compute data
    :return pl.DataFrame: DataFrame with robust data for each hitter.
    """

    df = pl.from_pandas(pyb.batting_stats_bref(year))

    # Ignore players with 0 plate appearances
    df = df.filter(pl.col('PA') > 0)

    df = df.with_columns(
            pl.struct(pl.all()).map_elements(calculate_woba, return_dtype=pl.Float64).alias('wOBA')
        )

    pl.Config(tbl_rows=100, tbl_cols=40)

    df = df.with_columns(
            pl.struct(pl.all()).map_elements(
                lambda row: calculate_wrcplus(row),
                return_dtype=pl.Float64).alias('wRC+')
        )


    xdf = pl.from_pandas(pyb.statcast_batter_expected_stats(year=2026, minPA=1))
    xdf = xdf[['player_id', 'est_woba']]

    df = df.rename({'mlbID': 'player_id'})

    final_df = df.join(xdf, how='inner', on='player_id')

    final_df = final_df.with_columns(
            pl.struct(pl.all()).map_elements(get_fg_abbreviation, return_dtype=pl.String).alias('Team'),
            pl.col('wRC+').round_sig_figs(3).cast(pl.Int32),
            pl.col('Name').map_elements(
                lambda x: x.encode('latin-1').decode('unicode_escape').encode('latin-1').decode('utf-8'), 
                return_dtype=pl.String).alias('Name')
        )

    final_df = final_df.rename({
        "est_woba": "xWOBA",
        "player_id": "playerID",
        "BA": "AVG"
        })

    final_df = final_df[['Name', 'playerID', 'Team', 'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI', 'BB', 'SO', 'SB', 'AVG', 'OBP', 'OPS', 'wRC+', 'xWOBA']]

    return final_df


if __name__ == '__main__':
    df = get_detailed_batter_stats(2026)
    print(df)
