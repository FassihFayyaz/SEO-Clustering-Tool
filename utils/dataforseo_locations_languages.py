# utils/dataforseo_locations_languages.py
import requests
import json
import os
from typing import Dict, List, Optional
import streamlit as st

# Cache file paths
CACHE_DIR = "cache"
LANGUAGES_CACHE_FILE = os.path.join(CACHE_DIR, "google_languages.json")
LOCATIONS_CACHE_FILE = os.path.join(CACHE_DIR, "google_locations.json")

def ensure_cache_dir():
    """Ensure cache directory exists"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def fetch_google_languages() -> List[Dict]:
    """Fetch Google languages from DataForSEO API or cache"""
    ensure_cache_dir()
    
    # Try to load from cache first
    if os.path.exists(LANGUAGES_CACHE_FILE):
        try:
            with open(LANGUAGES_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # If no cache or cache failed, use static data
    languages = [
        {"language_name": "English", "language_code": "en"},
        {"language_name": "Spanish", "language_code": "es"},
        {"language_name": "French", "language_code": "fr"},
        {"language_name": "German", "language_code": "de"},
        {"language_name": "Italian", "language_code": "it"},
        {"language_name": "Portuguese", "language_code": "pt"},
        {"language_name": "Russian", "language_code": "ru"},
        {"language_name": "Chinese", "language_code": "zh"},
        {"language_name": "Japanese", "language_code": "ja"},
        {"language_name": "Korean", "language_code": "ko"},
        {"language_name": "Arabic", "language_code": "ar"},
        {"language_name": "Hindi", "language_code": "hi"},
        {"language_name": "Dutch", "language_code": "nl"},
        {"language_name": "Swedish", "language_code": "sv"},
        {"language_name": "Norwegian", "language_code": "no"},
        {"language_name": "Danish", "language_code": "da"},
        {"language_name": "Finnish", "language_code": "fi"},
        {"language_name": "Polish", "language_code": "pl"},
        {"language_name": "Turkish", "language_code": "tr"},
        {"language_name": "Greek", "language_code": "el"},
        {"language_name": "Hebrew", "language_code": "he"},
        {"language_name": "Thai", "language_code": "th"},
        {"language_name": "Vietnamese", "language_code": "vi"},
        {"language_name": "Indonesian", "language_code": "id"},
        {"language_name": "Malay", "language_code": "ms"},
        {"language_name": "Filipino", "language_code": "fil"},
        {"language_name": "Ukrainian", "language_code": "uk"},
        {"language_name": "Czech", "language_code": "cs"},
        {"language_name": "Hungarian", "language_code": "hu"},
        {"language_name": "Romanian", "language_code": "ro"},
        {"language_name": "Bulgarian", "language_code": "bg"},
        {"language_name": "Croatian", "language_code": "hr"},
        {"language_name": "Slovak", "language_code": "sk"},
        {"language_name": "Slovenian", "language_code": "sl"},
        {"language_name": "Estonian", "language_code": "et"},
        {"language_name": "Latvian", "language_code": "lv"},
        {"language_name": "Lithuanian", "language_code": "lt"},
        {"language_name": "Catalan", "language_code": "ca"},
        {"language_name": "Basque", "language_code": "eu"},
        {"language_name": "Galician", "language_code": "gl"},
        {"language_name": "Icelandic", "language_code": "is"},
        {"language_name": "Irish", "language_code": "ga"},
        {"language_name": "Welsh", "language_code": "cy"}
    ]
    
    # Save to cache
    try:
        with open(LANGUAGES_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(languages, f, ensure_ascii=False, indent=2)
    except:
        pass
    
    return languages

def fetch_google_locations() -> List[Dict]:
    """Fetch Google locations from DataForSEO API or cache"""
    ensure_cache_dir()
    
    # Try to load from cache first
    if os.path.exists(LOCATIONS_CACHE_FILE):
        try:
            with open(LOCATIONS_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # If no cache or cache failed, use static data for major locations
    locations = [
        {"location_code": 2840, "location_name": "United States", "country_iso_code": "US", "location_type": "Country"},
        {"location_code": 2826, "location_name": "United Kingdom", "country_iso_code": "GB", "location_type": "Country"},
        {"location_code": 2124, "location_name": "Canada", "country_iso_code": "CA", "location_type": "Country"},
        {"location_code": 2036, "location_name": "Australia", "country_iso_code": "AU", "location_type": "Country"},
        {"location_code": 2276, "location_name": "Germany", "country_iso_code": "DE", "location_type": "Country"},
        {"location_code": 2250, "location_name": "France", "country_iso_code": "FR", "location_type": "Country"},
        {"location_code": 2724, "location_name": "Spain", "country_iso_code": "ES", "location_type": "Country"},
        {"location_code": 2380, "location_name": "Italy", "country_iso_code": "IT", "location_type": "Country"},
        {"location_code": 2528, "location_name": "Netherlands", "country_iso_code": "NL", "location_type": "Country"},
        {"location_code": 2056, "location_name": "Belgium", "country_iso_code": "BE", "location_type": "Country"},
        {"location_code": 2756, "location_name": "Switzerland", "country_iso_code": "CH", "location_type": "Country"},
        {"location_code": 2040, "location_name": "Austria", "country_iso_code": "AT", "location_type": "Country"},
        {"location_code": 2752, "location_name": "Sweden", "country_iso_code": "SE", "location_type": "Country"},
        {"location_code": 2578, "location_name": "Norway", "country_iso_code": "NO", "location_type": "Country"},
        {"location_code": 2208, "location_name": "Denmark", "country_iso_code": "DK", "location_type": "Country"},
        {"location_code": 2246, "location_name": "Finland", "country_iso_code": "FI", "location_type": "Country"},
        {"location_code": 2616, "location_name": "Poland", "country_iso_code": "PL", "location_type": "Country"},
        {"location_code": 2203, "location_name": "Czech Republic", "country_iso_code": "CZ", "location_type": "Country"},
        {"location_code": 2348, "location_name": "Hungary", "country_iso_code": "HU", "location_type": "Country"},
        {"location_code": 2642, "location_name": "Romania", "country_iso_code": "RO", "location_type": "Country"},
        {"location_code": 2076, "location_name": "Brazil", "country_iso_code": "BR", "location_type": "Country"},
        {"location_code": 2484, "location_name": "Mexico", "country_iso_code": "MX", "location_type": "Country"},
        {"location_code": 2032, "location_name": "Argentina", "country_iso_code": "AR", "location_type": "Country"},
        {"location_code": 2152, "location_name": "Chile", "country_iso_code": "CL", "location_type": "Country"},
        {"location_code": 2170, "location_name": "Colombia", "country_iso_code": "CO", "location_type": "Country"},
        {"location_code": 2356, "location_name": "India", "country_iso_code": "IN", "location_type": "Country"},
        {"location_code": 2156, "location_name": "China", "country_iso_code": "CN", "location_type": "Country"},
        {"location_code": 2392, "location_name": "Japan", "country_iso_code": "JP", "location_type": "Country"},
        {"location_code": 2410, "location_name": "South Korea", "country_iso_code": "KR", "location_type": "Country"},
        {"location_code": 2702, "location_name": "Singapore", "country_iso_code": "SG", "location_type": "Country"},
        {"location_code": 2458, "location_name": "Malaysia", "country_iso_code": "MY", "location_type": "Country"},
        {"location_code": 2764, "location_name": "Thailand", "country_iso_code": "TH", "location_type": "Country"},
        {"location_code": 2360, "location_name": "Indonesia", "country_iso_code": "ID", "location_type": "Country"},
        {"location_code": 2608, "location_name": "Philippines", "country_iso_code": "PH", "location_type": "Country"},
        {"location_code": 2704, "location_name": "Vietnam", "country_iso_code": "VN", "location_type": "Country"},
        {"location_code": 2784, "location_name": "United Arab Emirates", "country_iso_code": "AE", "location_type": "Country"},
        {"location_code": 2682, "location_name": "Saudi Arabia", "country_iso_code": "SA", "location_type": "Country"},
        {"location_code": 2376, "location_name": "Israel", "country_iso_code": "IL", "location_type": "Country"},
        {"location_code": 2792, "location_name": "Turkey", "country_iso_code": "TR", "location_type": "Country"},
        {"location_code": 2710, "location_name": "South Africa", "country_iso_code": "ZA", "location_type": "Country"},
        {"location_code": 2818, "location_name": "Egypt", "country_iso_code": "EG", "location_type": "Country"},
        {"location_code": 2504, "location_name": "Morocco", "country_iso_code": "MA", "location_type": "Country"},
        {"location_code": 2012, "location_name": "Algeria", "country_iso_code": "DZ", "location_type": "Country"},
        {"location_code": 2788, "location_name": "Tunisia", "country_iso_code": "TN", "location_type": "Country"}
    ]
    
    # Save to cache
    try:
        with open(LOCATIONS_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(locations, f, ensure_ascii=False, indent=2)
    except:
        pass
    
    return locations

def get_language_options() -> Dict[str, str]:
    """Get language options as {display_name: code} dict"""
    languages = fetch_google_languages()
    return {lang["language_name"]: lang["language_code"] for lang in languages}

def get_location_options() -> Dict[str, int]:
    """Get location options as {display_name: code} dict"""
    locations = fetch_google_locations()
    return {loc["location_name"]: loc["location_code"] for loc in locations}

def get_popular_locations() -> Dict[str, int]:
    """Get popular locations for quick selection"""
    return {
        "United States": 2840,
        "United Kingdom": 2826,
        "Canada": 2124,
        "Australia": 2036,
        "Germany": 2276,
        "France": 2250,
        "Spain": 2724,
        "Italy": 2380,
        "Netherlands": 2528,
        "India": 2356,
        "Japan": 2392,
        "Brazil": 2076
    }

def get_popular_languages() -> Dict[str, str]:
    """Get popular languages for quick selection"""
    return {
        "English": "en",
        "Spanish": "es",
        "French": "fr",
        "German": "de",
        "Italian": "it",
        "Portuguese": "pt",
        "Chinese": "zh",
        "Japanese": "ja",
        "Arabic": "ar",
        "Hindi": "hi",
        "Dutch": "nl",
        "Russian": "ru"
    }
