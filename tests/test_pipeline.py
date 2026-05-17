import csv
import sqlite3
import tempfile
import unittest
from pathlib import Path

from catan_ai import CatanSimulation
from catan_game import CatanGame, roadFindAdjRoads, settlementFindAdjSettlements
from scripts.validate_data import run_checks


def clear_board(game):
    for road_id in range(1, 73):
        road = game.board[f"r{road_id}"]
        road.hasRoad = False
        road.controller = None
    for settlement_id in range(1, 55):
        settlement = game.board[f"s{settlement_id}"]
        settlement.hasSettlement = False
        settlement.hasCity = False
        settlement.controller = None
        settlement.blocked = False
    for player in game.players:
        player.resources = {resource: 0 for resource in player.resources}
        player.legacyResources = {resource: 0 for resource in player.legacyResources}
        player.roadSpots.clear()
        player.settlementSpots.clear()
        player.citySpots.clear()
        player.victory_points = 0
        player.downDevs = {card: 0 for card in player.downDevs}
        player.newDevs = {card: 0 for card in player.newDevs}
        player.upDevs = {card: 0 for card in player.upDevs}
        player.largest_army = False
        player.longest_road = False
    game.bank = {resource: 19 for resource in game.bank}
    game.game_over = False
    game.winner = None
    game._refresh_all_player_options()


class BoardAdjacencyTests(unittest.TestCase):
    def test_road_adjacency_is_symmetric(self):
        for road_id in range(1, 73):
            for neighbor_id in roadFindAdjRoads(road_id):
                self.assertIn(road_id, roadFindAdjRoads(neighbor_id))

    def test_settlement_adjacency_is_symmetric(self):
        for settlement_id in range(1, 55):
            for neighbor_id in settlementFindAdjSettlements(settlement_id):
                self.assertIn(settlement_id, settlementFindAdjSettlements(neighbor_id))


class PipelineOutputTests(unittest.TestCase):
    def test_simulation_writes_csv_and_sqlite_outputs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            output_dir = tmp_path / "output"
            sqlite_path = tmp_path / "catan_analytics.db"

            simulation = CatanSimulation(num_players=4, num_games=1)
            simulation.run_simulation()
            simulation.write_outputs(output_dir)
            simulation.write_sqlite(sqlite_path)

            games_csv = output_dir / "raw" / "games.csv"
            player_games_csv = output_dir / "raw" / "player_games.csv"
            turns_csv = output_dir / "raw" / "turns.csv"
            actions_csv = output_dir / "raw" / "actions.csv"
            resource_events_csv = output_dir / "raw" / "resource_events.csv"
            resource_values_csv = output_dir / "marts" / "resource_values.csv"

            self.assertTrue(games_csv.exists())
            self.assertTrue(player_games_csv.exists())
            self.assertTrue(turns_csv.exists())
            self.assertTrue(actions_csv.exists())
            self.assertTrue(resource_events_csv.exists())
            self.assertTrue(resource_values_csv.exists())

            with games_csv.open(newline="") as csvfile:
                games = list(csv.DictReader(csvfile))
            self.assertEqual(len(games), 1)

            with player_games_csv.open(newline="") as csvfile:
                player_games = list(csv.DictReader(csvfile))
            self.assertEqual(len(player_games), 4)

            with turns_csv.open(newline="") as csvfile:
                turns = list(csv.DictReader(csvfile))
            self.assertGreater(len(turns), 0)

            with actions_csv.open(newline="") as csvfile:
                actions = list(csv.DictReader(csvfile))
            self.assertGreater(len(actions), 0)

            conn = sqlite3.connect(sqlite_path)
            try:
                game_count = conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]
                player_game_count = conn.execute("SELECT COUNT(*) FROM player_games").fetchone()[0]
                turn_count = conn.execute("SELECT COUNT(*) FROM turns").fetchone()[0]
                action_count = conn.execute("SELECT COUNT(*) FROM actions").fetchone()[0]
            finally:
                conn.close()

            self.assertEqual(game_count, 1)
            self.assertEqual(player_game_count, 4)
            self.assertEqual(turn_count, len(turns))
            self.assertEqual(action_count, len(actions))
            self.assertTrue(all(passed for _, passed in run_checks(sqlite_path)))


class FaithfulCatanRuleTests(unittest.TestCase):
    def test_game_requires_traditional_four_players(self):
        with self.assertRaises(ValueError):
            CatanGame(3)

    def test_initial_setup_places_two_settlements_and_roads_per_player(self):
        game = CatanGame(4)
        for player in game.players:
            settlements = sum(
                1
                for settlement_id in range(1, 55)
                if game.board[f"s{settlement_id}"].hasSettlement
                and game.board[f"s{settlement_id}"].controller == player.id
            )
            roads = sum(
                1
                for road_id in range(1, 73)
                if game.board[f"r{road_id}"].hasRoad and game.board[f"r{road_id}"].controller == player.id
            )
            self.assertEqual(settlements, 2)
            self.assertEqual(roads, 2)
            self.assertEqual(player.victory_points, 2)

    def test_road_cannot_continue_through_opponent_settlement(self):
        game = CatanGame(4)
        clear_board(game)
        game.board["r1"].hasRoad = True
        game.board["r1"].controller = 0
        game.board["s1"].hasSettlement = True
        game.board["s1"].controller = 1
        game.board["s1"].blocked = True
        game.players[0].resources["brick"] = 1
        game.players[0].resources["lumber"] = 1
        game._refresh_all_player_options()

        self.assertNotIn(2, game.legal_road_spots(0))

    def test_longest_road_counts_to_but_not_through_opponent_building(self):
        game = CatanGame(4)
        clear_board(game)
        for road_id in [1, 2]:
            game.board[f"r{road_id}"].hasRoad = True
            game.board[f"r{road_id}"].controller = 0
        game.board["s1"].hasCity = True
        game.board["s1"].controller = 1
        game.board["s1"].blocked = True

        self.assertEqual(game.compute_longest_road(0), 1)

    def test_longest_road_is_removed_when_interrupted_below_five(self):
        game = CatanGame(4)
        clear_board(game)
        for road_id in [1, 2, 3, 4, 5]:
            game.board[f"r{road_id}"].hasRoad = True
            game.board[f"r{road_id}"].controller = 0
        game.players[0].victory_points = 5
        game.update_longest_road()
        self.assertTrue(game.players[0].longest_road)

        game.board["s2"].hasSettlement = True
        game.board["s2"].controller = 1
        game.board["s2"].blocked = True
        game.update_longest_road()

        self.assertFalse(game.players[0].longest_road)
        self.assertEqual(game.players[0].victory_points, 5)

    def test_largest_army_holder_keeps_tie_and_win_is_detected(self):
        game = CatanGame(4)
        game.players[0].victory_points = 8
        game.players[0].upDevs["knight"] = 3
        game.update_largest_army()
        self.assertTrue(game.game_over)
        self.assertEqual(game.winner, 0)

        game.game_over = False
        game.winner = None
        game.players[1].upDevs["knight"] = 3
        game.update_largest_army()
        self.assertTrue(game.players[0].largest_army)
        self.assertFalse(game.players[1].largest_army)

    def test_road_building_card_builds_free_roads_without_resources(self):
        game = CatanGame(4)
        player = game.players[0]
        player.downDevs["roadBuilding"] = 1
        player.resources = {resource: 0 for resource in player.resources}
        before = game._road_count(0)
        game.played_dev_this_turn = False

        self.assertTrue(game.play_dev_card(0))
        self.assertGreater(game._road_count(0), before)

if __name__ == "__main__":
    unittest.main()
