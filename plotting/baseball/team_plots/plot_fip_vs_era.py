import argparse
from datetime import datetime
import pybaseball

from plotting.base_plots.ratio_scatter import RatioScatterPlot


def main(year):
    """
    Main function gets the data from fangraphs via pybaseball and calls the plot methods.

    :param int year: Year for which to gather data.
    """
    df = pybaseball.team_pitching(year)
    df = df[['Team', 'ERA', 'FIP']]
    df['team'] = df['Team']

    avg_era = df['ERA'].mean()
    avg_fip = df['FIP'].mean()

    plot = RatioScatterPlot(dataframe=df, filename='era_v_fip.png',
                            x_column='ERA', y_column='FIP',
                            title='Team Pitching: ERA vs FIP',
                            sport='baseball',
                            scale='team',
                            x_label='Team ERA',
                            y_label='Team FIP',
                            plot_x_mean=True, plot_y_mean=True,
                            scale_to_extreme=True,
                            plot_league_average=avg_era,
                            quadrant_labels=['RESULTS', 'PROCESS'])

    plot.make_plot()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--year', type=int, default=datetime.now().year,
                        help='Year for which to get data, defaults to current year')
    args = parser.parse_args()

    main(year=args.year)
