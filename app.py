# app.py

import streamlit as st
import pandas as pd
import json
import time
import io

# --- Import Project Modules ---
from config import API_BASE_URL, SERP_TASK_POST, SERP_TASK_GET_ADVANCED, SEARCH_VOLUME_TASK_POST, SEARCH_VOLUME_TASK_GET, BULK_KD_LIVE, SEARCH_INTENT_LIVE
from modules.database import DatabaseManager
from modules.dataforseo_client import DataForSeoClient
from modules.clustering import perform_serp_clustering

# --- Page Configuration ---
st.set_page_config(
    page_title="SEO Keyword Clustering Tool",
    page_icon="🔑",
    layout="wide"
)

st.title("🔑 SEO Keyword Clustering Tool")
st.markdown("An efficient, cache-enabled tool for keyword analysis and SERP-based clustering.")

# --- Helper Functions ---
def get_keywords_from_input(text_input, file_input):
    """Extracts keywords from either a text area or an uploaded CSV file."""
    keywords = []
    if text_input:
        keywords = [kw.strip() for kw in text_input.split('\n') if kw.strip()]
    elif file_input:
        try:
            df = pd.read_csv(file_input)
            # Assuming the keywords are in the first column
            if not df.empty:
                keywords = [str(kw).strip() for kw in df.iloc[:, 0].dropna().tolist()]
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
            return []
    return list(set(keywords)) # Return unique keywords

def df_to_excel(df_detailed, df_summary):
    """Converts two DataFrames to a multi-sheet Excel file in memory."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_detailed.to_excel(writer, sheet_name='Clustered Keywords', index=False)
        df_summary.to_excel(writer, sheet_name='Cluster Summary', index=False)
    processed_data = output.getvalue()
    return processed_data

# --- Initialization & Session State ---
if 'clustered_data' not in st.session_state:
    st.session_state.clustered_data = None
    st.session_state.summary_data = None

# --- Load Static Data & Initialize Clients ---
@st.cache_resource
def load_data_and_clients():
    """Loads static JSON data and initializes API clients."""
    try:
        with open('data/locations.json', 'r') as f:
            locations = json.load(f)
        with open('data/languages.json', 'r') as f:
            languages = json.load(f)
    except FileNotFoundError:
        st.error("Error: `locations.json` or `languages.json` not found in `data/` directory.")
        return None, None, None, None
    
    # Load credentials
    try:
        api_login = st.secrets["dataforseo"]["api_login"]
        api_password = st.secrets["dataforseo"]["api_password"]
    except (FileNotFoundError, KeyError):
        api_login, api_password = None, None
        
    db_manager = DatabaseManager() # Initializes the db
    client = DataForSeoClient(api_login, api_password, API_BASE_URL)
    
    return locations, languages, db_manager, client

locations, languages, db_manager, client = load_data_and_clients()

# Check for secrets and stop if not found
if not client.login or not client.password:
    st.error("DataForSEO credentials are not configured. Please add them to your `.streamlit/secrets.toml` file.")
    st.stop()
    
# --- Main Application UI (Tabs) ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Data Fetcher", 
    "🧠 Local Clustering (Placeholder)", 
    "🔗 SERP Clustering", 
    "📈 Data Analysis"
])

# == TAB 1: DATA FETCHER ==
with tab1:
    st.header("Fetch and Cache Keyword Data")
    st.info("This module fetches data from DataForSEO. It checks the local cache first to avoid duplicate API calls.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Keyword Input")
        kw_text_input = st.text_area("Paste Keywords (one per line):", height=200)
    with col2:
        st.subheader("Or Upload CSV")
        kw_file_input = st.file_uploader("Upload a one-column CSV file with keywords.", type=['csv'])

    st.subheader("Search Parameters")
    c1, c2, c3 = st.columns(3)
    location_options = [loc['name'] for loc in locations]
    language_options = [lang['name'] for lang in languages]
    
    selected_location = c1.selectbox("Select Location:", location_options, index=0)
    selected_language = c2.selectbox("Select Language:", language_options, index=0)
    selected_device = c3.selectbox("Select Device:", ["desktop", "mobile"])

    st.subheader("Data to Fetch")
    fetch_serp = st.checkbox("SERP Results (for clustering)", value=True)
    # Add other data points here in the future
    # fetch_volume = st.checkbox("Search Volume & CPC")
    # fetch_kd = st.checkbox("Keyword Difficulty")
    # fetch_intent = st.checkbox("Search Intent")

    if st.button("🚀 Start Task", type="primary"):
        keywords = get_keywords_from_input(kw_text_input, kw_file_input)
        if not keywords:
            st.warning("Please provide at least one keyword.")
        else:
            st.success(f"Found {len(keywords)} unique keywords. Starting process...")
            log_area = st.container()
            progress_bar = st.progress(0)
            
            total_kws = len(keywords)
            for i, kw in enumerate(keywords):
                progress_bar.progress((i + 1) / total_kws, text=f"Processing: {kw}")
                
                # --- SERP Data Fetching Logic ---
                if fetch_serp:
                    # Construct a unique key for the cache
                    cache_key = f"serp|{kw.lower()}|{selected_location}|{selected_language}|{selected_device}"
                    
                    cached_data = db_manager.check_cache(cache_key)
                    if cached_data:
                        log_area.info(f"✅ Cache HIT for SERP data: '{kw}'")
                    else:
                        log_area.warning(f"❌ Cache MISS for SERP data: '{kw}'. Calling API...")
                        # This part would contain the logic to post a task and get results
                        # For simplicity in this example, we'll simulate it.
                        # In a real scenario, you'd call client.post_serp_tasks and then poll for results.
                        # For now, we just note that it would be fetched.
                        # For the purpose of this example, we will skip the live API call.
                        # You would need to implement the polling logic here.
                        log_area.error(f"API call for '{kw}' not implemented in this example. Please manually add data to the cache for now.")

# == TAB 2: LOCAL CLUSTERING (PLACEHOLDER) ==
with tab2:
    st.header("Local Semantic Clustering")
    st.info("This feature is reserved for a future implementation of a local, ML-based clustering model.")
    st.warning("Not yet implemented.")

# == TAB 3: SERP CLUSTERING ==
with tab3:
    st.header("Cluster Keywords by SERP Overlap")
    st.info("This module clusters keywords based on the number of shared URLs in their search results. It ONLY uses data from the local cache.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Keyword Input")
        cluster_kw_text = st.text_area("Paste keywords to cluster:", height=200, key="cluster_kw")
    with c2:
        st.subheader("Clustering Parameters")
        urls_to_check = st.slider("Number of Top URLs to Check:", min_value=5, max_value=20, value=10)
        min_intersections = st.number_input("Minimum Intersections to Cluster:", min_value=2, max_value=10, value=3)

    if st.button("🧩 Run SERP Clustering", type="primary"):
        keywords_to_cluster = get_keywords_from_input(cluster_kw_text, None)
        if not keywords_to_cluster:
            st.warning("Please provide keywords to cluster.")
        else:
            keyword_serp_data = {}
            missing_keywords = []
            
            st.write("Verifying data in local cache...")
            with st.spinner("Checking cache..."):
                for kw in keywords_to_cluster:
                    # NOTE: This assumes a fixed location/language/device for simplicity.
                    # A more robust app would let the user select which cached data to use.
                    cache_key = f"serp|{kw.lower()}|united states|english|desktop"
                    data = db_manager.check_cache(cache_key)
                    if data and 'tasks' in data and data['tasks'][0]['result']:
                        serp_results = data['tasks'][0]['result'][0]['items']
                        keyword_serp_data[kw] = [item['url'] for item in serp_results if 'url' in item]
                    else:
                        missing_keywords.append(kw)
            
            if missing_keywords:
                st.error("SERP data not found in cache for the following keywords. Please fetch them in the 'Data Fetcher' tab first:")
                st.json(missing_keywords)
            else:
                st.success("All keywords have cached SERP data. Running clustering...")
                clusters = perform_serp_clustering(keyword_serp_data, min_intersections, urls_to_check)
                st.info(f"Generated {len(clusters)} clusters.")
                
                # Post-process and create DataFrame
                # In a real app, you would now pull Volume, KD, etc., from the cache for these keywords.
                # For now, we create a placeholder dataframe.
                
                output_data = []
                for cluster in clusters:
                    main_keyword = cluster[0] # Simplistic main kw assignment
                    for keyword in cluster:
                        output_data.append({
                            "Cluster Main Keyword": main_keyword,
                            "Keyword": keyword,
                            "Volume": "N/A",
                            "CPC": "N/A",
                            "KD": "N/A"
                        })
                
                if output_data:
                    df_detailed = pd.DataFrame(output_data)
                    st.session_state.clustered_data = df_detailed
                    st.dataframe(df_detailed)
                    st.success("Clustering complete. View and analyze the results in the 'Data Analysis' tab.")
                else:
                    st.warning("Could not form any clusters based on the current settings.")


# == TAB 4: DATA ANALYSIS ==
with tab4:
    st.header("Analyze and Export Clusters")
    if st.session_state.clustered_data is None:
        st.info("Run clustering in the 'SERP Clustering' tab to see results here.")
    else:
        df_detailed = st.session_state.clustered_data
        
        st.subheader("Detailed Cluster Data (Filterable)")
        # For now, we just display it. A real app would use st.data_editor for filtering.
        st.dataframe(df_detailed, use_container_width=True)
        
        st.subheader("Cluster Summary")
        # In a real app, this would be calculated from the detailed data.
        # df_summary = df_detailed.groupby('Cluster Main Keyword').agg(...)
        # st.session_state.summary_data = df_summary
        st.info("Summary generation is not yet implemented.")

        st.download_button(
           label="📥 Export to Excel",
           # data=df_to_excel(df_detailed, st.session_state.summary_data),
           data=df_to_excel(df_detailed, pd.DataFrame()), # Placeholder for summary
           file_name=f"seo_clusters_{time.strftime('%Y%m%d')}.xlsx",
           mime="application/vnd.ms-excel"
        )
