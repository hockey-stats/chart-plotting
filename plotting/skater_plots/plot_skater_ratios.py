import os
import argparse
import pandas as pd

from plotting.plot import RatioScatterPlot

"""
Script used to plot on-ice ratios for individual players.
"""

def main(team, min_icetime):
  base_df = pd.read_csv(os.path.join('data', 'player_ratios.csv'))
  xg_filename = f'{team}_player_xg_ratios.png' if team is not None else 'player_xg_ratios.png'
  g_filename = f'{team}_player_g_ratios.png' if team is not None else 'player_g_ratios.png'

  if team != "ALL":
    base_df = base_df[base_df['team'] == team]
  # Apply minimum icetime
  base_df = base_df[base_df['icetime'] >= (min_icetime * 60)]

  xg_plot = RatioScatterPlot(dataframe=base_df, filename=xg_filename, x_column='xGFph', y_column='xGAph',
                             title=f'{team} Player xG Rates (5v5)', scale='player',
                             x_label='Expected Goals For per hour', y_label='Expected Goals Against per hour (inverted)',
                             ratio_lines=True, invert_y=True, plot_x_mean=False, plot_y_mean=False,
                             quadrant_labels=(('DULL', 'GOOD'), ('BAD', 'FUN')))
  xg_plot.make_plot()

  g_plot = RatioScatterPlot(dataframe=base_df, filename=g_filename, x_column='GFph', y_column='GAph',
                            title=f'{team} Player G Rates (5v5)', scale='player',
                            x_label='Goals For per hour', y_label='Goals Against per hour (inverted)',
                            ratio_lines=True, invert_y=True, plot_x_mean=False, plot_y_mean=False,
                            quadrant_labels=(('DULL', 'GOOD'), ('BAD', 'FUN')))
  g_plot.make_plot()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-t', '--team', type=str, default='ALL',
                      help='Team to get stats for, defaults to ALL.')
  parser.add_argument('-i', '--min_icetime', type=int, default=0,
                      help='Minimum icetime, in minutes cuttoff for players (defaults to 0')
  args = parser.parse_args()

  main(team=args.team, min_icetime=args.min_icetime)