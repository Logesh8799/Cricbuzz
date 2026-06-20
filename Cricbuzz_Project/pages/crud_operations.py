import streamlit as st
import mysql.connector
import pandas as pd

# --- 1. DATABASE CONNECTION---
def get_db_connection():
    """Establishes and returns a fresh connection using your specific parameters."""
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Iyal@244", 
        database="cricbuzz"
    )
def run_query(query, params=(), fetch=False):
    """Utility wrapper to execute queries using your standard connection layout."""
    conn = get_db_connection()
    cursor = conn.cursor(buffered=True)
    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return []
    except mysql.connector.Error as err:
        st.error(f"MySQL Execution Error: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

def init_db():
    """Initializes the database schema if tables do not exist."""
    query = """
    CREATE TABLE IF NOT EXISTS players (
        player_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        country VARCHAR(100) NOT NULL,
        role ENUM('Batsman', 'Bowler', 'All-Rounder', 'Wicket-Keeper') NOT NULL,
        matches_played INT DEFAULT 0
    ) ENGINE=InnoDB;
    """
    run_query(query)

init_db()

# --- 2. STREAMLIT FRAMEWORK SETUP ---
st.set_page_config(page_title="Cricbuzz Analytics Studio", layout="wide")
st.title("🏏 Player Management Database Engine")

st.sidebar.header("Navigation Panel")
operation = st.sidebar.radio(
    "Select Database Task",
    ["View Players (READ)", "Add Player (CREATE)", "Modify Record (UPDATE)", "Remove Player (DELETE)"]
)

# --- 3. DATABASE CRUD INTERFACES ---


# READ: View Table & Summary Data
if operation == "View Players (READ)":
    st.subheader("📋 Active Player Details")
    
    # Establish a local connection directly for pandas to read
    conn = get_db_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM players", conn)
    finally:
        conn.close()

    if df.empty:
        st.info("The database is currently empty. Head over to 'Add Player' to insert records.")
    else:
        # Visual metric cards
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Profiles", len(df))
        col2.metric("Unique Countries", df["country"].nunique())
        col3.metric("Avg Matches Played", int(df["matches_played"].mean()))

        st.dataframe(df, use_container_width=True, hide_index=True)

# CREATE: Insert Profiles Into System

elif operation == "Add Player (CREATE)":
    st.subheader("➕ Register New Player Profile")
    
    with st.form("add_player_form", clear_on_submit=True):
        name = st.text_input("Full Name").strip()
        country = st.text_input("Representing Country").strip()
        role = st.selectbox("On-Field Role", ["Batsman", "Bowler", "All-Rounder", "Wicket-Keeper"])
        matches = st.number_input("Career Matches Played", min_value=0, step=1, value=0)
        
        submitted = st.form_submit_button("Commit Entry to MySQL")
        
        if submitted:
            if name and country:
                run_query(
                    "INSERT INTO players (name, country, role, matches_played) VALUES (%s, %s, %s, %s)",
                    (name, country, role, matches)
                )
                st.success(f"Successfully recorded data for {name} ({country})!")
            else:
                st.error("Submission failed. 'Full Name' and 'Representing Country' cannot be blank.")

# UPDATE: Modify Selected Row Parameters

elif operation == "Modify Record (UPDATE)":
    st.subheader("🔄 Update Existing Profiles")
    
    player_records = run_query("SELECT player_id, name FROM players", fetch=True)
    
    if not player_records:
        st.warning("No entries found inside the system to update.")
    else:
        player_dict = {f"{row[1]} (ID: {row[0]})": row[0] for row in player_records}
        selected_player = st.selectbox("Target Profile to Edit", list(player_dict.keys()))
        target_id = player_dict[selected_player]
        
        # Populate fields with current entry metrics
        current_data = run_query(
            "SELECT name, country, role, matches_played FROM players WHERE player_id = %s", 
            (target_id,), fetch=True
        )[0]
        
        with st.form("update_player_form"):
            new_name = st.text_input("Update Full Name", value=current_data[0])
            new_country = st.text_input("Update Representing Country", value=current_data[1])
            roles_list = ["Batsman", "Bowler", "All-Rounder", "Wicket-Keeper"]
            new_role = st.selectbox("Update On-Field Role", roles_list, index=roles_list.index(current_data[2]))
            new_matches = st.number_input("Update Career Matches", min_value=0, step=1, value=current_data[3])
            
            update_submitted = st.form_submit_button("Push Changes to MySQL")
            
            if update_submitted:
                if new_name.strip() and new_country.strip():
                    run_query(
                        """UPDATE players 
                           SET name = %s, country = %s, role = %s, matches_played = %s 
                           WHERE player_id = %s""",
                        (new_name, new_country, new_role, new_matches, target_id)
                    )
                    st.success(f"System profile update for ID {target_id} processed successfully!")
                   # st.rerun()
                else:
                    st.error("Changes rejected. Profile metadata fields cannot be saved empty.")

# DELETE: Destructive Row Removal

elif operation == "Remove Player (DELETE)":
    st.subheader("🗑️ Deleting Player Profiles")
    
    player_records = run_query("SELECT player_id, name, country FROM players", fetch=True)
    
    if not player_records:
        st.warning("No valid player data rows exist inside database tables.")
    else:
        player_dict = {f"{row[1]} ({row[2]} - ID: {row[0]})": row[0] for row in player_records}
        selected_player = st.selectbox("Target Profile to Erase", list(player_dict.keys()))
        target_id = player_dict[selected_player]
        
                
        if st.button("Delete Entry Permanently"):
           
                run_query("DELETE FROM players WHERE player_id = %s", (target_id,))
                st.success("The selected entry has been completely erased from the SQL database.")
                st.rerun()
           
