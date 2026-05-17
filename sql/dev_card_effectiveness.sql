SELECT
    SUM(CAST(won AS INTEGER)) AS wins,
    ROUND(AVG(CAST(played_knight AS REAL)), 2) AS avg_played_knights,
    ROUND(AVG(CAST(played_victoryPoint AS REAL)), 2) AS avg_victory_point_cards,
    ROUND(AVG(CAST(played_roadBuilding AS REAL)), 2) AS avg_road_building_cards,
    ROUND(AVG(CAST(played_yearOfPlenty AS REAL)), 2) AS avg_year_of_plenty_cards,
    ROUND(AVG(CAST(played_monopoly AS REAL)), 2) AS avg_monopoly_cards
FROM player_games
GROUP BY won
ORDER BY won DESC;
