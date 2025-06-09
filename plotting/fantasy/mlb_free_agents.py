import argparse
import polars as pl

from plotting.base_plots.ratio_scatter import RatioScatterPlot


def main(position: str, dashboard: bool = False, term=None) -> None:
    """
    Script that will generate a fantasy free-agency plot for baseball fantasy leagues.

    :param str position: Position we're looking at free agents for.
    :param bool dashboard: If True, returns the plot figure object instead of saving it as
                           an image. This is used by panel to create dashboards.
    """


    if position in {'1B', '2B', '3B', 'SS', 'C', 'OF'}:
        x = 'xwOBA'
        y = 'wRC+'
    else:
        x = 'K-BB%'
        y = 'Stuff+'

    if dashboard:
        df = pl.read_csv(f"data/fantasy_data_{position}.csv").to_pandas()
        df = df[df['term'] == term]
    else:
        df = pl.read_csv('fantasy_data.csv').to_pandas()

    plot = RatioScatterPlot(df, filename='fantasy_plot.png',
                            y_column=y, x_column=x,
                            title=f'Interesting Free Agents - {position}',
                            y_label=y, x_label=x,
                            quadrant_labels=None,
                            invert_x=False,
                            #size=(10, 15),
                            break_even_line=False,
                            scale='player',
                            data_disclaimer='fangraphs',
                            sport='baseball',
                            fantasy_mode=True)

    if dashboard:
        fig = plot.make_plot(dashboard=True)
        return fig
    else:
        plot.make_plot()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--position', type=str, required=True,
                        choices=['1B', '2B', '3B', 'C', 'SS', 'OF', 'P', 'SP', 'RP'],
                        help='Position for which to display free agents.')
    args = parser.parse_args()

    main(args.position.upper())
