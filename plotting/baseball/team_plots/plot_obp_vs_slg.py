import argparse
from datetime import datetime
import pybaseball

from plotting.base_plots.ratio_scatter import RatioScatterPlot


def main(year):
    """
    Main function gets the data from fangraphs via pybaseball and calls the plot methods.

    :param int year: Year for which to gather data.
    """
    df = pybaseball.team_batting(year)
    df = df[['Team', 'OBP', 'SLG']]

    df['team'] = df['Team']
    del df['Team']

    plot = RatioScatterPlot(dataframe=df, filename='obp_vs_slg.png',
                            x_column='OBP', y_column='SLG',
                            title='Team Batting - On-Base % vs Slugging %',
                            sport='baseball',
                            scale='team',
                            x_label='Team On-Base %',
                            y_label='Team Slugging %',
                            break_even_line=False,
                            plot_x_mean=True, plot_y_mean=True,
                            scale_to_extreme=False,
                            #plot_league_average=avg_slg,
                            quadrant_labels=['POWER', 'TRAFFIC'])

    plot.make_plot()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--year', type=int, default=datetime.now().year,
                        help='Year for which to get data, defaults to current year')
    args = parser.parse_args()

    main(year=args.year)
