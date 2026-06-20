import streamlit as st
import requests

# 1. API Configuration Setup
API_HOST = "cricbuzz-cricket.p.rapidapi.com"
API_KEY = "1b0e280e4dmshf40794f4f289c27p1311a4jsn0a577eeb6dd4"

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST,
    "Content-Type": "application/json"
}

st.title("🏏 Player Profile Search")

# 2. Text Input Search Bar
search_name = st.text_input("Search for a player:", placeholder="e.g., MS Dhoni")
    
if search_name:
    # STEP 1: Search for the player name to fetch their unique ID
    # Endpoint for cricbuzz-cricket host is usually /stats/v1/player/search
    search_url = f"https://{API_HOST}/stats/v1/player/search"
    
    with st.spinner("Searching for player..."):
        try:
            querystring = {"plrN":f"{search_name}"}
            search_response = requests.get(search_url, headers=headers, params=querystring)
            search_data = search_response.json()
            players_list = search_data.get("player", [])
        except Exception as e:
            st.error(f"Search API error: {e}")
            players_list = []

    if players_list:
        # Create a dictionary to handle duplicate names across teams
        player_map = {
            f"{p.get('name')} ({p.get('teamName', 'International')})": p.get('id') 
            for p in players_list
        }
        
        # Dropdown selection in case multiple matching profiles are found
        selected_player = st.selectbox("Select the exact player:", options=list(player_map.keys()))
        chosen_id = player_map[selected_player]
        
        # STEP 2: Use your specific dynamic ID URL to load profile data
        if chosen_id:
            profile_url = f"https://{API_HOST}/stats/v1/player/{chosen_id}"
            
            with st.spinner("Fetching career stats..."):
                profile_response = requests.get(profile_url, headers=headers)
                profile_data = profile_response.json()
            
            # 3. Render Profile Layout dynamically
            st.divider()
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Fallback to generic icon if image URL is absent in payload
                st.subheader(profile_data.get("name", search_name))
                st.caption(f"Team: {profile_data.get('intlTeam', 'Domestic/Other')}")

            with col2:
                st.markdown(f"**Role:** {profile_data.get('role', 'N/A')}")
                st.markdown(f"**Batting Style:** {profile_data.get('bat', 'N/A')}")
                st.markdown(f"**Bowling Style:** {profile_data.get('bowl', 'N/A')}")
                st.markdown(f"**Date of Birth:** {profile_data.get('DoB', 'N/A')}")
            
            # 4. Render Statistical Dataframes
            st.subheader("📊 Career Performance")
            batting_stats = profile_data.get("rankings", {}).get("bat", {})
            bowling_stats = profile_data.get("rankings", {}).get("bowl", {})
            
            if batting_stats:
                st.write("**Batting Record**")
                st.dataframe(batting_stats, use_container_width=True)
            if bowling_stats:
                st.write("**Bowling Record**")
                st.dataframe(bowling_stats, use_container_width=True)
    else:
        st.warning("No players matched your search. Try checking the spelling.")
