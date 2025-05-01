import argparse
from datetime import datetime
import pybaseball

from plotting.base_plots.swarm import SwarmPlot



def main(year, qual, team):
    data = pybaseball.batting_stats(year, qual=qual)[['Team', 'Name', 'AB', 'wRC+']]
    data['team'] = data['Team']

    plot = SwarmPlot(dataframe=data,
                      filename=f'{team}_wrc.png',
                      column='wRC+',
                      team=team,
                      y_label='wRC+',
                      title=f'{team} Hitters by wRC+',
                      subtitle=f'Compared to league distribution, min. {qual} PAs')
    
    plot.make_plot()




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--year', type=int, default=datetime.now().year,
                        help='Year for which to get data, defaults to current year')
    parser.add_argument('-q', '--qual', default=20, type=int,
                        help='Minimum plate appearances to qualify in query, defaults to 15')
    parser.add_argument('-t', '--team', required=True, type=str,
                        help='Team for which players should be highlighted.')
    args = parser.parse_args()

    main(year=args.year, qual=args.qual, team=args.team)

