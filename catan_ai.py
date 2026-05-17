import csv
import sqlite3
from pathlib import Path

from catan_game import CatanGame, ResourceType


DEV_CARD_TYPES = ["knight", "victoryPoint", "roadBuilding", "yearOfPlenty", "monopoly"]


class CatanAI:
    def __init__(self, player_id):
        self.player_id = player_id
        self.resource_correlation = {rt: 0.0 for rt in ResourceType}
        self.dev_correlation = {dev_card: 0 for dev_card in DEV_CARD_TYPES}
        self.games_played = 0
        self.games_won = 0

    def make_move(self, game):
        return game.play_turn(self.player_id)

    def update_correlation(self, game_state, won):
        self.games_played += 1
        if not won:
            return

        self.games_won += 1
        player_data = game_state["players"][self.player_id]
        for dev_name, count in player_data["upDevs"].items():
            self.dev_correlation[dev_name] += count
        for resource_name, count in player_data["legacyResources"].items():
            self.resource_correlation[ResourceType(resource_name)] += count

    def get_resource_values(self):
        total = sum(self.resource_correlation.values())
        if total == 0:
            return {rt: 0.0 for rt in ResourceType}
        return {rt: value / total for rt, value in self.resource_correlation.items()}

    def get_dev_card_values(self):
        total = sum(self.dev_correlation.values())
        if total == 0:
            return {card: 0.0 for card in self.dev_correlation}
        return {card: value / total for card, value in self.dev_correlation.items()}


class CatanSimulation:
    def __init__(self, num_players=4, num_games=100, verbose=False):
        self.num_players = num_players
        self.num_games = num_games
        self.agents = [CatanAI(i) for i in range(num_players)]
        self.verbose = verbose
        self.game_records = []
        self.player_game_records = []
        self.turn_records = []
        self.action_records = []
        self.resource_event_records = []
        self.validation_errors = []

    def run_simulation(self):
        for game_num in range(self.num_games):
            if game_num % 1000 == 0:
                print(f"Finished Game {game_num}")

            game_id = game_num + 1
            game = CatanGame(self.num_players)

            if self.verbose:
                print(f"\nStarting Game {game_id}/{self.num_games}")
                game.print_board()

            while not game.game_over:
                for agent in self.agents:
                    before_resources = self._resource_snapshot(game)
                    turn_summary = agent.make_move(game)
                    if turn_summary:
                        self._record_turn_events(game_id, game, turn_summary, before_resources)

                    if self.verbose and game.turn_number % 5 == 0:
                        print(f"\nTurn {game.turn_number} - Player {agent.player_id}'s move:")
                        game.print_board()

                    if game.game_over:
                        break

            game_state = game.get_game_state()
            winner_id = game_state["winner"]
            self.validation_errors.extend(self.validate_game_state(game_id, game_state))

            for agent in self.agents:
                agent.update_correlation(game_state, agent.player_id == winner_id)

            self._record_game(game_id, game, game_state)

            if self.verbose:
                print(f"\nGame {game_id} finished! Winner: Player {winner_id}")
                game.print_board()

    def _resource_snapshot(self, game):
        return {player.id: dict(player.resources) for player in game.players}

    def _record_turn_events(self, game_id, game, turn_summary, before_resources):
        self.turn_records.append(
            {
                "game_id": game_id,
                "turn_number": turn_summary["turn_number"],
                "player_id": turn_summary["player_id"],
                "dice_roll": turn_summary["dice_roll"],
                "actions_taken": turn_summary["actions_taken"],
                "victory_points_start": turn_summary["victory_points_start"],
                "victory_points_end": turn_summary["victory_points_end"],
                "robber_tile_start": turn_summary["robber_tile_start"],
                "robber_tile_after": turn_summary["robber_tile_after"],
                "robber_moved": turn_summary["robber_moved"],
                "game_over": turn_summary["game_over"],
            }
        )

        for action in turn_summary["actions"]:
            self.action_records.append(
                {
                    "game_id": game_id,
                    "turn_number": action["turn_number"],
                    "action_order": action["action_order"],
                    "player_id": action["player_id"],
                    "action_type": action["action_type"],
                    "success": action["success"],
                    "victory_points_after": action["victory_points_after"],
                }
            )

        for player in game.players:
            for resource in ResourceType:
                resource_name = resource.value
                quantity = player.resources[resource_name] - before_resources[player.id][resource_name]
                if quantity != 0:
                    self.resource_event_records.append(
                        {
                            "game_id": game_id,
                            "turn_number": turn_summary["turn_number"],
                            "player_id": player.id,
                            "resource": resource_name,
                            "quantity": quantity,
                            "event_type": "net_turn_change",
                        }
                    )

    def _record_game(self, game_id, game, game_state):
        winner_id = game_state["winner"]
        self.game_records.append(
            {
                "game_id": game_id,
                "num_players": self.num_players,
                "turns": game_state["turn_number"],
                "winner_id": winner_id,
                "winner_victory_points": game.players[winner_id].victory_points,
            }
        )

        for player in game.players:
            row = {
                "game_id": game_id,
                "player_id": player.id,
                "won": int(player.id == winner_id),
                "victory_points": player.victory_points,
                "largest_army": int(player.largest_army),
                "longest_road": int(player.longest_road),
            }
            for resource in ResourceType:
                row[f"current_{resource.value}"] = player.resources[resource.value]
                row[f"legacy_{resource.value}"] = player.legacyResources[resource.value]
            for dev_card in DEV_CARD_TYPES:
                row[f"played_{dev_card}"] = player.upDevs[dev_card]
                row[f"unplayed_{dev_card}"] = player.downDevs[dev_card]
            self.player_game_records.append(row)

    def validate_game_state(self, game_id, game_state):
        errors = []
        winner_id = game_state["winner"]
        if winner_id is None:
            errors.append({"game_id": game_id, "error": "completed game has no winner"})
        elif winner_id < 0 or winner_id >= self.num_players:
            errors.append({"game_id": game_id, "error": f"invalid winner_id {winner_id}"})

        for player in game_state["players"]:
            player_id = player["id"]
            if player["victory_points"] < 0:
                errors.append({"game_id": game_id, "error": f"player {player_id} has negative victory points"})
            for resource_type in ResourceType:
                resource_name = resource_type.value
                if player["resources"][resource_name] < 0:
                    errors.append({"game_id": game_id, "error": f"player {player_id} has negative {resource_name}"})
                if player["legacyResources"][resource_name] < 0:
                    errors.append({"game_id": game_id, "error": f"player {player_id} has negative legacy {resource_name}"})
        return errors

    def print_results(self):
        print(f"Simulation Results ({self.num_games} games):")
        print("-" * 50)
        for agent in self.agents:
            win_rate = agent.games_won / agent.games_played * 100
            print(f"Agent {agent.player_id}: {agent.games_won} wins ({win_rate:.1f}%)")
            print("Resource Values:")
            for resource_type, value in agent.get_resource_values().items():
                print(f"  {resource_type.value}: {value:.4f}")
            print("-" * 50)
        if self.validation_errors:
            print(f"Data quality warnings: {len(self.validation_errors)}")

    def get_resource_values(self):
        all_values = [agent.get_resource_values() for agent in self.agents]
        avg_values = {
            resource_type: sum(agent_values[resource_type] for agent_values in all_values) / len(all_values)
            for resource_type in ResourceType
        }
        resource_tile_counts = {
            ResourceType.LUMBER: 4,
            ResourceType.BRICK: 3,
            ResourceType.WOOL: 4,
            ResourceType.GRAIN: 4,
            ResourceType.ORE: 3,
        }
        weighted = {rt: avg_values[rt] / resource_tile_counts[rt] for rt in ResourceType}
        total_weighted = sum(weighted.values())
        if total_weighted == 0:
            return {rt: 1 / len(ResourceType) for rt in ResourceType}
        return {rt: value / total_weighted for rt, value in weighted.items()}

    def get_dev_card_values(self):
        all_values = [agent.get_dev_card_values() for agent in self.agents]
        avg_values = {
            card: sum(agent_values[card] for agent_values in all_values) / len(all_values)
            for card in self.agents[0].dev_correlation
        }
        dev_card_counts = {"knight": 14, "victoryPoint": 5, "roadBuilding": 2, "yearOfPlenty": 2, "monopoly": 2}
        weighted = {card: avg_values[card] / dev_card_counts[card] for card in avg_values}
        total_weighted = sum(weighted.values())
        if total_weighted == 0:
            return {card: 1 / len(avg_values) for card in avg_values}
        return {card: value / total_weighted for card, value in weighted.items()}

    def write_outputs(self, output_dir):
        output_dir = Path(output_dir)
        raw_dir = output_dir / "raw"
        marts_dir = output_dir / "marts"
        raw_dir.mkdir(parents=True, exist_ok=True)
        marts_dir.mkdir(parents=True, exist_ok=True)

        self._write_csv(raw_dir / "games.csv", self.game_records)
        self._write_csv(raw_dir / "player_games.csv", self.player_game_records)
        self._write_csv(raw_dir / "turns.csv", self.turn_records)
        self._write_csv(raw_dir / "actions.csv", self.action_records)
        self._write_csv(raw_dir / "resource_events.csv", self.resource_event_records)
        self._write_csv(raw_dir / "validation_errors.csv", self.validation_errors)
        self._write_csv(marts_dir / "player_win_rates.csv", self._player_win_rate_rows())
        self._write_csv(marts_dir / "resource_values.csv", self._resource_value_rows())
        self._write_csv(marts_dir / "dev_card_values.csv", self._dev_card_value_rows())

    def write_sqlite(self, db_path):
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        schema_path = Path("sql/schema.sql")
        conn = sqlite3.connect(db_path)
        try:
            conn.executescript(schema_path.read_text())
            self._insert_rows(conn, "games", self.game_records)
            self._insert_rows(conn, "player_games", self.player_game_records)
            self._insert_rows(conn, "turns", self.turn_records)
            self._insert_rows(conn, "actions", self.action_records)
            self._insert_rows(conn, "resource_events", self.resource_event_records)
            self._insert_rows(conn, "validation_errors", self.validation_errors)
            self._insert_rows(conn, "player_win_rates", self._player_win_rate_rows())
            self._insert_rows(conn, "resource_values", self._resource_value_rows())
            self._insert_rows(conn, "dev_card_values", self._dev_card_value_rows())
            conn.commit()
        finally:
            conn.close()

    def _player_win_rate_rows(self):
        return [
            {
                "player_id": agent.player_id,
                "games_played": agent.games_played,
                "wins": agent.games_won,
                "win_rate": agent.games_won / agent.games_played if agent.games_played else 0,
            }
            for agent in self.agents
        ]

    def _resource_value_rows(self):
        return [
            {"resource": resource_type.value, "value": value}
            for resource_type, value in self.get_resource_values().items()
        ]

    def _dev_card_value_rows(self):
        return [
            {"dev_card": dev_card, "value": value}
            for dev_card, value in self.get_dev_card_values().items()
        ]

    def _write_csv(self, path, rows):
        if not rows:
            path.write_text("")
            return
        with path.open("w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    def _insert_rows(self, conn, table_name, rows):
        if not rows:
            return
        columns = list(rows[0].keys())
        placeholders = ", ".join("?" for _ in columns)
        conn.executemany(
            f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})",
            [[row[column] for column in columns] for row in rows],
        )
