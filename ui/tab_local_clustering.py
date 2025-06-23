# ui/tab_local_clustering.py
import streamlit as st

import time

from utils import get_keywords_from_input
from modules.semantic_clustering import SemanticClusteringEngine

def render():
    st.header("🧠 Semantic Clustering")
    st.info("Cluster keywords using AI embedding models. No API costs, unlimited keywords, runs locally on your machine.")

    # Check dependencies
    engine = SemanticClusteringEngine()
    if not engine.check_dependencies():
        st.error("❌ **Required dependencies not installed**")
        st.markdown("""
        To use semantic clustering, please install the required packages:
        ```bash
        pip install sentence-transformers torch
        ```
        After installation, restart the application.
        """)
        return

    # Main UI layout
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📝 Keyword Input")
        kw_text_input = st.text_area(
            "Paste Keywords (one per line):",
            height=200,
            key="semantic_clustering_input",
            help="Enter your keywords, one per line. You can cluster unlimited keywords!"
        )

        kw_file_input = st.file_uploader(
            "Or Upload CSV file:",
            type=['csv'],
            help="Upload a CSV file with keywords in the first column"
        )

        # Display keyword count
        keywords = []
        try:
            keywords = get_keywords_from_input(kw_text_input, kw_file_input)
            if keywords:
                st.success(f"✅ Found {len(keywords)} keywords ready for clustering")
        except Exception as e:
            if kw_text_input.strip() or kw_file_input:
                st.error(f"Error reading keywords: {e}")

    with col2:
        st.subheader("⚙️ Clustering Configuration")

        # Model selection
        available_models = engine.get_available_models()
        model_options = list(available_models.keys())

        selected_model = st.selectbox(
            "🤖 Select Embedding Model:",
            options=model_options,
            index=3,  # Default to gte-large (balanced option)
            help="""
            **Model Recommendations:**
            - **gte-large / bge-large**: Best for most users (CPU/GPU, 2GB+ VRAM)
            - **sentence-t5-xl**: High quality results (5GB+ VRAM)
            - **Qwen models**: Top performance but require more VRAM
            """
        )

        # Clustering parameters
        st.markdown("**🎯 Clustering Parameters**")

        similarity_threshold = st.slider(
            "Similarity Threshold:",
            min_value=0.1,
            max_value=1.0,
            value=0.95,
            step=0.05,
            help="Higher values create smaller, more specific clusters. Lower values create larger, broader clusters."
        )

        min_cluster_size = st.number_input(
            "Minimum Cluster Size:",
            min_value=2,
            max_value=50,
            value=2,
            help="Minimum number of keywords required to form a cluster"
        )

        # Device info
        device, device_info = engine.detect_device()
        if device == 'cuda':
            st.success(f"🚀 GPU Detected: {device_info}")
        else:
            st.info(f"💻 Using CPU: {device_info}")

    # Clustering button and process
    if st.button("🧠 Start Semantic Clustering", type="primary", disabled=len(keywords) == 0):
        if not keywords:
            st.warning("Please provide keywords to cluster.")
            return

        # Create progress containers
        progress_container = st.container()
        log_container = st.container()

        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()

        with log_container:
            log_area = st.empty()

        # Progress callback function
        def progress_callback(message):
            with log_area:
                st.text(message)

        # Update progress for different stages
        progress_bar.progress(0.1)
        status_text.text("Initializing clustering engine...")

        try:
            # Perform clustering
            progress_bar.progress(0.2)
            status_text.text("Loading embedding model...")

            results_df = engine.cluster_keywords(
                keywords=keywords,
                model_key=selected_model,
                similarity_threshold=similarity_threshold,
                min_cluster_size=min_cluster_size,
                progress_callback=progress_callback
            )

            progress_bar.progress(1.0)
            status_text.text("Clustering complete!")

            if results_df is not None and not results_df.empty:
                # Display results
                st.success(f"🎉 Clustering completed successfully!")

                # Summary statistics
                total_clusters = results_df['Parent Keyword'].nunique()
                total_keywords_clustered = len(results_df)
                avg_cluster_size = results_df.groupby('Parent Keyword').size().mean()

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Clusters", total_clusters)
                with col2:
                    st.metric("Keywords Clustered", total_keywords_clustered)
                with col3:
                    st.metric("Avg Cluster Size", f"{avg_cluster_size:.1f}")

                # Display results table
                st.subheader("📊 Clustering Results")

                # Add cluster size info and reorder columns
                display_df = results_df[['Parent Keyword', 'Child Keyword', 'Cluster Size']].copy()

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    height=400
                )

                # Store results for analysis tab
                st.session_state.semantic_clustered_data = results_df

                # Download option
                csv_data = results_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv_data,
                    file_name=f"semantic_clusters_{int(time.time())}.csv",
                    mime="text/csv"
                )

                st.success("✅ Results saved! You can also view detailed analysis in the 'Data Analysis' tab.")

            else:
                st.warning("⚠️ No clusters were formed with the current settings. Try lowering the similarity threshold or minimum cluster size.")

        except Exception as e:
            progress_bar.progress(0)
            status_text.text("Clustering failed!")
            st.error(f"❌ An error occurred during clustering: {str(e)}")

            # Show troubleshooting tips
            with st.expander("🔧 Troubleshooting Tips"):
                st.markdown("""
                **Common issues and solutions:**

                1. **Out of memory errors:**
                   - Try a smaller model (gte-large or bge-large)
                   - Reduce the number of keywords
                   - Close other applications to free up memory

                2. **Model loading errors:**
                   - Check your internet connection (models download on first use)
                   - Try a different model
                   - Restart the application

                3. **No clusters formed:**
                   - Lower the similarity threshold (try 0.8 or 0.7)
                   - Reduce minimum cluster size to 2
                   - Check if your keywords are related enough to cluster

                4. **Slow performance:**
                   - Use GPU if available
                   - Try the "Fastest" Qwen model for large keyword lists
                   - Consider processing keywords in smaller batches
                """)

    # Information section
    with st.expander("ℹ️ About Semantic Clustering"):
        st.markdown("""
        **What is Semantic Clustering?**

        Semantic clustering groups keywords based on their meaning and context, not just shared SERP URLs.
        It uses AI embedding models to understand the semantic similarity between keywords.

        **Advantages over SERP Clustering:**
        - ✅ **No API costs** - runs completely locally
        - ✅ **Unlimited keywords** - cluster millions of keywords
        - ✅ **Fast processing** - no waiting for API responses
        - ✅ **Semantic understanding** - groups by meaning, not just SERP overlap
        - ✅ **Offline capability** - works without internet after model download

        **When to use Semantic vs SERP Clustering:**
        - **Semantic**: Large keyword lists, cost-sensitive projects, semantic grouping
        - **SERP**: Precise content targeting, SERP-based strategy, smaller keyword lists

        **Model Selection Guide:**
        - **gte-large/bge-large**: Best starting point, works on most hardware
        - **sentence-t5-xl**: Higher quality, needs more VRAM
        - **Qwen models**: Top performance, requires significant VRAM
        """)

    # Hardware requirements info
    with st.expander("💻 Hardware Requirements"):
        st.markdown("""
        **Minimum Requirements:**
        - **CPU**: Any modern processor
        - **RAM**: 4GB+ (8GB+ recommended for large keyword lists)
        - **Storage**: 2-10GB for model files (downloaded once)

        **GPU Requirements (Optional but Recommended):**
        - **gte-large/bge-large**: 2GB+ VRAM
        - **sentence-t5-xl**: 5GB+ VRAM
        - **Qwen-0.6B**: 4GB+ VRAM
        - **Qwen-4B**: 10GB+ VRAM
        - **Qwen-8B**: 20GB+ VRAM

        **Performance Tips:**
        - GPU acceleration provides 5-10x speed improvement
        - Models are downloaded once and cached locally
        - Larger models generally provide better clustering quality
        """)

