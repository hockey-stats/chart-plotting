import pyhockey as ph

from hockey.skater_plots.plot_skater_points import main


if __name__ == '__main__':
    teams = list(ph.team_seasons(season=2025, situation='all')['team'])
    teams = set(teams)

    for team in teams:
        main(team=team, season=2025, min_icetime_minutes=150, situation='5on5')
