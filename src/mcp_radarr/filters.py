from typing import Any, List, Dict, Optional, Union
from pydantic import BaseModel, Field, ConfigDict

from .types import RadarrError, MovieDetailsFull, MovieMinimal, RadarrStatus, MovieFileFull, MovieFileMediaInfoFull, MovieFileQuality, RatingFull, Image

def filter_keys(data: Any, keys: List[str]) -> Any:
    """
    Filter a dict (or list of dicts) to only include the specified keys.
    For nested keys, use dot notation (e.g., 'images.coverType').
    Supports '*' as a wildcard for all keys at a level (e.g., 'ratings.*.value').
    If a key points to a dict, the entire dict is included unless subkeys are specified via dot notation.
    """
    if isinstance(data, list):
        return [filter_keys(item, keys) for item in data if isinstance(item, dict)]
    result = {}
    top_level = set()
    nested = {}
    for k in keys:
        if '.' in k:
            first, rest = k.split('.', 1)
            nested.setdefault(first, []).append(rest)
        else:
            top_level.add(k)
    for k in top_level:
        if k == '*':
            for all_key in data:
                result[all_key] = data[all_key]
        elif k in data:
            result[k] = data[k]
    for k, subkeys in nested.items():
        if k == '*':
            for all_key in data:
                if isinstance(data[all_key], dict):
                    result[all_key] = filter_keys(data[all_key], subkeys)
                elif isinstance(data[all_key], list):
                    result[all_key] = [filter_keys(item, subkeys) for item in data[all_key] if isinstance(item, dict)]
        elif k in data:
            if isinstance(data[k], dict):
                result[k] = filter_keys(data[k], subkeys)
            elif isinstance(data[k], list):
                result[k] = [filter_keys(item, subkeys) for item in data[k] if isinstance(item, dict)]
    return result

def filter_movie(movie: Dict[str, Any], api: "RadarrAPI") -> MovieDetailsFull:
    keys = [
        "id", "title", "originalTitle", "year", "status", "overview", "inCinemas", "studio", "runtime", "genres",
        "imdbId", "tmdbId", "certification", "hasFile", "path", "monitored", 'qualityProfileId',
        # Ratings (wildcard)
        "ratings.*.value", "ratings.*.votes",
        # Images
        "images.coverType", "images.remoteUrl", "images.url",
        # movieFile details
        "movieFile.size", "movieFile.quality.name", "movieFile.languages", 
        "movieFile.mediaInfo.audioChannels", "movieFile.mediaInfo.audioCodec",
        "movieFile.mediaInfo.videoDynamicRange", "movieFile.mediaInfo.subtitles",
        # Popularity for sorting
        "popularity"
    ]
    filtered_movie = filter_keys(movie, keys)

    convert_urls_to_absolute(filtered_movie, ["images.*.url"], api)

    filtered_movie["radarr_status"] = radarr_status(movie)
    try:
        return MovieDetailsFull.model_validate(filtered_movie)
    except Exception as e:
        # pretty print PydanticType
        import json
        print(json.dumps(movie, indent=2))
        raise RadarrError(e.errors(), 500)

def filter_movie_minimal(movie: Dict[str, Any], includeFields: Optional[List[str]] = None) -> MovieMinimal:
    keys = ["id", "title", "year", "tmdbId"]
    if includeFields:
        keys = list(dict.fromkeys(keys + list(includeFields)))  # merge and deduplicate
    filtered = filter_keys(movie, keys)
    return MovieMinimal.model_validate(filtered)

def radarr_status(movie: dict) -> RadarrStatus:
    status = {
        'tracked': 'id' in movie,
        'monitored': movie.get('monitored', False),
        'downloaded': 'movieFile' in movie
    }
    return RadarrStatus.model_validate(status)

def convert_urls_to_absolute(data: dict, keys: list[str], api: "RadarrAPI"):
    """Convert relative URLs to absolute URLs by prefixing with the Radarr base URL.
    
    Args:
        data: Dictionary containing nested data
        keys: List of dot-notation key paths to URLs that need conversion
            Supports '*' as a wildcard for all keys at a level (e.g., 'images.*.url')
    
    Returns:
        The modified dictionary with absolute URLs
    """
    
    def convert_url_value(value):
        """Convert a single URL string to absolute form"""
        if not isinstance(value, str) or not value:
            return value
            
        if value.startswith('/'):
            return f"{api.get_url()}{value}"
        else:
            return f"{api.get_url()}/{value}"
    
    def process_path(data, path_parts):
        """Process a single path through the data structure"""
        if not data or not path_parts:
            return
            
        # Get the current part and remaining path
        current = path_parts[0]
        remaining = path_parts[1:]
        
        # If we're at the final part in the path (the URL to convert)
        if not remaining:
            if current == '*':
                # Apply to all items at this level
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, str):
                            data[key] = convert_url_value(value)
                elif isinstance(data, list):
                    for i, value in enumerate(data):
                        if isinstance(value, str):
                            data[i] = convert_url_value(value)
            elif isinstance(data, dict) and current in data:
                # Apply to specific key
                data[current] = convert_url_value(data[current])
            return
            
        # Handle intermediate parts
        if current == '*':
            # Process all items at this level
            if isinstance(data, dict):
                for key in data:
                    process_path(data[key], remaining)
            elif isinstance(data, list):
                for item in data:
                    process_path(item, remaining)
        elif isinstance(data, dict) and current in data:
            # Process specific key
            process_path(data[current], remaining)
    
    # Process each key path
    for key in keys:
        parts = key.split('.')
        process_path(data, parts)
    
    return data