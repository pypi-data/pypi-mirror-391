#!/usr/bin/env python3
"""
Submagic MCP Server

AI-powered video editing with automatic captions, magic zooms, B-rolls, and social media optimization.
Provides tools for creating viral short-form content with 100+ language support.
"""

import os
import asyncio
import httpx
from typing import Optional, List, Any, Dict
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field, field_validator

# Constants
API_BASE_URL = "https://api.submagic.co/v1"
CHARACTER_LIMIT = 25000

# Initialize MCP server
app = FastMCP("submagic_mcp")

# ==============================================================================
# Pydantic Models for Input Validation
# ==============================================================================

class CreateProjectInput(BaseModel):
    """Input model for creating a video project with AI captions"""
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Descriptive title for your video project"
    )
    language: str = Field(
        ...,
        pattern="^[a-z]{2}(-[A-Z]{2})?$",
        description="Language code for transcription (e.g., 'en', 'es', 'fr')"
    )
    video_url: str = Field(
        ...,
        description="Public URL to your video file (must be accessible without authentication)"
    )
    template_name: Optional[str] = Field(
        None,
        description="Template name for styling (e.g., 'Hormozi 2', 'Sara'). Use submagic_list_templates to see options."
    )
    user_theme_id: Optional[str] = Field(
        None,
        description="Custom theme UUID. Cannot be used with template_name."
    )
    webhook_url: Optional[str] = Field(
        None,
        description="URL to receive webhook notifications when processing completes"
    )
    dictionary: Optional[List[str]] = Field(
        None,
        max_length=100,
        description="Custom words/phrases to improve transcription accuracy"
    )
    magic_zooms: Optional[bool] = Field(
        True,
        description="Enable AI-powered dynamic zooms for emphasis"
    )
    magic_brolls: Optional[bool] = Field(
        True,
        description="Enable automatic B-roll insertion from Storyblocks"
    )
    magic_brolls_percentage: Optional[int] = Field(
        75,
        ge=0,
        le=100,
        description="Percentage of video to fill with B-rolls (0-100)"
    )
    remove_silence_pace: Optional[str] = Field(
        "natural",
        pattern="^(natural|fast|extra-fast)$",
        description="Silence removal speed: natural (0.6+ sec), fast (0.2-0.6 sec), or extra-fast (0.1-0.2 sec)"
    )
    remove_bad_takes: Optional[bool] = Field(
        True,
        description="Automatically remove filler words and bad takes"
    )

    @field_validator('template_name', 'user_theme_id')
    def validate_template_theme_exclusivity(cls, v, info):
        """Ensure template_name and user_theme_id are not both provided"""
        if info.data.get('template_name') and info.data.get('user_theme_id'):
            raise ValueError("Cannot use both template_name and user_theme_id")
        return v


class GetProjectInput(BaseModel):
    """Input model for retrieving project details"""
    project_id: str = Field(
        ...,
        description="UUID of the project to retrieve"
    )


class UpdateProjectInput(BaseModel):
    """Input model for updating project settings - only supports editing features, not AI toggles"""
    project_id: str = Field(
        ...,
        description="UUID of the project to update"
    )
    remove_silence_pace: Optional[str] = Field(
        None,
        pattern="^(natural|fast|extra-fast)$",
        description="Adjust silence removal speed: natural (0.6+ sec), fast (0.2-0.6 sec), or extra-fast (0.1-0.2 sec)"
    )
    remove_bad_takes: Optional[bool] = Field(
        None,
        description="Enable AI-powered detection and removal of filler words and bad takes (takes 1-2 minutes)"
    )
    items: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Array of custom B-roll clips to insert. Each item: {startTime: float, endTime: float, userMediaId: string}"
    )


class ExportProjectInput(BaseModel):
    """Input model for exporting rendered video"""
    project_id: str = Field(
        ...,
        description="UUID of the project to export"
    )
    fps: Optional[int] = Field(
        None,
        ge=1,
        le=60,
        description="Frames per second for exported video (1-60). Defaults to project's original fps or 30."
    )
    width: Optional[int] = Field(
        None,
        ge=100,
        le=4000,
        description="Video width in pixels (100-4000). Defaults to project's original width or 1080."
    )
    height: Optional[int] = Field(
        None,
        ge=100,
        le=4000,
        description="Video height in pixels (100-4000). Defaults to project's original height or 1920."
    )
    webhook_url: Optional[str] = Field(
        None,
        description="URL to receive notification when export is complete"
    )


class CreateMagicClipsInput(BaseModel):
    """Input model for generating viral clips from long-form video with full control"""
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Title for the clips project"
    )
    youtube_url: str = Field(
        ...,
        description="YouTube URL of the long-form video to clip"
    )
    language: str = Field(
        ...,
        pattern="^[a-z]{2,10}(_[a-z]{2})?$",
        description="Language code for captions (e.g., 'en', 'es', 'cmn_en')"
    )
    webhook_url: Optional[str] = Field(
        None,
        description="URL to receive notification when clip generation completes"
    )
    user_theme_id: Optional[str] = Field(
        None,
        description="UUID of custom branded theme to apply to clips"
    )
    min_clip_length: Optional[int] = Field(
        15,
        ge=15,
        le=300,
        description="Minimum clip duration in seconds (15-300). Perfect for platform requirements."
    )
    max_clip_length: Optional[int] = Field(
        60,
        ge=15,
        le=300,
        description="Maximum clip duration in seconds (15-300). Must be >= minClipLength."
    )


# ==============================================================================
# API Helper Functions
# ==============================================================================

def get_api_key() -> str:
    """Get Submagic API key from environment"""
    api_key = os.getenv("SUBMAGIC_API_KEY")
    if not api_key:
        raise ValueError(
            "SUBMAGIC_API_KEY environment variable is required. "
            "Get your API key from https://app.submagic.co/signup"
        )
    return api_key


async def make_api_request(
    method: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Make HTTP request to Submagic API with error handling
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint path (without base URL)
        data: Request body data
        params: Query parameters
        
    Returns:
        JSON response data
        
    Raises:
        Exception: If API request fails with descriptive error message
    """
    api_key = get_api_key()
    url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                return {
                    "error": "Rate limit exceeded",
                    "message": "You've hit the rate limit for this operation. Please wait and try again.",
                    "limits": {
                        "lightweight_operations": "1000 requests/hour",
                        "standard_operations": "500 requests/hour",
                        "upload_operations": "500 requests/hour"
                    }
                }
            
            # Handle authentication errors
            if response.status_code == 401:
                return {
                    "error": "Authentication failed",
                    "message": "Invalid API key. Check your SUBMAGIC_API_KEY environment variable."
                }
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("message", error_data.get("error", str(error_data)))
            except:
                error_detail = e.response.text or str(e)
            
            return {
                "error": f"API Error ({e.response.status_code})",
                "message": error_detail,
                "suggestion": "Check the API documentation at https://docs.submagic.co for more details."
            }
            
        except httpx.TimeoutException:
            return {
                "error": "Request timeout",
                "message": "The request took too long to complete. The video might be too large or the server is busy.",
                "suggestion": "Try with a smaller video or wait a few minutes and retry."
            }
            
        except Exception as e:
            return {
                "error": "Request failed",
                "message": str(e),
                "suggestion": "Check your internet connection and API key configuration."
            }


def truncate_text(text: str, max_length: int = CHARACTER_LIMIT) -> str:
    """Truncate text to maximum length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_project_response(project: Dict[str, Any], detail_level: str = "summary") -> str:
    """
    Format project data for LLM consumption
    
    Args:
        project: Project data from API
        detail_level: "summary" or "detailed"
        
    Returns:
        Formatted markdown string
    """
    if detail_level == "summary":
        return f"""# Project: {project.get('title', 'Untitled')}

**ID:** `{project.get('id')}`
**Status:** {project.get('status', 'unknown')}
**Language:** {project.get('language', 'unknown')}
**Template:** {project.get('templateName', 'default')}
**Created:** {project.get('createdAt', 'unknown')}

**Features Enabled:**
- Magic Zooms: {'✓' if project.get('magicZooms') else '✗'}
- Magic B-rolls: {'✓' if project.get('magicBrolls') else '✗'}
- Remove Bad Takes: {'✓' if project.get('removeBadTakes') else '✗'}
"""
    
    # Detailed format
    output = f"""# Project Details: {project.get('title', 'Untitled')}

## Basic Information
- **Project ID:** `{project.get('id')}`
- **Status:** {project.get('status', 'unknown')}
- **Language:** {project.get('language', 'unknown')}
- **Created:** {project.get('createdAt', 'unknown')}
- **Updated:** {project.get('updatedAt', 'unknown')}

## Styling
- **Template:** {project.get('templateName', 'default')}
- **User Theme ID:** {project.get('userThemeId', 'none')}

## AI Features
- **Magic Zooms:** {'Enabled' if project.get('magicZooms') else 'Disabled'}
- **Magic B-rolls:** {'Enabled' if project.get('magicBrolls') else 'Disabled'}
- **B-roll Percentage:** {project.get('magicBrollsPercentage', 'N/A')}%
- **Remove Silence Pace:** {project.get('removeSilencePace', 'medium')}
- **Remove Bad Takes:** {'Enabled' if project.get('removeBadTakes') else 'Disabled'}

## Integration
- **Webhook URL:** {project.get('webhookUrl', 'none')}
"""
    
    if project.get('videoUrl'):
        output += f"\n**Video URL:** {project.get('videoUrl')}"
    
    if project.get('outputUrl'):
        output += f"\n\n## Output\n**Download URL:** {project.get('outputUrl')}"
    
    return truncate_text(output)


# ==============================================================================
# MCP Tool Implementations
# ==============================================================================

@app.tool()
async def submagic_list_languages() -> List[TextContent]:
    """
    Get list of supported languages for transcription and captions.
    
    Returns comprehensive list of 100+ language codes that can be used
    when creating projects. Useful for determining which language code
    to use for your video content.
    
    Returns:
        List of language codes with names (e.g., "en - English", "es - Spanish")
        
    Rate Limit: 1000 requests/hour
    """
    result = await make_api_request("GET", "languages")
    
    if "error" in result:
        return [TextContent(
            type="text",
            text=f"Error: {result['error']}\n{result['message']}\n\n{result.get('suggestion', '')}"
        )]
    
    languages = result.get("languages", [])
    
    output = f"""# Supported Languages ({len(languages)} total)

Available language codes for transcription and captions:

"""
    
    for lang in languages:
        if isinstance(lang, dict):
            code = lang.get('code', '')
            name = lang.get('name', '')
            output += f"- **{code}** - {name}\n"
        else:
            # Sometimes API returns simple string codes
            output += f"- {lang}\n"
    
    output += "\n**Usage:** Use the language code (e.g., 'en', 'es') when creating a project."
    
    return [TextContent(type="text", text=truncate_text(output))]


@app.tool()
async def submagic_list_templates() -> List[TextContent]:
    """
    Get list of available video styling templates.
    
    Returns all pre-made templates that can be applied to projects for
    professional caption styling, animations, and effects. Each template
    has a unique visual style optimized for different content types.
    
    Popular templates include:
    - Hormozi series (1-5): High-energy business/marketing style
    - Sara: General social media optimized (default)
    - Beast: MrBeast-inspired style
    
    Returns:
        List of template names that can be used in submagic_create_project
        
    Rate Limit: 1000 requests/hour
    
    Example:
        Use "Hormozi 2" for business/sales content
        Use "Sara" for general social media
        Use "Beast" for entertainment content
    """
    result = await make_api_request("GET", "templates")
    
    if "error" in result:
        return [TextContent(
            type="text",
            text=f"Error: {result['error']}\n{result['message']}\n\n{result.get('suggestion', '')}"
        )]
    
    templates = result.get("templates", [])
    
    output = f"""# Available Templates ({len(templates)} total)

Choose a template name to apply professional styling to your videos:

"""
    
    # Categorize templates for better organization
    hormozi_templates = [t for t in templates if 'hormozi' in t.lower()]
    other_templates = [t for t in templates if 'hormozi' not in t.lower()]
    
    if hormozi_templates:
        output += "## Hormozi Series (Business/Sales)\n"
        for template in sorted(hormozi_templates):
            output += f"- `{template}`\n"
        output += "\n"
    
    if other_templates:
        output += "## Other Styles\n"
        for template in sorted(other_templates):
            output += f"- `{template}`\n"
    
    output += """\n**Usage:** Pass the exact template name to `submagic_create_project`

**Note:** Template names are case-sensitive. If not specified, "Sara" is used by default."""
    
    return [TextContent(type="text", text=truncate_text(output))]


@app.tool()
async def submagic_create_project(
    title: str,
    language: str,
    video_url: str,
    template_name: Optional[str] = None,
    user_theme_id: Optional[str] = None,
    webhook_url: Optional[str] = None,
    dictionary: Optional[List[str]] = None,
    magic_zooms: bool = True,
    magic_brolls: bool = True,
    magic_brolls_percentage: int = 75,
    remove_silence_pace: str = "medium",
    remove_bad_takes: bool = True
) -> List[TextContent]:
    """
    Create a new video project with AI-powered captions and effects.
    
    This is the primary tool for processing videos through Submagic. It will:
    1. Download the video from the provided URL
    2. Transcribe audio to text with high accuracy
    3. Generate animated captions with chosen template
    4. Apply AI features like magic zooms and B-rolls
    5. Remove silence and filler words
    
    Processing typically takes 2-10 minutes depending on video length.
    Check status with submagic_get_project using the returned project ID.
    
    Args:
        title: Descriptive project title (1-100 characters)
        language: Language code (get from submagic_list_languages)
        video_url: Public URL to video file (must be accessible)
        template_name: Styling template (get from submagic_list_templates)
        user_theme_id: Custom theme UUID (cannot use with template_name)
        webhook_url: URL for completion notification
        dictionary: Custom words for better transcription accuracy
        magic_zooms: Enable AI-powered dynamic zooms (default: true)
        magic_brolls: Auto-insert B-roll footage (default: true)
        magic_brolls_percentage: B-roll coverage 0-100% (default: 75)
        remove_silence_pace: Silence removal speed: natural/fast/extra-fast (default: natural)
        remove_bad_takes: Remove filler words automatically (default: true)
    
    Returns:
        Project ID and initial status information
        
    Rate Limit: 500 requests/hour
    
    Example:
        Create a business video with Hormozi style:
        title="Product Launch Video"
        language="en"
        video_url="https://example.com/video.mp4"
        template_name="Hormozi 2"
        magic_zooms=True
        magic_brolls=True
    """
    # Validate inputs
    try:
        input_data = CreateProjectInput(
            title=title,
            language=language,
            video_url=video_url,
            template_name=template_name,
            user_theme_id=user_theme_id,
            webhook_url=webhook_url,
            dictionary=dictionary,
            magic_zooms=magic_zooms,
            magic_brolls=magic_brolls,
            magic_brolls_percentage=magic_brolls_percentage,
            remove_silence_pace=remove_silence_pace,
            remove_bad_takes=remove_bad_takes
        )
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Input validation error: {str(e)}\n\nPlease check your parameters and try again."
        )]
    
    # Prepare API request body
    request_body = {
        "title": input_data.title,
        "language": input_data.language,
        "videoUrl": input_data.video_url,
        "magicZooms": input_data.magic_zooms,
        "magicBrolls": input_data.magic_brolls,
        "magicBrollsPercentage": input_data.magic_brolls_percentage,
        "removeSilencePace": input_data.remove_silence_pace,
        "removeBadTakes": input_data.remove_bad_takes
    }
    
    if input_data.template_name:
        request_body["templateName"] = input_data.template_name
    
    if input_data.user_theme_id:
        request_body["userThemeId"] = input_data.user_theme_id
    
    if input_data.webhook_url:
        request_body["webhookUrl"] = input_data.webhook_url
    
    if input_data.dictionary:
        request_body["dictionary"] = input_data.dictionary
    
    result = await make_api_request("POST", "projects", data=request_body)
    
    if "error" in result:
        return [TextContent(
            type="text",
            text=f"Error: {result['error']}\n{result['message']}\n\n{result.get('suggestion', '')}"
        )]
    
    formatted_output = format_project_response(result, detail_level="detailed")
    
    output = f"""{formatted_output}

## Next Steps
1. Save the project ID: `{result.get('id')}`
2. Check processing status with: `submagic_get_project("{result.get('id')}")`
3. Once status is "completed", use `submagic_export_project` to download

**Processing Time:** Usually 2-10 minutes depending on video length
**Status Check:** Poll every 30-60 seconds until complete
"""
    
    return [TextContent(type="text", text=truncate_text(output))]


@app.tool()
async def submagic_get_project(project_id: str) -> List[TextContent]:
    """
    Get detailed information about a specific project including processing status.
    
    Use this tool to:
    - Check if processing is complete
    - Get download URL for finished videos
    - View applied settings and features
    - Monitor progress of ongoing renders
    
    Project Statuses:
    - "processing": Video is being transcribed and edited
    - "completed": Ready to export/download
    - "failed": Processing encountered an error
    - "queued": Waiting to start processing
    
    Args:
        project_id: UUID of the project (from submagic_create_project)
    
    Returns:
        Complete project details including status and settings
        
    Rate Limit: 500 requests/hour
    
    Example:
        Check status every 60 seconds:
        submagic_get_project("550e8400-e29b-41d4-a716-446655440000")
    """
    try:
        input_data = GetProjectInput(project_id=project_id)
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Input validation error: {str(e)}"
        )]
    
    result = await make_api_request("GET", f"projects/{input_data.project_id}")
    
    if "error" in result:
        return [TextContent(
            type="text",
            text=f"Error: {result['error']}\n{result['message']}\n\n{result.get('suggestion', '')}"
        )]
    
    formatted_output = format_project_response(result, detail_level="detailed")
    
    status = result.get('status', 'unknown')
    
    if status == "processing":
        formatted_output += "\n\n**⏳ Status: Processing**\nCheck again in 30-60 seconds."
    elif status == "completed":
        formatted_output += "\n\n**✅ Status: Completed**\nReady to export! Use `submagic_export_project` to download."
    elif status == "failed":
        formatted_output += f"\n\n**❌ Status: Failed**\nError: {result.get('error', 'Unknown error')}"
    
    return [TextContent(type="text", text=truncate_text(formatted_output))]


@app.tool()
async def submagic_update_project(
    project_id: str,
    remove_silence_pace: Optional[str] = None,
    remove_bad_takes: Optional[bool] = None,
    custom_broll_items: Optional[List[Dict[str, Any]]] = None
) -> List[TextContent]:
    """
    Update an existing project with advanced editing features.
    
    This tool allows you to enhance your video after initial processing by:
    - Adjusting silence removal aggressiveness
    - Enabling AI-powered filler word removal
    - Inserting custom B-roll clips from your media library
    
    Important: Changes require re-exporting the project to take effect.
    Note: magicZooms and magicBrolls can only be set during project creation, not updated later.
    
    Args:
        project_id: UUID of the project to update
        remove_silence_pace: Adjust silence removal - natural/fast/extra-fast
            - natural: 0.6+ seconds (gentle, preserves natural pauses)
            - fast: 0.2-0.6 seconds (moderate, tightens pacing)
            - extra-fast: 0.1-0.2 seconds (aggressive, maximum compression)
        remove_bad_takes: Enable AI removal of filler words like "um", "uh", "like"
            Warning: Takes 1-2 minutes to process
        custom_broll_items: Insert your own B-roll clips at specific timestamps
            Each item must have:
            - startTime (float): When clip should start in seconds
            - endTime (float): When clip should end in seconds (must be > startTime)
            - userMediaId (string): UUID of your uploaded media (find in Submagic editor → B-roll tab → My videos)
            
            Example: [{"startTime": 10.5, "endTime": 15.0, "userMediaId": "abc-123-def"}]
    
    Returns:
        Updated project information
        
    Rate Limit: 100 requests/hour
    
    Important Notes:
    - After updating, you MUST re-export the project to apply changes
    - remove_bad_takes processing takes 1-2 minutes
    - Custom B-roll clips overlay your existing video content
    - To find userMediaId: Open Submagic editor → B-roll tab → My videos → Copy the UUID shown
    
    Example 1 - Speed up a slow video:
        submagic_update_project(
            project_id="550e8400-e29b-41d4-a716-446655440000",
            remove_silence_pace="extra-fast"
        )
    
    Example 2 - Clean up filler words:
        submagic_update_project(
            project_id="550e8400-e29b-41d4-a716-446655440000",
            remove_bad_takes=True
        )
    
    Example 3 - Replace boring section with product demo:
        submagic_update_project(
            project_id="550e8400-e29b-41d4-a716-446655440000",
            custom_broll_items=[
                {
                    "startTime": 30.0,
                    "endTime": 45.0,
                    "userMediaId": "your-product-demo-uuid"
                }
            ]
        )
    
    Example 4 - Combine all features:
        submagic_update_project(
            project_id="550e8400-e29b-41d4-a716-446655440000",
            remove_silence_pace="fast",
            remove_bad_takes=True,
            custom_broll_items=[
                {"startTime": 10.0, "endTime": 15.0, "userMediaId": "uuid-1"},
                {"startTime": 30.0, "endTime": 35.0, "userMediaId": "uuid-2"}
            ]
        )
    """
    try:
        input_data = UpdateProjectInput(
            project_id=project_id,
            remove_silence_pace=remove_silence_pace,
            remove_bad_takes=remove_bad_takes,
            items=custom_broll_items
        )
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Input validation error: {str(e)}\n\nPlease check your parameters and try again."
        )]
    
    # Build update body with proper API field names
    update_body = {}
    
    if input_data.remove_silence_pace:
        update_body["removeSilencePace"] = input_data.remove_silence_pace
    
    if input_data.remove_bad_takes is not None:
        update_body["removeBadTakes"] = input_data.remove_bad_takes
    
    if input_data.items:
        # Convert to API format with camelCase
        update_body["items"] = [
            {
                "startTime": item["startTime"],
                "endTime": item["endTime"],
                "userMediaId": item["userMediaId"]
            }
            for item in input_data.items
        ]
    
    if not update_body:
        return [TextContent(
            type="text",
            text="No updates provided. Please specify at least one field to update:\n- remove_silence_pace\n- remove_bad_takes\n- custom_broll_items"
        )]
    
    result = await make_api_request("PUT", f"projects/{input_data.project_id}", data=update_body)
    
    if "error" in result:
        return [TextContent(
            type="text",
            text=f"Error: {result['error']}\n{result['message']}\n\n{result.get('suggestion', '')}"
        )]
    
    # Format response with update summary
    output = f"""# Project Updated Successfully

**Project ID:** {input_data.project_id}
**Status:** {result.get('status', 'updated')}

## Updates Applied:
"""
    
    if input_data.remove_silence_pace:
        pace_desc = {
            "natural": "Natural (0.6+ sec) - Gentle pacing",
            "fast": "Fast (0.2-0.6 sec) - Moderate compression",
            "extra-fast": "Extra-Fast (0.1-0.2 sec) - Maximum compression"
        }
        output += f"- **Silence Removal:** {pace_desc.get(input_data.remove_silence_pace, input_data.remove_silence_pace)}\n"
    
    if input_data.remove_bad_takes is not None:
        if input_data.remove_bad_takes:
            output += "- **Bad Takes Removal:** Enabled (AI processing filler words - takes 1-2 min)\n"
        else:
            output += "- **Bad Takes Removal:** Disabled\n"
    
    if input_data.items:
        output += f"- **Custom B-rolls:** {len(input_data.items)} clip(s) inserted\n"
        for i, item in enumerate(input_data.items, 1):
            duration = item['endTime'] - item['startTime']
            output += f"  - Clip {i}: {item['startTime']}s to {item['endTime']}s ({duration:.1f}s duration)\n"
    
    output += f"""\n## Next Steps
1. **Wait for processing:** If you enabled remove_bad_takes, wait 1-2 minutes
2. **Check status:** Use `submagic_get_project("{input_data.project_id}")` to verify completion
3. **Re-export:** Run `submagic_export_project("{input_data.project_id}")` to apply changes
4. **Download:** Get the new video with your updates!

**Important:** Changes won't appear in the video until you re-export!

## Pro Tips
- Use extra-fast silence removal for tutorials and talking heads
- Enable remove_bad_takes for podcast and interview content
- Custom B-rolls work great for covering transitions or adding product shots
- You can update and re-export multiple times to fine-tune your video
"""
    
    return [TextContent(type="text", text=truncate_text(output))]


@app.tool()
async def submagic_export_project(
    project_id: str,
    fps: Optional[int] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    webhook_url: Optional[str] = None
) -> List[TextContent]:
    """
    Export and download a completed project video.
    
    Triggers the rendering/export process for a completed project with customizable
    output parameters. The export process is asynchronous - download URLs will be
    available once rendering completes.
    
    Args:
        project_id: UUID of completed project
        fps: Frames per second (1-60). Defaults to project's original fps or 30.
        width: Video width in pixels (100-4000). Defaults to original width or 1080.
        height: Video height in pixels (100-4000). Defaults to original height or 1920.
        webhook_url: URL to receive notification when export completes
    
    Returns:
        Export confirmation with project status
        
    Rate Limit: 500 requests/hour
    
    Note: Project must have status="completed" before exporting.
    Check status with submagic_get_project first.
    
    Example:
        Export in 4K (3840x2160):
        submagic_export_project(
            project_id="550e8400-e29b-41d4-a716-446655440000",
            width=3840,
            height=2160,
            fps=30
        )
    """
    try:
        input_data = ExportProjectInput(
            project_id=project_id,
            fps=fps,
            width=width,
            height=height,
            webhook_url=webhook_url
        )
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Input validation error: {str(e)}\n\nPlease check your parameters and try again."
        )]
    
    # Build export request body (only include provided parameters)
    export_body = {}
    if input_data.fps is not None:
        export_body["fps"] = input_data.fps
    if input_data.width is not None:
        export_body["width"] = input_data.width
    if input_data.height is not None:
        export_body["height"] = input_data.height
    if input_data.webhook_url is not None:
        export_body["webhookUrl"] = input_data.webhook_url
    
    result = await make_api_request("POST", f"projects/{input_data.project_id}/export", data=export_body)
    
    if "error" in result:
        return [TextContent(
            type="text",
            text=f"Error: {result['error']}\n{result['message']}\n\n{result.get('suggestion', '')}"
        )]
    
    output = f"""# Export Started Successfully

**Project ID:** {input_data.project_id}
**Status:** {result.get('status', 'exporting')}

## Export Settings
- **FPS:** {input_data.fps or 'Project default'}
- **Width:** {input_data.width or 'Project default'}
- **Height:** {input_data.height or 'Project default'}
- **Webhook:** {input_data.webhook_url or 'None'}

## Next Steps
1. The export process is asynchronous and will take a few minutes
2. Monitor progress with: `submagic_get_project("{input_data.project_id}")`
3. Once complete, the project will have `downloadUrl` and `directUrl` fields

**Tip:** Use `submagic_get_project` to check when the export is ready and get the download URL.
"""
    
    return [TextContent(type="text", text=truncate_text(output))]


@app.tool()
async def submagic_create_magic_clips(
    title: str,
    youtube_url: str,
    language: str,
    webhook_url: Optional[str] = None,
    user_theme_id: Optional[str] = None,
    min_clip_length: int = 15,
    max_clip_length: int = 60
) -> List[TextContent]:
    """
    Automatically generate viral short-form clips from a YouTube video with full control.
    
    AI analyzes the full video to find the most engaging moments and creates
    multiple clips optimized for TikTok, Instagram Reels, and YouTube Shorts.
    Now with complete control over clip durations and branding!
    
    Each clip includes:
    - AI-selected engaging content
    - Auto-generated captions
    - Applied template/theme styling
    - Optimized aspect ratio (9:16)
    
    Perfect for repurposing long-form content into platform-specific clips.
    
    Args:
        title: Project title for the clips collection
        youtube_url: Full YouTube URL (e.g., https://youtube.com/watch?v=...)
        language: Language code for captions (e.g., 'en', 'es', 'cmn_en')
        webhook_url: URL to receive notification when generation completes
        user_theme_id: UUID of your custom branded theme (get from Submagic editor)
        min_clip_length: Minimum clip duration in seconds (15-300). Default: 15
        max_clip_length: Maximum clip duration in seconds (15-300). Default: 60
    
    Returns:
        Magic clips project ID and generation status
        
    Rate Limit: 500 requests/hour
    
    Processing Time: 5-15 minutes depending on source video length
    
    Platform-Specific Examples:
    
    Example 1 - TikTok clips (15-30 seconds):
        submagic_create_magic_clips(
            title="TikTok Highlights",
            youtube_url="https://youtube.com/watch?v=abc123",
            language="en",
            min_clip_length=15,
            max_clip_length=30
        )
    
    Example 2 - Instagram Reels (30 seconds exactly):
        submagic_create_magic_clips(
            title="Reels Pack",
            youtube_url="https://youtube.com/watch?v=abc123",
            language="en",
            min_clip_length=30,
            max_clip_length=30
        )
    
    Example 3 - Branded YouTube Shorts (60 seconds with custom theme):
        submagic_create_magic_clips(
            title="Branded Shorts",
            youtube_url="https://youtube.com/watch?v=abc123",
            language="en",
            min_clip_length=45,
            max_clip_length=60,
            user_theme_id="your-theme-uuid-here",
            webhook_url="https://yoursite.com/webhook"
        )
    
    Example 4 - Podcast snippets (2-3 minutes):
        submagic_create_magic_clips(
            title="Podcast Clips",
            youtube_url="https://youtube.com/watch?v=abc123",
            language="en",
            min_clip_length=120,
            max_clip_length=180
        )
    """
    try:
        input_data = CreateMagicClipsInput(
            title=title,
            youtube_url=youtube_url,
            language=language,
            webhook_url=webhook_url,
            user_theme_id=user_theme_id,
            min_clip_length=min_clip_length,
            max_clip_length=max_clip_length
        )
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Input validation error: {str(e)}\n\nPlease check your parameters and try again."
        )]
    
    # Validate min <= max
    if input_data.min_clip_length > input_data.max_clip_length:
        return [TextContent(
            type="text",
            text=f"Invalid clip lengths: minClipLength ({input_data.min_clip_length}) must be <= maxClipLength ({input_data.max_clip_length})"
        )]
    
    # Build request with proper API field names
    request_body = {
        "title": input_data.title,
        "youtubeUrl": input_data.youtube_url,
        "language": input_data.language,
        "minClipLength": input_data.min_clip_length,
        "maxClipLength": input_data.max_clip_length
    }
    
    if input_data.webhook_url:
        request_body["webhookUrl"] = input_data.webhook_url
    
    if input_data.user_theme_id:
        request_body["userThemeId"] = input_data.user_theme_id
    
    result = await make_api_request("POST", "projects/magic-clips", data=request_body)
    
    if "error" in result:
        return [TextContent(
            type="text",
            text=f"Error: {result['error']}\n{result['message']}\n\n{result.get('suggestion', '')}"
        )]
    
    project_id = result.get('id', result.get('projectId', 'Unknown'))
    
    # Determine platform suggestion based on duration
    platform_hint = ""
    if input_data.max_clip_length <= 30:
        platform_hint = "Perfect for TikTok!"
    elif input_data.max_clip_length <= 60:
        platform_hint = "Optimized for Instagram Reels & YouTube Shorts!"
    elif input_data.max_clip_length <= 90:
        platform_hint = "Great for extended YouTube Shorts!"
    else:
        platform_hint = "Ideal for longer social media content!"
    
    output = f"""# Magic Clips Generation Started

**Project ID:** `{project_id}`
**Title:** {input_data.title}
**Source:** {input_data.youtube_url}

## Configuration
- **Clip Length:** {input_data.min_clip_length}s to {input_data.max_clip_length}s
- **Language:** {input_data.language}
- **Theme:** {"Custom branded theme" if input_data.user_theme_id else "Default template"}
- **Webhook:** {"Configured" if input_data.webhook_url else "None"}

**Platform Fit:** {platform_hint}

**Status:** {result.get('status', 'processing')}

## Next Steps
1. Wait 5-15 minutes for AI analysis and clip generation
2. Check status with: `submagic_get_project("{project_id}")`
3. Once complete, the response will include individual clip IDs with download URLs
4. Each clip will be {input_data.min_clip_length}-{input_data.max_clip_length} seconds long

## What's Happening Now
The AI is analyzing your YouTube video to:
- Identify the most engaging moments
- Find natural cut points for viral clips
- Apply captions and styling
- Optimize for social media algorithms

**Note:** Clips are selected for maximum viral potential based on content analysis!
"""
    
    return [TextContent(type="text", text=truncate_text(output))]


# ==============================================================================
# Server Lifecycle
# ==============================================================================

def main():
    """Main entry point for the MCP server"""
    app.run()


if __name__ == "__main__":
    main()
