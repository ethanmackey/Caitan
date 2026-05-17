SELECT
    player_id,
    games_played,
    wins,
    ROUND(CAST(win_rate AS REAL), 4) AS win_rate
FROM player_win_rates
ORDER BY CAST(win_rate AS REAL) DESC;
