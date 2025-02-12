import argparse
import pandas as pd

from numpy import array
from plotting.base_plots.rolling_average import RollingAveragePlot
from plotting.base_plots.multiplot import MultiPlot


def xg_by_division_multiplot():
    """
    Plot each teams rolling 10-game average, in a 2x2 plot where each plot shows
    all the teams in one division.
    """
    atl = {'teams': {'TOR', 'TBL', 'BOS', 'DET', 'MTL', 'OTT', 'FLA', 'BUF'},
           'name': 'Atlantic'}
    met = {'teams': {'NYR', 'NYI', 'NJD', 'CAR', 'CBJ', 'PIT', 'WSH', 'PHI'},
           'name': 'Metropolitan'}
    pac = {'teams': {'VAN', 'CGY', 'EDM', 'ANA', 'VGK', 'SJS', 'LAK', 'SEA'},
           'name': 'Pacific'}
    cen = {'teams': {'COL', 'DAL', 'WPG', 'STL', 'ARI', 'MIN', 'CHI', 'NSH'},
           'name': 'Central'}

    df = pd.read_csv('data/xGoalsPercentage_rolling_avg.csv')
    df['xGoalsPercentageRollingAvg'] = df.apply(lambda row:
                                                round(row['xGoalsPercentageRollingAvg'] * 100, 2), 1)
    plots = []
    for div in [atl, met, pac, cen]:
        div_df = df[df['team'].isin(div['teams'])]
        div_plot = RollingAveragePlot(dataframe=div_df, filename='',
                                      x_column='gameNumber',
                                      y_column='xGoalsPercentageRollingAvg',
                                      title=div['name'], x_label='Game #',
                                      y_label='5v5 xG% - 10-Game Rolling Average',
                                      multiline_key='team', add_team_logos=True)

        plots.append(div_plot)


    arrangement = {
        "dimensions": (9, 2),
        "plots": [
            {
                "plot": plots[0],
                "position": (0, 0),
                "rowspan": 4
            },
            {
                "plot": plots[1],
                "position": (0, 1),
                "rowspan": 4
            },
            {
                "plot": plots[2],
                "position": (4, 0),
                "rowspan": 4
            },
            {
                "plot": plots[3],
                "position": (4, 1),
                "rowspan": 4
            }
        ]
    }

    multiplot = MultiPlot(arrangement=arrangement, filename='xg_rolling_avg_by_division',
                          title='5v5 Expected Goal Share 10-Game Rolling Average\n'\
                                'Over the Last 25 Games')

    multiplot.make_multiplot()


def main(type):
    """
    Main function which disambiguates the stat to be plotted, calls the plotting methods
    and saves the output.
    """
    if type == 'xg_by_division':
        xg_by_division_multiplot()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', default='xg_by_division',
                        const='xg_by_division',
                        nargs='?',
                        choices=['xg_by_division'])
    args = parser.parse_args()
    main(args.type)
