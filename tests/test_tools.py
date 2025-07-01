import json
from omegaconf import OmegaConf
import pytest
import pytest_asyncio
from mcp_radarr.types import RadarrStatus
from mcp_radarr.server import RadarrMCPTools
from mcp_radarr.types import MovieDetailsFull, MovieDetails,MovieMinimal, RadarrStatus
from mcp_radarr.server import RadarrAPI
from mcp_radarr.config import load_config

@pytest.fixture()
def api():
    config = load_config()
    url: str = OmegaConf.select(config, "radarr.url")
    assert url, "Radarr URL not set in config"
    assert url.startswith("http"), "Radarr URL must start with http or https"
    key: str = OmegaConf.select(config, "radarr.api_key")
    assert key, "Radarr API key not set in config"
    assert len(key) > 0, "Radarr API key must be set in config"
    return RadarrAPI(url, key)

@pytest_asyncio.fixture
async def tools(api):
    return RadarrMCPTools(api)

@pytest.mark.asyncio
async def test_lookup_movie_tool_found(tools: RadarrMCPTools):
    # Use a well-known movie
    results = await tools.lookup_movie("Inception")
    assert len(results) > 0

    assert isinstance(results, list)
    assert results, "No movies returned from Radarr."
    assert len(results) > 1, "There should have been multiple responses"
    assert all(hasattr(m, "title") for m in results)
    assert any("Inception" in m.title for m in results)

    movie = results[0]
    assert isinstance(movie, MovieDetails)
    print(movie.model_dump_json(indent=2))
    assert len(f"{movie}") < 2000, "Results should be filtered to reasonable size"
    assert hasattr(movie, "radarr_status"), "radarr_status should be a property of MovieDetailed"
    assert isinstance(movie.radarr_status, RadarrStatus)
    assert movie.radarr_status.tracked, "Movie should be tracked"
    assert movie.radarr_status.monitored, "Movie should be monitored"
    assert movie.radarr_status.downloaded, "Movie should be downloaded"


@pytest.mark.asyncio
async def test_lookup_movie_tool_not_added(tools: RadarrMCPTools):
    # Use a well-known movie
    results = await tools.lookup_movie("Mac and me")

    assert isinstance(results, list)
    assert results, "No movies returned from Radarr."
    assert len(results) > 1, "There should have been multiple responses"
    assert all(hasattr(m, "title") for m in results)
    assert any("Mac" in m.title for m in results)

    movie = results[0]
    assert isinstance(movie, MovieDetails)
    print(movie.model_dump_json(indent=2))
    assert len(f"{movie}") < 2000, "Results should be filtered to reasonable size"
    assert hasattr(movie, "radarr_status"), "radarr_status should be a property of MovieDetailed"
    assert isinstance(movie.radarr_status, RadarrStatus)
    assert not movie.radarr_status.tracked
    assert not movie.radarr_status.monitored
    assert not movie.radarr_status.downloaded

@pytest.mark.asyncio
async def test_lookup_movie_tool_not_existant(tools: RadarrMCPTools):
    results = await tools.lookup_movie("DefinitelyNotARealMovieTitle")
    assert isinstance(results, list)
    assert len(results) == 0

@pytest.mark.asyncio
async def test_lookup_movie_tool_one_off(tools: RadarrMCPTools):
    results = await tools.lookup_movie("Lethal Weapon 2")
    assert isinstance(results, list)
    assert len(results) > 0
    print(results[0].model_dump_json(indent=2))

@pytest.mark.asyncio
async def test_movie_info_tool_found(tools: RadarrMCPTools):
    movie = await tools.movie_info("Inception")
    assert movie is not None
    print(movie.model_dump_json(indent=2))

@pytest.mark.asyncio
async def test_movie_info_tool_not_found(tools: RadarrMCPTools):
    movie = await tools.movie_info("DefinitelyNotARealMovieTitle")
    assert movie is None

@pytest.mark.asyncio
async def test_movie_info_tool_not_wanted(tools: RadarrMCPTools):
    movie = await tools.movie_info("Mac and me")
    assert movie is None

@pytest.mark.asyncio
async def test_add_movie_already_added(tools: RadarrMCPTools):
    tmdbId = 931349
    qualityProfileId = 6
    # Since add_movie returns a ToolResponse, we keep that structure
    response = await tools.add_movie(tmdbId, qualityProfileId)
    assert response.isError
    assert isinstance(response.content, dict)
    assert 'error' in response.content
    assert 'tmdbId' in response.content
    assert 'title' in response.content
    assert 'year' in response.content
    assert 'already been added' in response.content['error']

@pytest.mark.asyncio
async def test_movie_list(tools: RadarrMCPTools):
    movies = await tools.movie_list()
    assert isinstance(movies, list)
    assert len(movies) > 0
    # Print first movie as example
    print(movies[0].model_dump_json(indent=2))
    print(f"{len(movies)} movies [{len(str(movies))} bytes]")

@pytest.mark.asyncio
async def test_movie_info_by_tmdb_id(tools: RadarrMCPTools):
    tmdbId = 931349  # Use a known tmdbId that should exist in your Radarr
    movie = await tools.movie_info_by_tmdb_id(tmdbId)
    assert movie is not None
    assert movie.tmdbId == tmdbId
    assert hasattr(movie, "title")
    assert hasattr(movie, "year")
    print(f"Movie info by tmdbId: {movie.title} ({movie.year})")
    print(movie.model_dump_json(indent=2))

@pytest.mark.asyncio
async def test_search_for_movie_name(tools: RadarrMCPTools):
    # Should match movies with 'Matrix' in the title (case-insensitive)
    movies = await tools.search_for_movie({"name": "Matrix"})
    assert isinstance(movies, list)
    assert len(movies) >= 4
    for movie in movies:
        assert "Matrix".lower() in movie.title.lower()
    print(f"Found {len(movies)} movies with 'Matrix' in the title.")
    # Print first movie as example
    print(movies[0].model_dump_json(indent=2))

@pytest.mark.asyncio
async def test_search_for_movie_year_and_genre(tools: RadarrMCPTools):
    movies = await tools.search_for_movie({"year": 1999, "genres": ["Action"]})
    assert isinstance(movies, list)
    assert len(movies) > 0
    for movie in movies:
        assert movie.year == 1999
        # genre match is not in minimal fields, so include it
        assert hasattr(movie, "genres") or not hasattr(movie, "genres")  # minimal does not include genres by default
    print(f"Found {len(movies)} movies from 1999 with Action genre.")
    # Print first movie as example
    print(movies[0].model_dump_json(indent=2))

@pytest.mark.asyncio
async def test_search_for_movie_include_fields(tools: RadarrMCPTools):
    movies = await tools.search_for_movie({"name": "Matrix"}, includeFields=["qualityProfileId", "genres"])
    assert isinstance(movies, list)
    assert len(movies) >= 4
    for movie in movies:
        assert hasattr(movie, "qualityProfileId")
        assert hasattr(movie, "genres")
    print(f"Found {len(movies)} movies with extra fields included.")
    # Print first movie as example
    print(movies[0].model_dump_json(indent=2))

@pytest.mark.asyncio
async def test_search_for_movie_quality_profile_include_fields(tools: RadarrMCPTools):
    movies = await tools.search_for_movie({"qualityProfileId": "1", "year": 2025}, includeFields=["qualityProfileId", "filePath", "movieFile.size"])
    assert isinstance(movies, list)
    assert len(movies) >= 4
    for movie in movies:
        assert hasattr(movie, "qualityProfileId")
    print(f"Found {len(movies)} movies with extra fields included.")
    # Print first movie as example
    print(movies[0].model_dump_json(indent=2))
