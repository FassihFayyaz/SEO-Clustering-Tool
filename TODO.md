# 📋 Project To-Do List

This file tracks the planned features and improvements for the SEO Keyword Clustering Tool.

### High Priority
- [x] **Add Intersection Count Column:** Display the number of overlapping URLs for each keyword in the cluster results table.
- [x] **Improve Cluster Summary UI:** Rework the "Data Analysis" tab to show a summary row above each cluster's detailed keywords, creating a single hierarchical table.

### Medium Priority
- [x] **Optimize API Calls with Bulk Requests:** Refactor the data fetcher to use true bulk `task_post` calls for SERP and Volume APIs to increase speed.
- [x] **Refine Clustering Algorithm:** Implement three clustering algorithms (Default, Strict, Balanced Strict) with different cluster strategies (Volume vs CPC).

### Low Priority / Future Features
- [ ] **Implement User Login:** Add a secure authentication system.
- [ ] **Develop "Local Clustering" (Tab 2):** Implement the functionality for users to apply their own local ML models for clustering.