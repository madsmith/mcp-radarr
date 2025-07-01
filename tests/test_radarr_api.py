import json
from omegaconf import OmegaConf
import pytest
from mcp_radarr.server import RadarrAPI, filter_movie
from mcp_radarr.config import load_config

@pytest.fixture()
def api():
    config = load_config()
    url = OmegaConf.select(config, "radarr.url")
    assert isinstance(url, str)
    assert url, "Radarr URL not set in config"
    assert url.startswith("http"), "Radarr URL must start with http or https"
    key = OmegaConf.select(config, "radarr.api_key")
    assert key, "Radarr API key not set in config"
    assert len(key) > 0, "Radarr API key must be set in config"
    return RadarrAPI(url, key)

@pytest.mark.asyncio
async def test_quality_profiles(api: RadarrAPI):
    profiles = await api.request("qualityprofile")
    print(f"Received {len(profiles)} quality profiles ({len(str(profiles))} bytes)")
    print(json.dumps(profiles, indent=2))
    assert isinstance(profiles, list)
    assert profiles, "No quality profiles returned from Radarr."

@pytest.mark.asyncio
async def test_root_folders(api: RadarrAPI):
    folders = await api.request("rootfolder")
    print(f"Received {len(folders)} root folders ({len(str(folders))} bytes)")
    print(json.dumps(folders, indent=2))
    assert isinstance(folders, list)
    assert folders, "No root folders returned from Radarr."

@pytest.mark.asyncio
async def test_movie_lookup(api: RadarrAPI):
    results = await api.request("movie/lookup", params={"term": "Inception"})
    print(f"Received {len(results)} movies ({len(str(results))} bytes)")
    movies = [filter_movie(m, api) for m in results]
    print(movies[0].model_dump_json(indent=2))
    print(movies[-1].model_dump_json(indent=2))
    assert isinstance(results, list)
    assert any("Inception" in m.get("title", "") for m in results)

@pytest.mark.asyncio
async def test_movie_lookup_year(api: RadarrAPI):
    results = await api.request("movie/lookup", params={"term": "Inception (2010)"})
    print(f"Received {len(results)} movies ({len(str(results))} bytes)")
    movies = [filter_movie(m, api) for m in results]
    print(movies[0].model_dump_json(indent=2))
    print(movies[-1].model_dump_json(indent=2))
    assert isinstance(results, list)
    assert any("Inception" in m.get("title", "") for m in results)

@pytest.mark.asyncio
async def test_movie_list(api: RadarrAPI):
    movies = await api.request("movie")
    print(f"Received {len(movies)} movies ({len(str(movies))} bytes)")

    filtered_movies = filter_movie(movies[0], api)
    print(filtered_movies.model_dump_json(indent=2))

    print(f"Before: {len(str(movies[0]))} bytes")
    print(f"After: {len(str(filtered_movies))} bytes")
    assert isinstance(movies, list)

@pytest.mark.skip(reason="Can only be run once be TMDB ID as test modifies system")
@pytest.mark.asyncio
async def test_add_movie(api: RadarrAPI):
    tmdbId = 931349
    response = await api.request("movie", method="POST", data={"tmdbId": tmdbId})
    print(f"{response}")
    assert not response["isError"]
    print(f"{response['content']}")
    assert len(response["content"]) > 0
    

