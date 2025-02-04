import os
import pandas as pd

from plotting.base_plots.scoreboard import ScoreBoardPlot


def main(s_df, g_df):
    plot = ScoreBoardPlot(filename='test.png', skater_df=s_df, goalie_df=g_df)

    plot.make_plot()


if __name__ == '__main__':
    skater_df = pd.read_csv(os.path.join('data', '20844_skaters.csv'), encoding='utf-8-sig')
    goalie_df = pd.read_csv(os.path.join('data', '20844_goalies.csv'), encoding='utf-8-sig')

    main(skater_df, goalie_df)
