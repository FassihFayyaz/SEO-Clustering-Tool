# modules/bulk_data_fetcher.py

import time
from config import SERP_TASK_GET_ADVANCED, SEARCH_VOLUME_TASK_GET

class BulkDataFetcher:
    """
    A class to handle bulk data fetching operations for SERP and search volume data.
    This implementation follows the pattern from the demo code to efficiently process
    multiple keywords in batches.
    """
    
    def __init__(self, client, db_manager):
        """
        Initialize the bulk data fetcher.
        
        Args:
            client: DataForSeoClient instance
            db_manager: DatabaseManager instance for caching
        """
        self.client = client
        self.db_manager = db_manager
    
    def fetch_bulk_serp_data(self, keywords, location_code, language_code, device, 
                           cache_duration_days=None, log_callback=None, progress_callback=None):
        """
        Fetch SERP data for multiple keywords using bulk API calls.
        
        Args:
            keywords (list): List of keywords to process
            location_code (int): Location code for the search
            language_code (str): Language code for the search
            device (str): Device type ('desktop' or 'mobile')
            cache_duration_days (int): Cache duration in days, None for forever
            log_callback (function): Callback function for logging messages
            progress_callback (function): Callback function for progress updates
            
        Returns:
            dict: Results mapping keywords to their data
        """
        if not log_callback:
            log_callback = lambda msg, level="info": print(f"[{level.upper()}] {msg}")
        
        if not progress_callback:
            progress_callback = lambda current, total, msg: print(f"Progress: {current}/{total} - {msg}")
        
        # Check cache first and separate keywords that need fetching
        keywords_to_fetch = []
        cached_results = {}
        
        for kw in keywords:
            cache_key = f"serp|{kw}|{location_code}|{language_code}|{device}"
            cached_data = self.db_manager.check_cache(cache_key, max_age_days=cache_duration_days)
            
            if cached_data is not None:
                cached_results[kw] = cached_data
                log_callback(f"✅ SERP Cache HIT for: '{kw}'", "info")
            else:
                keywords_to_fetch.append(kw)
                log_callback(f"❌ SERP Cache MISS for: '{kw}'. Will fetch...", "warning")
        
        if not keywords_to_fetch:
            log_callback("All keywords found in cache. No API calls needed.", "info")
            return cached_results
        
        # Process keywords in batches of 100 (DataForSEO limit)
        batch_size = 100
        all_results = cached_results.copy()
        
        for i in range(0, len(keywords_to_fetch), batch_size):
            batch_keywords = keywords_to_fetch[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(keywords_to_fetch) + batch_size - 1) // batch_size
            
            log_callback(f"Processing batch {batch_num}/{total_batches} ({len(batch_keywords)} keywords)", "info")
            
            # Post bulk tasks
            post_response = self.client.post_bulk_serp_tasks(
                batch_keywords, location_code, language_code, device
            )
            
            if not (post_response and post_response.get("status_code") == 20000 and post_response.get("tasks")):
                log_callback(f"❌ Failed to post batch {batch_num}. Response: {post_response}", "error")
                continue
            
            # Extract task IDs and create mapping
            posted_tasks = post_response["tasks"]
            task_keyword_map = {}
            pending_task_ids = set()
            
            for j, task in enumerate(posted_tasks):
                if task and 'id' in task and j < len(batch_keywords):
                    task_id = task['id']
                    keyword = batch_keywords[j]
                    task_keyword_map[task_id] = keyword
                    pending_task_ids.add(task_id)
            
            log_callback(f"✅ Posted {len(pending_task_ids)} tasks for batch {batch_num}", "info")
            
            # Poll for results
            batch_results = self._poll_for_serp_results(
                pending_task_ids, task_keyword_map, location_code, language_code, device,
                log_callback, progress_callback, batch_num
            )
            
            all_results.update(batch_results)
        
        return all_results
    
    def _poll_for_serp_results(self, pending_task_ids, task_keyword_map, location_code, 
                              language_code, device, log_callback, progress_callback, batch_num):
        """
        Poll for SERP task results until all are complete or timeout.
        """
        start_time = time.time()
        timeout_seconds = 300  # 5-minute timeout
        batch_results = {}
        
        log_callback(f"Polling for batch {batch_num} results... (checking every 15 seconds)", "info")
        
        while pending_task_ids and time.time() - start_time < timeout_seconds:
            completed_this_cycle = set()
            
            for task_id in pending_task_ids:
                keyword = task_keyword_map[task_id]
                get_url = SERP_TASK_GET_ADVANCED + task_id
                task_result = self.client.get_task_results(get_url)
                
                # Check if task is complete
                if (task_result and
                    task_result.get("tasks") and
                    task_result["tasks"] and
                    task_result["tasks"][0].get("result")):
                    
                    # Cache the result
                    cache_key = f"serp|{keyword}|{location_code}|{language_code}|{device}"
                    self.db_manager.update_cache(cache_key, task_result)
                    batch_results[keyword] = task_result
                    completed_this_cycle.add(task_id)
                    
                    log_callback(f"✅ Completed SERP for '{keyword}'", "info")
            
            # Remove completed tasks
            if completed_this_cycle:
                pending_task_ids.difference_update(completed_this_cycle)
                progress_callback(
                    len(batch_results), 
                    len(task_keyword_map), 
                    f"Batch {batch_num}: {len(batch_results)}/{len(task_keyword_map)} complete"
                )
            
            if pending_task_ids:
                time.sleep(15)
        
        # Handle timeouts
        if pending_task_ids:
            timed_out_keywords = [task_keyword_map[tid] for tid in pending_task_ids]
            log_callback(f"❌ {len(pending_task_ids)} tasks timed out: {timed_out_keywords}", "error")
        
        return batch_results
    
    def fetch_bulk_search_volume_data(self, keywords, location_code, language_code,
                                    cache_duration_days=None, log_callback=None, progress_callback=None):
        """
        Fetch search volume data for multiple keywords using bulk API calls.
        
        Args:
            keywords (list): List of keywords to process
            location_code (int): Location code for the search
            language_code (str): Language code for the search
            cache_duration_days (int): Cache duration in days, None for forever
            log_callback (function): Callback function for logging messages
            progress_callback (function): Callback function for progress updates
            
        Returns:
            dict: Results mapping keywords to their data
        """
        if not log_callback:
            log_callback = lambda msg, level="info": print(f"[{level.upper()}] {msg}")
        
        if not progress_callback:
            progress_callback = lambda current, total, msg: print(f"Progress: {current}/{total} - {msg}")
        
        # Check cache first
        keywords_to_fetch = []
        cached_results = {}
        
        for kw in keywords:
            cache_key = f"volume|{kw}|{location_code}|{language_code}"
            cached_data = self.db_manager.check_cache(cache_key, max_age_days=cache_duration_days)
            
            if cached_data is not None:
                cached_results[kw] = cached_data
                log_callback(f"✅ Volume Cache HIT for: '{kw}'", "info")
            else:
                keywords_to_fetch.append(kw)
                log_callback(f"❌ Volume Cache MISS for: '{kw}'. Will fetch...", "warning")
        
        if not keywords_to_fetch:
            log_callback("All volume data found in cache. No API calls needed.", "info")
            return cached_results
        
        # For search volume, we can send all keywords in a single request
        log_callback(f"Posting search volume task for {len(keywords_to_fetch)} keywords", "info")
        
        post_response = self.client.post_bulk_search_volume_tasks(
            keywords_to_fetch, location_code, language_code
        )
        
        if not (post_response and post_response.get("status_code") == 20000 and post_response.get("tasks")):
            log_callback(f"❌ Failed to post search volume task. Response: {post_response}", "error")
            return cached_results
        
        task_id = post_response["tasks"][0]["id"]
        log_callback(f"✅ Posted search volume task: {task_id}", "info")
        
        # Poll for results
        volume_results = self._poll_for_volume_results(
            task_id, keywords_to_fetch, location_code, language_code,
            log_callback, progress_callback
        )
        
        all_results = cached_results.copy()
        all_results.update(volume_results)
        
        return all_results
    
    def _poll_for_volume_results(self, task_id, keywords, location_code, language_code,
                               log_callback, progress_callback):
        """
        Poll for search volume task results until complete or timeout.
        """
        start_time = time.time()
        timeout_seconds = 180  # 3-minute timeout for volume data
        
        log_callback("Polling for search volume results... (checking every 10 seconds)", "info")
        
        while time.time() - start_time < timeout_seconds:
            get_url = SEARCH_VOLUME_TASK_GET + task_id
            task_result = self.client.get_task_results(get_url)
            
            if (task_result and
                task_result.get("tasks") and
                task_result["tasks"] and
                task_result["tasks"][0].get("result")):
                
                # Process and cache results for each keyword
                results = {}
                result_data = task_result["tasks"][0]["result"]
                
                if result_data:
                    for item in result_data:
                        keyword = item.get("keyword")
                        if keyword in keywords:
                            # Create individual task result for caching
                            individual_result = {
                                "tasks": [{
                                    "result": [item]
                                }]
                            }
                            cache_key = f"volume|{keyword}|{location_code}|{language_code}"
                            self.db_manager.update_cache(cache_key, individual_result)
                            results[keyword] = individual_result
                
                log_callback(f"✅ Completed search volume for {len(results)} keywords", "info")
                progress_callback(len(results), len(keywords), f"Volume data complete")
                
                return results
            
            time.sleep(10)
        
        log_callback("❌ Search volume task timed out", "error")
        return {}
