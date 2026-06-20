import mysql.connector
import requests
import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. ESTABLISH CONNECTIVITY ---
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="Iyal@244",
    database="cricbuzz"
)
cursor = conn.cursor(buffered=True)

# --- 2. CREATE PLAYERS TABLE query 1 ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS players_list (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(100),
    role VARCHAR(100),
    battingStyle VARCHAR(100),
    bowlingStyle VARCHAR(100)
) ENGINE=InnoDB;
""")
conn.commit()
print("Players table created successfully.")

# --- 3. FETCH & PROCESS PLAYER DATA ---
url = "https://cricbuzz-cricket.p.rapidapi.com/teams/v1/2/players"

headers = {
	"x-rapidapi-key": "1b0e280e4dmshf40794f4f289c27p1311a4jsn0a577eeb6dd4",
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com",
	"Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
data_players = response.json()

rows = data_players.get("player", [])
player_inserted_count = 0
current_role = None

role_map = {
    "BATSMEN": "Batsman",
    "ALL ROUNDER": "All-Rounder",
    "WICKET KEEPER": "Wicket-Keeper",
    "BOWLER": "Bowler"
}

try:
    for item in rows:
        item_name = item.get("name")
            
        # Context Check: If item does not have an 'id', it is a category header
        if "id" not in item:
            if item_name in role_map:
                current_role = role_map[item_name]
            continue  # Move directly to the next item loop iteration

        # Extract variables safely (Only executes if 'id' exists)
        player_id = item.get("id")
        name = item_name
        batting_style = item.get("battingStyle", "N/A")
        bowling_style = item.get("bowlingStyle", "N/A")
        
        # FIX: Pointed to players_list and implemented modern MySQL 'AS new_data' row alias
        query_player = """
            INSERT INTO players_list (id, name, role, battingStyle, bowlingStyle) 
            VALUES (%s, %s, %s, %s, %s)
            AS new_data
            ON DUPLICATE KEY UPDATE 
                name = new_data.name,
                role = new_data.role,
                battingStyle = new_data.battingStyle,
                bowlingStyle = new_data.bowlingStyle;
        """
        
        cursor.execute(query_player, (player_id, name, current_role, batting_style, bowling_style))
        player_inserted_count += 1
            
    conn.commit()
    print(f"🚀 Success! Safely processed {player_inserted_count} player records.")
        
except mysql.connector.Error as err:
    print(f"❌ Player Database error encountered: {err}")
     

#create table for query 2
cursor.execute("""
CREATE TABLE IF NOT EXISTS matches (
                match_id INT PRIMARY KEY,
                match_name VARCHAR(255),
                match_date DATETIME,
                match_description VARCHAR(255),
                match_status VARCHAR(50),
                team_1_name VARCHAR(100),
                team_2_name VARCHAR(100),
                winning_team VARCHAR(100),
                victory_margin VARCHAR(100),
                venue_id INT,
                venue_name VARCHAR(255),
                venue_city VARCHAR(100)
            )
""")
conn.commit()
print("Table created successfully")

#Fetching data of matches details from API
url = "https://cricbuzz-cricket2.p.rapidapi.com/matches/v1/recent"

headers = {
	"x-rapidapi-key": "1b0e280e4dmshf40794f4f289c27p1311a4jsn0a577eeb6dd4",
	"x-rapidapi-host": "cricbuzz-cricket2.p.rapidapi.com",
	"Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
data_match = response.json()

def parse_match_data(data_match):
    """Loops through JSON and extracts targeted match schema fields."""
    parsed_records = []
    
    for type_match in data_match.get("typeMatches", []):
        for series_match in type_match.get("seriesMatches", []):
            wrapper = series_match.get("seriesAdWrapper", {})
            for match in wrapper.get("matches", []):
                info = match.get("matchInfo", {})
                score = match.get("matchScore", {})
                team1_runs = score.get("team1Score", {}).get("inngs1", {}).get("runs", "Unknown")
                team2_runs = score.get("team2Score", {}).get("inngs1", {}).get("runs", "Unknown")
                 # Format Match Name
                team1 = info.get("team1", {}).get("teamName", "Unknown")
                team2 = info.get("team2", {}).get("teamName", "Unknown")
                # Default values if math cannot be completed
                winning_team = "No Result / Ongoing"
                victory_margin = "N/A"

                # 2. Safely parse, compare, and determine the winner
                if team1_runs and team2_runs:
                    try:
                        # Convert "240/5" -> 240
                        t1_runs = int(str(team1_runs).split('/')[0])
                        t2_runs = int(str(team2_runs).split('/')[0])

                        # Calculate Margin
                        victory_margin = str(abs(t1_runs - t2_runs))
        
                        # Compare to find the winning team
                        if t1_runs > t2_runs:
                            winning_team = team1
                        elif t2_runs > t1_runs:
                            winning_team = team2
                        else:
                            winning_team = "Match Tied"
            
                    except (ValueError, IndexError):
                        # Fallback if data format is unexpected
                        winning_team = "Data Error"
                        victory_margin = "Unknown"
         
                # Convert Millisecond Timestamp to MySQL Standard DATETIME (YYYY-MM-DD HH:MM:SS)
                timestamp_ms = info.get("startDate")
                formatted_date = None
                if timestamp_ms:
                    formatted_date = datetime.fromtimestamp(float(timestamp_ms) / 1000).strftime('%Y-%m-%d %H:%M:%S')

                # Create structured tuple matching table column order
                match_record = (
                    info.get("matchId"), # Unique Key
                    info.get("seriesName"),
                    formatted_date,
                    info.get("matchDesc"),
                    info.get("state"),
                    team1,
                    team2,
                    winning_team,
                    victory_margin,
                    info.get("venueInfo", {}).get("id"),
                    info.get("venueInfo", {}).get("ground"),
                    info.get("venueInfo", {}).get("city")
                )
                parsed_records.append(match_record)
                
    return parsed_records

# Insert parsed match records into the database
insert_query = """
INSERT INTO matches (
    match_id, match_name, match_date, match_description, match_status,
    team_1_name, team_2_name, winning_team,
    victory_margin, venue_id, venue_name, venue_city
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    match_id = VALUES(match_id),
    match_name = VALUES(match_name),
    match_date = VALUES(match_date),
    match_description = VALUES(match_description),
    match_status = VALUES(match_status),
    team_1_name = VALUES(team_1_name),
    team_2_name = VALUES(team_2_name),
    winning_team = VALUES(winning_team),
    victory_margin = VALUES(victory_margin),
    venue_id = VALUES(venue_id),
    venue_name = VALUES(venue_name),
    venue_city = VALUES(venue_city);
"""

# Extract the data using your existing function
match_records = parse_match_data(data_match)

# Loop through each row and execute individually
inserted_count = 0
for record in match_records:
    try:
        cursor.execute(insert_query, record)
        inserted_count += 1
    except Exception as e:
        print(f"Failed to insert record {record[0]} due to: {e}")

# Commit all successful changes once after the loop
conn.commit()
print(f"Successfully processed {inserted_count} records.")

#create table for query 3
cursor.execute("""
CREATE TABLE IF NOT EXISTS ODI_match_scorecard (
                player_id INT PRIMARY KEY,
                player_name VARCHAR(255),
                runs VARCHAR(100),
                batting_avg VARCHAR(100),
                venue_name VARCHAR(255),
                venue_city VARCHAR(100)
            )
""")
conn.commit()
print("Table created successfully")

#create table for query 4
cursor.execute("""
CREATE TABLE IF NOT EXISTS venue_details (
                venue_id INT PRIMARY KEY,
                venue_name VARCHAR(255),
                venue_city VARCHAR(100),
                venue_country VARCHAR(100),
                venue_capacity INT
            )
""")
conn.commit()
print("Table created successfully")

sql_query = """select venue_id from matches;"""
cursor.execute(sql_query)
venue_ids = cursor.fetchall()
count=0
for venue_id in venue_ids:
    url = f"https://cricbuzz-cricket.p.rapidapi.com/venues/v1/{venue_id[0]}"
    headers = {
        "x-rapidapi-key": "1b0e280e4dmshf40794f4f289c27p1311a4jsn0a577eeb6dd4",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    venue_data = response.json()
    venue_record = (
        venue_data.get("id"),
        venue_data.get("ground"),
        venue_data.get("city"),
        venue_data.get("country"),
        venue_data.get("capacity")
    )
    insert_query = """
    INSERT INTO venue_details (venue_id, venue_name, venue_city, venue_country, venue_capacity)
    VALUES (%s, %s, %s, %s, %s) """
    cursor.execute(insert_query, venue_record)
    count+=1
conn.commit()
print(f"Venue details inserted successfully. Total records: {count}")


