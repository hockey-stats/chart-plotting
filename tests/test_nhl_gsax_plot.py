import pyhockey as ph

from hockey.goalie_plots.games_by_gsax_bar_chart import main


if __name__ == '__main__':
    teams = list(ph.team_seasons(season=2025, situation='all')['team'])
    teams = set(teams)

    for team in teams:
        main(team=team, season=2025)
