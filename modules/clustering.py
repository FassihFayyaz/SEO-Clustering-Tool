# modules/clustering.py

import pandas as pd
from typing import List

class ClusteringAlgorithms:
    """
    Enhanced clustering algorithms for SERP-based keyword clustering.
    Implements Default, Strict, and Balanced Strict algorithms with different cluster strategies.
    """

    @staticmethod
    def default_algorithm(keyword_serp_data: dict, keyword_metrics: dict, min_intersections: int = 3,
                         urls_to_check: int = 10, cluster_strategy: str = "volume") -> List[List[str]]:
        """
        Default Algorithm: Groups keywords if they share X URLs with the primary keyword.
        Creates broader topic clusters. Best for content hubs and category planning.

        Args:
            keyword_serp_data: Dictionary mapping keywords to their SERP URLs
            keyword_metrics: Dictionary mapping keywords to their metrics (volume, cpc, etc.)
            min_intersections: Minimum number of shared URLs required
            urls_to_check: Number of top URLs to consider
            cluster_strategy: "volume" or "cpc" for primary keyword selection

        Returns:
            List of clusters, where each cluster is a list of keywords
        """
        # Sort keywords by the chosen strategy (volume or CPC) to determine primary keywords
        sorted_keywords = ClusteringAlgorithms._sort_keywords_by_strategy(
            list(keyword_serp_data.keys()), keyword_metrics, cluster_strategy
        )

        clusters = []
        unclustered_keywords = set(sorted_keywords)

        while unclustered_keywords:
            # Take the highest-ranking unclustered keyword as the primary keyword
            primary_keyword = next(kw for kw in sorted_keywords if kw in unclustered_keywords)
            cluster = [primary_keyword]
            unclustered_keywords.remove(primary_keyword)

            primary_urls = set(keyword_serp_data[primary_keyword][:urls_to_check])

            # Find all keywords that share enough URLs with the primary keyword
            candidates_to_remove = []
            for candidate in unclustered_keywords:
                candidate_urls = set(keyword_serp_data[candidate][:urls_to_check])
                intersections = len(primary_urls.intersection(candidate_urls))

                if intersections >= min_intersections:
                    cluster.append(candidate)
                    candidates_to_remove.append(candidate)

            # Remove clustered candidates
            for candidate in candidates_to_remove:
                unclustered_keywords.remove(candidate)

            clusters.append(cluster)

        return clusters

    @staticmethod
    def strict_algorithm(keyword_serp_data: dict, keyword_metrics: dict, min_intersections: int = 3,
                        urls_to_check: int = 10, cluster_strategy: str = "volume") -> List[List[str]]:
        """
        Strict Algorithm: Groups keywords only if ALL keywords in the cluster share X URLs with each other.
        Creates very tight, highly relevant clusters. Best for precise content targeting.

        Args:
            keyword_serp_data: Dictionary mapping keywords to their SERP URLs
            keyword_metrics: Dictionary mapping keywords to their metrics (volume, cpc, etc.)
            min_intersections: Minimum number of shared URLs required between ALL pairs
            urls_to_check: Number of top URLs to consider
            cluster_strategy: "volume" or "cpc" for primary keyword selection

        Returns:
            List of clusters, where each cluster is a list of keywords
        """
        sorted_keywords = ClusteringAlgorithms._sort_keywords_by_strategy(
            list(keyword_serp_data.keys()), keyword_metrics, cluster_strategy
        )

        clusters = []
        unclustered_keywords = set(sorted_keywords)

        while unclustered_keywords:
            # Take the highest-ranking unclustered keyword as seed
            seed_keyword = next(kw for kw in sorted_keywords if kw in unclustered_keywords)
            cluster = [seed_keyword]
            unclustered_keywords.remove(seed_keyword)

            # Try to add keywords that share enough URLs with ALL existing cluster members
            candidates_to_remove = []
            for candidate in list(unclustered_keywords):
                can_join_cluster = True
                candidate_urls = set(keyword_serp_data[candidate][:urls_to_check])

                # Check if candidate shares enough URLs with ALL cluster members
                for cluster_member in cluster:
                    member_urls = set(keyword_serp_data[cluster_member][:urls_to_check])
                    intersections = len(candidate_urls.intersection(member_urls))

                    if intersections < min_intersections:
                        can_join_cluster = False
                        break

                if can_join_cluster:
                    cluster.append(candidate)
                    candidates_to_remove.append(candidate)

            # Remove clustered candidates
            for candidate in candidates_to_remove:
                unclustered_keywords.remove(candidate)

            clusters.append(cluster)

        return clusters

    @staticmethod
    def balanced_strict_algorithm(keyword_serp_data: dict, keyword_metrics: dict, min_intersections: int = 3,
                                 urls_to_check: int = 10, cluster_strategy: str = "volume") -> List[List[str]]:
        """
        Balanced Strict Algorithm: Uses progressive thresholds to solve the strict algorithm's limitations.
        - Small clusters (2-5 keywords): requires 100% match (like Strict)
        - Medium clusters (6-10): requires 80% match
        - Large clusters (11+): requires 60% match

        Args:
            keyword_serp_data: Dictionary mapping keywords to their SERP URLs
            keyword_metrics: Dictionary mapping keywords to their metrics (volume, cpc, etc.)
            min_intersections: Base minimum number of shared URLs required
            urls_to_check: Number of top URLs to consider
            cluster_strategy: "volume" or "cpc" for primary keyword selection

        Returns:
            List of clusters, where each cluster is a list of keywords
        """
        sorted_keywords = ClusteringAlgorithms._sort_keywords_by_strategy(
            list(keyword_serp_data.keys()), keyword_metrics, cluster_strategy
        )

        clusters = []
        unclustered_keywords = set(sorted_keywords)

        while unclustered_keywords:
            # Take the highest-ranking unclustered keyword as seed
            seed_keyword = next(kw for kw in sorted_keywords if kw in unclustered_keywords)
            cluster = [seed_keyword]
            unclustered_keywords.remove(seed_keyword)

            # Iteratively try to add keywords with progressive thresholds
            added_keywords = True
            while added_keywords:
                added_keywords = False
                candidates_to_remove = []

                for candidate in list(unclustered_keywords):
                    candidate_urls = set(keyword_serp_data[candidate][:urls_to_check])

                    # Determine the required match percentage based on potential cluster size
                    potential_size = len(cluster) + 1
                    if 2 <= potential_size <= 5:
                        required_match_percentage = 1.0  # 100% match (strict)
                    elif 6 <= potential_size <= 10:
                        required_match_percentage = 0.8  # 80% match
                    else:
                        required_match_percentage = 0.6  # 60% match

                    # Count how many cluster members the candidate shares enough URLs with
                    matching_members = 0
                    for cluster_member in cluster:
                        member_urls = set(keyword_serp_data[cluster_member][:urls_to_check])
                        intersections = len(candidate_urls.intersection(member_urls))

                        if intersections >= min_intersections:
                            matching_members += 1

                    # Check if candidate meets the required match percentage
                    match_percentage = matching_members / len(cluster)
                    if match_percentage >= required_match_percentage:
                        cluster.append(candidate)
                        candidates_to_remove.append(candidate)
                        added_keywords = True

                # Remove clustered candidates
                for candidate in candidates_to_remove:
                    unclustered_keywords.remove(candidate)

            clusters.append(cluster)

        return clusters

    @staticmethod
    def _sort_keywords_by_strategy(keywords: List[str], keyword_metrics: dict, strategy: str) -> List[str]:
        """
        Sort keywords by the chosen cluster strategy (volume or CPC).

        Args:
            keywords: List of keywords to sort
            keyword_metrics: Dictionary mapping keywords to their metrics
            strategy: "volume" or "cpc"

        Returns:
            Sorted list of keywords (highest first)
        """
        def get_sort_key(keyword):
            metrics = keyword_metrics.get(keyword, {})
            if strategy == "cpc":
                return metrics.get('cpc', 0) or 0
            else:  # default to volume
                return metrics.get('volume', 0) or 0

        return sorted(keywords, key=get_sort_key, reverse=True)

def perform_serp_clustering(keyword_serp_data: dict, min_intersections: int = 3, urls_to_check: int = 10,
                           algorithm: str = "balanced_strict", cluster_strategy: str = "volume",
                           keyword_metrics: dict = None):
    """
    Enhanced SERP-based keyword clustering with multiple algorithms and cluster strategies.

    Args:
        keyword_serp_data (dict): Dictionary mapping keywords to their SERP URLs
        min_intersections (int): Minimum number of shared URLs required
        urls_to_check (int): Number of top URLs to consider for intersection
        algorithm (str): Clustering algorithm - "default", "strict", or "balanced_strict"
        cluster_strategy (str): Primary keyword selection strategy - "volume" or "cpc"
        keyword_metrics (dict): Dictionary mapping keywords to their metrics (volume, cpc, etc.)

    Returns:
        list: A list of lists, where each inner list represents a cluster of keywords
    """
    # If no metrics provided, create empty metrics dict for backward compatibility
    if keyword_metrics is None:
        keyword_metrics = {}

    # Choose the appropriate algorithm
    if algorithm == "default":
        return ClusteringAlgorithms.default_algorithm(
            keyword_serp_data, keyword_metrics, min_intersections, urls_to_check, cluster_strategy
        )
    elif algorithm == "strict":
        return ClusteringAlgorithms.strict_algorithm(
            keyword_serp_data, keyword_metrics, min_intersections, urls_to_check, cluster_strategy
        )
    elif algorithm == "balanced_strict":
        return ClusteringAlgorithms.balanced_strict_algorithm(
            keyword_serp_data, keyword_metrics, min_intersections, urls_to_check, cluster_strategy
        )
    else:
        # Fallback to legacy implementation for backward compatibility
        return _legacy_clustering(keyword_serp_data, min_intersections, urls_to_check)

def _legacy_clustering(keyword_serp_data: dict, min_intersections: int = 3, urls_to_check: int = 10):
    """
    Legacy clustering implementation for backward compatibility.
    This is the original "Balanced Strict Algorithm" implementation.
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