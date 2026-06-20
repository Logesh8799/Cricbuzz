import streamlit as st

st.title("🏏Cricbuzz Dashboard")
st.markdown("This dashboard provides live cricket match data fetched from the Cricbuzz API and stored in a MySQL database. The data is updated every 5 minutes to ensure you have the latest information on ongoing matches, player statistics, and more.")

st.info("Use the sidebar to navigate between different sections of the dashboard, including live scores, player statistics, SQL analytics, and CRUD operations on the database.")

st.sidebar.title("Cricket Dashboard")


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