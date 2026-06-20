import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Cricbuzz Live Match Dashboard", page_icon="https://www.cricbuzz.com/favicon.ico")
st.title("Cricbuzz Live Match Dashboard")

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

url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"

headers = {
	"x-rapidapi-key": "1b0e280e4dmshf40794f4f289c27p1311a4jsn0a577eeb6dd4",
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com",
	"Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
data=response.json()


def load_and_parse_data(json_data):
    matches_dict = {}

    # Traverse the nested JSON structure
    for match_type_group in json_data.get("typeMatches", []):
        for series_match in match_type_group.get("seriesMatches", []):
            wrapper = series_match.get("seriesAdWrapper", {})
            series_name = wrapper.get("seriesName", "Unknown Series")

            for match in wrapper.get("matches", []):
                match_info = match.get("matchInfo", {})
                match_score = match.get("matchScore", {})

                # Extract basic info
                match_id = match_info.get("matchId")
                team1 = match_info.get("team1", {}).get("teamName", "Team 1")
                team2 = match_info.get("team2", {}).get("teamName", "Team 2")
                match_desc = match_info.get("matchDesc", "Match")

                # Create a user-friendly label for the selectbox
                display_label = (
                    f"{team1} vs {team2} ({match_desc})"
                )

                # Store the match data mapped to its unique display label
                matches_dict[display_label] = {
                    "info": match_info,
                    "score": match_score,
                    "series_name": series_name,
                }

    return matches_dict

def build_scorecard_dataframe(innings_data, batting_team, bowling_team):
    if not innings_data:
        return None, None

    # Extracted data from payload
    runs = innings_data.get("runs", 0)
    wickets = innings_data.get("wickets", 0)
    overs = innings_data.get("overs", 0.0)

    # Calculate run rate
    run_rate = round(runs / overs, 2) if overs > 0 else 0.0

    # 1. Structured Batting DataFrame
    batting_df = pd.DataFrame(
        [
            {
                "Team": batting_team,
                "Runs Scored": runs,
                "Wickets Lost": wickets,
                "Overs Faced": overs,
                "Run Rate (CRR)": run_rate,
            }
        ]
    )

    # 2. Structured Bowling DataFrame
    bowling_df = pd.DataFrame(
        [
            {
                "Bowling Team": bowling_team,
                "Overs Bowled": overs,
                "Runs Conceded": runs,
                "Wickets Taken": wickets,
                "Economy Rate": run_rate,
            }
        ]
    )

    return batting_df, bowling_df



parsed_matches = load_and_parse_data(data)
selected_match = st.selectbox(
    "Select an ongoing match:", options=list(parsed_matches.keys())
)

if selected_match:
    match_data = parsed_matches[selected_match]
    info = match_data["info"]
    score = match_data["score"]

    t1 = info.get("team1", {}).get("teamName")
    t2 = info.get("team2", {}).get("teamName")

    st.info(f"💡 **Live Status Update:** {info.get('status')}")

    # --- INNINGS 1 TABULAR SECTION ---
    st.markdown("## 1️⃣ Innings 1 Performance Scorecard")
    inn1_data = score.get("team1Score", {}).get("inngs1", {})

    if inn1_data:
        # Team 1 bats first, Team 2 bowls first
        bat_df1, bowl_df1 = build_scorecard_dataframe(
            inn1_data, batting_team=t1, bowling_team=t2
        )

        st.markdown("#### 🏏 Batting Performance")
        st.table(bat_df1)

        st.markdown("#### 🥎 Bowling Performance")
        st.table(bowl_df1)
    else:
        st.warning("Innings 1 has not commenced yet.")

    st.markdown("---")

    # --- INNINGS 2 TABULAR SECTION ---
    st.markdown("## 2️⃣ Innings 2 Performance Scorecard")
    inn2_data = score.get("team2Score", {}).get("inngs1", {})

    if inn2_data:
        # Team 2 bats second, Team 1 bowls second
        bat_df2, bowl_df2 = build_scorecard_dataframe(
            inn2_data, batting_team=t2, bowling_team=t1
        )

        st.markdown("#### 🏏 Batting Performance")
        st.table(bat_df2)

        st.markdown("#### 🥎 Bowling Performance")
        st.table(bowl_df2)
    else:
        st.warning("Innings 2 data is empty or not yet available.")

