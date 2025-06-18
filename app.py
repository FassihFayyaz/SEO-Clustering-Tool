# app.py

import streamlit as st
import pandas as pd
import json
import time
import io

# --- Import Project Modules ---
from config import API_BASE_URL
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
            if not df.empty:
                keywords = [str(kw).strip() for kw in df.iloc[:, 0].dropna().tolist()]
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
            return []
    return list(set(kw.lower() for kw in keywords)) # Return unique, lowercase keywords

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

locations, languages, locations_map, languages_map, db_manager, client = load_data_and_clients()

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
        kw_text_input = st.text_area("Paste Keywords (one per line):", height=200, key="data_fetcher_input")
    with col2:
        st.subheader("Or Upload CSV")
        kw_file_input = st.file_uploader("Upload a one-column CSV file with keywords.", type=['csv'])

    st.subheader("Search Parameters")
    c1, c2, c3 = st.columns(3)
    location_options = [loc['name'] for loc in locations]
    language_options = [lang['name'] for lang in languages]
    
    selected_location_name = c1.selectbox("Select Location:", location_options, index=0)
    selected_language_name = c2.selectbox("Select Language:", language_options, index=0)
    selected_device = c3.selectbox("Select Device (for SERP):", ["desktop", "mobile"])

    st.subheader("Data to Fetch")
    c1, c2, c3, c4 = st.columns(4)
    fetch_serp = c1.checkbox("SERP Results", value=True)
    fetch_volume = c2.checkbox("Search Volume/CPC", value=True)
    fetch_kd = c3.checkbox("Keyword Difficulty", value=True)
    fetch_intent = c4.checkbox("Search Intent", value=True)

    if st.button("🚀 Start Task", type="primary", key="start_fetch"):
        keywords = get_keywords_from_input(kw_text_input, kw_file_input)
        if not keywords:
            st.warning("Please provide at least one keyword.")
        else:
            st.success(f"Found {len(keywords)} unique keywords. Starting process...")
            log_area = st.container()
            progress_bar = st.progress(0)
            
            # Get corresponding codes for selected names
            location_code = locations_map[selected_location_name]
            language_code = languages_map[selected_language_name]

            # --- FULLY IMPLEMENTED API LOGIC ---
            total_kws = len(keywords)
            
            # Process Live APIs first (KD and Intent) as they are faster
            if fetch_kd:
                log_area.info("Fetching Keyword Difficulty...")
                cache_key = f"kd|{','.join(sorted(keywords))}|{location_code}|{language_code}"
                cached_data = db_manager.check_cache(cache_key)
                if cached_data:
                    log_area.success("✅ Found Bulk KD data in cache.")
                else:
                    response = client.fetch_bulk_keyword_difficulty(keywords, location_code, language_code)
                    if response and response.get('status_code') == 20000:
                        db_manager.update_cache(cache_key, response)
                        log_area.success("✅ Successfully fetched and cached Bulk KD.")
                    else:
                        log_area.error(f"❌ Failed to fetch Bulk KD. Response: {response}")

            if fetch_intent:
                log_area.info("Fetching Search Intent...")
                cache_key = f"intent|{','.join(sorted(keywords))}|{location_code}|{language_code}"
                cached_data = db_manager.check_cache(cache_key)
                if cached_data:
                    log_area.success("✅ Found Bulk Intent data in cache.")
                else:
                    response = client.fetch_search_intent(keywords, location_code, language_code)
                    if response and response.get('status_code') == 20000:
                        db_manager.update_cache(cache_key, response)
                        log_area.success("✅ Successfully fetched and cached Bulk Intent.")
                    else:
                        log_area.error(f"❌ Failed to fetch Bulk Intent. Response: {response}")

            # Process Asynchronous APIs (SERP and Volume)
            # This requires checking each keyword individually
            for i, kw in enumerate(keywords):
                progress_text = f"Processing keyword {i+1}/{total_kws}: {kw}"
                progress_bar.progress((i + 1) / total_kws, text=progress_text)

                # Fetch SERP Data
                if fetch_serp:
                    cache_key = f"serp|{kw}|{location_code}|{language_code}|{selected_device}"
                    if db_manager.check_cache(cache_key):
                        log_area.info(f"✅ SERP Cache HIT for: '{kw}'")
                    else:
                        log_area.warning(f"❌ SERP Cache MISS for: '{kw}'. Posting task...")
                        post_response = client.post_serp_tasks([kw], selected_location_name, selected_language_name, selected_device)
                        if post_response and post_response['tasks']:
                            task_id = post_response['tasks'][0]['id']
                            log_area.info(f"   - Task posted. ID: {task_id}. Polling for results...")
                            
                            get_url = f"{API_BASE_URL}/v3/serp/google/organic/task_get/advanced/{task_id}"
                            for _ in range(30): # Poll for 5 minutes max (30 * 10s)
                                time.sleep(10)
                                task_result = client.get_task_results(get_url)
                                if task_result and task_result.get('tasks') and task_result['tasks'][0].get('result'):
                                    db_manager.update_cache(cache_key, task_result)
                                    log_area.success(f"   - ✅ Got and cached SERP for '{kw}'")
                                    break
                            else:
                                log_area.error(f"   - ❌ SERP task timed out for '{kw}'")
                        else:
                            log_area.error(f"   - ❌ Failed to post SERP task for '{kw}'")
                
                # Fetch Volume Data
                if fetch_volume:
                    cache_key = f"volume|{kw}|{location_code}|{language_code}"
                    if db_manager.check_cache(cache_key):
                        log_area.info(f"✅ Volume Cache HIT for: '{kw}'")
                    else:
                        # Note: Volume API is also async but task_post accepts multiple kws. 
                        # For simplicity here, we post one by one to fit the loop.
                        # A bulk implementation would be more efficient.
                        log_area.warning(f"❌ Volume Cache MISS for: '{kw}'. Posting task...")
                        post_response = client.post_search_volume_tasks([kw], selected_location_name, selected_language_name)
                        if post_response and post_response['tasks']:
                            task_id = post_response['tasks'][0]['id']
                            log_area.info(f"   - Task posted. ID: {task_id}. Polling...")
                            get_url = f"{API_BASE_URL}/v3/keywords_data/google_ads/search_volume/task_get/{task_id}"
                            time.sleep(5) # Give it a moment before first poll
                            task_result = client.get_task_results(get_url)
                            if task_result and task_result.get('tasks') and task_result['tasks'][0].get('result'):
                                db_manager.update_cache(cache_key, task_result)
                                log_area.success(f"   - ✅ Got and cached Volume for '{kw}'")
                            else:
                                log_area.error(f"   - ❌ Failed to get Volume for '{kw}'")
                        else:
                            log_area.error(f"   - ❌ Failed to post Volume task for '{kw}'")


# == TAB 2: LOCAL CLUSTERING (PLACEHOLDER) ==
with tab2:
    st.header("Local Semantic Clustering")
    st.info("This feature is reserved for a future implementation of a local, ML-based clustering model.")
    st.warning("Not yet implemented.")

# == TAB 3: SERP CLUSTERING ==
with tab3:
    st.header("Cluster Keywords by SERP Overlap")
    st.info("This module clusters keywords based on shared URLs in their search results. It ONLY uses data from the local cache.")
    
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
            keyword_data_map = {} # Will hold all data: SERPs, volume, etc.
            missing_keywords = []
            
            st.write("Verifying data in local cache...")
            with st.spinner("Checking cache for all required data..."):
                # A more robust app would let the user select which cached data to use.
                # We assume the same params as the default fetcher for now.
                location_code = locations_map["United States"]
                language_code = languages_map["English"]
                
                # --- FIX: Load bulk data caches ONCE outside the loop for efficiency ---
                kd_key = f"kd|{','.join(sorted(keywords_to_cluster))}|{location_code}|{language_code}"
                kd_cache = db_manager.check_cache(kd_key)
                
                for kw in keywords_to_cluster:
                    keyword_data_map[kw] = {}
                    # 1. Fetch SERP
                    serp_key = f"serp|{kw}|{location_code}|{language_code}|desktop"
                    serp_data = db_manager.check_cache(serp_key)
                    if serp_data and 'tasks' in serp_data and serp_data['tasks'][0].get('result'):
                        serp_items = serp_data['tasks'][0]['result'][0]['items']
                        keyword_data_map[kw]['urls'] = [item['url'] for item in serp_items if 'url' in item]
                    else:
                        missing_keywords.append(f"{kw} (SERP)")
                        continue
                    
                    # 2. Fetch Volume
                    vol_key = f"volume|{kw}|{location_code}|{language_code}"
                    vol_data = db_manager.check_cache(vol_key)
                    if vol_data and 'tasks' in vol_data and vol_data['tasks'][0].get('result'):
                        # The result for single-keyword volume is a list with one item
                        if vol_data['tasks'][0]['result']:
                            result = vol_data['tasks'][0]['result'][0]
                            keyword_data_map[kw]['volume'] = result.get('search_volume', 0)
                            keyword_data_map[kw]['cpc'] = result.get('cpc', 0)

                    # 3. Get KD from the pre-loaded bulk cache
                    if kd_cache and kd_cache['tasks'][0].get('result'):
                        for item in kd_cache['tasks'][0]['result']:
                            # The 'keyword' key IS present in the bulk KD result items
                            if item.get('keyword') == kw:
                                keyword_data_map[kw]['kd'] = item.get('keyword_difficulty', 0)

            if missing_keywords:
                st.error("Data not found in cache for the following. Please fetch them in the 'Data Fetcher' tab first:")
                st.json(list(set(missing_keywords)))
            else:
                st.success("All keywords have cached SERP data. Running clustering...")
                keyword_serp_data_for_clustering = {kw: data['urls'] for kw, data in keyword_data_map.items() if 'urls' in data}
                
                clusters = perform_serp_clustering(keyword_serp_data_for_clustering, min_intersections, urls_to_check)
                st.info(f"Generated {len(clusters)} clusters.")
                
                output_data = []
                if clusters:
                    for cluster in clusters:
                        if not cluster: continue
                        main_keyword = max(cluster, key=lambda k: keyword_data_map.get(k, {}).get('volume', 0))
                        
                        for keyword in cluster:
                            data = keyword_data_map.get(keyword, {})
                            output_data.append({
                                "Cluster Main Keyword": main_keyword,
                                "Keyword": keyword,
                                "Volume": data.get('volume', 'N/A'),
                                "CPC": data.get('cpc', 'N/A'),
                                "KD": data.get('kd', 'N/A')
                            })
                
                if output_data:
                    df_detailed = pd.DataFrame(output_data)
                    st.session_state.clustered_data = df_detailed
                    st.dataframe(df_detailed)
                    st.success("Clustering complete! View/Export in the 'Data Analysis' tab.")
                else:
                    st.warning("Could not form any clusters based on the current settings.")

# == TAB 4: DATA ANALYSIS ==
with tab4:
    st.header("Analyze and Export Clusters")
    if st.session_state.clustered_data is None:
        st.info("Run clustering in the 'SERP Clustering' tab to see results here.")
    else:
        df_detailed = st.session_state.clustered_data
        
        st.subheader("Detailed Cluster Data")
        # Using st.data_editor makes the dataframe filterable by the user
        filtered_df = st.data_editor(df_detailed, use_container_width=True, num_rows="dynamic")
        
        st.subheader("Cluster Summary")
        if not filtered_df.empty:
            # Ensure numeric columns are treated as such, coercing errors
            numeric_cols = ['Volume', 'CPC', 'KD']
            for col in numeric_cols:
                filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
            
            df_summary = filtered_df.groupby('Cluster Main Keyword').agg(
                Keywords_in_Cluster=('Keyword', lambda x: ', '.join(x)),
                Total_Volume=('Volume', 'sum'),
                Average_CPC=('CPC', 'mean'),
                Average_KD=('KD', 'mean')
            ).reset_index()
            
            # Format the summary table for better readability
            df_summary['Total_Volume'] = df_summary['Total_Volume'].astype(int)
            df_summary['Average_CPC'] = df_summary['Average_CPC'].round(2)
            df_summary['Average_KD'] = df_summary['Average_KD'].round(1)
            
            st.dataframe(df_summary, use_container_width=True)
            st.session_state.summary_data = df_summary

        if st.session_state.get('summary_data') is not None:
            st.download_button(
               label="📥 Export to Excel",
               data=df_to_excel(filtered_df, st.session_state.summary_data),
               file_name=f"seo_clusters_{time.strftime('%Y%m%d')}.xlsx",
               mime="application/vnd.ms-excel"
            )

