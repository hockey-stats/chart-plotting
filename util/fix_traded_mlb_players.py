import pandas as pd


def fix_teams_for_traded_pitchers(df: pd.DataFrame) -> pd.DataFrame:
    """
    For players who have played on multiple teams, fangraphs returns their 'Team' value as
    '- - -'. Replace these values with the actual current team.
    """
    traded_players = list(df[df['team'] == '- - -']['Name'])
    traded_db = {
        'Jordan Hicks': 'BOS',
        'Sean Newcomb': 'ATH',
        'Tyler Alexander': 'CHW',
        'Aaron Civale': 'CHW',
        'Bryan Baker': 'TBR',
        'Joey Wentz': 'ATL',
        'Carlos Hernandez': 'DET',
        'Jorge Alcala': 'BOS',
        'Lou Trivino': 'LAD',
        'Scott Blewett': 'BAL',
        'Luis Garcia': 'LAA',
        'Andrew Chafin': 'LAA',
        'Jake Eder': 'WSN',
        'Tyler Kinley': 'ATL',
        'Austin Smith': 'COL',
        'Gage Ziehl': 'CWS',
        'Seranthony Dominguez': 'TOR',
        'Carlos Carrasco': 'ATL',
        'Chris Paddack': 'DET',
        'Randy Dobnak': 'DET',
        'Amed Rosario': 'NYY',
        'Randal Grichuk': 'KCR',
        "Ke'Byran Hayes": "CIN",
        "Mason Miller": "SDP",
        "JP Sears": "SDP",
        "Shane Bieber": "TOR",
        "Steven Matz": "BOS",
        "Andrew Kittredge": "CHI",
        "Zack Litell": "CIN",
        "Rafael Montero": "DET",
        "Michael Soroka": "CHI",
        "Ryan Helsley": "NYM",
        "Jhoan Duran": "PHI",
        "Mick Abel": "MIN",
        "Caleb Ferguson": "SEA",
        "Tyler Rogers": "NYM",
        "Taylor Rogers": "PIT",
        "Charlie Morton": "DET",
        "Shelby Miller": "MIL",
        "Jordan Montgomery": "MIL",
        "Phil Maton": "TEX",
        "Louie Varland": "TOR",
        "Griffin Jax": "TBR",
        "Camilo Doval": "NYY",
        "Bailey Falter": "KCR",
        "Adrian Houser": "TBR",
        "Nestor Cortes": "SDP",
        "Dustin May": "BOS",
        "Merril Kelly": "TEX",
        "Jake Bird": "NYY",
        "David Bednar": "NYY",
        "Codei Heuer": "DET",
        "Paul Sewald": "DET",
        "Brock Stewart": "LAD",
        "Kyle Finnegan": "DET",
    }

    for name in traded_players:
        if name in traded_db:
            index = df[df['Name'] == name].index
            df.loc[index, 'team'] = traded_db[name]

    return df


def fix_teams_for_traded_batters(df: pd.DataFrame) -> pd.DataFrame:
    """
    For players who have played on multiple teams, fangraphs returns their 'Team' value as
    '- - -'. Replace these values with the actual current team.
    """
    traded_players = list(df[df['team'] == '- - -']['Name'])
    traded_db = {
        'Rafael Devers': 'SFG',
        'Kody Clemens': 'MIN',
        'Matt Thaiss': 'TBR',
        'Austin Wynns': 'ATH',
        'Garret Hampson': 'STL',
        'Jonah Bride': 'MIN',
        'Leody Taveras': 'SEA',
        'LaMonte Wade Jr.': 'LAA',
        'Josh Naylor': 'SEA',
        'Ryan McMahon': 'NYY',
        'Sam Brown': 'WSN',
        'Austin Slater': 'NYY',
        'Nick Fortes': 'TBR',
        'Matthew Etzel': 'MIA',
        'Danny Jansen': 'MIL',
        'Andrew Hoffman': 'ARI',
        "Ramon Urias": "HOU",
        "Eugenio Suarez": "SEA",
        "Mike Yastrzemski": "KCR",
        "Miguel Andujar": "CIN",
        "Ty France": "TOR",
        "Alan Roden": "MIN",
        "Jose Caballero": "NYY",
        "Oswald Peraza": "LAA",
        "Willi Castro": "CHC",
        "Jesus Sanchez": "TEX",
        "Ryan O'Hearn": "SDP",
        "Ramon Laureano": "SDP",
        "Carlos Correa": "HOU",
        "Cedric Mullins": "NYM",
        "Harrison Bader": "PHI",
        "Andrew Vaughn": "MIL"
    }
    for name in traded_players:
        if name in traded_db:
            index = df[df['Name'] == name].index
            df.loc[index, 'team'] = traded_db[name]

    return df
