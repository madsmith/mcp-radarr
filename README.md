# MCP Radarr

A Python MCP server interface for the Radarr movie management tool. Provides tools to look up movies, query movie info, and add movies to the wanted list using the Radarr API.

## Features

- MCP interface for Radarr
- Lookup movies by name
- Query movie info in the wanted list
- Add movies to the Radarr wanted list

## Setup

Install the package:
```bash
uv pip install -e .
```

## Running the Server

The server can be run in either stdio mode (default) or SSE server mode:

```bash
# Run in stdio mode (default)
mcp-radarr

# Run in SSE server mode
mcp-radarr --server

# Run in SSE server mode with custom host and port
mcp-radarr --server -H localhost -p 8080
```

## Configuration

Set your Radarr API key and URL as environment variables:

```bash
export RADARR_API_KEY="your_api_key"
export RADARR_URL="http://localhost:7878"
```

## MCP Tools

- `lookup_movie`: Search for movies by name using the Radarr API.
- `movie_info`: Query details about a movie in the wanted list.
- `add_movie`: Add a movie to the Radarr wanted list.

API documentation: https://radarr.video/docs/api/#/
