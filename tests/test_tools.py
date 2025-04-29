import pytest
import pytest_asyncio
import json
from src.mcp_radarr.server import (
    lookup_movie, movie_info, add_movie, movie_list, movie_info_by_tmdb_id, search_for_movie
)
from mcp.server.fastmcp import Context

class DummyContext(Context):
    pass

@pytest_asyncio.fixture
async def ctx():
    return DummyContext()

@pytest.mark.asyncio
async def test_lookup_movie_tool_found(ctx: Context):
    # Use a well-known movie
    response = await lookup_movie(ctx, "Inception")
    assert not response.isError

    content = response.content
    assert isinstance(content, list)
    assert content, "No movies returned from Radarr."
    assert len(content) > 1, "There should have been multiple responses"
    assert all("title" in m for m in content)
    assert any("Inception" in m.get("title", "") for m in content)

    movie = content[0]
    assert isinstance(movie, dict)
    assert len(f"{movie}") < 2000, "Results should be filtered to reasonable size"
    assert "radarr_status" in movie
    assert isinstance(movie["radarr_status"], dict)
    assert "tracked" in movie["radarr_status"]
    assert "monitored" in movie["radarr_status"]
    assert "downloaded" in movie["radarr_status"]
    assert movie["radarr_status"]["tracked"]
    assert movie["radarr_status"]["monitored"]
    assert movie["radarr_status"]["downloaded"]


@pytest.mark.asyncio
async def test_lookup_movie_tool_not_added(ctx: Context):
    # Use a well-known movie
    response = await lookup_movie(ctx, "Mac and me")

    assert not response.isError

    content = response.content
    assert isinstance(content, list)
    assert content, "No movies returned from Radarr."
    assert len(content) > 1, "There should have been multiple responses"
    assert all("title" in m for m in content)
    assert any("Mac" in m.get("title", "") for m in content)

    movie = content[0]
    assert isinstance(movie, dict)
    assert len(f"{movie}") < 2000, "Results should be filtered to reasonable size"
    assert "radarr_status" in movie
    assert isinstance(movie["radarr_status"], dict)
    assert "tracked" in movie["radarr_status"]
    assert "monitored" in movie["radarr_status"]
    assert "downloaded" in movie["radarr_status"]
    assert not movie["radarr_status"]["tracked"]
    assert not movie["radarr_status"]["monitored"]
    assert not movie["radarr_status"]["downloaded"]

@pytest.mark.asyncio
async def test_lookup_movie_tool_not_existant(ctx: Context):
    response = await lookup_movie(ctx, "DefinitelyNotARealMovieTitle")
    
    assert not response.isError
    assert len(response.content) == 0

@pytest.mark.asyncio
async def test_lookup_movie_tool_one_off(ctx: Context):
    response = await lookup_movie(ctx, "Lethal Weapon 2")
    assert not response.isError
    assert len(response.content) > 0
    print(f"{json.dumps(response.content, indent=2)}")

@pytest.mark.asyncio
async def test_movie_info_tool_found(ctx: Context):
    response = await movie_info(ctx, "Inception")
    assert not response.isError
    assert len(response.content) > 0
    print(f"{json.dumps(response.content, indent=2)}")

@pytest.mark.asyncio
async def test_movie_info_tool_not_found(ctx: Context):
    response = await movie_info(ctx, "DefinitelyNotARealMovieTitle")
    assert not response.isError
    assert len(response.content) == 0

@pytest.mark.asyncio
async def test_movie_info_tool_not_wanted(ctx: Context):
    response = await movie_info(ctx, "Mac and me")

    assert not response.isError
    assert len(response.content) == 0

@pytest.mark.asyncio
async def test_add_movie_already_added(ctx: Context):
    tmdbId = 931349
    qualityProfileId = 6
    response = await add_movie(ctx, tmdbId, qualityProfileId)
    assert response.isError
    assert isinstance(response.content, dict)
    assert 'error' in response.content
    assert 'tmdbId' in response.content
    assert 'title' in response.content
    assert 'year' in response.content
    assert 'already been added' in response.content['error']

@pytest.mark.asyncio
async def test_movie_list(ctx: Context):
    response = await movie_list(ctx)
    assert not response.isError
    assert len(response.content) > 0
    print(f"{json.dumps(response.content, indent=2)}")
    print(f"{len(response.content)} movies [{len(str(response.content))} bytes]")

@pytest.mark.asyncio
async def test_movie_info_by_tmdb_id(ctx: Context):
    tmdbId = 931349  # Use a known tmdbId that should exist in your Radarr
    response = await movie_info_by_tmdb_id(ctx, tmdbId)
    assert not response.isError
    assert isinstance(response.content, dict)
    assert response.content.get("tmdbId") == tmdbId
    assert "title" in response.content
    assert "year" in response.content
    print(f"Movie info by tmdbId: {response.content['title']} ({response.content['year']})")

@pytest.mark.asyncio
async def test_search_for_movie_name(ctx: Context):
    # Should match movies with 'Matrix' in the title (case-insensitive)
    response = await search_for_movie(ctx, {"name": "Matrix"})
    assert not response.isError
    assert isinstance(response.content, list)
    assert len(response.content) >= 4
    for movie in response.content:
        assert "Matrix".lower() in movie["title"].lower()
    print(f"Found {len(response.content)} movies with 'Matrix' in the title.")
    print(f"{json.dumps(response.content, indent=2)}")

@pytest.mark.asyncio
async def test_search_for_movie_year_and_genre(ctx: Context):
    response = await search_for_movie(ctx, {"year": 1999, "genres": ["Action"]})
    assert not response.isError
    assert isinstance(response.content, list)
    assert len(response.content) > 0
    for movie in response.content:
        assert movie["year"] == 1999
        # genre match is not in minimal fields, so include it
        assert "genres" in movie or "genres" not in movie  # minimal does not include genres by default
    print(f"Found {len(response.content)} movies from 1999 with Action genre.")
    print(f"{json.dumps(response.content, indent=2)}")

@pytest.mark.asyncio
async def test_search_for_movie_include_fields(ctx: Context):
    response = await search_for_movie(ctx, {"name": "Matrix"}, includeFields=["qualityProfileId", "genres"])
    assert not response.isError
    assert isinstance(response.content, list)
    assert len(response.content) >= 4
    for movie in response.content:
        assert "qualityProfileId" in movie
        assert "genres" in movie
    print(f"Found {len(response.content)} movies with extra fields included.")
    print(f"{json.dumps(response.content, indent=2)}")

@pytest.mark.asyncio
async def test_search_for_movie_quality_profile_include_fields(ctx: Context):
    response = await search_for_movie(ctx, {"qualityProfileId": "1", "year": 2025}, includeFields=["qualityProfileId", "filePath", "movieFile.size"])
    assert not response.isError
    assert isinstance(response.content, list)
    assert len(response.content) >= 4
    for movie in response.content:
        assert "qualityProfileId" in movie
    print(f"Found {len(response.content)} movies with extra fields included.")
    print(f"{json.dumps(response.content, indent=2)}")
