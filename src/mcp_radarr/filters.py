from typing import Any, List, Dict, Optional

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

def filter_movie(movie: Dict[str, Any]) -> Dict[str, Any]:
    keys = [
        "id", "title", "originalTitle", "year", "status", "overview", "inCinemas", "studio", "runtime", "genres",
        "imdbId", "tmdbId", "certification", "hasFile", "path", "monitored", 'qualityProfileId',
        # Ratings (wildcard)
        "ratings.*.value", "ratings.*.votes",
        # Images
        "images.coverType", "images.remoteUrl",
        # movieFile details
        "movieFile.size", "movieFile.quality.name", "movieFile.languages", 
        "movieFile.mediaInfo.audioChannels", "movieFile.mediaInfo.audioCodec",
        "movieFile.mediaInfo.videoDynamicRange", "movieFile.mediaInfo.subtitles",
        # Popularity for sorting
        "popularity"
    ]
    filtered_movie = filter_keys(movie, keys)
    filtered_movie["radarr_status"] = radarr_status(movie)
    return filtered_movie

def filter_movie_minimal(movie: Dict[str, Any], includeFields: Optional[List[str]] = None) -> Dict[str, Any]:
    keys = ["id", "title", "year", "tmdbId"]
    if includeFields:
        keys = list(dict.fromkeys(keys + list(includeFields)))  # merge and deduplicate
    return filter_keys(movie, keys)

def radarr_status(movie: dict) -> dict:
    status = {
        'tracked': 'id' in movie,
        'monitored': movie.get('monitored', False),
        'downloaded': 'movieFile' in movie
    }
    return status