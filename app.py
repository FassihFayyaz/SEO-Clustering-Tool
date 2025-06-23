# app.py

import streamlit as st
import json

# --- Import Project Modules ---
from config import API_BASE_URL
from modules.database import DatabaseManager
from modules.dataforseo_client import DataForSeoClient

# --- Import UI Modules ---
from ui import tab_data_fetcher, tab_local_clustering, tab_serp_clustering, tab_data_analysis, tab_debug_cache

# --- Page Configuration ---
st.set_page_config(
    page_title="SEO Keyword Clustering Tool", page_icon="🔑", layout="wide"
)

st.title("🔑 SEO Keyword Clustering Tool")
st.markdown("An efficient, cache-enabled tool for keyword analysis and SERP-based clustering.")

# --- Helper Functions ---
# Helper functions have been moved to utils.py

# --- Initialization & Session State ---
if 'clustered_data_for_analysis' not in st.session_state:
    st.session_state.clustered_data_for_analysis = None
if 'confirm_delete' not in st.session_state:
    st.session_state.confirm_delete = False

# --- Load Static Data & Initialize Clients ---
@st.cache_resource
def load_data_and_clients():
    try:
        with open('data/locations.json', 'r') as f:
            locations = json.load(f)
        with open('data/languages.json', 'r') as f:
            languages = json.load(f)
    except FileNotFoundError:
        st.error("Error: `locations.json` or `languages.json` not found in `data/` directory.")
        return None

    locations_map = {loc['name']: loc['code'] for loc in locations}
    languages_map = {lang['name']: lang['code'] for lang in languages}
    
    try:
        api_login = st.secrets["dataforseo"]["api_login"]
        api_password = st.secrets["dataforseo"]["api_password"]
    except (FileNotFoundError, KeyError):
        api_login, api_password = None, None
        
    db_manager = DatabaseManager()
    client = DataForSeoClient(api_login, api_password, API_BASE_URL)
    
    return locations, languages, locations_map, languages_map, db_manager, client

loaded_data = load_data_and_clients()

if loaded_data is None:
    st.stop() # Stop if data loading failed

locations, languages, locations_map, languages_map, db_manager, client = loaded_data

if not client or not client.login or not client.password:
    st.error("DataForSEO credentials are not configured. Please add them to your `.streamlit/secrets.toml` file.")
    st.stop()
    
# --- Main Application UI (Tabs) ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Data Fetcher", "🧠 Local Clustering (Placeholder)", "🔗 SERP Clustering", "📈 Data Analysis", "🐞 Debug & Cache"]
)

# == TAB 1: DATA FETCHER ==
with tab1:
    tab_data_fetcher.render(client, db_manager, locations, languages, locations_map, languages_map)

# == TAB 2: LOCAL CLUSTERING (PLACEHOLDER) ==
with tab2:
    tab_local_clustering.render()

# == TAB 3: SERP CLUSTERING ==
with tab3:
    tab_serp_clustering.render(db_manager, locations_map, languages_map)

# == TAB 4: DATA ANALYSIS ==
with tab4:
    tab_data_analysis.render()

# == TAB 5: DEBUG & CACHE ==
with tab5:
    tab_debug_cache.render(db_manager)
