DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS player_games;
DROP TABLE IF EXISTS turns;
DROP TABLE IF EXISTS actions;
DROP TABLE IF EXISTS resource_events;
DROP TABLE IF EXISTS validation_errors;
DROP TABLE IF EXISTS player_win_rates;
DROP TABLE IF EXISTS resource_values;
DROP TABLE IF EXISTS dev_card_values;

CREATE TABLE games (
    game_id INTEGER PRIMARY KEY,
    num_players INTEGER NOT NULL,
    turns INTEGER NOT NULL,
    winner_id INTEGER NOT NULL,
    winner_victory_points INTEGER NOT NULL
);

CREATE TABLE player_games (
    game_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    won INTEGER NOT NULL,
    victory_points INTEGER NOT NULL,
    largest_army INTEGER NOT NULL,
    longest_road INTEGER NOT NULL,
    current_brick INTEGER NOT NULL,
    legacy_brick INTEGER NOT NULL,
    current_lumber INTEGER NOT NULL,
    legacy_lumber INTEGER NOT NULL,
    current_ore INTEGER NOT NULL,
    legacy_ore INTEGER NOT NULL,
    current_grain INTEGER NOT NULL,
    legacy_grain INTEGER NOT NULL,
    current_wool INTEGER NOT NULL,
    legacy_wool INTEGER NOT NULL,
    played_knight INTEGER NOT NULL,
    unplayed_knight INTEGER NOT NULL,
    played_victoryPoint INTEGER NOT NULL,
    unplayed_victoryPoint INTEGER NOT NULL,
    played_roadBuilding INTEGER NOT NULL,
    unplayed_roadBuilding INTEGER NOT NULL,
    played_yearOfPlenty INTEGER NOT NULL,
    unplayed_yearOfPlenty INTEGER NOT NULL,
    played_monopoly INTEGER NOT NULL,
    unplayed_monopoly INTEGER NOT NULL,
    PRIMARY KEY (game_id, player_id)
);

CREATE TABLE turns (
    game_id INTEGER NOT NULL,
    turn_number INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    dice_roll INTEGER NOT NULL,
    actions_taken INTEGER NOT NULL,
    victory_points_start INTEGER NOT NULL,
    victory_points_end INTEGER NOT NULL,
    robber_tile_start INTEGER NOT NULL,
    robber_tile_after INTEGER NOT NULL,
    robber_moved INTEGER NOT NULL,
    game_over INTEGER NOT NULL,
    PRIMARY KEY (game_id, turn_number)
);

CREATE TABLE actions (
    game_id INTEGER NOT NULL,
    turn_number INTEGER NOT NULL,
    action_order INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    success INTEGER NOT NULL,
    victory_points_after INTEGER NOT NULL,
    PRIMARY KEY (game_id, turn_number, action_order)
);

CREATE TABLE resource_events (
    game_id INTEGER NOT NULL,
    turn_number INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    resource TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    event_type TEXT NOT NULL
);

CREATE TABLE validation_errors (
    game_id INTEGER NOT NULL,
    error TEXT NOT NULL
);

CREATE TABLE player_win_rates (
    player_id INTEGER PRIMARY KEY,
    games_played INTEGER NOT NULL,
    wins INTEGER NOT NULL,
    win_rate REAL NOT NULL
);

CREATE TABLE resource_values (
    resource TEXT PRIMARY KEY,
    value REAL NOT NULL
);

CREATE TABLE dev_card_values (
    dev_card TEXT PRIMARY KEY,
    value REAL NOT NULL
);
