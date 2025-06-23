# ui/tab_data_analysis.py
import streamlit as st
import pandas as pd
import time

from utils import df_to_csv

def render():
    st.header("Analyze and Export Clusters")
    if 'clustered_data_for_analysis' not in st.session_state or st.session_state.clustered_data_for_analysis is None:
        st.info("Run clustering in the 'SERP Clustering' tab to see results here.")
    else:
        df_analysis = st.session_state.clustered_data_for_analysis.copy()

        numeric_cols = ['Volume', 'CPC', 'KD', 'Intersections']
        for col in numeric_cols:
            df_analysis[col] = pd.to_numeric(df_analysis[col], errors='coerce')

        summary_agg = {
            'Total_Volume': ('Volume', 'sum'),
            'Average_CPC': ('CPC', 'mean'),
            'Average_KD': ('KD', 'mean'),
            'Average_Intersections': ('Intersections', 'mean'),
            'Primary_Intent': ('Search Intent', lambda x: x.mode()[0] if not x.mode().empty else 'N/A')
        }
        df_summary = df_analysis.groupby('Cluster Main Keyword').agg(**summary_agg).reset_index()

        # --- HIERARCHICAL TABLE CREATION ---
        hierarchical_rows = []
        main_keywords_list = df_summary['Cluster Main Keyword'].tolist()
        
        for index, summary_row in df_summary.iterrows():
            main_kw = summary_row['Cluster Main Keyword']
            
            # 1. Add the Summary Row
            hierarchical_rows.append({
                "Cluster": main_kw,
                "Keyword": main_kw,
                "Intersections": f"{summary_row['Average_Intersections']:.1f}",
                "Volume": f"{int(summary_row['Total_Volume']):,}",
                "CPC": f"${summary_row['Average_CPC']:.2f}",
                "KD": f"{summary_row['Average_KD']:.1f}",
                "Search Intent": summary_row['Primary_Intent'].capitalize()
            })

            # 2. Add the Detail Rows
            cluster_details = df_analysis[df_analysis['Cluster Main Keyword'] == main_kw]
            for _, detail_row in cluster_details.iterrows():
                hierarchical_rows.append({
                    "Cluster": "", # Blank for detail rows
                    "Keyword": detail_row['Keyword'],
                    "Intersections": detail_row['Intersections'],
                    "Volume": detail_row['Volume'],
                    "CPC": detail_row['CPC'],
                    "KD": detail_row['KD'],
                    "Search Intent": detail_row['Search Intent']
                })

        if hierarchical_rows:
            df_hierarchical = pd.DataFrame(hierarchical_rows)
            
            # --- Styling Function to make the summary row bold ---
            def style_main_keyword(row, main_kws):
                is_main_summary_row = row.Keyword in main_kws and row.Cluster != ""
                style = 'font-weight: bold; font-size: 1.1em; background-color: #262730;'
                return [style if is_main_summary_row else '' for col in row]

            styler = df_hierarchical.style.apply(style_main_keyword, main_kws=main_keywords_list, axis=1)
            
            st.dataframe(styler, use_container_width=True)
            
            st.download_button(
               label="📥 Export to CSV",
               data=df_to_csv(df_hierarchical),
               file_name=f"seo_cluster_analysis_{time.strftime('%Y%m%d')}.csv",
               mime="text/csv"
            )
        else:
            st.warning("No data to display.")

