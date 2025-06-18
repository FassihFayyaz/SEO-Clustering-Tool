# config.py

# This file centralizes the configuration for API endpoints.
# It allows for easy switching between the DataForSEO Sandbox and Live environments.

# Set to True to use the free Sandbox API for development and testing.
# Set to False to use the live API (this will incur costs).
USE_SANDBOX = True

# Determine the base URL based on the sandbox setting
if USE_SANDBOX:
    API_BASE_URL = "https://sandbox.dataforseo.com"
else:
    API_BASE_URL = "https://api.dataforseo.com"

# --- API Endpoint Paths ---

# SERP API (Asynchronous)
# Used for fetching Google organic search results.
# Note the trailing slash on SERP_TASK_GET, which is required for appending the task ID.
SERP_TASK_POST = f"{API_BASE_URL}/v3/serp/google/organic/task_post"
SERP_TASK_GET_ADVANCED = f"{API_BASE_URL}/v3/serp/google/organic/task_get/advanced/"

# Keywords Data API (Asynchronous)
# Used for fetching Google Ads Search Volume and CPC data.
SEARCH_VOLUME_TASK_POST = f"{API_BASE_URL}/v3/keywords_data/google_ads/search_volume/task_post"
SEARCH_VOLUME_TASK_GET = f"{API_BASE_URL}/v3/keywords_data/google_ads/search_volume/task_get/"

# DataForSEO Labs API (Live)
# These endpoints provide data directly without a task queue.

# Used for getting Keyword Difficulty scores for up to 1,000 keywords at once.
BULK_KD_LIVE = f"{API_BASE_URL}/v3/dataforseo_labs/google/bulk_keyword_difficulty/live"

# Used for determining search intent for up to 1,000 keywords at once.
SEARCH_INTENT_LIVE = f"{API_BASE_URL}/v3/dataforseo_labs/google/search_intent/live"
