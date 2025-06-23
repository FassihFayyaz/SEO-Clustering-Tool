# modules/dataforseo_client.py

import requests
import json
import time
import base64

class DataForSeoClient:
    """
    A client class to manage all API communications with the DataForSEO service.
    It handles authentication, request posting, and basic error handling.
    """

    def __init__(self, login, password, api_base_url):
        """
        Initializes the client with user credentials and the API base URL.
        It prepares the authentication header exactly as specified.
        """
        self.api_base_url = api_base_url
        self.login = login
        self.password = password
        
        # Manually prepare the Basic Authentication header to exactly match the working script.
        cred = base64.b64encode(f"{login}:{password}".encode()).decode()
        self.headers = {
            'Authorization': f'Basic {cred}',
            'Content-Type': 'application/json'
        }

    def _post_request(self, url, payload):
        """
        A private helper method for sending POST requests to the API.
        """
        try:
            response = requests.post(
                url,
                headers=self.headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred during API request to {url}: {e}")
            return None
        except json.JSONDecodeError:
            print(f"Failed to decode JSON response from {url}")
            return None
    
    def _get_request(self, url):
        """
        A private helper method for sending GET requests, used for retrieving task results.
        """
        try:
            response = requests.get(
                url,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred during API GET request to {url}: {e}")
            return None

    def post_serp_tasks(self, keyword, location_code, language_code, device):
        """Posts a SERP task for a single keyword."""
        url = f"{self.api_base_url}/v3/serp/google/organic/task_post"
        post_data = [{
            "location_code": location_code,
            "language_code": language_code,
            "keyword": keyword,
            "device": device,
            "depth": 100
        }]
        return self._post_request(url, post_data)

    def post_bulk_serp_tasks(self, keywords, location_code, language_code, device):
        """
        Posts SERP tasks for multiple keywords in a single bulk request.

        Args:
            keywords (list): List of keywords to process
            location_code (int): Location code for the search
            language_code (str): Language code for the search
            device (str): Device type ('desktop' or 'mobile')

        Returns:
            dict: API response containing task IDs for all posted keywords
        """
        url = f"{self.api_base_url}/v3/serp/google/organic/task_post"
        post_data = []

        for keyword in keywords:
            post_data.append({
                "location_code": location_code,
                "language_code": language_code,
                "keyword": keyword,
                "device": device,
                "depth": 100
            })

        return self._post_request(url, post_data)

    def post_search_volume_tasks(self, keyword, location_code, language_code):
        """Posts a search volume task for a single keyword."""
        url = f"{self.api_base_url}/v3/keywords_data/google_ads/search_volume/task_post"
        post_data = [{
            "keywords": [keyword],
            "location_code": location_code,
            "language_code": language_code,
        }]
        return self._post_request(url, post_data)

    def post_bulk_search_volume_tasks(self, keywords, location_code, language_code):
        """
        Posts search volume tasks for multiple keywords in a single bulk request.

        Args:
            keywords (list): List of keywords to process
            location_code (int): Location code for the search
            language_code (str): Language code for the search

        Returns:
            dict: API response containing task IDs for all posted keywords
        """
        url = f"{self.api_base_url}/v3/keywords_data/google_ads/search_volume/task_post"
        post_data = [{
            "keywords": keywords,
            "location_code": location_code,
            "language_code": language_code,
        }]
        return self._post_request(url, post_data)

    def fetch_keyword_difficulty(self, keyword, location_code, language_code):
        """Fetches Keyword Difficulty for a single keyword."""
        # Note: This still uses the 'bulk' endpoint name, but we only send one keyword.
        url = f"{self.api_base_url}/v3/dataforseo_labs/google/bulk_keyword_difficulty/live"
        payload = [{
            "keywords": [keyword],
            "location_code": location_code,
            "language_code": language_code
        }]
        return self._post_request(url, payload)

    def fetch_search_intent(self, keyword, location_code, language_code):
        """Fetches Search Intent for a single keyword."""
        url = f"{self.api_base_url}/v3/dataforseo_labs/google/search_intent/live"
        payload = [{
            "keywords": [keyword],
            "location_code": location_code,
            "language_code": language_code
        }]
        return self._post_request(url, payload)
    
    def get_task_results(self, url):
        """Retrieves the results of a previously posted asynchronous task."""
        return self._get_request(url)
