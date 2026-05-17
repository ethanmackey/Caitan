import argparse

from catan_ai import CatanSimulation


def main():
    parser = argparse.ArgumentParser(description="Run Catan simulation analytics pipeline")
    parser.add_argument("--players", type=int, default=4, help="Number of players; traditional Catan supports 4 here (default: 4)")
    parser.add_argument("--games", type=int, default=10000, help="Number of games to simulate (default: 10000)")
    parser.add_argument("--verbose", action="store_true", help="Print detailed game information")
    parser.add_argument(
        "--output-dir",
        default="data/output",
        help="Directory for CSV pipeline outputs (default: data/output)",
    )
    parser.add_argument(
        "--sqlite-path",
        default="data/catan_analytics.db",
        help="SQLite database path for analytical tables (default: data/catan_analytics.db)",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Run the simulation without writing CSV or SQLite outputs",
    )
    args = parser.parse_args()

    simulation = CatanSimulation(num_players=args.players, num_games=args.games, verbose=args.verbose)

    print(f"Running Catan simulation analytics pipeline with {args.players} players for {args.games} games...")
    simulation.run_simulation()

    simulation.print_results()

    avg_values = simulation.get_resource_values()
    print("\nAverage Resource Values Across All Agents:")
    print("-" * 50)
    for resource_type, value in avg_values.items():
        print(f"{resource_type.value}: {value:.4f}")

    avg_dev_values = simulation.get_dev_card_values()
    print("\nAverage Development Card Values Across All Agents:")
    print("-" * 50)
    for dev_card, value in avg_dev_values.items():
        print(f"{dev_card}: {value:.4f}")

    if not args.no_write:
        simulation.write_outputs(args.output_dir)
        simulation.write_sqlite(args.sqlite_path)
        print(f"\nWrote CSV outputs to {args.output_dir}")
        print(f"Wrote SQLite analytical database to {args.sqlite_path}")


if __name__ == "__main__":
    main()
