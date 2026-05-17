SELECT
    COUNT(*) AS games_played,
    ROUND(AVG(CAST(turns AS REAL)), 2) AS avg_turns,
    MIN(CAST(turns AS INTEGER)) AS min_turns,
    MAX(CAST(turns AS INTEGER)) AS max_turns
FROM games;
