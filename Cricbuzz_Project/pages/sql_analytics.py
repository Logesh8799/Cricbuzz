import streamlit as st
import pandas as pd
import mysql.connector
import requests
from datetime import datetime

st.set_page_config(page_title="SQL Analytics Dashboard", page_icon="https://www.cricbuzz.com/favicon.ico")
st.title("SQL Analytics Dashboard")

page_map = {
    "Select a page": None,
    "Home": "pages/home.py",
    "Live Scores": "pages/livescore.py",
    "Player Stats": "pages/player_stats.py",
    "SQL Analytics": "pages/sql_analytics.py",
    "CRUD Operations": "pages/crud_operations.py"
}

# 2. Render the selectbox
selection = st.sidebar.selectbox("Navigate to:", options=list(page_map.keys()))
page_file = page_map[selection]
if page_file:
    st.write(f"Loading page: {page_file}")
    st.switch_page(page_file)

queries_dict = {
    "Q1: Indian Players Profile": """
        SELECT name, role, battingStyle, bowlingStyle 
        FROM players_list;
    """,
    
    "Q2: Matches Played in the Last Few Days": """SELECT match_id, 
    match_name, 
    match_date, 
    match_description, 
    team_1_name, 
    team_2_name, 
    venue_name, 
    venue_city
FROM matches
WHERE match_date >= NOW() - INTERVAL 5 DAY
ORDER BY match_date DESC;""",
    
    "Q3: Top 10 Highest Run Scorers in ODIs": """
        SELECT player_name, total_runs, batting_average, centuries 
        FROM odi_batting_stats 
        ORDER BY total_runs DESC 
        LIMIT 10;
    """,
    
    "Q4: Top 10 Stadiums with >25k Capacity": """
        SELECT venue_name, city, country, capacity 
        FROM venues 
        WHERE capacity > 25000 
        ORDER BY capacity DESC 
        LIMIT 10;
    """,
    
    "Q5: Total Match Wins by Team": """
        SELECT winning_team AS team_name, COUNT(*) AS total_wins 
        FROM matches 
        WHERE winning_team IS NOT NULL 
        GROUP BY winning_team 
        ORDER BY total_wins DESC;
    """,
    
    "Q6: Player Count by Playing Role": """
        SELECT role, COUNT(*) AS player_count 
        FROM players_list
        GROUP BY role 
        ORDER BY player_count DESC;
    """,
    
    "Q7: Highest Individual Score by Format": """
        SELECT format, MAX(highest_score) AS highest_individual_score 
        FROM batting_records 
        GROUP BY format;
    """,
    
    "Q8: Cricket Series Started in 2024": """
        SELECT series_name, host_country, match_type, start_date, total_matches_planned 
        FROM series 
        WHERE YEAR(start_date) = 2024;
    """,
    
    "Q9: Elite All-Rounders (>1000 Runs & >50 Wickets)": """
        SELECT player_name, total_runs, total_wickets, format 
        FROM career_stats 
        WHERE playing_role LIKE '%All-rounder%' 
          AND total_runs > 1000 
          AND total_wickets > 50;
    """,
    
    "Q10: Details of Last 20 Completed Matches": """
        SELECT match_description, team_1_name, team_2_name, winning_team, victory_margin, match_status, venue_name 
        FROM matches 
        WHERE match_status = 'Complete' 
        ORDER BY match_date DESC 
        LIMIT 20;
    """,
    
    "Q11: Cross-Format Player Batting Comparison": """
        SELECT 
            player_name,
            SUM(CASE WHEN format = 'Test' THEN total_runs ELSE 0 END) AS test_runs,
            SUM(CASE WHEN format = 'ODI' THEN total_runs ELSE 0 END) AS odi_runs,
            SUM(CASE WHEN format = 'T20I' THEN total_runs ELSE 0 END) AS t20i_runs,
            AVG(batting_average) AS overall_average
        FROM career_stats
        GROUP BY player_name
        HAVING COUNT(DISTINCT format) >= 2;
    """,
    
    "Q12: Team Performance (Home vs Away Wins)": """
        SELECT 
            team_name,
            SUM(CASE WHEN venue_country = team_country THEN 1 ELSE 0 END) AS home_wins,
            SUM(CASE WHEN venue_country != team_country THEN 1 ELSE 0 END) AS away_wins
        FROM (
            SELECT winning_team AS team_name, t.country AS team_country, v.country AS venue_country
            FROM matches m
            JOIN teams t ON m.winning_team = t.team_name
            JOIN venues v ON m.venue_id = v.venue_id
        ) as win_data
        GROUP BY team_name;
    """,
    
    "Q13: Century Partnerships (Consecutive Batsmen)": """
        SELECT 
            p1.player_name AS batsman_1, 
            p2.player_name AS batsman_2, 
            (p1.runs_scored + p2.runs_scored) AS combined_partnership_runs, 
            p1.innings_number
        FROM batting_innings p1
        JOIN batting_innings p2 ON p1.match_id = p2.match_id 
                               AND p1.innings_number = p2.innings_number 
                               AND p1.batting_position = p2.batting_position - 1
        WHERE (p1.runs_scored + p2.runs_scored) >= 100;
    """,
    
    "Q14: Venue Bowling Analysis (Min 3 Matches)": """
        SELECT bowler_name, venue_name, AVG(economy_rate) AS avg_economy, SUM(wickets_taken) AS total_wickets, COUNT(DISTINCT match_id) AS matches_played
        FROM bowling_performance
        WHERE overs_bowled >= 4
        GROUP BY bowler_name, venue_name
        HAVING COUNT(DISTINCT match_id) >= 3;
    """,
    
    "Q15: Clutch Players in Close Matches": """
        SELECT 
            bp.player_name, 
            AVG(bp.runs_scored) AS avg_runs, 
            COUNT(DISTINCT m.match_id) AS close_matches_played,
            SUM(CASE WHEN m.winning_team = bp.team_name THEN 1 ELSE 0 END) AS matches_won
        FROM batting_performance bp
        JOIN matches m ON bp.match_id = m.match_id
        WHERE (m.victory_type = 'runs' AND m.victory_margin < 50) 
           OR (m.victory_type = 'wickets' AND m.victory_margin < 5)
        GROUP BY bp.player_name;
    """,
    
    "Q16: Yearly Batting Performance Trends (Since 2020)": """
        SELECT player_name, YEAR(match_date) AS match_year, AVG(runs_scored) AS avg_runs_per_match, AVG(strike_rate) AS avg_strike_rate
        FROM batting_performance bp
        JOIN matches m ON bp.match_id = m.match_id
        WHERE m.match_date >= '2020-01-01'
        GROUP BY player_name, YEAR(match_date)
        HAVING COUNT(DISTINCT m.match_id) >= 5;
    """,
    
    "Q17: Toss Decision Win-Advantage Analysis": """
        SELECT 
            toss_decision,
            COUNT(*) AS total_matches,
            SUM(CASE WHEN toss_winner = winning_team THEN 1 ELSE 0 END) AS matches_won,
            (SUM(CASE WHEN toss_winner = winning_team THEN 1 ELSE 0 END) / COUNT(*)) * 100 AS win_percentage
        FROM matches
        WHERE winning_team IS NOT NULL
        GROUP BY toss_decision;
    """,
    
    "Q18: Most Economical Limited-Overs Bowlers": """
        SELECT bowler_name, AVG(economy_rate) AS overall_economy, SUM(wickets_taken) AS total_wickets
        FROM bowling_performance
        WHERE format IN ('ODI', 'T20')
        GROUP BY bowler_name
        HAVING COUNT(DISTINCT match_id) >= 10 AND AVG(overs_bowled) >= 2;
    """,
    
    "Q19: Most Consistent Batsmen (Since 2022)": """
        SELECT player_name, AVG(runs_scored) AS avg_runs, STDDEV(runs_scored) AS runs_std_dev
        FROM batting_performance bp
        JOIN matches m ON bp.match_id = m.match_id
        WHERE m.match_date >= '2022-01-01' AND bp.balls_faced >= 10
        GROUP BY player_name
        ORDER BY runs_std_dev ASC;
    """,
    
    "Q20: Multi-Format Match Appearances & Averages": """
        SELECT 
            player_name,
            SUM(CASE WHEN format = 'Test' THEN 1 ELSE 0 END) AS test_matches,
            AVG(CASE WHEN format = 'Test' THEN runs_scored END) AS test_avg,
            SUM(CASE WHEN format = 'ODI' THEN 1 ELSE 0 END) AS odi_matches,
            AVG(CASE WHEN format = 'ODI' THEN runs_scored END) AS odi_avg,
            SUM(CASE WHEN format = 'T20' THEN 1 ELSE 0 END) AS t20_matches,
            AVG(CASE WHEN format = 'T20' THEN runs_scored END) AS t20_avg
        FROM batting_performance
        GROUP BY player_name
        HAVING COUNT(match_id) >= 20;
    """
}

conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="Iyal@244",
    database="cricbuzz"
)

cursor = conn.cursor()

# 1. Generate dropdown options from dict keys
selected_title = st.selectbox(
    label="Choose a query to execute:",
    options=list(queries_dict.keys())
)

# 2. Extract corresponding SQL code
sql_query = queries_dict[selected_title]

# 3. Code display box (helps verify query structure)
st.subheader("Target SQL Syntax")
st.code(sql_query, language="sql")

# 4. Data execution and display block
if st.button("Run Analytics Query"):
    try:
        # Assumes 'cursor' and 'conn' variables are pre-configured
        cursor.execute(sql_query)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        
        df = pd.DataFrame(data, columns=columns)
        
        st.subheader("📊 Query Results")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Database query execution failed: {e}")




cursor.close()
conn.close()