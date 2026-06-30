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
        SELECT player_name, runs as total_runs, average as batting_average,hundreds as centuries 
        FROM player_batting_stats where format_type='ODI' 
        ORDER BY runs DESC 
        LIMIT 10;
    """,
        
    "Q4: Top 10 Stadiums with >25k Capacity": """
        SELECT venue_name, venue_city, venue_country, venue_capacity 
        FROM venue_details 
        WHERE venue_capacity > 25000 
        ORDER BY venue_capacity DESC 
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
        SELECT format_type, MAX(highest_score) AS highest_individual_score 
        FROM player_batting_stats 
        GROUP BY format_type;
    """,
    
    "Q8: Cricket Series Started in 2024": """
        SELECT series_name, host_country, match_type, start_date, total_matches
        FROM international_series_2024 
        WHERE YEAR(start_date) = 2024;
    """,
     "Q9: Elite All-Rounders (>1000 Runs & >50 Wickets)": """
        SELECT distinct Player_name, Runs as Total_runs, Wickets as Total_wickets, Format_type 
        FROM player_bowler_stats 
        WHERE Runs > 1000 
          AND Wickets > 50;
    """,
        
    "Q10: Details of Last 20 Completed Matches": """
        SELECT match_description, team_1_name, team_2_name, winning_team, victory_margin, match_status, venue_name 
        FROM matches 
        WHERE match_status = 'Complete' 
        ORDER BY match_date DESC 
        LIMIT 20;
    """,
    "Q11: Cross-Format Player Batting Comparison": """
       SELECT player_name,
            SUM(CASE WHEN format_type = 'Test' THEN runs ELSE 0 END) AS test_runs,
            SUM(CASE WHEN format_type = 'ODI' THEN runs ELSE 0 END) AS odi_runs,
            SUM(CASE WHEN format_type = 'T20' THEN runs ELSE 0 END) AS t20_runs,
            AVG(average) AS overall_average
        FROM player_batting_stats
        GROUP BY player_name
        HAVING COUNT(DISTINCT format_type) >= 2;
    """,
    "Q12: Team Performance (Home vs Away Wins)" : """
        WITH normalized_matches AS (
        SELECT 
        match_id,
        team_1_name,
        team_2_name,
        winning_team,
        CASE 
            WHEN venue_city LIKE '%Jamaica%' THEN 'West Indies'
            WHEN venue_city IN ('Manchester', 'Southampton', 'Birmingham', 'Leeds', 'Scarborough', 'Leicester', 'Hove', 'Nottingham', 'Northampton', 'Blackpool', 'Worcester', 'Chester-le-Street', 'Kibworth', 'Bromsgrove', 'West Sussex', 'Horton') THEN 'England'
            WHEN venue_city IN ('Dharamsala', 'Lucknow', 'Mumbai') THEN 'India'
            WHEN venue_city IN ('Dhaka', 'Chattogram') THEN 'Bangladesh'
            WHEN venue_city = 'Dambulla' THEN 'Sri Lanka'
            WHEN venue_city = 'Dallas' THEN 'United States'
            WHEN venue_city = 'King City' THEN 'Canada'
            WHEN venue_city = 'Kigali City' THEN 'Rwanda'
            WHEN venue_city = 'Stockholm' THEN 'Sweden'
            WHEN venue_city = 'Brondby' THEN 'Denmark'
            ELSE 'Unknown'
        END AS venue_country
    FROM matches
    WHERE match_status = 'Complete'
),
team_performances AS (
       SELECT 
        team_1_name AS team,
        CASE 
            WHEN team_1_name LIKE '%' || venue_country || '%' THEN 'Home' 
            ELSE 'Away' 
        END AS match_location,
        CASE WHEN winning_team = team_1_name THEN 1 ELSE 0 END AS is_win
    FROM normalized_matches

    UNION ALL
    
    SELECT 
        team_2_name AS team,
        CASE 
            WHEN team_2_name LIKE '%' || venue_country || '%' THEN 'Home' 
            ELSE 'Away' 
        END AS match_location,
        CASE WHEN winning_team = team_2_name THEN 1 ELSE 0 END AS is_win
    FROM normalized_matches
)
SELECT 
    team,
    SUM(CASE WHEN match_location = 'Home' THEN is_win ELSE 0 END) AS home_wins,
    SUM(CASE WHEN match_location = 'Away' THEN is_win ELSE 0 END) AS away_wins,
    SUM(CASE WHEN match_location = 'Home' THEN 1 ELSE 0 END) AS total_home_matches,
    SUM(CASE WHEN match_location = 'Away' THEN 1 ELSE 0 END) AS total_away_matches
FROM team_performances
WHERE team NOT IN ('Yorkshire', 'Warwickshire', 'Essex', 'Leicestershire', 'Glamorgan', 'Sussex', 'Somerset', 'Nottinghamshire', 'Northamptonshire', 'Gloucestershire', 'Kent', 'Lancashire', 'Middlesex', 'Worcestershire', 'Durham', 'Derbyshire', 'Seattle Orcas', 'Texas Super Kings', 'San Francisco Unicorns', 'Los Angeles Knight Riders', 'Washington Freedom', 'MSC Maratha Royals', 'ARCS Andheri', 'Kent Women', 'Leicestershire Women', 'Middlesex Women', 'Worcestershire Women', 'Gloucestershire Women', 'Sussex Women', 'Derbyshire Women', 'Northamptonshire Women')
GROUP BY team
ORDER BY (home_wins + away_wins) DESC, team ASC;
    """,

    "Q13: batting partnerships runs of two consecutive batsmen": """
        select bat1name as Batsman_1, bat2name as Batsman_2, total_runs as Combined_partnership_runs,
 innings_id as Innings from batsman_partnership_details where total_runs > 100;
    """,

    "Q14: bowling performance at different venues": """
        SELECT 
        bowler_name,
        venue_id,
        COUNT(*) AS matches_played,
        SUM(wickets) AS total_wickets,
        ROUND(AVG(economy_rate), 2) AS average_economy_rate FROM bowler_scorecard_details WHERE overs >= 4 GROUP BY bowler_name,venue_id
    HAVING COUNT(*) >= 3
    ORDER BY venue_id ASC, average_economy_rate ASC;
 """,
    "Q15: players who perform exceptionally well in close matches" : """    
        SELECT 
            b.batsman_name,
            COUNT(DISTINCT m.match_id) AS total_close_matches_played,
            ROUND(AVG(b.runs), 2) AS average_runs_scored
        FROM batsman_scorecard_details b
        JOIN matches m ON b.match_id = m.match_id
        WHERE m.victory_margin < 50
        GROUP BY b.batsman_name
        HAVING COUNT(DISTINCT m.match_id) >= 3
        ORDER BY average_runs_scored DESC;"""
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
