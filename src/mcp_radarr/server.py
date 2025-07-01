import argparse
import asyncio
import json
from typing import Any, Optional
import omegaconf
from pydantic import BaseModel
import aiohttp
from fastmcp import FastMCP, Context
import importlib.metadata

from .filters import filter_keys, filter_movie, filter_movie_minimal
from .types import RadarrError, MovieDetailsFull, MovieDetails, MovieMinimal, QualityProfile
from .config import load_config

config = load_config()

version = importlib.metadata.version("mcp-radarr")

class ToolResponse(BaseModel):
    isError: Optional[bool] = None
    content: Any

class RadarrAPI:
    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key

    def get_url(self):
        return self.url

    async def request(self, endpoint: str, method: str = "GET", params=None, data=None) -> dict:
        endpoint_uri = f"{self.url}/api/v3/{endpoint}"
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                endpoint_uri,
                headers=headers,
                params=params,
                json=data
            ) as response:
                if response.status >= 400:
                    result = await response.json()
                    raise RadarrError(result, response.status)
                return await response.json()

class RadarrMCPTools:

    def __init__(self, api: RadarrAPI):
        self.api = api

    async def lookup_movie(self, query: str) -> list[MovieDetails]:
        """
        Searches for movies by name or title using the Radarr API.

        This tool helps you find movies in external databases that can be added to Radarr.
        It returns detailed information about matching movies that aren't necessarily in your Radarr library yet.

        Args:
            query (str): The movie name/title to search for. Can include year for better precision
                         (e.g., "Hackers", "The Matrix (1999)")

        Returns:
            list[MovieDetailed]: List of matching movie objects with fields like:
                - title: Movie title
                - year: Release year
                - tmdbId: The Movie Database ID (required for adding movies)
                - overview: Plot summary
                - images: Poster and backdrop URLs
                - radarr_status: Information about movie status in Radarr
                    
        Example use case: When a user wants to add a new movie to their Radarr watchlist
        """
        results = await self.api.request("movie/lookup", params={"term": query})

        return [MovieDetails.fromDetailsFull(filter_movie(m, self.api)) for m in results]

    async def movie_list(self) -> list[MovieMinimal]:
        """
        Retrieves a complete list of all movies currently tracked in your Radarr library.

        This tool provides a comprehensive view of your entire movie collection that is already
        being managed by Radarr, with minimal details to avoid excessive data transfer.

        Args:
            None

        Returns:
            list[MovieMinimal]: List of movie objects with essential fields like:
                - title: Movie title
                - year: Release year
                - tmdbId: The Movie Database ID
                - status: Current status (e.g., "downloaded", "missing")
                    
        Example use case: When a user wants to review their entire library or check if movies are already added
        """
        movies = await self.api.request("movie")

        return [filter_movie_minimal(m) for m in movies]

    async def movie_info(self, title: str) -> Optional[MovieDetailsFull]:
        """
        Retrieves detailed information about a specific movie in your Radarr library by exact title.

        This tool provides comprehensive metadata about a movie that is already in your Radarr library,
        including file information if the movie has been downloaded.

        Args:
            title (str): The exact movie title to search for (case-insensitive, must match completely)

        Returns:
            Optional[MovieDetailed]: If found, a MovieDetailed object with detailed movie information including:
                - title: Movie title
                - year: Release year
                - overview: Plot summary
                - status: Current status in Radarr
                - path: Storage location
                - movieFile: File details if downloaded (size, quality, audio/video specs)
              If not found, returns None
                    
        Example use case: When a user wants detailed information about a specific movie they know is in their library
        """
        movies = await self.api.request("movie")
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
                return MovieDetailsFull.model_validate(filtered)
        
        return None

    async def movie_info_by_tmdb_id(self, tmdbId: int) -> Optional[MovieDetailsFull]:
        """
        Retrieves detailed information about a specific movie in your Radarr library by TMDB ID.

        This tool provides a reliable way to get movie information using The Movie Database ID,
        which is more precise than searching by title as it guarantees an exact match.

        Args:
            tmdbId (int): The TMDb (The Movie Database) ID of the movie
                         (not the same as Radarr's internal ID)

        Returns:
            Optional[MovieDetailed]: If successful, a MovieDetailed object with detailed information
                                   If not found, returns None
                    
        Example use case: When you need precise information about a movie without ambiguity,
        especially after using lookup_movie to find the correct tmdbId
        """
        movies = await self.api.request("movie", params={"tmdbId": tmdbId})
        if not movies:
            return None
        return filter_movie(movies[0], self.api)

    async def get_quality_profiles(self) -> list[QualityProfile]:
        """
        Retrieves all configured quality profiles from Radarr.

        Quality profiles determine what video quality Radarr will search for and download.
        This information is essential when adding new movies to specify desired quality.

        Args:
            None

        Returns:
            list[QualityProfile]: List of quality profile objects with:
                - id: The profile ID (required when adding movies)
                - name: Human-readable profile name (e.g., "HD-1080p", "Ultra-HD")
                - allowed_qualities: List of quality levels included in this profile
                    
        Example use case: Before adding a new movie, to determine available quality options
        and their corresponding IDs
        """
        profiles = await self.api.request("qualityprofile")
        result = []
        for profile in profiles:
            allowed_qualities = [item["quality"]["name"] for item in profile.get("items", []) if item.get("allowed") and "quality" in item and "name" in item["quality"]]
            result.append(QualityProfile(
                id=profile.get("id"),
                name=profile.get("name"),
                allowed_qualities=allowed_qualities
            ))
        return result

    async def add_movie(self, tmdbId: int, qualityProfileId: int, rootFolderPath: Optional[str] = None) -> ToolResponse:
        """
        Adds a new movie to the Radarr wanted list and triggers a search for it.

        This tool lets you add a movie to Radarr's monitoring list so it can be automatically
        downloaded when available. The movie will be searched for immediately after adding.

        Args:
            tmdbId (int): The TMDb (The Movie Database) ID of the movie to add
                         (obtain this from lookup_movie first)
            qualityProfileId (int): The quality profile ID to use for this movie
                                  (obtain available IDs from get_quality_profiles)
            rootFolderPath (str, optional): Storage path for the movie. If not provided,
                                          the default Radarr folder will be used.

        Returns:
            ToolResponse: A response object containing:
                - isError (bool): True if adding failed, False if successful
                - content (dict): Configuration used to add the movie if successful,
                                 or error message if failed
                    
        Note: This method returns a ToolResponse instead of a Pydantic model because
              it needs to handle errors and provide status information about the operation.
                    
        Example use case: After using lookup_movie to find a movie and get_quality_profiles
        to select quality, use this to add the movie to Radarr for downloading
        """
        try:
            # Get defaults if not provided
            folders = await self.api.request("rootfolder")
            if not rootFolderPath:
                rootFolderPath = folders[0]["path"]
            # Lookup movie info
            movie = await self.api.request("movie/lookup/tmdb", params={"tmdbId": tmdbId})
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
            result = await self.api.request("movie", method="POST", data=payload)
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

    async def edit_movie(self, edits: dict) -> ToolResponse:
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
                movie = await self.api.request(f"movie/{movieId}")
                if not movie:
                    return ToolResponse(isError=True, content=f"Movie with ID {movieId} not found.")

            # Insure tags is a list
            if "tags" in edits and not isinstance(edits["tags"], list):
                return ToolResponse(isError=True, content="tags must be a list of tag IDs")
            for tagId in edits["tags"]:
                tag = await self.api.request(f"tag/{tagId}")
                if not tag:
                    return ToolResponse(isError=True, content=f"Tag with ID {tagId} not found.")

            # Insure applyTags is valid
            if "applyTags" in edits and edits["applyTags"] not in ["replace", "add", "remove"]:
                return ToolResponse(isError=True, content="applyTags must be 'replace', 'add', or 'remove'")

            # Insure qualityProfileId is valid
            if "qualityProfileId" in edits:
                profiles = await self.get_quality_profiles()
                if not profiles:
                    return ToolResponse(isError=True, content="No quality profiles found.")
                profileIds = [p["id"] for p in profiles]
                if edits["qualityProfileId"] not in profileIds:
                    return ToolResponse(isError=True, content=f"Invalid quality profile ID: {edits['qualityProfileId']}")
            result = await self.api.request("movie/editor", method="PUT", data=edits)
            return ToolResponse(isError=False, content=result)
        except RadarrError as e:
            return ToolResponse(isError=True, content={"error": str(e), "details": getattr(e, 'errors', None)})
        except Exception as e:
            return ToolResponse(isError=True, content={"error": str(e)})

    async def search_for_movie(self, criteria: dict, includeFields: list = None) -> ToolResponse:
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
        movies = await self.api.request("movie")
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
        return results

    def register_mcp(self, server: FastMCP):
        # Register all functions as tools
        server.tool(self.lookup_movie)
        server.tool(self.movie_list)
        server.tool(self.movie_info)
        server.tool(self.movie_info_by_tmdb_id)
        server.tool(self.get_quality_profiles)
        server.tool(self.add_movie)
        server.tool(self.edit_movie)
        server.tool(self.search_for_movie)

async def run_server(args):
    server = FastMCP(
        "mcp-radarr",
        instructions="""
        Radarr is a movie collection and download manager. Use this tool to manage
        the movie collection and to queue movies for download and addition into the
        movie library.  Radarr works along side with Plex to provide a complete
        movie management solution.
        """,
        version=version
    )

    # Load configuration details
    config = load_config()
    radarr_url = omegaconf.select(config, "radarr.url")
    if not radarr_url:
        raise RuntimeError("Radarr URL not set in config")

    radarr_api_key = omegaconf.select(config, "radarr.api_key")
    if not radarr_api_key or radarr_api_key == "changeme":
        raise RuntimeError("Radarr API key not set in config")
    

    api = RadarrAPI(radarr_url, radarr_api_key)
    tools = RadarrMCPTools(api)

    # Register all tool functions
    tools.register_mcp(server)
    
    transport = args.mode

    if args.mode == 'stdio':
        transport_kwargs = {}
    else:
        assert args.host, "Host is required for non-stdio mode"
        assert args.port, "Port is required for non-stdio mode"

        transport_kwargs = {
            "host": args.host,
            "port": args.port,
        }

    await server.run_async(transport, **transport_kwargs)

def main():
    parser = argparse.ArgumentParser(description="MCP server for Radarr integration")
    parser.add_argument(
        "--mode",
        choices=["stdio", "sse", "http", "streamable-http"],
        default="stdio",
        help="Server transport mode (default: stdio)")
    parser.add_argument("-p", "--port", type=int, default=8050, help="Port to run the server on (default: 8050)")
    parser.add_argument("-H", "--host", default="0.0.0.0", help="Host to run the server on (default: 0.0.0.0)")
    args = parser.parse_args()

    asyncio.run(run_server(args))

if __name__ == "__main__":
    main()
