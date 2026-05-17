import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


RESOURCE_COLUMNS = ["brick", "lumber", "ore", "grain", "wool"]
DEV_CARD_COLUMNS = ["knight", "victoryPoint", "roadBuilding", "yearOfPlenty", "monopoly"]


st.set_page_config(page_title="Catan Resource & Dev Card Value", layout="wide")
st.title("Catan Resource & Development Card Value")
st.caption("Random-agent Catan simulations analyzed through resource value, development-card value, and general run statistics.")

db_path = st.sidebar.text_input("SQLite database", "data/catan_analytics.db")


@st.cache_data
def load_table(path, table_name):
    with sqlite3.connect(path) as conn:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)


def winner_lift(player_games, columns, prefix):
    rows = []
    for name in columns:
        column = f"{prefix}_{name}"
        winner_avg = player_games.loc[player_games["won"] == 1, column].mean()
        loser_avg = player_games.loc[player_games["won"] == 0, column].mean()
        lift = winner_avg / loser_avg if pd.notna(loser_avg) and loser_avg > 0 else 0
        rows.append(
            {
                "item": name,
                "winner_avg": winner_avg,
                "loser_avg": loser_avg,
                "winner_lift": lift,
            }
        )
    return pd.DataFrame(rows).sort_values("winner_lift", ascending=False)


def display_name(value):
    return value.replace("Point", " Point").replace("Building", " Building").replace("Of", " Of ").title()


if not Path(db_path).exists():
    st.info("Run the pipeline first: python main.py --players 4 --games 100")
    st.stop()

games = load_table(db_path, "games")
player_games = load_table(db_path, "player_games")
turns = load_table(db_path, "turns")
actions = load_table(db_path, "actions")
resource_events = load_table(db_path, "resource_events")
resource_values = load_table(db_path, "resource_values")
dev_card_values = load_table(db_path, "dev_card_values")
validation_errors = load_table(db_path, "validation_errors")

resource_value_tab, dev_card_value_tab, simulation_stats_tab = st.tabs(
    ["Resource Value", "Development Card Value", "Simulation Stats"]
)

with resource_value_tab:
    st.header("Resource value")
    st.write(
        "Resource value is shown two ways: the pipeline's normalized winner-based score, "
        "and winner lift, which compares average production by winners against losers. "
        "A lift above 1.0 means winners produced more of that item on average."
    )

    resource_values = resource_values.sort_values("value", ascending=False)
    resource_lift = winner_lift(player_games, RESOURCE_COLUMNS, "legacy")
    top_resource = resource_values.iloc[0]
    top_resource_lift = resource_lift.iloc[0]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Top normalized resource", display_name(top_resource["resource"]))
    col2.metric("Top normalized value", f"{top_resource['value']:.3f}")
    col3.metric("Top winner lift", display_name(top_resource_lift["item"]), f"{top_resource_lift['winner_lift']:.2f}x")
    col4.metric("Resources tracked", len(resource_values))

    st.plotly_chart(
        px.bar(
            resource_values,
            x="resource",
            y="value",
            title="Normalized Resource Value",
            text_auto=".3f",
        ),
        width="stretch",
    )

    st.plotly_chart(
        px.bar(
            resource_lift,
            x="item",
            y="winner_lift",
            title="Winner Lift by Resource Produced",
            text_auto=".2f",
        ),
        width="stretch",
    )

    resource_avg = resource_lift.melt(
        id_vars="item",
        value_vars=["winner_avg", "loser_avg"],
        var_name="outcome",
        value_name="avg_produced",
    )
    resource_avg["outcome"] = resource_avg["outcome"].map({"winner_avg": "Winner", "loser_avg": "Loser"})
    st.plotly_chart(
        px.bar(
            resource_avg,
            x="item",
            y="avg_produced",
            color="outcome",
            barmode="group",
            title="Average Produced Resources: Winners vs Losers",
        ),
        width="stretch",
    )

    st.dataframe(resource_lift, width="stretch")

with dev_card_value_tab:
    st.header("Development card value")
    st.write(
        "Development-card value is based on cards used by winners, normalized by card frequency. "
        "Victory-point cards count immediately when bought. Winner lift compares average card usage "
        "for winners against losers."
    )

    dev_card_values = dev_card_values.sort_values("value", ascending=False)
    dev_lift = winner_lift(player_games, DEV_CARD_COLUMNS, "played")
    top_card = dev_card_values.iloc[0]
    top_dev_lift = dev_lift.iloc[0]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Top normalized dev card", display_name(top_card["dev_card"]))
    col2.metric("Top normalized value", f"{top_card['value']:.3f}")
    col3.metric("Top winner lift", display_name(top_dev_lift["item"]), f"{top_dev_lift['winner_lift']:.2f}x")
    col4.metric("Cards tracked", len(dev_card_values))

    st.plotly_chart(
        px.bar(
            dev_card_values,
            x="dev_card",
            y="value",
            title="Normalized Development Card Value",
            text_auto=".3f",
        ),
        width="stretch",
    )

    st.plotly_chart(
        px.bar(
            dev_lift,
            x="item",
            y="winner_lift",
            title="Winner Lift by Development Card Played",
            text_auto=".2f",
        ),
        width="stretch",
    )

    dev_avg = dev_lift.melt(
        id_vars="item",
        value_vars=["winner_avg", "loser_avg"],
        var_name="outcome",
        value_name="avg_played",
    )
    dev_avg["outcome"] = dev_avg["outcome"].map({"winner_avg": "Winner", "loser_avg": "Loser"})
    st.plotly_chart(
        px.bar(
            dev_avg,
            x="item",
            y="avg_played",
            color="outcome",
            barmode="group",
            title="Average Played Development Cards: Winners vs Losers",
        ),
        width="stretch",
    )

    st.dataframe(dev_lift, width="stretch")

with simulation_stats_tab:
    st.header("General simulation statistics")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Games", len(games))
    col2.metric("Average turns", f"{games['turns'].mean():.1f}")
    col3.metric("Turn records", len(turns))
    col4.metric("Validation errors", len(validation_errors))

    wins = player_games.groupby("player_id", as_index=False)["won"].sum()
    action_counts = actions.groupby("action_type", as_index=False).size()
    robber_moves = turns.groupby("player_id", as_index=False)["robber_moved"].sum()

    st.plotly_chart(px.bar(wins, x="player_id", y="won", title="Wins by Player"), width="stretch")
    st.plotly_chart(px.histogram(games, x="turns", nbins=30, title="Game Length Distribution"), width="stretch")
    st.plotly_chart(px.bar(action_counts, x="action_type", y="size", title="Action Counts"), width="stretch")
    st.plotly_chart(px.bar(robber_moves, x="player_id", y="robber_moved", title="Robber Moves by Player"), width="stretch")

    if resource_events.empty:
        st.info("No resource events found.")
    else:
        resource_totals = resource_events.groupby("resource", as_index=False)["quantity"].sum()
        st.plotly_chart(
            px.bar(resource_totals, x="resource", y="quantity", title="Net Resource Movement by Resource"),
            width="stretch",
        )
