import argparse
import sqlite3
from pathlib import Path


VALID_ACTIONS = {"end_turn", "settlement", "city", "road", "trade", "buyDev", "playDev"}
VALID_RESOURCES = {"brick", "lumber", "ore", "grain", "wool"}


def scalar(conn, query):
    return conn.execute(query).fetchone()[0]


def run_checks(db_path):
    checks = []
    conn = sqlite3.connect(db_path)
    try:
        checks.append(("games_loaded", scalar(conn, "SELECT COUNT(*) FROM games") > 0))
        checks.append(("four_players_per_game", scalar(conn, "SELECT COUNT(*) FROM games g WHERE (SELECT COUNT(*) FROM player_games p WHERE p.game_id = g.game_id) != 4") == 0))
        checks.append(("one_winner_per_game", scalar(conn, "SELECT COUNT(*) FROM games g WHERE (SELECT COUNT(*) FROM player_games p WHERE p.game_id = g.game_id AND p.won = 1) != 1") == 0))
        checks.append(("winner_has_10_points", scalar(conn, "SELECT COUNT(*) FROM games WHERE winner_victory_points < 10") == 0))
        checks.append(("valid_player_ids", scalar(conn, "SELECT COUNT(*) FROM player_games WHERE player_id NOT BETWEEN 0 AND 3") == 0))
        checks.append(("turns_loaded", scalar(conn, "SELECT COUNT(*) FROM turns") > 0))
        checks.append(("valid_dice_rolls", scalar(conn, "SELECT COUNT(*) FROM turns WHERE dice_roll NOT BETWEEN 2 AND 12") == 0))
        checks.append(("actions_loaded", scalar(conn, "SELECT COUNT(*) FROM actions") > 0))
        invalid_action_count = scalar(conn, f"SELECT COUNT(*) FROM actions WHERE action_type NOT IN ({','.join(repr(action) for action in sorted(VALID_ACTIONS))})")
        checks.append(("valid_action_types", invalid_action_count == 0))
        invalid_resource_count = scalar(conn, f"SELECT COUNT(*) FROM resource_events WHERE resource NOT IN ({','.join(repr(resource) for resource in sorted(VALID_RESOURCES))})")
        checks.append(("valid_resource_names", invalid_resource_count == 0))
        checks.append(("no_negative_victory_points", scalar(conn, "SELECT COUNT(*) FROM player_games WHERE victory_points < 0") == 0))
        checks.append(("no_pipeline_validation_errors", scalar(conn, "SELECT COUNT(*) FROM validation_errors") == 0))
    finally:
        conn.close()
    return checks


def write_report(checks, report_path):
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Data Quality Report", "", "| Check | Status |", "| --- | --- |"]
    for name, passed in checks:
        lines.append(f"| {name} | {'PASS' if passed else 'FAIL'} |")
    report_path.write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Validate Catan analytics pipeline outputs")
    parser.add_argument("--db-path", default="data/catan_analytics.db")
    parser.add_argument("--report-path", default="reports/data_quality_report.md")
    args = parser.parse_args()

    checks = run_checks(args.db_path)
    write_report(checks, Path(args.report_path))
    failed = [name for name, passed in checks if not passed]
    if failed:
        print(f"Data quality failed: {', '.join(failed)}")
        raise SystemExit(1)
    print(f"Data quality passed. Report written to {args.report_path}")


if __name__ == "__main__":
    main()
