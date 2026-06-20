import streamlit as st
import requests
import mysql.connector
import json
import pandas as pd
from datetime import datetime
import time

#Page configuration
st.set_page_config(page_title="Cricbuzz Dashboard", 
                   layout="wide",
                   initial_sidebar_state="expanded",
                   page_icon="https://www.cricbuzz.com/favicon.ico")
st.title("Cricbuzz Dashboard")
url = "https://thumbs.dreamstime.com/b/cricket-player-hitting-ball-stadium-crowd-lights-powerfully-swings-his-bat-surrounded-floodlights-cheering-364002906.jpg?w=992"
st.image(url, caption="Cricket Pitch")

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