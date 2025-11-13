import argparse
from datetime import datetime

import polars as pl
import pybaseball as pyb

from plot_types.ratio_scatter import RatioScatterPlot


def main(year: int):
    """
    Main function gets the data from fangraphs via pybaseball and calls the plot methods.

    :param int year: Year for which to gather data.
    """
    # Getting runs scored/allowed from batting/pitching stats, resp.
    p_df = pl.from_pandas(pyb.team_pitching(2025)[['Team', 'GS', 'R']])
    b_df = pl.from_pandas(pyb.team_batting(2025)[['Team', 'R']])

    # Rename columns from 'R' to 'RA' or 'RS' for runs scored/allowed
    p_df = p_df.rename({"R": "RA"})
    b_df = b_df.rename({"R": "RS"})

    # Join into a single DF
    df = p_df.join(b_df, how='inner', on=['Team'])
    df = df.rename({"Team": "team"})

    league_avg = float(df.select(pl.mean('RS')).item())

    plot = RatioScatterPlot(dataframe=df.to_pandas(), filename="team_run_diff.png",
                            title='Runs Scored vs Runs Allowed for All Teams',
                            y_column='RA', y_label='Runs Allowed (Reversed)',
                            invert_y=True,
                            x_column='RS', x_label='Runs Scored',
                            scale='team', sport='baseball',
                            break_even_line=True,
                            plot_x_mean=True, plot_y_mean=True,
                            scale_to_extreme=True,
                            ratio_lines=True,
                            plot_league_average=league_avg,
                            quadrant_labels=['OFFENSE', 'DEFENSE'],
                            data_disclaimer='fangraphs')
    
    plot.make_plot()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--year', type=int, default=datetime.now().year,
                        help='Year for which to get data, defaults to current year')
    args = parser.parse_args()

    main(year=args.year)
