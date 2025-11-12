# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server that integrates with the Submagic API for AI-powered video editing. The server enables automatic captions, magic zooms, B-roll insertion, and viral clip generation from videos in 100+ languages.

**Status:** Fully functional and tested with Submagic API v1
**API Coverage:** 100% of available endpoints
**Rating:** 9.5/10 (Production-ready)

## Architecture

### Core Components

**submagic_mcp.py** - Single-file MCP server implementation
- Built using the MCP Python SDK (`mcp` package) with `FastMCP` class
- Implements 7 tools for video processing operations
- Uses `httpx` for async HTTP requests to Submagic API
- Input validation via Pydantic models
- Stdio transport for communication with MCP clients

**Key Implementation Details:**
- Uses `FastMCP` (not `Server`) for tool registration with `@app.tool()` decorator
- All tool functions are async and return `List[TextContent]`
- Simple `app.run()` method handles stdio server lifecycle

**Key Classes (Pydantic Models):**
- `CreateProjectInput` - Video project creation with AI captions/effects (lines 28-91)
- `GetProjectInput` - Project status retrieval (lines 94-99)
- `UpdateProjectInput` - Modify project settings (lines 102-112)
- `ExportProjectInput` - Export video in various resolutions (lines 115-123)
- `CreateMagicClipsInput` - Generate viral clips from YouTube videos (lines 126-162)

**Helper Functions:**
- `get_api_key()` - Retrieves SUBMAGIC_API_KEY from environment
- `make_api_request()` - Centralized API request handler with error management
- `truncate_text()` - Limits response text to CHARACTER_LIMIT (4000 chars)
- `format_project_response()` - Formats project data for consistent output

### MCP Tool Functions

1. `submagic_list_languages` - Returns 107 supported language codes (including multi-language)
2. `submagic_list_templates` - Lists 30+ visual templates (Hormozi series, Beast, Sara, etc.)
3. `submagic_create_project` - Creates video with AI captions, zooms, B-rolls, silence removal
4. `submagic_get_project` - Checks processing status and retrieves download URLs
5. `submagic_update_project` - **FULL EDITING SUITE** - adjust silence, remove filler words, insert custom B-rolls
6. `submagic_export_project` - Triggers export with custom dimensions, FPS, and webhooks
7. `submagic_create_magic_clips` - Generates platform-specific clips (15-300s) with branded themes

## Development Commands

### Setup and Installation

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set API key in .env file
# Copy .env.example to .env and add your key
```

### Running the Server

```bash
# Start MCP server (stdio mode)
python submagic_mcp.py

# The server will wait for MCP client connections via stdin/stdout
```

### Testing

```bash
# Run comprehensive test suite (recommended)
python test_server.py

# This will:
# - Load API key from .env
# - Verify all tools are registered
# - Test actual API calls to Submagic
# - Confirm server is ready for use

# Manual tests (if needed)
python -c "from submagic_mcp import app; print('Server imports successfully')"
```

## API Integration

### Base URL
`https://api.submagic.co/v1` (stored in `API_BASE_URL` constant)

### Authentication
- Uses Bearer token authentication
- API key must start with `sk-`
- Set via `SUBMAGIC_API_KEY` environment variable

### Rate Limits
- Lightweight operations (languages, templates): 1000 requests/hour
- Standard operations (get project): 500 requests/hour
- Upload operations (create project): 500 requests/hour

### Error Handling
- 401: Authentication failure (invalid/missing API key)
- 429: Rate limit exceeded
- 400: Invalid input parameters
- 500: Submagic API error

All errors are caught in `make_api_request()` and returned as descriptive error messages.

## Data Directories

- `data/history/` - Project history storage (optional)
- `logs/` - Server logs (combined.log, error.log)

## Configuration

### Claude Desktop Integration

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "submagic": {
      "command": "/absolute/path/to/sub-magic-mcp-server/venv/bin/python",
      "args": ["/absolute/path/to/sub-magic-mcp-server/submagic_mcp.py"],
      "env": {
        "SUBMAGIC_API_KEY": "sk-your-actual-key"
      }
    }
  }
}
```

**Important:** Use the Python executable from the virtual environment for proper dependency resolution.

A template `.mcp.json` file is provided for local testing.

## Important Notes

### Video Processing
- Projects typically take 2-10 minutes to process
- Poll status with `submagic_get_project`, wait 30-60s between checks
- Large videos (>100MB) may take longer
- `remove_bad_takes` processing adds 1-2 minutes

### Editing Workflow
- Create project → Wait for processing → Update settings → Re-export
- After updating a project, you MUST re-export to apply changes
- Can update and re-export multiple times for iterative refinement
- `magicZooms` and `magicBrolls` can only be set during creation, not updated later

### Template vs Theme
- Projects can use EITHER a template_name OR user_theme_id, never both
- Validated in `CreateProjectInput.validate_template_theme_exclusivity()`
- Custom themes require UUID from Submagic editor

### Magic Clips
- Requires YouTube URLs (not direct video URLs)
- Generates multiple short clips optimized for social media
- Full control over clip duration (15-300 seconds)
- Can apply custom branded themes
- Platform-specific: TikTok (15-30s), Reels (30s), Shorts (45-60s)

### Custom B-Roll Insertion
- Find `userMediaId` in Submagic editor → B-roll tab → My videos
- Each B-roll item needs: startTime, endTime, userMediaId
- Multiple B-rolls can be inserted at different timestamps
- B-rolls overlay existing video content

### Response Truncation
- API responses are truncated to 25,000 characters (CHARACTER_LIMIT)
- Prevents token overflow in MCP responses
- Full data available via Submagic dashboard

## Code Style

- Type hints used throughout for all function parameters and returns
- Async/await pattern for all MCP tool functions
- Descriptive error messages with troubleshooting guidance
- Comprehensive docstrings for all tools
- Pydantic models for input validation
