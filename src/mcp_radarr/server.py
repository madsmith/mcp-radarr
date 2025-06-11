import argparse
import asyncio
import json
from typing import Any, Optional
import os
from pydantic import BaseModel
import aiohttp
from mcp.server.fastmcp import FastMCP, Context
from omegaconf import OmegaConf
from pathlib import Path

from .filters import filter_keys, filter_movie, filter_movie_minimal

class RadarrError(RuntimeError):
    def __init__(self, errors: dict, status: int):
        super().__init__(f"Radarr API error {status}: {errors}")
        self.errors = errors
        self.status = status

# Load configuration at startup
def load_config():
    config_path = os.environ.get("RADARR_CONFIG", str(Path(__file__).parent.parent.parent / "config.yaml"))
    if not Path(config_path).exists():
        raise RuntimeError(f"Config file not found: {config_path}")
    return OmegaConf.load(config_path)

config = load_config()

def get_radarr_url() -> str:
    url = OmegaConf.select(config, "radarr.url")
    if not url:
        raise RuntimeError("Radarr URL not set in config")
    return url.rstrip("/")

def get_radarr_api_key() -> str:
    key = OmegaConf.select(config, "radarr.api_key")
    if not key or key == "changeme":
        raise RuntimeError("Radarr API key not set in config")
    return key

class ToolResponse(BaseModel):
    isError: Optional[bool] = None
    content: Any

mcp = FastMCP(
    "mcp-radarr",
    description="MCP server for Radarr movie management integration"
)

async def radarr_request(endpoint: str, method: str = "GET", params=None, data=None) -> dict:
    url = f"{get_radarr_url()}/api/v3/{endpoint}"
    headers = {"X-Api-Key": get_radarr_api_key(), "Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, headers=headers, params=params, json=data) as resp:
            if resp.status >= 400:
                result = await resp.json()
                raise RadarrError(result, resp.status)
            return await resp.json()

@mcp.tool()
async def lookup_movie(ctx: Context, query: str) -> ToolResponse:
    """
    Lookup movies by name using the Radarr API. Returns list of matching movies with details
    needed to add the movie to the library.
    Args:
        ctx: MCP context
        query: Movie name to search for ("Hackers" or "The Matrix (1999)")
    """
    results = await radarr_request("movie/lookup", params={"term": query})

    filtered = [filter_movie(m) for m in results]

    response = ToolResponse(isError=False, content=filtered)

    return response

@mcp.tool()
async def movie_list(ctx: Context) -> ToolResponse:
    """
    Returns a list of all movies tracked by Radarr.
    Args:
        ctx: MCP context
    """
    movies = await radarr_request("movie")

    filtered = [filter_movie_minimal(m) for m in movies]
    return ToolResponse(isError=False, content=filtered)

@mcp.tool()
async def movie_info(ctx: Context, title: str) -> ToolResponse:
    """Query details about a movie in the wanted list. Returns info if present, or not found message.
    Args:
        ctx: MCP context
        title: Movie title to search for in the wanted list
    """
    movies = await radarr_request("movie")
    for movie in movies:
        if movie.get("title", "").lower() == title.lower():
            keys = [
                "title", "originalTitle", "year", "status", "overview", "inCinemas", "studio", "runtime", "genres",
                "imdbId", "tmdbId", "certification", "hasFile", "path", "monitored", "qualityProfileId",
                # Ratings (wildcard)
                "ratings.*.value", "ratings.*.votes",
                # Images
                "images.coverType", "images.remoteUrl",
                # movieFile details
                "movieFile.size", "movieFile.quality.name", "movieFile.languages", 
                "movieFile.mediaInfo.audioChannels", "movieFile.mediaInfo.audioCodec",
                "movieFile.mediaInfo.videoDynamicRange", "movieFile.mediaInfo.subtitles"
            ]

            filtered = filter_keys(movie, keys)

            return ToolResponse(isError=False, content=filtered)
    
    return ToolResponse(isError=False, content=[])

@mcp.tool()
async def movie_info_by_tmdb_id(ctx: Context, tmdbId: int) -> ToolResponse:
    """
    Returns details about a specific movied identified by tmdbID.
    Args:
        ctx: MCP context
        tmdbId: TMDb ID of the movie
    """
    movies = await radarr_request("movie", params={"tmdbId": tmdbId})
    if not movies:
        return ToolResponse(isError=True, content=f"Movie with tmdbId {tmdbId} not found.")
    return ToolResponse(isError=False, content=filter_movie(movies[0]))

@mcp.tool()
async def get_quality_profiles(ctx: Context) -> ToolResponse:
    """Return Radarr quality profiles.  Returning their id, name, and allowed_qualities."""
    profiles = await radarr_request("qualityprofile")
    filtered = []
    for profile in profiles:
        allowed_qualities = [item["quality"]["name"] for item in profile.get("items", []) if item.get("allowed") and "quality" in item and "name" in item["quality"]]
        filtered.append({
            "id": profile.get("id"),
            "name": profile.get("name"),
            "allowed_qualities": allowed_qualities
        })
    return ToolResponse(isError=False, content=filtered)

@mcp.tool()
async def add_movie(ctx: Context, tmdbId: int, qualityProfileId: int, rootFolderPath: Optional[str] = None) -> str:
    """Add a movie to the Radarr wanted list by TMDb ID. Optionally specify quality profile and root folder.
    Args:
        ctx: MCP context
        tmdbId: The TMDb ID of the movie
        qualityProfileId: (optional) Quality profile to use
        rootFolderPath: (optional) Root folder path for the movie
    """
    try:
        # Get defaults if not provided
        folders = await radarr_request("rootfolder")
        if not rootFolderPath:
            rootFolderPath = folders[0]["path"]
        # Lookup movie info
        movie = await radarr_request("movie/lookup/tmdb", params={"tmdbId": tmdbId})
        if not movie:
            return json.dumps({"isError": True, "content": f"Movie with tmdbId {tmdbId} not found."})
        payload = {
            "tmdbId": tmdbId,
            "title": movie["title"],
            "year": movie["year"],
            "qualityProfileId": qualityProfileId,
            "rootFolderPath": rootFolderPath,
            "minimumAvailability": "released",
            "monitored": True,
            "addOptions": {"searchForMovie": True}
        }
        # Add movie
        result = await radarr_request("movie", method="POST", data=payload)
        return ToolResponse(isError=False, content=payload)
    except RadarrError as e:
        error = e.errors[0]
        payload = {
            'tmdbId': tmdbId,
            'error': error['errorMessage']
        }
        if movie:
            payload['title'] = movie['title']
            payload['year'] = movie['year']
        return ToolResponse(isError=True, content=payload)
    except Exception as e:
        return ToolResponse(isError=True, content=e)

@mcp.tool()
async def edit_movie(ctx: Context, edits: dict) -> ToolResponse:
    """
    Edit movies using Radarr's movie/editor endpoint. Edits dict must include 'movieIds'. Available fields:
    {
        "movieIds": [int], // List of radar ids for the movies being edited (NOT tmdbids)
        "monitored": true|false,
        "qualityProfileId": int,
        "minimumAvailability": "announced"|"released"|"inCinemas",
        "tags": [int], // Tag IDs
        "applyTags": "replace"|"add"|"remove",
    }
    Only movieIds and the fields being changed need to be specified.
    Args:
        ctx: MCP context
        edits: Dictionary of fields to edit. Must include 'movieIds' (list of movie IDs).
    """
    try:
        # Validate only allowed fields are specified
        allowed_fields = ["movieIds", "monitored", "qualityProfileId", "minimumAvailability", "tags", "applyTags"]
        for field in edits:
            if field not in allowed_fields:
                return ToolResponse(isError=True, content=f"Invalid field: {field}")
        # Insure movieids exists and contains valid movies.
        if "movieIds" not in edits:
            return ToolResponse(isError=True, content="Missing required field: movieIds")
        if not isinstance(edits["movieIds"], list):
            return ToolResponse(isError=True, content="movieIds must be a list of movie IDs")
        for movieId in edits["movieIds"]:
            movie = await radarr_request(f"movie/{movieId}")
            if not movie:
                return ToolResponse(isError=True, content=f"Movie with ID {movieId} not found.")

        # Insure tags is a list
        if "tags" in edits and not isinstance(edits["tags"], list):
            return ToolResponse(isError=True, content="tags must be a list of tag IDs")
        for tagId in edits["tags"]:
            tag = await radarr_request(f"tag/{tagId}")
            if not tag:
                return ToolResponse(isError=True, content=f"Tag with ID {tagId} not found.")

        # Insure applyTags is valid
        if "applyTags" in edits and edits["applyTags"] not in ["replace", "add", "remove"]:
            return ToolResponse(isError=True, content="applyTags must be 'replace', 'add', or 'remove'")

        # Insure qualityProfileId is valid
        if "qualityProfileId" in edits:
            profiles = await get_quality_profiles(ctx)
            if not profiles:
                return ToolResponse(isError=True, content="No quality profiles found.")
            profileIds = [p["id"] for p in profiles]
            if edits["qualityProfileId"] not in profileIds:
                return ToolResponse(isError=True, content=f"Invalid quality profile ID: {edits['qualityProfileId']}")
        result = await radarr_request("movie/editor", method="PUT", data=edits)
        return ToolResponse(isError=False, content=result)
    except RadarrError as e:
        return ToolResponse(isError=True, content={"error": str(e), "details": getattr(e, 'errors', None)})
    except Exception as e:
        return ToolResponse(isError=True, content={"error": str(e)})

@mcp.tool()
async def search_for_movie(ctx: Context, criteria: dict, includeFields: list = None) -> ToolResponse:
    """
    Search for movies matching given criteria.
    Supported criteria keys:
      - name: str (partial match, case-insensitive)
      - qualityProfileId: int
      - genres: list of str (any genre matches)
      - certification: str [G, PG, PG-13, R, NC-17, etc.]
      - year: int or dict with gt, lt, eq operators (e.g., {"gt": 2000, "lt": 2010})
      - monitored: bool
      - status: str [announced, released, inCinemas]
      - movieFile.size: {"gt": int, "lt": int} (bytes)
    Optionally, includeFields: list of additional field names to include in results.
    Example:
      {"name": "Matrix", "year": 1999, "genres": ["Action"]}, includeFields=["qualityProfileId", "genres"]
    """
    movies = await radarr_request("movie")
    results = []
    for m in movies:
        match = True
        # Name (partial, case-insensitive)
        if "name" in criteria:
            if criteria["name"].lower() not in m.get("title", "").lower():
                match = False
        # qualityProfileId
        if match and "qualityProfileId" in criteria:
            if int(m.get("qualityProfileId")) != int(criteria["qualityProfileId"]):
                match = False
        # genres (any match)
        if match and "genres" in criteria:
            movie_genres = set([g.lower() for g in m.get("genres", [])])
            search_genres = set([g.lower() for g in criteria["genres"]])
            if not movie_genres.intersection(search_genres):
                match = False
        # certification
        if match and "certification" in criteria:
            if m.get("certification", "").lower() != criteria["certification"].lower():
                match = False
        # year (int or dict with gt, lt, eq)
        if match and "year" in criteria:
            movie_year = m.get("year")
            year_crit = criteria["year"]
            if isinstance(year_crit, dict):
                if "eq" in year_crit and movie_year != year_crit["eq"]:
                    match = False
                if "gt" in year_crit and (movie_year is None or movie_year <= year_crit["gt"]):
                    match = False
                if "lt" in year_crit and (movie_year is None or movie_year >= year_crit["lt"]):
                    match = False
            else:
                if movie_year != year_crit:
                    match = False
        # monitored
        if match and "monitored" in criteria:
            if m.get("monitored") != criteria["monitored"]:
                match = False
        # status
        if match and "status" in criteria:
            if m.get("status", "").lower() != criteria["status"].lower():
                match = False
        # movieFile.size
        if match and "movieFile.size" in criteria:
            size_criteria = criteria["movieFile.size"]
            size = m.get("movieFile", {}).get("size")
            if size is not None:
                if "gt" in size_criteria and size <= size_criteria["gt"]:
                    match = False
                if "lt" in size_criteria and size >= size_criteria["lt"]:
                    match = False
            else:
                match = False
        if match:
            results.append(filter_movie_minimal(m, includeFields=includeFields))
    return ToolResponse(isError=False, content=results)

def main():
    parser = argparse.ArgumentParser(description="MCP server for Radarr integration")
    parser.add_argument("-s", "--server", action="store_true", help="Run in SSE server mode (default: stdio mode)")
    parser.add_argument("-p", "--port", type=int, default=8050, help="Port to run the server on (default: 8050)")
    parser.add_argument("-H", "--host", default="0.0.0.0", help="Host to run the server on (default: 0.0.0.0)")
    args = parser.parse_args()
    async def run():
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        if args.server:
            await mcp.run_sse_async()
        else:
            await mcp.run_stdio_async()
    asyncio.run(run())

if __name__ == "__main__":
    main()
