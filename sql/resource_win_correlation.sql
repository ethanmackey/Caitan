SELECT
    won,
    ROUND(AVG(CAST(legacy_brick AS REAL)), 2) AS avg_legacy_brick,
    ROUND(AVG(CAST(legacy_lumber AS REAL)), 2) AS avg_legacy_lumber,
    ROUND(AVG(CAST(legacy_ore AS REAL)), 2) AS avg_legacy_ore,
    ROUND(AVG(CAST(legacy_grain AS REAL)), 2) AS avg_legacy_grain,
    ROUND(AVG(CAST(legacy_wool AS REAL)), 2) AS avg_legacy_wool
FROM player_games
GROUP BY won
ORDER BY won DESC;
