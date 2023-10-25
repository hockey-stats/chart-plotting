import os
import argparse
import pandas as pd
from util.team_maps import nst_team_mapping, eh_team_mapping


"""
Script to read in the three team tables and compile them all into a single table 
containing averages (when applicable) for each of:
    xGF/xGA per hour
    CF/CA per hour
    GF/GA per hour
    Sh%
    Sv%
    GF-xGF/GA-xGA per hour
"""

# Disable an annoying warning
pd.options.mode.chained_assignment = None


def convert_raw_to_ph(total_toi, flat_total, team):
    rate_value = round(flat_total * (60.0/ total_toi), 2)
    return rate_value


def read_nst_table(path):
    df = pd.read_csv(os.path.join(path, 'nst_team_table.csv'))
    df['Team'] = df.apply(lambda row: nst_team_mapping[row['Team']], axis=1)
    df = df.sort_values(by=['Team'])
    df.index = df.Team
    return df


def read_mp_table(path):
    df = pd.read_csv(os.path.join(path, 'mp_team_table.csv'), 
            usecols=['team', 'situation', 'iceTime', 
                     'flurryScoreVenueAdjustedxGoalsFor', 'flurryScoreVenueAdjustedxGoalsAgainst'])
    df = df[df['situation'] == '5on5'].sort_values(by=['team'])
    df.index = df.team
    return df


def read_eh_table(path):
    df = pd.read_csv(os.path.join(path, 'eh_team_table.csv')).sort_values(by=['Team'])
    df['Team'] = df.apply(lambda row: eh_team_mapping.get(row['Team'], row['Team']), axis=1)
    df.index = df.Team
    return df


def main(path):
    #eh_df = read_eh_table(path)
    nst_df = read_nst_table(path)
    mp_df = read_mp_table(path)

    print(nst_df.columns)
    df = mp_df[['team', 'iceTime']]
    df['Sh%'] = nst_df['SH%']
    df['Sv%'] = nst_df['SV%']
    df['CFph'] = nst_df['CF/60']
    df['CAph'] = nst_df['CA/60']
    df['GFph'] = nst_df['GF/60']
    df['GAph'] = nst_df['GA/60']
    #df['eh_xGFph'] = eh_df['xGF/60']
    #df['eh_xGAph'] = eh_df['xGA/60']
    df['mp_xGFph'] = list(mp_df.apply(lambda row: convert_raw_to_ph(row['iceTime'] / 60.0, 
                                                                    row['flurryScoreVenueAdjustedxGoalsFor'], 
                                                                    row['team']), axis=1))
    df['mp_xGAph'] = list(mp_df.apply(lambda row: convert_raw_to_ph(row['iceTime'] / 60.0, 
                                                                    row['flurryScoreVenueAdjustedxGoalsAgainst'], 
                                                                    row['team']), axis=1))
    df['nst_xGFph'] = nst_df['xGF/60']
    df['nst_xGAph'] = nst_df['xGA/60']

    df['xGFph'] = df.apply(lambda row: round((row['nst_xGFph'] + row['mp_xGFph']) / 2, 2), axis=1)
    df['xGAph'] = df.apply(lambda row: round((row['nst_xGAph'] + row['mp_xGAph']) / 2, 2), axis=1)

    df.to_csv(os.path.join(path, 'team_ratios.csv'), columns=['Sh%', 'Sv%', 'CFph', 'CAph', 'GFph', 
                                                              'GAph', 'xGFph', 'xGAph'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', default=os.path.join(os.getcwd(), 'data'), 
                        help='Path to base folder of repo')
    args = parser.parse_args()
    
    main(path=args.path)
