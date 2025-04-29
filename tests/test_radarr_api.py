import json
import pytest
from src.mcp_radarr.server import radarr_request, get_radarr_url, get_radarr_api_key, filter_movie, RadarrError

@pytest.mark.asyncio
async def test_get_radarr_url_and_api_key():
    url = get_radarr_url()
    key = get_radarr_api_key()
    assert url.startswith("http")
    assert len(key) > 0

@pytest.mark.asyncio
async def test_quality_profiles():
    profiles = await radarr_request("qualityprofile")
    print(f"Received {len(profiles)} quality profiles ({len(str(profiles))} bytes)")
    print(json.dumps(profiles, indent=2))
    assert isinstance(profiles, list)
    assert profiles, "No quality profiles returned from Radarr."

@pytest.mark.asyncio
async def test_root_folders():
    folders = await radarr_request("rootfolder")
    print(f"Received {len(folders)} root folders ({len(str(folders))} bytes)")
    print(json.dumps(folders, indent=2))
    assert isinstance(folders, list)
    assert folders, "No root folders returned from Radarr."

@pytest.mark.asyncio
async def test_movie_lookup():
    results = await radarr_request("movie/lookup", params={"term": "Inception"})
    print(f"Received {len(results)} movies ({len(str(results))} bytes)")
    movies = [filter_movie(m) for m in results]
    print(json.dumps(movies, indent=2))
    print(json.dumps(results[0], indent=2))
    print(json.dumps(results[-1], indent=2))
    assert isinstance(results, list)
    assert any("Inception" in m.get("title", "") for m in results)

@pytest.mark.asyncio
async def test_movie_lookup_year():
    results = await radarr_request("movie/lookup", params={"term": "Inception (2010)"})
    print(f"Received {len(results)} movies ({len(str(results))} bytes)")
    movies = [filter_movie(m) for m in results]
    print(json.dumps(movies, indent=2))
    print(json.dumps(results[0], indent=2))
    print(json.dumps(results[-1], indent=2))
    assert isinstance(results, list)
    assert any("Inception" in m.get("title", "") for m in results)

@pytest.mark.asyncio
async def test_movie_list():
    movies = await radarr_request("movie")
    print(f"Received {len(movies)} movies ({len(str(movies))} bytes)")

    filtered_movies = filter_movie(movies[0])
    print(json.dumps(filtered_movies, indent=2))

    print(f"Before: {len(str(movies[0]))} bytes")
    print(f"After: {len(str(filtered_movies))} bytes")
    assert isinstance(movies, list)

@pytest.mark.asyncio
async def test_add_movie():
    tmdbId = 931349
    response = await radarr_request("movie", method="POST", data={"tmdbId": tmdbId})
    print(f"{response}")
    assert not response["isError"]
    print(f"{response['content']}")
    assert len(response["content"]) > 0
    

