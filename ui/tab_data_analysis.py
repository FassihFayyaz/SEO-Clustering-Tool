# ui/tab_data_analysis.py
import streamlit as st
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils import df_to_csv

def render():
    st.header("📊 Cluster Analysis & Insights")

    # Check for both SERP and Semantic clustering data
    has_serp_data = 'clustered_data_for_analysis' in st.session_state and st.session_state.clustered_data_for_analysis is not None
    has_semantic_data = 'semantic_clustered_data' in st.session_state and st.session_state.semantic_clustered_data is not None

    if not has_serp_data and not has_semantic_data:
        st.info("🔍 Run clustering in the 'SERP Clustering' or 'Semantic Clustering' tab to see results here.")
        return

    # Data source selection
    data_source = "SERP"
    if has_serp_data and has_semantic_data:
        data_source = st.selectbox(
            "📋 Select Data Source:",
            ["SERP", "Semantic"],
            help="Choose which clustering results to analyze"
        )
    elif has_semantic_data:
        data_source = "Semantic"

    # Load appropriate data
    if data_source == "SERP" and has_serp_data:
        df_analysis = st.session_state.clustered_data_for_analysis.copy()
        cluster_col = 'Cluster Main Keyword'
        keyword_col = 'Keyword'
    elif data_source == "Semantic" and has_semantic_data:
        df_analysis = st.session_state.semantic_clustered_data.copy()
        cluster_col = 'Parent Keyword'
        keyword_col = 'Child Keyword'
    else:
        st.error("No data available for the selected source.")
        return

    # Process data based on source
    if data_source == "SERP":
        numeric_cols = ['Volume', 'CPC', 'KD', 'Intersections']
        for col in numeric_cols:
            df_analysis[col] = pd.to_numeric(df_analysis[col], errors='coerce')

        # Create summary statistics
        summary_agg = {
            'Keyword_Count': (keyword_col, 'count'),
            'Total_Volume': ('Volume', 'sum'),
            'Average_CPC': ('CPC', 'mean'),
            'Average_KD': ('KD', 'mean'),
            'Average_Intersections': ('Intersections', 'mean'),
            'Primary_Intent': ('Search Intent', lambda x: x.mode()[0] if not x.mode().empty else 'N/A')
        }
        df_summary = df_analysis.groupby(cluster_col).agg(**summary_agg).reset_index()
    else:  # Semantic
        # For semantic clustering, we have different data structure
        df_summary = df_analysis.groupby(cluster_col).agg({
            'Cluster Size': 'first',
            keyword_col: 'count'
        }).reset_index()
        df_summary.rename(columns={keyword_col: 'Keyword_Count'}, inplace=True)

    # Display overview metrics
    render_overview_metrics(df_summary, data_source)

    # Filters section
    st.subheader("🔍 Filters & Controls")
    filtered_data = render_filters(df_analysis, df_summary, cluster_col, data_source)

    # Main data table
    st.subheader("📋 Detailed Cluster Data")
    render_hierarchical_table(filtered_data, cluster_col, keyword_col, data_source)

    # Cluster cards section
    st.subheader("🎯 Cluster Insights")
    render_cluster_cards(filtered_data, cluster_col, keyword_col, data_source)


def render_overview_metrics(df_summary, data_source):
    """Display overview metrics at the top of the analysis"""
    if data_source == "SERP":
        total_clusters = len(df_summary)
        total_keywords = df_summary['Keyword_Count'].sum()
        total_volume = df_summary['Total_Volume'].sum() if 'Total_Volume' in df_summary.columns else 0
        avg_cpc = df_summary['Average_CPC'].mean() if 'Average_CPC' in df_summary.columns else 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🎯 Total Clusters", f"{total_clusters:,}")
        with col2:
            st.metric("🔑 Total Keywords", f"{total_keywords:,}")
        with col3:
            st.metric("📊 Total Volume", f"{int(total_volume):,}")
        with col4:
            st.metric("💰 Avg CPC", f"${avg_cpc:.2f}")
    else:  # Semantic
        total_clusters = len(df_summary)
        total_keywords = df_summary['Keyword_Count'].sum()
        avg_cluster_size = df_summary['Keyword_Count'].mean()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🎯 Total Clusters", f"{total_clusters:,}")
        with col2:
            st.metric("🔑 Total Keywords", f"{total_keywords:,}")
        with col3:
            st.metric("📏 Avg Cluster Size", f"{avg_cluster_size:.1f}")


def render_filters(df_analysis, df_summary, cluster_col, data_source):
    """Render filter controls and return filtered data"""
    col1, col2, col3 = st.columns(3)

    with col1:
        # Cluster selection filter
        cluster_options = ['All'] + sorted(df_summary[cluster_col].tolist())
        selected_clusters = st.multiselect(
            "🎯 Select Clusters:",
            cluster_options,
            default=['All'],
            help="Filter by specific clusters"
        )

    if data_source == "SERP":
        with col2:
            # Volume filter
            if 'Volume' in df_analysis.columns:
                min_vol, max_vol = st.slider(
                    "📊 Volume Range:",
                    min_value=int(df_analysis['Volume'].min()),
                    max_value=int(df_analysis['Volume'].max()),
                    value=(int(df_analysis['Volume'].min()), int(df_analysis['Volume'].max())),
                    help="Filter keywords by search volume"
                )
            else:
                min_vol, max_vol = 0, 999999

        with col3:
            # Search intent filter
            if 'Search Intent' in df_analysis.columns:
                intent_options = ['All'] + sorted(df_analysis['Search Intent'].dropna().unique().tolist())
                selected_intents = st.multiselect(
                    "🎯 Search Intent:",
                    intent_options,
                    default=['All'],
                    help="Filter by search intent"
                )
            else:
                selected_intents = ['All']

    # Apply filters
    filtered_data = df_analysis.copy()

    # Cluster filter
    if 'All' not in selected_clusters:
        filtered_data = filtered_data[filtered_data[cluster_col].isin(selected_clusters)]

    if data_source == "SERP":
        # Volume filter
        if 'Volume' in filtered_data.columns:
            filtered_data = filtered_data[
                (filtered_data['Volume'] >= min_vol) &
                (filtered_data['Volume'] <= max_vol)
            ]

        # Intent filter
        if 'Search Intent' in filtered_data.columns and 'All' not in selected_intents:
            filtered_data = filtered_data[filtered_data['Search Intent'].isin(selected_intents)]

    # Display filter results
    st.info(f"📋 Showing {len(filtered_data):,} keywords from {filtered_data[cluster_col].nunique():,} clusters")

    return filtered_data


def render_hierarchical_table(filtered_data, cluster_col, keyword_col, data_source):
    """Render the main hierarchical data table"""
    if filtered_data.empty:
        st.warning("No data matches the current filters.")
        return

    if data_source == "SERP":
        # Create summary for filtered data
        numeric_cols = ['Volume', 'CPC', 'KD', 'Intersections']
        for col in numeric_cols:
            if col in filtered_data.columns:
                filtered_data[col] = pd.to_numeric(filtered_data[col], errors='coerce')

        summary_agg = {
            'Keyword_Count': (keyword_col, 'count'),
            'Total_Volume': ('Volume', 'sum') if 'Volume' in filtered_data.columns else (keyword_col, 'count'),
            'Average_CPC': ('CPC', 'mean') if 'CPC' in filtered_data.columns else (keyword_col, 'count'),
            'Average_KD': ('KD', 'mean') if 'KD' in filtered_data.columns else (keyword_col, 'count'),
            'Average_Intersections': ('Intersections', 'mean') if 'Intersections' in filtered_data.columns else (keyword_col, 'count'),
            'Primary_Intent': ('Search Intent', lambda x: x.mode()[0] if not x.mode().empty else 'N/A') if 'Search Intent' in filtered_data.columns else (keyword_col, lambda x: 'N/A')
        }
        df_summary = filtered_data.groupby(cluster_col).agg(**summary_agg).reset_index()

        # Create hierarchical table
        hierarchical_rows = []
        main_keywords_list = df_summary[cluster_col].tolist()

        for _, summary_row in df_summary.iterrows():
            main_kw = summary_row[cluster_col]

            # Add summary row
            hierarchical_rows.append({
                "Cluster": main_kw,
                "Keyword": main_kw,
                "Count": f"{summary_row['Keyword_Count']} keywords",
                "Volume": f"{int(summary_row['Total_Volume']):,}" if 'Volume' in filtered_data.columns else "N/A",
                "CPC": f"${summary_row['Average_CPC']:.2f}" if 'CPC' in filtered_data.columns else "N/A",
                "KD": f"{summary_row['Average_KD']:.1f}" if 'KD' in filtered_data.columns else "N/A",
                "Intent": summary_row['Primary_Intent'].capitalize() if 'Search Intent' in filtered_data.columns else "N/A"
            })

            # Add detail rows
            cluster_details = filtered_data[filtered_data[cluster_col] == main_kw]
            for _, detail_row in cluster_details.iterrows():
                hierarchical_rows.append({
                    "Cluster": "",
                    "Keyword": detail_row[keyword_col],
                    "Count": "",
                    "Volume": f"{int(detail_row['Volume']):,}" if 'Volume' in detail_row and pd.notna(detail_row['Volume']) else "N/A",
                    "CPC": f"${detail_row['CPC']:.2f}" if 'CPC' in detail_row and pd.notna(detail_row['CPC']) else "N/A",
                    "KD": f"{detail_row['KD']:.1f}" if 'KD' in detail_row and pd.notna(detail_row['KD']) else "N/A",
                    "Intent": detail_row['Search Intent'].capitalize() if 'Search Intent' in detail_row and pd.notna(detail_row['Search Intent']) else "N/A"
                })

    else:  # Semantic
        # For semantic clustering, simpler structure
        hierarchical_rows = []
        main_keywords_list = filtered_data[cluster_col].unique().tolist()

        for main_kw in main_keywords_list:
            cluster_data = filtered_data[filtered_data[cluster_col] == main_kw]

            # Add summary row
            hierarchical_rows.append({
                "Cluster": main_kw,
                "Keyword": main_kw,
                "Count": f"{len(cluster_data)} keywords",
                "Similarity": "Parent",
                "Type": "Main Cluster"
            })

            # Add detail rows
            for _, detail_row in cluster_data.iterrows():
                hierarchical_rows.append({
                    "Cluster": "",
                    "Keyword": detail_row[keyword_col],
                    "Count": "",
                    "Similarity": f"{detail_row.get('Similarity', 0):.3f}" if 'Similarity' in detail_row else "N/A",
                    "Type": "Child Keyword"
                })

    if hierarchical_rows:
        df_hierarchical = pd.DataFrame(hierarchical_rows)

        # Styling function
        def style_main_keyword(row, main_kws):
            is_main_summary_row = row.Keyword in main_kws and row.Cluster != ""
            style = 'font-weight: bold; font-size: 1.1em; background-color: #262730;'
            return [style if is_main_summary_row else '' for col in row]

        styler = df_hierarchical.style.apply(style_main_keyword, main_kws=main_keywords_list, axis=1)
        st.dataframe(styler, use_container_width=True)

        # Export button
        st.download_button(
            label="📥 Export to CSV",
            data=df_to_csv(df_hierarchical),
            file_name=f"seo_cluster_analysis_{data_source.lower()}_{time.strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data to display.")


def render_cluster_cards(filtered_data, cluster_col, keyword_col, data_source):
    """Render cluster cards similar to keyword insights"""
    if filtered_data.empty:
        return

    # Get unique clusters
    clusters = filtered_data[cluster_col].unique()

    # Pagination for clusters
    clusters_per_page = 6
    total_pages = (len(clusters) + clusters_per_page - 1) // clusters_per_page

    if total_pages > 1:
        page = st.selectbox(
            f"📄 Page (showing {clusters_per_page} clusters per page):",
            range(1, total_pages + 1),
            format_func=lambda x: f"Page {x} of {total_pages}"
        )
        start_idx = (page - 1) * clusters_per_page
        end_idx = start_idx + clusters_per_page
        clusters_to_show = clusters[start_idx:end_idx]
    else:
        clusters_to_show = clusters

    # Display cluster cards in rows of 3
    for i in range(0, len(clusters_to_show), 3):
        cols = st.columns(3)
        for j, cluster in enumerate(clusters_to_show[i:i+3]):
            with cols[j]:
                render_single_cluster_card(filtered_data, cluster, cluster_col, keyword_col, data_source)


def render_single_cluster_card(data, cluster_name, cluster_col, keyword_col, data_source):
    """Render a single cluster card"""
    cluster_data = data[data[cluster_col] == cluster_name]

    if data_source == "SERP":
        # Calculate metrics for SERP data
        keyword_count = len(cluster_data)
        total_volume = cluster_data['Volume'].sum() if 'Volume' in cluster_data.columns else 0
        avg_cpc = cluster_data['CPC'].mean() if 'CPC' in cluster_data.columns else 0
        avg_kd = cluster_data['KD'].mean() if 'KD' in cluster_data.columns else 0
        primary_intent = cluster_data['Search Intent'].mode()[0] if 'Search Intent' in cluster_data.columns and not cluster_data['Search Intent'].mode().empty else 'N/A'

        # Create card
        with st.container():
            st.markdown(f"""
            <div style="
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                background-color: #f8f9fa;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <h4 style="margin-top: 0; color: #2c3e50;">🎯 {cluster_name}</h4>
                <p><strong>📊 Keywords:</strong> {keyword_count:,}</p>
                <p><strong>🔍 Total Volume:</strong> {int(total_volume):,}</p>
                <p><strong>💰 Avg CPC:</strong> ${avg_cpc:.2f}</p>
                <p><strong>📈 Avg KD:</strong> {avg_kd:.1f}</p>
                <p><strong>🎯 Intent:</strong> {primary_intent.capitalize()}</p>
            </div>
            """, unsafe_allow_html=True)

            # Show top keywords
            with st.expander(f"🔍 View Keywords ({keyword_count})"):
                if 'Volume' in cluster_data.columns:
                    top_keywords = cluster_data.nlargest(10, 'Volume')[keyword_col].tolist()
                else:
                    top_keywords = cluster_data[keyword_col].head(10).tolist()

                for kw in top_keywords:
                    st.write(f"• {kw}")

                if len(cluster_data) > 10:
                    st.write(f"... and {len(cluster_data) - 10} more keywords")

    else:  # Semantic
        keyword_count = len(cluster_data)
        avg_similarity = cluster_data['Similarity'].mean() if 'Similarity' in cluster_data.columns else 0

        # Create card
        with st.container():
            st.markdown(f"""
            <div style="
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                background-color: #f0f8ff;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <h4 style="margin-top: 0; color: #2c3e50;">🧠 {cluster_name}</h4>
                <p><strong>📊 Keywords:</strong> {keyword_count:,}</p>
                <p><strong>🎯 Avg Similarity:</strong> {avg_similarity:.3f}</p>
                <p><strong>🔗 Cluster Type:</strong> Semantic</p>
            </div>
            """, unsafe_allow_html=True)

            # Show keywords
            with st.expander(f"🔍 View Keywords ({keyword_count})"):
                keywords_with_sim = []
                for _, row in cluster_data.iterrows():
                    kw = row[keyword_col]
                    sim = row.get('Similarity', 0)
                    keywords_with_sim.append((kw, sim))

                # Sort by similarity
                keywords_with_sim.sort(key=lambda x: x[1], reverse=True)

                for kw, sim in keywords_with_sim[:10]:
                    st.write(f"• {kw} (similarity: {sim:.3f})")

                if len(keywords_with_sim) > 10:
                    st.write(f"... and {len(keywords_with_sim) - 10} more keywords")

