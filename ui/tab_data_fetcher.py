# ui/tab_data_fetcher.py
import streamlit as st
import time

from config import API_BASE_URL
from utils import get_keywords_from_input
from modules.bulk_data_fetcher import BulkDataFetcher

def render(client, db_manager, locations, languages, locations_map, languages_map):
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

    st.subheader("Processing Mode")
    processing_mode = st.radio(
        "Choose processing mode:",
        ["🚀 Bulk Mode (Recommended)", "🐌 Individual Mode (Legacy)"],
        help="Bulk mode processes multiple keywords simultaneously for faster results. Individual mode processes one keyword at a time."
    )
    use_bulk_mode = processing_mode.startswith("🚀")

    if use_bulk_mode:
        st.info("💡 Bulk mode will process up to 100 keywords per batch for SERP data and all keywords at once for other data types.")

    st.subheader("Data to Fetch")
    c1, c2, c3, c4 = st.columns(4)
    fetch_serp = c1.checkbox("SERP Results", value=True)
    fetch_volume = c2.checkbox("Search Volume/CPC", value=True)
    fetch_kd = c3.checkbox("Keyword Difficulty", value=True)
    fetch_intent = c4.checkbox("Search Intent", value=True)

    if st.button("🚀 Start Task", type="primary", key="start_fetch"):
        keywords = []
        try:
            keywords = get_keywords_from_input(kw_text_input, kw_file_input)
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")

        if not keywords:
            st.warning("Please provide at least one keyword.")
        else:
            st.success(f"Found {len(keywords)} unique keywords. Starting process...")
            log_area = st.container()
            progress_bar = st.progress(0)

            location_code = locations_map[selected_location_name]
            language_code = languages_map[selected_language_name]

            if use_bulk_mode:
                # Use bulk processing
                bulk_fetcher = BulkDataFetcher(client, db_manager)

                def log_callback(message, level="info"):
                    if level == "error":
                        log_area.error(message)
                    elif level == "warning":
                        log_area.warning(message)
                    else:
                        log_area.info(message)

                def progress_callback(current, total, message):
                    progress_bar.progress(current / total, text=message)

                # Process each data type in bulk
                if fetch_serp:
                    log_area.info("🚀 Starting bulk SERP data fetch...")
                    serp_results = bulk_fetcher.fetch_bulk_serp_data(
                        keywords, location_code, language_code, selected_device,
                        cache_duration_days, log_callback, progress_callback
                    )
                    log_area.success(f"✅ Completed SERP fetch for {len(serp_results)} keywords")

                if fetch_volume:
                    log_area.info("🚀 Starting bulk search volume data fetch...")
                    volume_results = bulk_fetcher.fetch_bulk_search_volume_data(
                        keywords, location_code, language_code,
                        cache_duration_days, log_callback, progress_callback
                    )
                    log_area.success(f"✅ Completed volume fetch for {len(volume_results)} keywords")

                # KD and Intent still use individual calls as they are live endpoints
                if fetch_kd or fetch_intent:
                    log_area.info("Processing Keyword Difficulty and Search Intent (individual calls)...")
                    for i, kw in enumerate(keywords):
                        progress_text = f"Processing KD/Intent {i+1}/{len(keywords)}: {kw}"
                        progress_bar.progress((i + 1) / len(keywords), text=progress_text)

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

                progress_bar.progress(1.0, text="All bulk processing complete!")

            else:
                # Use individual processing (legacy mode)
                for i, kw in enumerate(keywords):
                    progress_text = f"Processing keyword {i+1}/{len(keywords)}: {kw}"
                    progress_bar.progress((i + 1) / len(keywords), text=progress_text)

                    if fetch_serp:
                        cache_key = f"serp|{kw}|{location_code}|{language_code}|{selected_device}"
                        if db_manager.check_cache(cache_key, max_age_days=cache_duration_days) is None:
                            log_area.warning(f"❌ SERP Cache MISS for: '{kw}'. Posting task...")
                            post_response = client.post_serp_tasks(kw, location_code, language_code, selected_device)
                            if post_response and post_response.get('tasks'):
                                task_id = post_response['tasks'][0]['id']
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


                    if fetch_volume:
                        cache_key = f"volume|{kw}|{location_code}|{language_code}"
                        if db_manager.check_cache(cache_key, max_age_days=cache_duration_days) is None:
                            log_area.warning(f"❌ Volume Cache MISS for: '{kw}'. Posting task...")
                            post_response = client.post_search_volume_tasks(kw, location_code, language_code)
                            if post_response and post_response.get('tasks'):
                                task_id = post_response['tasks'][0]['id']
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

