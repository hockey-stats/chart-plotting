"""
Script used to create layered lollipop plots to demonstrate team actual vs expected
performance on special teams.
"""

import os
import argparse
import pandas as pd

from plotting.plot import LayeredLollipopPlot


def make_5on4_plot(base_df):
    """
    Given DataFrame, create plot for 5on4.
    """

    pp_plot = LayeredLollipopPlot(dataframe=base_df, filename='5on4_offence.png',
                                  value_a='GFph', value_b='xGFph',
                                  title='5-on-4 Goals For by Team, Actual vs Expected',
                                  y_label='5-on-4 Goals For per hour',
                                  x_label='Teams, by Actual 5-on-4 Goals For per hour',
                                  size=(14, 6),
                                  value_a_label='Actual Goals',
                                  value_b_label='Expected Goals')
    pp_plot.make_plot()


def make_4on5_plot(base_df):
    """
    Given DataFrame, create plot for 4on5.
    """

    pk_plot = LayeredLollipopPlot(dataframe=base_df, filename='4on5_defence.png',
                                  value_a='GAph', value_b='xGAph',
                                  title='4-on-5 Goals Against by Team, Actual vs Expected',
                                  y_label='4-on-5 Goals Against per hour',
                                  x_label='Teams, by Actual 4-on-5 Goals Against per hour',
                                  size=(14, 6),
                                  value_a_label='Actual Goals',
                                  value_b_label='Expected Goals')
    pk_plot.make_plot()


def main(situation):
    """
    Main function which disambiguates and calls appropriate plotting function based on provided
    situation.
    """
    base_df = pd.read_csv(os.path.join('data', 'special_teams_ratios.csv'))

    if situation == '5on4':
        make_5on4_plot(base_df)

    elif situation == '4on5':
        make_4on5_plot(base_df)

    else:
        raise NotImplementedError("Unsupported situation provided. Options are '5on4' and '4on5'.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--situation', default='5on4',
                        help='Given game state for which to process table.')
    args = parser.parse_args()

    main(situation=args.situation)