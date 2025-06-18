# modules/dataforseo_client.py

import requests
import json
import time

class DataForSeoClient:
    """
    A client class to manage all API communications with the DataForSEO service.
    It handles authentication, request posting, and basic error handling.
    """

    def __init__(self, login, password, api_base_url):
        """
        Initializes the client with user credentials and the API base URL.

        Args:
            login (str): The API login email from DataForSEO.
            password (str): The API password from DataForSEO.
            api_base_url (str): The base URL for the API (sandbox or live).
        """
        self.login = login
        self.password = password
        self.api_base_url = api_base_url
        self.headers = {'Content-Type': 'application/json'}

    def _post_request(self, url, payload):
        """
        A private helper method for sending POST requests to the API.

        Args:
            url (str): The full API endpoint URL.
            payload (list): The data payload to be sent, typically a list of tasks.

        Returns:
            dict: The JSON response from the API, or None if an error occurs.
        """
        try:
            response = requests.post(
                url,
                auth=(self.login, self.password),
                headers=self.headers,
                data=json.dumps(payload)
            )
            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred during API request to {url}: {e}")
            # In a real app, you might want to log this or show a more user-friendly error.
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
                auth=(self.login, self.password),
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred during API GET request to {url}: {e}")
            return None

    def post_serp_tasks(self, keywords, location_name, language_name, device):
        """
        Posts tasks to the SERP API.

        Args:
            keywords (list): A list of keyword strings.
            location_name (str): User-friendly location name (e.g., "United States").
            language_name (str): User-friendly language name (e.g., "English").
            device (str): "desktop" or "mobile".

        Returns:
            dict: The API response from the task_post endpoint.
        """
        url = f"{self.api_base_url}/v3/serp/google/organic/task_post"
        post_data = []
        for kw in keywords:
            task = {
                "location_name": location_name,
                "language_name": language_name,
                "keyword": kw,
                "device": device,
                "depth": 100 # Fetch top 100 results
            }
            post_data.append(task)
        
        return self._post_request(url, post_data)

    def post_search_volume_tasks(self, keywords, location_name, language_name):
        """
        Posts tasks to the search volume API.
        """
        url = f"{self.api_base_url}/v3/keywords_data/google_ads/search_volume/task_post"
        post_data = {
            "keywords": keywords,
            "location_name": location_name,
            "language_name": language_name,
        }
        # Note: This endpoint expects a slightly different payload structure (a single object)
        return self._post_request(url, [post_data])

    def fetch_bulk_keyword_difficulty(self, keywords):
        """
        Fetches Keyword Difficulty for a list of keywords using the live endpoint.
        """
        url = f"{self.api_base_url}/v3/dataforseo_labs/google/bulk_keyword_difficulty/live"
        payload = [{"keywords": keywords}]
        return self._post_request(url, payload)

    def fetch_search_intent(self, keywords):
        """
        Fetches Search Intent for a list of keywords using the live endpoint.
        """
        url = f"{self.api_base_url}/v3/dataforseo_labs/google/search_intent/live"
        payload = [{"keywords": keywords}]
        return self._post_request(url, payload)
    
    def get_task_results(self, url):
        """
        Retrieves the results of a previously posted asynchronous task.
        """
        return self._get_request(url)

