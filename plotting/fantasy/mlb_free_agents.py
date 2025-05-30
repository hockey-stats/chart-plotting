import argparse
import polars as pl

from plotting.base_plots.ratio_scatter import RatioScatterPlot


def main(position: str) -> None:
    """
    Script that will generate a fantasy free-agency plot for baseball fantasy leagues.

    :param str position: Position we're looking at free agents for.
    """

    df = pl.read_csv('fantasy_data.csv').to_pandas()

    if position in {'1B', '2B', '3B', 'C', 'OF'}:
        x = 'xwOBA'
        y = 'wRC+'
        invert_x = False
    else:
        x = 'xERA'
        y = 'Stuff+'
        invert_x = True

    plot = RatioScatterPlot(df, filename='fantasy_plot.png',
                            y_column=y, x_column=x,
                            title=f'Interesting Free Agents - {position}',
                            y_label=y, x_label=x,
                            quadrant_labels=None,
                            invert_x=invert_x,
                            size=(10, 15),
                            break_even_line=False,
                            scale='player',
                            data_disclaimer='fangraphs',
                            sport='baseball',
                            fantasy_mode=True)

    plot.make_plot()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--position', type=str, required=True,
                        choices=['1B', '2B', '3B', 'C', 'OF', 'P', 'SP', 'RP'],
                        help='Position for which to display free agents.')
    args = parser.parse_args()

    main(args.position.upper())
