import polars as pl
import pandas as pd


def fix_teams_for_traded_pitchers(df):
    """
    For players who have played on multiple teams, replace their team abbreviation
    with the actual current team.
    Supports both pandas and polars DataFrames.
    """
    is_pandas = isinstance(df, pd.DataFrame)
    if is_pandas:
        ldf = pl.from_pandas(df)
    else:
        ldf = df

    traded_db = {
        "Tarik Skubal": "LAD",
        "Freddy Peralta": "TBR",
        "Kevin Gausman": "CHC",
        "Tyler Mahle": "ATL",
        "Huascar Brazoban": "CHW",
        "Camilo Doval": "PIT",
        "Bailey Falter": "ATL",
        "Dean Kremer": "MIN",
        "A.J. Minter": "MIN",
        "Chase Silseth": "TEX",
        "Jameson Taillon": "TOR",
        "Aaron Civale": "CHC",
        "Codi Heuer": "MIL",
        "Craig Yoho": "CLE",
        "Casey Mize": "SDP",
        "Foster Griffin": "CLE",
        "Clay Holmes": "CHC",
        "Dustin May": "MIL",
        "JoJo Romero": "MIL",
        "Luke Weaver": "PIT",
        "Kris Bubic": "LAD",
        "Robbie Ray": "SDP",
        "Tyler Wells": "TBR",
        "Ryan Zeferjahn": "CHC",
        "Braxton Garrett": "CHC",
        "Antonio Senzatela": "MIL",
        "Jeff Hoffman": "MIN",
        "Erik Miller": "BOS",
        "Brooks Raley": "PHI",
        "Brent Suter": "ATL",
        "Jose Soriano": "TOR",
        "Caleb Kilian": "PHI",
        "Luis Castillo": "CHW",
        "Kirby Yates": "PIT",
        "Hunter Stratton": "SDP",
        "Lake Bachar": "PIT",
        "Caleb Ferguson": "STL",
        "Seranthony Dominguez": "CHW",
        "Jose Urquidy": "CHW",
        "Seth Halvorsen": "LAD",
        "Nick Frasso": "COL",
        "Landyn Vidourek": "COL",
        "Anthony Molina": "SFG",
        "Victor Vodnik": "MIA",
    }

    ldf = ldf.with_columns(
        pl.col("Name").replace(traded_db, default=pl.col("team")).alias("team")
    )

    if is_pandas:
        return ldf.to_pandas()
    return ldf


def fix_teams_for_traded_batters(df):
    """
    For players who have played on multiple teams, replace their team abbreviation
    with the actual current team.
    Supports both pandas and polars DataFrames.
    """
    is_pandas = isinstance(df, pd.DataFrame)
    if is_pandas:
        ldf = pl.from_pandas(df)
    else:
        ldf = df

    traded_db = {
        "Adley Rutschman": "BOS",
        "Luis Arraez": "PHI",
        "Heliot Ramos": "NYY",
        "Daulton Varsho": "HOU",
        "Lane Thomas": "ATL",
        "Blake Perkins": "CLE",
        "Bo Naylor": "MIL",
        "Logan O'Hoppe": "TEX",
        "Luis Garcia Jr.": "NYY",
        "Lars Nootbaar": "ARI",
        "Nathaniel Lowe": "CLE",
        "Ben Rortvedt": "LAD",
        "Eli White": "BOS",
        "Joey Bart": "CHW",
        "Liam Hicks": "TBR",
        "Taylor Ward": "SEA",
        "Jo Adell": "CLE",
        "Brenton Doyle": "CHW",
        "Josh Smith": "TOR",
        "Curtis Mead": "BOS",
        "Marcelo Mayer": "SFG",
        "Tyrone Taylor": "CHC",
        "Juan Brito": "CIN",
        "Colby Thomas": "PHI",
        "Rece Hinds": "BAL",
        "Jack Suwinski": "TBR",
        "Christian Franklin": "BAL",
        "Nolan Jones": "CHW",
        "Jake Rogers": "BOS",
    }

    ldf = ldf.with_columns(
        pl.col("Name").replace(traded_db, default=pl.col("team")).alias("team")
    )

    if is_pandas:
        return ldf.to_pandas()
    return ldf
