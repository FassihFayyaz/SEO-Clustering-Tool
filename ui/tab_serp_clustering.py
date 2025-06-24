# ui/tab_serp_clustering.py
import streamlit as st
import pandas as pd

from utils import get_keywords_from_input
from modules.clustering import perform_serp_clustering
from utils.dataforseo_locations_languages import get_popular_locations, get_popular_languages, get_location_options, get_language_options

def render(db_manager, locations_map, languages_map):
    st.header("Cluster Keywords by SERP Overlap")
    st.info("This module clusters keywords based on shared URLs in their search results. It ONLY uses data from the local cache.")
    
    # Location and Language Selection
    st.subheader("🌍 Location & Language Settings")
    col1, col2, col3 = st.columns(3)

    with col1:
        # Get location options
        popular_locations = get_popular_locations()
        all_locations = get_location_options()

        location_mode = st.radio(
            "Location Selection:",
            ["Popular Locations", "All Locations"],
            help="Choose from popular locations or search all available locations"
        )

        if location_mode == "Popular Locations":
            selected_location_name = st.selectbox(
                "Select Location:",
                options=list(popular_locations.keys()),
                index=0
            )
            selected_location_code = popular_locations[selected_location_name]
        else:
            selected_location_name = st.selectbox(
                "Select Location:",
                options=list(all_locations.keys()),
                index=list(all_locations.keys()).index("United States") if "United States" in all_locations else 0
            )
            selected_location_code = all_locations[selected_location_name]

    with col2:
        # Get language options
        popular_languages = get_popular_languages()
        all_languages = get_language_options()

        language_mode = st.radio(
            "Language Selection:",
            ["Popular Languages", "All Languages"],
            help="Choose from popular languages or search all available languages"
        )

        if language_mode == "Popular Languages":
            selected_language_name = st.selectbox(
                "Select Language:",
                options=list(popular_languages.keys()),
                index=0
            )
            selected_language_code = popular_languages[selected_language_name]
        else:
            selected_language_name = st.selectbox(
                "Select Language:",
                options=list(all_languages.keys()),
                index=list(all_languages.keys()).index("English") if "English" in all_languages else 0
            )
            selected_language_code = all_languages[selected_language_name]

    with col3:
        st.write("**Selected Settings:**")
        st.write(f"📍 **Location:** {selected_location_name}")
        st.write(f"🗣️ **Language:** {selected_language_name}")
        st.write(f"📱 **Device:** Desktop")
        st.info("💡 Make sure your cached data was fetched with these same settings!")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Keyword Input")
        cluster_kw_text = st.text_area("Paste keywords to cluster:", height=200, key="cluster_kw")
    with c2:
        st.subheader("Clustering Parameters")
        urls_to_check = st.slider("Number of Top URLs to Check:", min_value=5, max_value=20, value=10)
        min_intersections = st.number_input("Minimum Intersections to Cluster:", min_value=2, max_value=10, value=3)

        st.subheader("Clustering Algorithm")
        algorithm_options = {
            "Balanced Strict (Recommended)": "balanced_strict",
            "Default (Broad Clusters)": "default",
            "Strict (Tight Clusters)": "strict"
        }

        selected_algorithm = st.selectbox(
            "Choose Clustering Algorithm:",
            options=list(algorithm_options.keys()),
            index=0,
            help="""
            • **Balanced Strict**: Progressive thresholds (2-5 kw: 100%, 6-10 kw: 80%, 11+ kw: 60%). Best balance of quality and growth.
            • **Default**: Groups keywords that share URLs with primary keyword. Creates broader topic clusters.
            • **Strict**: All keywords must share URLs with each other. Very tight clusters but may create many single-keyword clusters.
            """
        )

        st.subheader("Cluster Strategy")
        strategy_options = {
            "Search Volume (SEO Focus)": "volume",
            "Cost Per Click (PPC Focus)": "cpc"
        }

        selected_strategy = st.selectbox(
            "Primary Keyword Selection:",
            options=list(strategy_options.keys()),
            index=0,
            help="""
            • **Search Volume**: Uses keyword with highest search volume as cluster primary (best for SEO/content strategy)
            • **Cost Per Click**: Uses keyword with highest CPC as cluster primary (best for PPC/commercial keywords)
            """
        )

    if st.button("🧩 Run SERP Clustering", type="primary"):
        keywords_to_cluster = []
        try:
            keywords_to_cluster = get_keywords_from_input(cluster_kw_text, None)
        except Exception as e:
            st.error(f"An error occurred: {e}") # Should not happen with text input

        if not keywords_to_cluster:
            st.warning("Please provide keywords to cluster.")
        else:
            keyword_data_map = {}
            missing_keywords = []
            
            st.write("Verifying data in local cache...")
            with st.spinner("Checking cache for all required data..."):
                # Use selected location and language
                location_code = selected_location_code
                language_code = selected_language_code
                device = "desktop"
                
                for kw in keywords_to_cluster:
                    keyword_data_map[kw] = {}
                    serp_key = f"serp|{kw}|{location_code}|{language_code}|{device}"
                    serp_data = db_manager.check_cache(serp_key)
                    if serp_data and serp_data.get('tasks') and serp_data['tasks'][0].get('result'):
                        serp_items = serp_data['tasks'][0]['result'][0].get('items', [])
                        keyword_data_map[kw]['urls'] = [item['url'] for item in serp_items if 'url' in item][:urls_to_check]
                    else:
                        missing_keywords.append(f"{kw} (SERP)")
                        continue
                    
                    vol_key = f"volume|{kw}|{location_code}|{language_code}"
                    vol_data = db_manager.check_cache(vol_key)
                    if vol_data and vol_data.get('tasks') and vol_data['tasks'][0].get('result'):
                        if vol_data['tasks'][0]['result']:
                            result = vol_data['tasks'][0]['result'][0]
                            keyword_data_map[kw]['volume'] = result.get('search_volume')
                            keyword_data_map[kw]['cpc'] = result.get('cpc')
                    
                    kd_key = f"kd|{kw}|{location_code}|{language_code}"
                    kd_data = db_manager.check_cache(kd_key)
                    if kd_data and kd_data.get('tasks') and kd_data['tasks'][0].get('result'):
                        result_items = kd_data['tasks'][0]['result'][0].get('items', [])
                        if result_items:
                            keyword_data_map[kw]['kd'] = result_items[0].get('keyword_difficulty')
                    
                    intent_key = f"intent|{kw}|{location_code}|{language_code}"
                    intent_data = db_manager.check_cache(intent_key)
                    if intent_data and intent_data.get('tasks') and intent_data['tasks'][0].get('result'):
                        result_items = intent_data['tasks'][0]['result'][0].get('items', [])
                        if result_items:
                             first_result_item = result_items[0]
                             if first_result_item.get('keyword_intent'):
                                 keyword_data_map[kw]['intent'] = first_result_item['keyword_intent'].get('label')

            if missing_keywords:
                st.error("Data not found in cache for the following. Please fetch them in the 'Data Fetcher' tab first:")
                st.json(list(set(missing_keywords)))
            else:
                st.success("All keywords have cached data. Running clustering...")
                keyword_serp_data_for_clustering = {kw: data['urls'] for kw, data in keyword_data_map.items() if 'urls' in data}

                # Get the selected algorithm and strategy
                algorithm = algorithm_options[selected_algorithm]
                strategy = strategy_options[selected_strategy]

                # Prepare keyword metrics for the clustering algorithms
                keyword_metrics = {}
                for kw, data in keyword_data_map.items():
                    keyword_metrics[kw] = {
                        'volume': data.get('volume', 0) or 0,
                        'cpc': data.get('cpc', 0) or 0,
                        'kd': data.get('kd', 101) or 101
                    }

                clusters = perform_serp_clustering(
                    keyword_serp_data_for_clustering,
                    min_intersections,
                    urls_to_check,
                    algorithm=algorithm,
                    cluster_strategy=strategy,
                    keyword_metrics=keyword_metrics
                )

                # Display clustering results info
                st.info(f"Generated {len(clusters)} clusters using **{selected_algorithm}** algorithm with **{selected_strategy}** strategy.")

                # Show algorithm-specific insights
                if algorithm == "strict":
                    single_kw_clusters = sum(1 for cluster in clusters if len(cluster) == 1)
                    if single_kw_clusters > len(clusters) * 0.5:
                        st.warning(f"⚠️ Strict algorithm created {single_kw_clusters} single-keyword clusters. Consider using 'Balanced Strict' or lowering minimum intersections.")
                elif algorithm == "default":
                    avg_cluster_size = sum(len(cluster) for cluster in clusters) / len(clusters) if clusters else 0
                    st.info(f"📊 Average cluster size: {avg_cluster_size:.1f} keywords. Default algorithm creates broader topic groups.")
                elif algorithm == "balanced_strict":
                    large_clusters = sum(1 for cluster in clusters if len(cluster) >= 6)
                    st.info(f"🎯 Balanced Strict created {large_clusters} clusters with 6+ keywords, using progressive thresholds for natural growth.")
                
                output_data = []
                if clusters:
                    for cluster in clusters:
                        if not cluster: continue

                        # Select main keyword based on chosen strategy
                        if strategy == "cpc":
                            main_keyword = sorted(
                                cluster,
                                key=lambda k: (
                                    keyword_data_map.get(k, {}).get('cpc', 0) or 0,
                                    keyword_data_map.get(k, {}).get('volume', 0) or 0  # Secondary sort by volume
                                ),
                                reverse=True
                            )[0]
                        else:  # volume strategy (default)
                            main_keyword = sorted(
                                cluster,
                                key=lambda k: (
                                    keyword_data_map.get(k, {}).get('volume', 0) or 0,
                                    -1 * (keyword_data_map.get(k, {}).get('kd', 101) or 101)  # Secondary sort by lower KD
                                ),
                                reverse=True
                            )[0]
                        main_keyword_urls = set(keyword_data_map.get(main_keyword, {}).get('urls', []))

                        for keyword in cluster:
                            data = keyword_data_map.get(keyword, {})
                            current_keyword_urls = set(data.get('urls', []))
                            intersections = len(main_keyword_urls.intersection(current_keyword_urls))

                            output_data.append({
                                "Cluster Main Keyword": main_keyword,
                                "Keyword": keyword,
                                "Intersections": intersections,
                                "Volume": data.get('volume', 0),
                                "CPC": data.get('cpc', 0),
                                "KD": data.get('kd', 101),
                                "Search Intent": data.get('intent', 'N/A')
                            })
                
                if output_data:
                    df_detailed = pd.DataFrame(output_data)
                    cols_order = ["Cluster Main Keyword", "Keyword", "Intersections", "Volume", "CPC", "KD", "Search Intent"]
                    df_detailed = df_detailed[cols_order]
                    st.dataframe(df_detailed, use_container_width=True)
                    st.session_state.clustered_data_for_analysis = df_detailed 
                    st.success("Clustering complete! View and analyze the results in the 'Data Analysis' tab.")
                else:
                    st.warning("Could not form any clusters based on the current settings.")

