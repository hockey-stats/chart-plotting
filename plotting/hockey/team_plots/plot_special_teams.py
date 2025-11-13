"""
Script used to create layered lollipop plots to demonstrate team actual vs expected
performance on special teams.
"""

import argparse
from datetime import datetime

import pyhockey as ph

from plotting.base_plots.layered_lollipop import LayeredLollipopPlot


def make_5on4_plot(base_df):
    """
    Given DataFrame, create plot for 5on4.
    """

    pp_plot = LayeredLollipopPlot(dataframe=base_df, filename='5on4_offence.png',
                                  value_a='goalsForPerHour', value_b='xGoalsForPerHour',
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
                                  value_a='goalsAgainstPerHour', value_b='xGoalsAgainstPerHour',
                                  inverse_rank=True,
                                  title='4-on-5 Goals Against by Team, Actual vs Expected',
                                  y_label='4-on-5 Goals Against per hour',
                                  x_label='Teams, by Actual 4-on-5 Goals Against per hour',
                                  size=(14, 6),
                                  value_a_label='Actual Goals',
                                  value_b_label='Expected Goals',
                                  legend_loc='upper left')
    pk_plot.make_plot()


def main(situation, season):
    """
    Main function which disambiguates and calls appropriate plotting function based on provided
    situation.
    """
    base_df = ph.team_summary(situation=situation, season=season)

    if situation == '5on4':
        make_5on4_plot(base_df)

    elif situation == '4on5':
        make_4on5_plot(base_df)

    else:
        raise NotImplementedError("Unsupported situation provided. Options are '5on4' and '4on5'.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--situation', default='5on4',
                        help='Given game state for which to process table, e.g. 5on4 or 4on5')
    parser.add_argument('--season', type=int,
                        default=datetime.now().year - 1 if datetime.now().month < 10 \
                                else datetime.now().year,
                        help='Season for which we pull data')
    args = parser.parse_args()

    main(situation=args.situation, season=args.season)
