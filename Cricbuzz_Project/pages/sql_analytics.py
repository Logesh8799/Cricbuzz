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
    
        
    "Q3: Top 10 Stadiums with >25k Capacity": """
        SELECT venue_name, venue_city, venue_country, venue_capacity 
        FROM venue_details 
        WHERE venue_capacity > 25000 
        ORDER BY venue_capacity DESC 
        LIMIT 10;
    """,
    
    "Q4: Total Match Wins by Team": """
        SELECT winning_team AS team_name, COUNT(*) AS total_wins 
        FROM matches 
        WHERE winning_team IS NOT NULL 
        GROUP BY winning_team 
        ORDER BY total_wins DESC;
    """,
    
    "Q5: Player Count by Playing Role": """
        SELECT role, COUNT(*) AS player_count 
        FROM players_list
        GROUP BY role 
        ORDER BY player_count DESC;
    """,
    
    "Q6: Highest Individual Score by Format": """
        SELECT format_type, MAX(highest_score) AS highest_individual_score 
        FROM player_stats 
        GROUP BY format_type;
    """,
    
    "Q7: Cricket Series Started in 2024": """
        SELECT series_name, host_country, match_type, start_date, total_matches
        FROM international_series_2024 
        WHERE YEAR(start_date) = 2024;
    """,
    
        
    "Q8: Details of Last 20 Completed Matches": """
        SELECT match_description, team_1_name, team_2_name, winning_team, victory_margin, match_status, venue_name 
        FROM matches 
        WHERE match_status = 'Complete' 
        ORDER BY match_date DESC 
        LIMIT 20;
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
