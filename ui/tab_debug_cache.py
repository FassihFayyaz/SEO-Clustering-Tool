# ui/tab_debug_cache.py
import streamlit as st
import time

def render(db_manager):
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

