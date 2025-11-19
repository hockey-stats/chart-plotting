
import pyhockey as ph

from hockey.game_report.assemble_report import main


if __name__ == '__main__':
    games = list(ph.skater_games(season=2025)['gameID'])
    games = set(games[0:10])

    for game in games:
        main(game_id=game, filename='test_report.png', season=2025)
