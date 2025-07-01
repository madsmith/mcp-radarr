import pytest
from mcp_radarr.filters import convert_urls_to_absolute
from mcp_radarr.server import RadarrAPI


def test_convert_url_to_absolute_basic():
    """Test basic URL conversion in a simple dictionary."""
    # Create a mock RadarrAPI
    api = RadarrAPI("http://radarr.local:7878", "mock-api-key")
    
    # Test data
    data = {
        "poster": "/poster/path",
        "backdrop": "backdrop/path",
        "images": [
            {"url": "/image1.jpg"},
            {"url": "image2.jpg"}
        ],
        "nested": {
            "url": "/nested/path"
        }
    }
    
    # Convert URLs
    result = convert_urls_to_absolute(data, [
        "poster", 
        "backdrop", 
        "images.*.url",  # Use wildcard instead of digit indices 
        "nested.url",
        "nonexistent.path"  # This should be safely ignored
    ], api)
    
    # Check results
    assert result["poster"] == "http://radarr.local:7878/poster/path"
    assert result["backdrop"] == "http://radarr.local:7878/backdrop/path"
    # With wildcard patterns, both image URLs should be updated
    assert result["images"][0]["url"] == "http://radarr.local:7878/image1.jpg"
    assert result["images"][1]["url"] == "http://radarr.local:7878/image2.jpg"
    assert result["nested"]["url"] == "http://radarr.local:7878/nested/path"


def test_convert_url_to_absolute_for_else():
    """Test that the for...else construct works as expected."""
    # Create a mock RadarrAPI
    api = RadarrAPI("http://radarr.local:7878", "mock-api-key")
    
    # Test with invalid path that should break out of the loop
    data = {"level1": {"level2": {"url": "/path"}}}
    
    # Valid path
    result1 = convert_urls_to_absolute(data, ["level1.level2.url"], api)
    assert result1["level1"]["level2"]["url"] == "http://radarr.local:7878/path"
    
    # Invalid path - middle segment doesn't exist
    result2 = convert_urls_to_absolute(data, ["level1.nonexistent.url"], api)
    # Should not modify the data, just safely ignore the invalid path
    assert result2["level1"]["level2"]["url"] == "http://radarr.local:7878/path"
    
    # Invalid path - top segment doesn't exist
    result3 = convert_urls_to_absolute(data, ["nonexistent.level2.url"], api)
    # Should not modify the data, just safely ignore the invalid path
    assert result3["level1"]["level2"]["url"] == "http://radarr.local:7878/path"
