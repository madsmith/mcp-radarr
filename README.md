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

The server can be run in multiple transport modes:

```bash
# Run in stdio mode (default)
mcp-radarr

# Run in SSE server mode
mcp-radarr --mode sse --host localhost --port 8050

# Run in HTTP server mode
mcp-radarr --mode http --host localhost --port 8050

# Run in streamable HTTP mode
mcp-radarr --mode streamable-http --host localhost --port 8050
```

### Command-line Arguments

- `--mode`: Transport mode (choices: stdio, sse, http, streamable-http, default: stdio)
- `--port` or `-p`: Port to run the server on (default: 8050)
- `--host` or `-H`: Host to run the server on (default: 0.0.0.0)

## Configuration

MCP-Radarr provides multiple ways to configure the Radarr connection settings, checked in the following order of precedence:

### 1. Command-line Arguments

Directly specify Radarr connection details when starting the server:

```bash
# Specify Radarr URL and API key directly
mcp-radarr --radarr-url="http://localhost:7878" --radarr-api-key="your_api_key"

# Specify a custom config file location
mcp-radarr --config="/path/to/your/config.yaml"
```

### 2. Environment Variables

Set your Radarr API key and URL as environment variables:

```bash
export RADARR_API_KEY="your_api_key"
export RADARR_URL="http://localhost:7878"

# Optionally specify a custom config file location
export RADARR_CONFIG="/path/to/your/config.yaml"
```

### 3. Configuration Files

MCP-Radarr will look for configuration files in the following locations (in order):

1. Path specified by `RADARR_CONFIG` environment variable
2. User home directory: `~/.config/mcp-radarr/config.yaml`
3. Current working directory: `./config.yaml`
4. Package bundled default config

Example configuration file (YAML format):

```yaml
radarr:
  url: "http://localhost:7878"
  api_key: "your_api_key"
```

## MCP Tools

The following tools are available through the MCP interface:

- `lookup_movie`: Search for movies by name using the Radarr API
- `movie_list`: Retrieve a complete list of all movies currently tracked in your Radarr library
- `movie_info`: Query details about a movie in the wanted list by title
- `movie_info_by_tmdb_id`: Query details about a movie by TMDB ID
- `get_quality_profiles`: Retrieve all configured quality profiles from Radarr
- `add_movie`: Add a movie to the Radarr wanted list by TMDB ID
- `edit_movie`: Edit properties of movies in the Radarr library
- `search_for_movie`: Search for movies matching specific criteria like name, year, genre, etc.

API documentation: https://radarr.video/docs/api/#/
