# 🔑 SEO Keyword Clustering Tool

A cost-effective desktop application built with Python and Streamlit for advanced SEO keyword analysis and organization. This tool leverages the DataForSEO API and features a robust local caching system to minimize API costs and build a proprietary dataset over time.

## ✨ Key Features

- **Cost-Effective Data Fetching:** Fetches SERP results, Search Volume, CPC, Keyword Difficulty, and Search Intent from the DataForSEO API.
- **Intelligent Local Caching:** A built-in SQLite database caches all API responses. The tool checks the cache before every API call, preventing redundant requests and saving significant costs.
- **Advanced SERP Clustering:** Three clustering algorithms (Default, Strict, Balanced Strict) with two cluster strategies (Search Volume vs CPC) for optimal keyword grouping based on overlapping SERP URLs.
- **Semantic Clustering:** AI-powered clustering using embedding models for unlimited, cost-free keyword clustering based on semantic similarity.
- **Cache Control:** User-configurable cache duration lets you decide when to fetch fresh data vs. use existing local data.
- **Data Analysis & Export:** An interactive workbench to analyze, filter, and summarize cluster data. Final reports can be exported to a multi-sheet Excel file.

### 🧠 Semantic vs SERP Clustering

| Feature | Semantic Clustering | SERP Clustering |
|---------|-------------------|-----------------|
| **Cost** | ✅ Free (no API costs) | 💰 API costs ($0.50+ per keyword) |
| **Speed** | ⚡ Fast (local processing) | 🐌 Slow (API calls + polling) |
| **Keyword Limit** | ✅ Unlimited | ⚠️ Limited by API costs |
| **Accuracy** | 🎯 Semantic similarity | 🎯 SERP overlap |
| **Best For** | Large lists, semantic grouping | Precise SERP targeting |

## 🛠️ Technology Stack

- **Language:** Python 3.9+
- **GUI Framework:** Streamlit
- **Data Manipulation:** Pandas
- **Database:** SQLite
- **API Communication:** Requests

## 🚀 Setup and Installation

Follow these steps to get the application running on your local machine.

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/FassihFayyaz/SEO-Clustering-Tool.git
    cd SEO-Clustering-Tool
    ```

2.  **Create and Activate a Virtual Environment** (Recommended)
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    # Core dependencies
    pip install -r requirements.txt

    # Optional: For Semantic Clustering (AI-powered clustering)
    # Two-step installation process:

    # Step 1: Install PyTorch for your hardware
    # CPU Only:
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

    # NVIDIA GPU (check CUDA version with nvidia-smi):
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

    # AMD GPU (Linux only):
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.6

    # Apple Silicon:
    pip install torch torchvision torchaudio

    # Step 2: Install semantic clustering dependencies
    pip install -r requirements-semantic-cpu.txt
    ```

4.  **Configure API Credentials**
    -   Create a file at `.streamlit/secrets.toml`.
    -   Add your DataForSEO credentials in the following format:
        ```toml
        [dataforseo]
        api_login = "YOUR_DATAFORSEO_EMAIL"
        api_password = "YOUR_DATAFORSEO_PASSWORD"
        ```

5.  **Run the Application**
    ```bash
    streamlit run app.py
    ```
    The application will open in your web browser.

## 🗺️ Roadmap & Future Features

This project is actively being developed. The following features and improvements are planned for future releases. We encourage contributions! Please open an issue to discuss any ideas.

- [x] **Add Intersection Count:** Add a column to the cluster results table showing the number of overlapping URLs between a keyword and its cluster's main keyword.
- [x] **Improve Cluster Summary UI:** Rework the "Data Analysis" tab to display the cluster summary as a header row directly above the detailed keywords for each cluster, creating a more intuitive, hierarchical view.
- [x] **Optimize API Calls:** Implement true bulk requests for asynchronous tasks to significantly speed up the data fetching process for large keyword lists.
- [x] **Enhanced Clustering Algorithms:** Implement three clustering algorithms (Default, Strict, Balanced Strict) with two cluster strategies (Volume vs CPC) for optimal keyword grouping.
- [x] **Semantic Clustering:** Implement AI-powered semantic clustering using embedding models for unlimited, cost-free keyword clustering.
- [x] **Improve Data Analysis Tab** Improve the tab to show more detailed information about each cluster, including keyword counts, average CPC, and more with filters and then make another section below the table that will show cluster cards with there main cluster data like the keyword insights does.
- [ ] **Languages & Locations:** Add more languages and locations to the app that works with the DataForSEO API.
- [ ] **Login System:** Add a secure authentication system to allow multiple users.
- [ ] **Advestise me:** Add my name almost everywhere in the app (professionally) don't just stuff it in. Include some type of donate button. You can ask me for link of the button when you are doing this. 
- [ ] **Make the app fast** Currently it feels like it takes too much time to load so make it faster.
- [ ] Finish the project here with proper documentation, readme, and everything else.

##🤝 Contributing

Contributions are welcome! If you have suggestions for improvements or want to fix a bug, please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

Please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.