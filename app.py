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
    return list(set(kw.lower() for kw in keywords))

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
        return None, None, None, None, None, None
    
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

if not client or not client.login or not client.password:
    st.error("DataForSEO credentials are not configured. Please add them to your `.streamlit/secrets.toml` file.")
    st.stop()
    
# --- Main Application UI (Tabs) ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Data Fetcher", 
    "🧠 Local Clustering (Placeholder)", 
    "🔗 SERP Clustering", 
    "📈 Data Analysis",
    "🐞 Debug & Cache"
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

    st.subheader("Cache Settings")
    cache_options = {
        "Always Fetch New (0 Days)": 0,
        "Use Cache within 1 Day": 1,
        "Use Cache within 7 Days": 7,
        "Use Cache within 30 Days": 30,
        "Use Cache within 12 Months": 365,
        "Use Existing Forever": None
    }
    selected_cache_option = st.selectbox(
        "Cache Duration:",
        options=list(cache_options.keys()),
        index=5
    )
    cache_duration_days = cache_options[selected_cache_option]

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
            
            location_code = locations_map[selected_location_name]
            language_code = languages_map[selected_language_name]

            for i, kw in enumerate(keywords):
                progress_text = f"Processing keyword {i+1}/{len(keywords)}: {kw}"
                progress_bar.progress((i + 1) / len(keywords), text=progress_text)
                
                # --- Fetch SERP Data (Async) ---
                if fetch_serp:
                    cache_key = f"serp|{kw}|{location_code}|{language_code}|{selected_device}"
                    if db_manager.check_cache(cache_key, max_age_days=cache_duration_days) is None:
                        log_area.warning(f"❌ SERP Cache MISS for: '{kw}'. Posting task...")
                        post_response = client.post_serp_tasks(kw, location_code, language_code, selected_device)
                        if post_response and post_response.get('tasks'):
                            task_id = post_response['tasks'][0]['id']
                            log_area.info(f"   - Task posted. ID: {task_id}. Polling...")
                            get_url = f"{API_BASE_URL}/v3/serp/google/organic/task_get/advanced/{task_id}"
                            for _ in range(30): 
                                time.sleep(10)
                                task_result = client.get_task_results(get_url)
                                if task_result and task_result.get('tasks') and task_result['tasks'][0].get('result'):
                                    db_manager.update_cache(cache_key, task_result)
                                    log_area.success(f"   - ✅ Got and cached SERP for '{kw}'")
                                    break
                            else:
                                log_area.error(f"   - ❌ SERP task timed out for '{kw}'")
                        else:
                            log_area.error(f"   - ❌ Failed to post SERP task for '{kw}'.")
                    else:
                        log_area.info(f"✅ SERP Cache HIT for: '{kw}'")

                # --- Fetch Volume Data (Async) ---
                if fetch_volume:
                    cache_key = f"volume|{kw}|{location_code}|{language_code}"
                    if db_manager.check_cache(cache_key, max_age_days=cache_duration_days) is None:
                        log_area.warning(f"❌ Volume Cache MISS for: '{kw}'. Posting task...")
                        post_response = client.post_search_volume_tasks(kw, location_code, language_code)
                        if post_response and post_response.get('tasks'):
                            task_id = post_response['tasks'][0]['id']
                            log_area.info(f"   - Task posted. ID: {task_id}. Polling...")
                            get_url = f"{API_BASE_URL}/v3/keywords_data/google_ads/search_volume/task_get/{task_id}"
                            for _ in range(10): 
                                time.sleep(5)
                                task_result = client.get_task_results(get_url)
                                if task_result and task_result.get('tasks') and task_result['tasks'][0].get('result'):
                                    db_manager.update_cache(cache_key, task_result)
                                    log_area.success(f"   - ✅ Got and cached Volume for '{kw}'")
                                    break
                            else:
                                log_area.error(f"   - ❌ Volume task timed out for '{kw}'")
                        else:
                             log_area.error(f"   - ❌ Failed to post Volume task for '{kw}'.")
                    else:
                        log_area.info(f"✅ Volume Cache HIT for: '{kw}'")

                # --- Fetch Keyword Difficulty (Live) ---
                if fetch_kd:
                    cache_key = f"kd|{kw}|{location_code}|{language_code}"
                    if db_manager.check_cache(cache_key, max_age_days=cache_duration_days) is None:
                        log_area.warning(f"❌ KD Cache MISS for: '{kw}'. Calling API...")
                        response = client.fetch_keyword_difficulty(kw, location_code, language_code)
                        if response and response.get('status_code') == 20000:
                            db_manager.update_cache(cache_key, response)
                            log_area.success(f"✅ Fetched and cached KD for '{kw}'.")
                        else:
                            log_area.error(f"❌ Failed to fetch KD for '{kw}'. Response: {response}")
                    else:
                        log_area.info(f"✅ KD Cache HIT for: '{kw}'")

                # --- Fetch Search Intent (Live) ---
                if fetch_intent:
                    cache_key = f"intent|{kw}|{location_code}|{language_code}"
                    if db_manager.check_cache(cache_key, max_age_days=cache_duration_days) is None:
                        log_area.warning(f"❌ Intent Cache MISS for: '{kw}'. Calling API...")
                        response = client.fetch_search_intent(kw, location_code, language_code)
                        if response and response.get('status_code') == 20000:
                            db_manager.update_cache(cache_key, response)
                            log_area.success(f"✅ Fetched and cached Intent for '{kw}'.")
                        else:
                             log_area.error(f"❌ Failed to fetch Intent for '{kw}'. Response: {response}")
                    else:
                        log_area.info(f"✅ Intent Cache HIT for: '{kw}'")
            st.success("All tasks complete!")

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
            keyword_data_map = {}
            missing_keywords = []
            
            st.write("Verifying data in local cache...")
            with st.spinner("Checking cache for all required data..."):
                location_code = locations_map["United States"]
                language_code = languages_map["English"]
                device = "desktop"
                
                for kw in keywords_to_cluster:
                    keyword_data_map[kw] = {}
                    
                    # 1. Fetch SERP data
                    serp_key = f"serp|{kw}|{location_code}|{language_code}|{device}"
                    serp_data = db_manager.check_cache(serp_key)
                    if serp_data and serp_data.get('tasks') and serp_data['tasks'][0].get('result'):
                        serp_items = serp_data['tasks'][0]['result'][0].get('items', [])
                        keyword_data_map[kw]['urls'] = [item['url'] for item in serp_items if 'url' in item]
                    else:
                        missing_keywords.append(f"{kw} (SERP)")
                        continue
                    
                    # 2. Fetch Volume data
                    vol_key = f"volume|{kw}|{location_code}|{language_code}"
                    vol_data = db_manager.check_cache(vol_key)
                    if vol_data and vol_data.get('tasks') and vol_data['tasks'][0].get('result'):
                        if vol_data['tasks'][0]['result']:
                            result = vol_data['tasks'][0]['result'][0]
                            keyword_data_map[kw]['volume'] = result.get('search_volume', 'N/A')
                            keyword_data_map[kw]['cpc'] = result.get('cpc', 'N/A')
                    
                    # 3. Fetch KD data
                    kd_key = f"kd|{kw}|{location_code}|{language_code}"
                    kd_data = db_manager.check_cache(kd_key)
                    if kd_data and kd_data.get('tasks') and kd_data['tasks'][0].get('result'):
                        result_items = kd_data['tasks'][0]['result'][0].get('items', [])
                        if result_items:
                            keyword_data_map[kw]['kd'] = result_items[0].get('keyword_difficulty', 'N/A')
                    
                    # 4. Fetch Intent data
                    intent_key = f"intent|{kw}|{location_code}|{language_code}"
                    intent_data = db_manager.check_cache(intent_key)
                    if intent_data and intent_data.get('tasks') and intent_data['tasks'][0].get('result'):
                        result_items = intent_data['tasks'][0]['result'][0].get('items', [])
                        if result_items:
                            intent_values = result_items[0].get('intent_info', {}).get('values', [])
                            primary_intent = max(intent_values, key=lambda x: x['value'], default={})
                            keyword_data_map[kw]['intent'] = primary_intent.get('intent', 'N/A')

            if missing_keywords:
                st.error("Data not found in cache for the following. Please fetch them in the 'Data Fetcher' tab first:")
                st.json(list(set(missing_keywords)))
            else:
                st.success("All keywords have cached data. Running clustering...")
                keyword_serp_data_for_clustering = {kw: data['urls'] for kw, data in keyword_data_map.items() if 'urls' in data}
                
                clusters = perform_serp_clustering(keyword_serp_data_for_clustering, min_intersections, urls_to_check)
                st.info(f"Generated {len(clusters)} clusters.")
                
                output_data = []
                if clusters:
                    for cluster in clusters:
                        if not cluster: continue
                        main_keyword = max(cluster, key=lambda k: keyword_data_map.get(k, {}).get('volume', 0) or 0)
                        
                        for keyword in cluster:
                            data = keyword_data_map.get(keyword, {})
                            output_data.append({
                                "Cluster Main Keyword": main_keyword,
                                "Keyword": keyword,
                                "Volume": data.get('volume', 'N/A'),
                                "CPC": data.get('cpc', 'N/A'),
                                "KD": data.get('kd', 'N/A'),
                                "Search Intent": data.get('intent', 'N/A')
                            })
                
                if output_data:
                    df_detailed = pd.DataFrame(output_data)
                    st.session_state.clustered_data = df_detailed
                    st.dataframe(df_detailed, use_container_width=True)
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
        filtered_df = st.data_editor(df_detailed, use_container_width=True, num_rows="dynamic")
        
        st.subheader("Cluster Summary")
        if not filtered_df.empty:
            numeric_cols = ['Volume', 'CPC', 'KD']
            for col in numeric_cols:
                filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
            
            # --- AGGREGATION LOGIC ---
            # Group by main keyword to calculate stats
            summary_agg = {
                'Keywords_in_Cluster': ('Keyword', lambda x: ', '.join(x)),
                'Total_Volume': ('Volume', 'sum'),
                'Average_CPC': ('CPC', 'mean'),
                'Average_KD': ('KD', 'mean'),
            }
            # Special handling for intent - find the most common one (mode)
            if 'Search Intent' in filtered_df.columns:
                 summary_agg['Primary_Intent'] = ('Search Intent', lambda x: x.mode()[0] if not x.mode().empty else 'N/A')

            df_summary = filtered_df.groupby('Cluster Main Keyword').agg(**summary_agg).reset_index()
            
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

# == TAB 5: DEBUG & CACHE ==
with tab5:
    st.header("Inspect Raw Cache Data")
    st.info("Use this tab to look up the raw JSON data stored in the local SQLite database for a specific cache key.")
    
    st.markdown("""
    **Example Cache Keys:**
    - **SERP:** `serp|keyword|location_code|language_code|device`
    - **Volume:** `volume|keyword|location_code|language_code`
    - **KD:** `kd|keyword|location_code|language_code`
    - **Intent:** `intent|keyword|location_code|language_code`
    """)

    cache_key_input = st.text_input("Enter exact cache key to inspect:")
    
    if st.button("🔍 Check Cache", key="debug_check"):
        if cache_key_input:
            with st.spinner("Searching cache..."):
                cached_data = db_manager.check_cache(cache_key_input)
                if cached_data:
                    st.success("Data found in cache!")
                    st.json(cached_data)
                else:
                    st.warning("No data found for this key.")
        else:
            st.warning("Please enter a cache key.")
            
    st.divider()
    
    st.header("Cache Management")
    st.warning("This action will permanently delete all cached data and cannot be undone.", icon="⚠️")
    
    if st.button("Clear Entire Cache", type="secondary"):
        st.session_state.confirm_delete = True
        
    if st.session_state.confirm_delete:
        st.error("Are you absolutely sure? This will delete all content from the `seo_app_cache.db` file.")
        
        c1, c2 = st.columns(2)
        if c1.button("Yes, I am sure. Delete all data.", type="primary"):
            if db_manager.clear_all_cache():
                st.success("All cached data has been deleted.")
            else:
                st.error("An error occurred while clearing the cache.")
            st.session_state.confirm_delete = False
            time.sleep(2)
            st.rerun()
            
        if c2.button("Cancel"):
            st.session_state.confirm_delete = False
            st.rerun()
