# 🏏 Cricbuzz LiveStats: Real-Time Cricket Analytics Dashboard

[![Python](https://shields.io)](https://python.org)
[![Streamlit](https://shields.io)](https://streamlit.io)
[![MySQL](https://shields.io)](https://mysql.com)
[![Pandas](https://shields.io)](https://pydata.org)

A comprehensive **Cricket Analytics Dashboard** that integrates live data from the Cricbuzz API with a relational SQL database to create an interactive web application. The platform delivers real-time match updates, detailed player statistics, an interface for custom SQL-driven analytics, and a full administrative CRUD control panel to manage records manually.

---

## 🚀 Key Features

*   **⚡ Real-Time Match Updates:** Fetches live cricket match data, scorecards, batting/bowling breakdowns, and series statuses directly via REST API integration.
*   **📊 Detailed Player Statistics:** Displays aggregated player profile data, historical trends, running forms, and KPI visualization charts.
*   **🔍 SQL-Driven Analytics:** Includes a dedicated analytical workbench featuring custom pre-optimized SQL queries to uncover deep performance insights.
*   **🛠️ Full CRUD Operations:** Features a secure, form-based administrator interface to Create, Read, Update, and Delete player metrics and profiles manually.
*   **📤 Data Portability:** Enables downloading filtered statistical reports and analytical query outputs directly as CSV files.

---

## 🧰 Tech Stack

*   **Frontend / UI:** Streamlit (Multi-page interactive web framework)
*   **Backend / Programming:** Python 3.x
*   **Database Integration:** MySQL
*   **Data Processing:** Pandas
*   **External API Data:** Cricbuzz Official Cricket API via RapidAPI Portal

---

## 📋 Prerequisites

Before setting up the project locally, make sure you have:
*   Python 3.8 or higher installed.
*   An API Key for the Cricbuzz API.
*   A MySQL database environment running locally or remotely.

---

## ⚙️ Installation & Setup

Follow these step-by-step instructions to get your local environment running:

### 1. Clone the Repository
```bash
git clone https://github.com
cd Cricbuzz
```

### 2. Set Up a Virtual Environment
```bash
# Create the virtual environment
python -m venv venv

# Activate the virtual environment (Windows)
venv\Scripts\activate

# Activate the virtual environment (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a file named `.env` in the root directory of your project and configure your credentials:

```env
# Cricbuzz API Credentials
CRICBUZZ_API_KEY=your_rapidapi_key_here
CRICBUZZ_API_HOST=cricbuzz-cricket.p.rapidapi.com

# Database Configurations
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=your_database_password_here
DB_NAME=cricbuzz
```

### 5. Initialize the Database Schema
Execute the script to seed your tables and build your core relations:
```bash
python utils/db_connection.py
```

### 6. Run the Application
```bash
streamlit run app.py
```

---

## 📊 Dashboard Sections & Usage

*   **🔴 Live Matches:** Track active matches with automatically updating inning scorecards, batting metrics, and live economy rates.
*   **🧢 Player Profiles:** Search players to view a comprehensive breakdown of runs, wickets, strike rates, and centuries.
*   **💡 SQL Query Console:** A custom SQL query box with 25 pre-built beginner-to-advanced query options to run analytics on player averages, team forms, or venue records.
*   **🛡️ Data Control Panel (CRUD):** Form-based data manipulation cards. Securely fix data gaps, insert new players, or remove outdated records from persistent SQL tables.

