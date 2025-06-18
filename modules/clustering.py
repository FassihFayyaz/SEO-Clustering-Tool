# modules/clustering.py

import pandas as pd

def perform_serp_clustering(keyword_serp_data: dict, min_intersections: int = 3, urls_to_check: int = 10):
    """
    Performs SERP-based keyword clustering using a two-stage filtering process.

    This algorithm first ensures a baseline similarity (min_intersections) and then
    applies a "Balanced Strict Algorithm" where the required similarity increases
    for smaller, more tightly-themed clusters.

    Args:
        keyword_serp_data (dict): A dictionary where keys are keywords and values are
                                  lists of their top SERP URLs.
                                  e.g., {'kw1': ['url1', 'url2'], 'kw2': ['url2', 'url3']}
        min_intersections (int): The absolute minimum number of shared URLs required
                                 for a keyword to even be considered for a cluster.
        urls_to_check (int): The number of top URLs to consider for intersection.
                             Defaults to 10.

    Returns:
        list: A list of lists, where each inner list represents a cluster of keywords.
    """
    # Create a DataFrame for efficient processing.
    # We slice the URL list for each keyword to the specified `urls_to_check` limit.
    df = pd.DataFrame(list(keyword_serp_data.items()), columns=['keyword', 'urls'])
    df['urls'] = df['urls'].apply(lambda x: x[:urls_to_check] if isinstance(x, list) else [])
    
    # Keep track of which keywords have been assigned to a cluster.
    unclustered_keywords = list(df['keyword'])
    clusters = []

    # Loop as long as there are keywords left to be clustered.
    while unclustered_keywords:
        # Pop the first keyword to act as the seed for a new cluster.
        seed_keyword = unclustered_keywords.pop(0)
        new_cluster = [seed_keyword]
        
        # Get the set of URLs for the seed keyword for fast intersection calculation.
        seed_urls = set(df.loc[df['keyword'] == seed_keyword, 'urls'].iloc[0])

        # Create a copy of the list to iterate over, as we will modify the original list.
        candidates = unclustered_keywords[:]
        
        for candidate_keyword in candidates:
            candidate_urls = set(df.loc[df['keyword'] == candidate_keyword, 'urls'].iloc[0])
            
            # Calculate how many URLs the candidate shares with the seed.
            intersections = len(seed_urls.intersection(candidate_urls))
            
            # --- Two-Stage Filtering ---
            # 1. First, check if the candidate meets the basic minimum intersection requirement.
            if intersections >= min_intersections:
                
                # 2. If it does, then apply the stricter, "Balanced Strict" algorithm.
                potential_size = len(new_cluster) + 1
                if 2 <= potential_size <= 5:
                    # Very strict for small clusters to ensure high relevance.
                    threshold = 8 # Requires 80% similarity
                elif 6 <= potential_size <= 10:
                    # Slightly less strict as the topic is more established.
                    threshold = 6 # Requires 60% similarity
                else:
                    # More lenient for large clusters.
                    threshold = 4 # Requires 40% similarity

                # The candidate is only added if it meets this dynamic, stricter threshold.
                if intersections >= threshold:
                    new_cluster.append(candidate_keyword)
                    unclustered_keywords.remove(candidate_keyword)
        
        # Once all candidates have been checked against the seed, the cluster is complete.
        clusters.append(new_cluster)

    return clusters