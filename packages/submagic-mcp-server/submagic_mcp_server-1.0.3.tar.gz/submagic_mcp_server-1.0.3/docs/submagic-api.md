API Reference

# Health Check

Check the health status of the Submagic API

GET

/

health

Try it

Health Check

The health endpoint provides a simple way to check if the Submagic API is operational. This endpoint does not require authentication and can be used for monitoring and health checks.

This endpoint does not require authentication and is not subject to rate limiting.

Request


No parameters

void

This endpoint does not accept any parameters.

Response


status

string

The current status of the API service


service

string

The name of the service


timestamp

string

ISO 8601 timestamp of when the response was generated

Use Cases

## Uptime Monitoring

Use this endpoint to monitor API availability in your monitoring systems

## Load Balancer Health Checks

Configure your load balancer to use this endpoint for health checks

## CI/CD Pipeline Validation

Verify API availability before running integration tests

## Status Page Integration

Include this endpoint in your status page monitoring

Status Values

| Status        | Description                                     |
| ------------- | ----------------------------------------------- |
| `healthy`   | API is operational and ready to accept requests |
| `degraded`  | API is operational but experiencing issues      |
| `unhealthy` | API is not operational                          |

Example Monitoring Script

Here’s a simple monitoring script you can use:Bash

Node.js

Python

Copy

Ask AI

```
import requests
import time
import sys

def check_health():
    try:
        response = requests.get('https://api.submagic.co/health', timeout=10)
        data = response.json()

        if response.status_code == 200 and data.get('status') == 'healthy':
            print('✅ API is healthy')
            return True
        else:
            print(f'❌ API is not healthy: {data}')
            return False
    except Exception as e:
        print(f'❌ Failed to check API health: {e}')
        return False

if __name__ == '__main__':
    is_healthy = check_health()
    sys.exit(0 if is_healthy else 1)
```

The health endpoint is designed to respond quickly (typically under 100ms) to provide fast health check results for monitoring systems.


# Get Languages

Retrieve a list of all supported languages for video transcription

GET

/

v1

/

languages

Try it

Get Languages

Retrieve a comprehensive list of all supported languages for video transcription and caption generation. This endpoint returns language codes and names that can be used when creating projects.

This endpoint requires authentication and has a rate limit of 100 requests per minute.

Authentication


x-api-key

string

required

Your Submagic API key starting with `sk-`

Response


languages

array

Array of supported language objects

<details open="" class="expandable mt-4 border-standard rounded-xl" data-testid="undefined-children"><summary class="not-prose text-sm flex flex-row items-center content-center w-full cursor-pointer text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-gray-200 py-3 px-3.5 hover:bg-gray-50/50 dark:hover:bg-white/5 rounded-t-xl list-none [&::-webkit-details-marker]:hidden" aria-controls="Children attributes" aria-expanded="true" data-component-part="expandable-button"><svg class="h-2.5 w-2.5 bg-zinc-400 transition-transform rotate-90"></svg><div class="ml-3 leading-tight text-left"><p class="m-0" contenteditable="false">Hide<span> </span>Language Object</p></div></summary>


name

string

Human-readable name of the language (e.g., “English”, “Spanish”)


code

string

ISO language code used for API requests (e.g., “en”, “es”, “fr”)

</details>

Popular Languages

Here are some of the most commonly used language codes:

## English

**Code:** `en` Most widely supported with highest accuracy

## Spanish

**Code:** `es` Excellent support for Latin American and European Spanish

## French

**Code:** `fr` High accuracy for both European and Canadian French

## German

**Code:** `de` Great support for German language nuances

## Italian

**Code:** `it` Optimized for Italian pronunciation patterns

## Portuguese

**Code:** `pt` Supports both Brazilian and European Portuguese

Using Language Codes

Once you have the language codes, you can use them when creating projects:Copy

Ask AI

```
{
  "title": "My Spanish Video",
  "language": "es",
  "videoUrl": "https://example.com/spanish-video.mp4"
}
```

Best Practices

Caching Language Data

Since the list of supported languages doesn’t change frequently, consider caching the response:Copy

Ask AI

```
class LanguageCache {
  constructor() {
    this.cache = null;
    this.lastFetch = null;
    this.cacheDuration = 24 * 60 * 60 * 1000; // 24 hours
  }

  async getLanguages() {
    const now = Date.now();

    if (
      this.cache &&
      this.lastFetch &&
      now - this.lastFetch < this.cacheDuration
    ) {
      return this.cache;
    }

    const response = await fetch("https://api.submagic.co/v1/languages", {
      headers: { "x-api-key": process.env.SUBMAGIC_API_KEY },
    });

    this.cache = await response.json();
    this.lastFetch = now;

    return this.cache;
  }
}
```

Building Language Selectors

Create user-friendly language selection interfaces:Copy

Ask AI

```
const buildLanguageSelector = (languages) => {
  return languages
    .sort((a, b) => a.name.localeCompare(b.name))
    .map((lang) => ({
      value: lang.code,
      label: lang.name,
      flag: getFlagEmoji(lang.code), // Helper function for flag emojis
    }));
};
```

Error Responses


401 Unauthorized

object

Copy

Ask AI

```
{
  "error": "UNAUTHORIZED",
  "message": "Invalid or missing API key"
}
```


429 Rate Limited

object

Copy

Ask AI

```
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests",
  "retryAfter": 30
}
```


500 Server Error

object

Copy

Ask AI

```
{
  "error": "INTERNAL_SERVER_ERROR",
  "message": "An unexpected error occurred"
}
```


# Get Templates

Retrieve a list of all available video templates for styling and effects

GET

/

v1

/

templates

Try it

Get Templates

Retrieve a list of all available video templates that can be applied to your projects. Templates define the visual styling, animations, and effects that will be applied to your captions and video content.

This endpoint requires authentication and has a rate limit of 1000 requests per hour.

Authentication


x-api-key

string

required

Your Submagic API key starting with `sk-`

Response


templates

array

Array of available template names that can be used in project creation

Using Templates

When creating a project, specify the template name in your request:URL-based Project

File Upload Project

Copy

Ask AI

```
{
  "title": "My Trendy Video",
  "language": "en",
  "videoUrl": "https://example.com/video.mp4",
  "templateName": "Hormozi 2"
}
```

Template Features

Each template includes:*  **Caption Styling** : Font family, size, color, and positioning

* **Animation Effects** : How captions appear and disappear
* **Visual Elements** : Background shapes, highlights, and decorative elements
* **Color Schemes** : Coordinated color palettes optimized for the template theme
* **Emoji Integration** : How emojis are displayed and animated
* **Layout Options** : Caption positioning and text alignment

Template Preview

While the API doesn’t provide template previews directly, you can create small test projects with different templates to see how they look with your content style.

Template Testing Strategy

Copy

Ask AI

```
const testTemplates = async (videoUrl, templates) => {
  const results = [];

  for (const template of templates.slice(0, 3)) {
    // Test first 3 templates
    try {
      const response = await fetch("https://api.submagic.co/v1/projects", {
        method: "POST",
        headers: {
          "x-api-key": process.env.SUBMAGIC_API_KEY,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: `Test - ${template}`,
          language: "en",
          videoUrl: videoUrl,
          templateName: template,
        }),
      });

      const project = await response.json();
      results.push({ template, projectId: project.id });

      // Wait between requests to respect rate limits
      await new Promise((resolve) => setTimeout(resolve, 2000));
    } catch (error) {
      console.error(`Failed to test template ${template}:`, error);
    }
  }

  return results;
};
```

Best Practices

Caching Templates

Since templates don’t change frequently, cache the list:Copy

Ask AI

```
class TemplateCache {
  constructor() {
    this.templates = null;
    this.lastFetch = null;
    this.cacheFor = 6 * 60 * 60 * 1000; // 6 hours
  }

  async getTemplates() {
    if (
      this.templates &&
      this.lastFetch &&
      Date.now() - this.lastFetch < this.cacheFor
    ) {
      return this.templates;
    }

    const response = await fetch("https://api.submagic.co/v1/templates", {
      headers: { "x-api-key": process.env.SUBMAGIC_API_KEY },
    });

    const data = await response.json();
    this.templates = data.templates;
    this.lastFetch = Date.now();

    return this.templates;
  }
}
```

Error Responses


401 Unauthorized

object

Copy

Ask AI

```
{
  "error": "UNAUTHORIZED",
  "message": "Invalid or missing API key"
}
```


429 Rate Limited

object

Copy

Ask AI

```
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests",
  "retryAfter": 30
}
```


500 Server Error

object

Copy

Ask AI

```
{
  "error": "INTERNAL_SERVER_ERROR",
  "message": "An unexpected error occurred"
}
```

Default Template

If you don’t specify a `templateName` when creating a project, the system will automatically apply the “Sara” template, which is optimized for general social media content.

Template names are case-sensitive. Make sure to use the exact template name as returned by this endpoint.


# Create Project

Create a new video project using a video URL for AI-powered caption generation

POST

/

v1

/

projects

Try it

Create Project

Create a new video project by providing a video URL. This endpoint will download the video, transcribe the audio, and apply the specified template with AI-generated captions and effects.

This endpoint requires authentication and has a rate limit of 500 requests per hour.

Authentication


x-api-key

string

required

Your Submagic API key starting with `sk-`

Request Body


title

string

required

A descriptive title for your video project (1-100 characters)


language

string

required

Language code for transcription (e.g., “en”, “es”, “fr”). Use the [languages endpoint](https://docs.submagic.co/api-reference/languages) to get available options.


videoUrl

string

required

Public URL to your video file. Must be accessible without authentication and in a supported format.


templateName

string

Template to apply for styling. Use the [templates endpoint](https://docs.submagic.co/api-reference/templates) to get available options. Defaults to “Sara” if not specified. Cannot be used together with `userThemeId`.


userThemeId

string

ID of a custom user theme to apply for styling. Must be a valid UUID of a theme that belongs to you or your team. Cannot be used together with `templateName`. You can find the id of your custom theme by opening a project, selecting the theme, pressing the pen icon to edit it. You’ll see the id of the theme under theme’s name.


webhookUrl

string

URL to receive webhook notifications when processing is complete. Must be a valid HTTPS URL.


dictionary

array

Array of custom words or phrases to improve transcription accuracy (max 100 items, 50 characters each).


magicZooms

boolean

Enable automatic zoom effects on the video to enhance visual engagement. Optional, defaults to false.


magicBrolls

boolean

Enable automatic B-roll insertion to enhance video content with relevant supplementary footage. Optional, defaults to false.


magicBrollsPercentage

number

Percentage of automatic B-rolls to include in the video (0-100). Only effective when magicBrolls is enabled. Optional, defaults to 50.


removeSilencePace

string

Automatically remove silence from the video at the specified pace. Optional. Allowed values: `natural`, `fast`, `extra-fast`. - `extra-fast`: 0.1-0.2 seconds of silence removal - `fast`: 0.2-0.6 seconds of silence removal - `natural`: 0.6+ seconds of silence removal


removeBadTakes

boolean

Automatically detect and remove bad takes and silence from the video using AI analysis. Optional, defaults to false.

Supported Formats & Limits

## Supported Formats

* **MP4** (.mp4) - **MOV** (.mov)

## File Limits

* **Max size:** 2GB - **Max duration:** 2 hours

Response


id

string

Unique identifier for the created project (UUID format)


title

string

The title you provided for the project


language

string

Language code used for transcription


status

string

Current processing status: `processing`, `transcribing`, `exporting`, `completed`, or `failed`


webhookUrl

string

Webhook URL if provided in the request


templateName

string

Template name applied to the project


userThemeId

string

User theme ID applied to the project


magicZooms

boolean

Whether automatic zoom effects are enabled for the video


magicBrolls

boolean

Whether automatic B-roll insertion is enabled for the video


magicBrollsPercentage

number

Percentage of automatic B-rolls to include in the video (0-100)


removeSilencePace

string

Pace setting for automatic silence removal: `natural`, `fast`, or `extra-fast`


removeBadTakes

boolean

Whether automatic bad takes and silence removal is enabled


createdAt

string

ISO 8601 timestamp when the project was created


updatedAt

string

ISO 8601 timestamp when the project was last updated

Custom Dictionary

Improve transcription accuracy by providing custom terms:Copy

Ask AI

```
{
  "dictionary": [
    "Submagic",
    "API endpoint",
    "captions",
    "transcription",
    "AI-powered",
    "webhook notification"
  ]
}
```

**Best practices for dictionary terms:*** Include brand names, product names, or technical terms

* Add words that are frequently mispronounced or misunderstood
* Keep terms under 50 characters each
* Limit to 100 terms per project

Webhook Integration

Receive notifications when your project is complete:Copy

Ask AI

```
{
  "webhookUrl": "https://yoursite.com/webhook/submagic"
}
```

Your webhook endpoint will receive a POST request:Copy

Ask AI

```
{
  "projectId": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "downloadUrl": "https://app.submagic.co/api/file/download?path=3c6cd7cd-3f5e-4def-b662-69c48a7fc8ce/e568c322-7fa5-497a-8fb0-3ba32e9e67d2/364fe092-b68d-468a-9558-bfca7c4d130e-download.mp4&newFileName=ProMotion%20Display%20Breakthrough.mp4",
  "directUrl": "https://dqu1p08d61fh.cloudfront.net/api/9cc52d00-43d7-442f-9a22-050312bkm24f/1ddee5b4-101f-4c1e-a74a-b6b3bcfe206c/video.mp4-download.mp4",
  "timestamp": "2024-01-15T10:45:00.000Z"
}
```

Error Responses


400 Validation Error

object

Copy

Ask AI

```
{
  "error": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "details": [
    {
      "field": "videoUrl",
      "message": "Must be a valid URL",
      "value": "invalid-url"
    }
  ]
}
```


401 Unauthorized

object

Copy

Ask AI

```
{
  "error": "UNAUTHORIZED",
  "message": "Invalid or missing API key"
}
```


429 Rate Limited

object

Copy

Ask AI

```
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests",
  "retryAfter": 30
}
```


500 Server Error

object

Copy

Ask AI

```
{
  "error": "INTERNAL_SERVER_ERROR", 
  "message": "An unexpected error occurred"
}
```



API Reference

# Create Magic Clips

Automatically generate short-form video clips from YouTube videos using AI

POST

/

v1

/

projects

/

magic-clips

Try it

Create Magic Clips

Generate multiple engaging short-form video clips from YouTube videos automatically using AI. This endpoint processes YouTube videos and creates clips with automatic captions, animations, and effects optimized for social media platforms.

This endpoint requires authentication, Magic Clips subscription, and has a rate limit of 500 requests per hour.

Magic Clips created via API use your regular Magic Clips credits, not API credits.

Authentication


x-api-key

string

required

Your Submagic API key starting with `sk-`

Request Body


title

string

required

A descriptive title for your Magic Clips project (1-100 characters)


language

string

required

Language code for captions (2-10 characters, e.g., “en”, “es”, “fr”). Use the [languages endpoint](https://docs.submagic.co/api-reference/languages) to get available options.


youtubeUrl

string

required

Valid YouTube video URL to process for clip generation


webhookUrl

string

URL to receive webhook notifications when processing is complete. Must be a valid HTTPS URL.


userThemeId

string

ID of a custom user theme to apply for styling. Must be a valid UUID of a theme that belongs to you or your team.


minClipLength

number

Minimum clip duration in seconds (15-300 seconds). Defaults to 15 seconds.


maxClipLength

number

Maximum clip duration in seconds (15-300 seconds). Defaults to 60 seconds.

Response


id

string

Unique identifier for the created Magic Clips project (UUID format)


title

string

The title you provided for the project


language

string

Language code used for captions


status

string

Current processing status: `processing`


webhookUrl

string

Webhook URL if provided in the request


createdAt

string

ISO 8601 timestamp when the project was created

Webhook Integration

When processing is complete, a webhook notification will be sent to the provided `webhookUrl` (if specified). The webhook payload includes information about the main project and all generated clips.### 

Webhook Payload Structure

Copy

Ask AI

```
{
  "projectId": "e568c322-7fa5-497a-8fb0-3ba32e9e67d2",
  "status": "completed",
  "title": "YT magic-clips test1",
  "duration": 283,
  "completedAt": "2025-09-24T12:59:24.880Z",
  "magicClips": [
    {
      "id": "364fe092-b68d-468a-9558-bfca7c4d190e",
      "title": "ProMotion Display Breakthrough",
      "duration": 21.04,
      "status": "completed",
      "previewUrl": "https://app.submagic.co/view/364fe092-b68d-468a-9558-bfca7c4d190g",
      "downloadUrl": "https://app.submagic.co/api/file/download?path=3c6cd7cd-3f5e-4def-b662-69c48a7fc8ce/e568c322-7fa5-497a-8fb0-3ba32e9e67d2/364fe092-b68d-468a-9558-bfca7c4d130e-download.mp4&newFileName=ProMotion%20Display%20Breakthrough.mp4",
      "directUrl": "https://dqu1p08d61fh.cloudfront.net/api/9cc52d00-43d7-442f-9a22-050312bkm24f/1ddee5b4-101f-4c1e-a74a-b6b3bcfe206c/video.mp4-download.mp4"
    }
  ]
}
```

Webhook Response Fields


projectId

string

Main project identifier


status

string

Processing status: `completed` or `failed`


title

string

Project title


duration

number

Total duration of the original video in seconds


completedAt

string

ISO 8601 timestamp when processing completed


magicClips

array

Array of generated clips, each containing: - `id`: Unique clip identifier - `title`: AI-generated clip title - `duration`: Clip duration in seconds - `status`: Clip processing status - `previewUrl`: URL to preview the clip - `downloadUrl`: Direct download URL for the clip - `directUrl`: Direct URL that can be embedded on your website or used to play the clip directly

Error Responses


400 Bad Request

object

Copy

Ask AI

```
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid request parameters"
}
```


401 Unauthorized

object

Copy

Ask AI

```
{
  "error": "UNAUTHORIZED",
  "message": "Invalid or missing API key"
}
```


403 Forbidden

object

Copy

Ask AI

```
{
  "error": "FORBIDDEN",
  "message": "Magic Clips subscription required"
}
```


429 Too Many Requests

object

Copy

Ask AI

```
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests",
  "retryAfter": 60
}
```


500 Internal Server Error

object

Copy

Ask AI

```
{
  "error": "INTERNAL_SERVER_ERROR",
  "message": "An unexpected error occurred",
  "details": {}
}
```


# Upload Project

Create a new video project by uploading a video file directly for AI-powered caption generation

POST

/

v1

/

projects

/

upload

Try it

Upload Project

Create a new video project by uploading a video file directly to Submagic. This endpoint accepts multipart/form-data uploads and is ideal for applications where you have video files stored locally or want to upload directly from user devices.

This endpoint requires authentication and has a rate limit of 500 requests per hour due to the resource-intensive nature of file uploads.

Authentication


x-api-key

string

required

Your Submagic API key starting with `sk-`

Request Body (multipart/form-data)


title

string

required

A descriptive title for your video project (1-100 characters)


language

string

required

Language code for transcription (e.g., “en”, “es”, “fr”). Use the [languages endpoint](https://docs.submagic.co/api-reference/languages) to get available options.


file

file

required

Video file to upload. Must be in a supported format and under 2GB.


templateName

string

Template to apply for styling. Use the [templates endpoint](https://docs.submagic.co/api-reference/templates) to get available options. Defaults to “Sara” if not specified. Cannot be used together with `userThemeId`.


userThemeId

string

ID of a custom user theme to apply for styling. Must be a valid UUID of a theme that belongs to you or your team. Cannot be used together with `templateName`. You can find the id of your custom theme by opening a project, selecting the theme, pressing the pen icon to edit it. You’ll see the id of the theme under its name.


webhookUrl

string

URL to receive webhook notifications when processing is complete. Must be a valid HTTPS URL.


dictionary

string

JSON array string of custom words or phrases to improve transcription accuracy (max 100 items, 50 characters each).


magicZooms

string

Enable automatic zoom effects on the video to enhance visual engagement. Pass “true” or “false” as string. Optional, defaults to “false”.


magicBrolls

string

Enable automatic B-roll insertion to enhance video content with relevant supplementary footage. Pass “true” or “false” as string. Optional, defaults to “false”.


magicBrollsPercentage

string

Percentage of automatic B-rolls to include in the video (0-100). Pass as string. Only effective when magicBrolls is enabled. Optional, defaults to “50”.


removeSilencePace

string

Automatically remove silence from the video at the specified pace. Pass as string. Optional. Allowed values: “natural”, “fast”, “extra-fast”. - “extra-fast”: 0.1-0.2 seconds of silence removal - “fast”: 0.2-0.6 seconds of silence removal - “natural”: 0.6+ seconds of silence removal


removeBadTakes

string

Automatically detect and remove bad takes and silence from the video using AI analysis. Pass “true” or “false” as string. Optional, defaults to “false”.

Supported Formats & Limits

## Supported Formats

* **MP4** (.mp4) - **MOV** (.mov)

## File Limits

* **Max size:** 2GB - **Max duration:** 2 hours

Error Responses


400 Validation Error

object

Copy

Ask AI

```
{
  "error": "VALIDATION_ERROR",
  "message": "File validation failed",
  "details": [
    {
      "field": "file",
      "message": "File size exceeds 10GB limit",
      "value": null
    }
  ]
}
```


413 Payload Too Large

object

Copy

Ask AI

```
{
  "error": "PAYLOAD_TOO_LARGE",
  "message": "File size exceeds maximum allowed size"
}
```


415 Unsupported Media Type

object

Copy

Ask AI

```
{
  "error": "UNSUPPORTED_MEDIA_TYPE",
  "message": "Video format not supported"
}
```


# Get Project

Retrieve details of a specific video project including processing status and download links

GET

/

v1

/

projects

/

{id}

Try it

Get Project

Retrieve detailed information about a specific video project, including its current processing status, metadata, and download links when available.

This endpoint requires authentication and has a rate limit of 100 requests per hour.

Authentication


x-api-key

string

required

Your Submagic API key starting with `sk-`

Path Parameters


id

string

required

The unique identifier (UUID) of the project to retrieve

Response


id

string

Unique identifier of the project (UUID format)


title

string

The title of the project


language

string

Language code used for transcription


status

string

Current processing status: `processing`, `transcribing`, `exporting`, `completed`, or `failed`


webhookUrl

string

Webhook URL if provided in the request


templateName

string

Template name applied to the project (if using a built-in template)


userThemeId

string

User theme ID applied to the project (if using a custom theme)


downloadUrl

string

Direct download URL for the processed video (available when status is `completed`)


directUrl

string

Direct URL that can be embedded on your website or used to play the video directly (available when status is `completed`)


previewUrl

string

User-friendly preview page URL where the exported project can be previewed or downloaded: `https://app.submagic.co/view/{projectId}` (available when status is `completed`)


transcriptionStatus

string

Current transcription status: `PROCESSING`, `COMPLETED`, or `FAILED`


failureReason

string

Reason for failure if status is `failed`


magicZooms

boolean

Whether automatic zoom effects are enabled for the video


magicBrolls

boolean

Whether automatic B-roll insertion is enabled for the video


magicBrollsPercentage

number

Percentage of automatic B-rolls to include in the video (0-100)


removeSilencePace

string

Pace setting for automatic silence removal: `natural`, `fast`, or `extra-fast`


removeBadTakes

boolean

Whether automatic bad takes and silence removal is enabled


videoMetaData

object

Video metadata extracted from the source

<details open="" class="expandable mt-4 border-standard rounded-xl" data-testid="undefined-children"><summary class="not-prose text-sm flex flex-row items-center content-center w-full cursor-pointer text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-gray-200 py-3 px-3.5 hover:bg-gray-50/50 dark:hover:bg-white/5 rounded-t-xl list-none [&::-webkit-details-marker]:hidden" aria-controls="Children attributes" aria-expanded="true" data-component-part="expandable-button"><svg class="h-2.5 w-2.5 bg-zinc-400 transition-transform rotate-90"></svg><div class="ml-3 leading-tight text-left"><p class="m-0" contenteditable="false">Hide<span> </span>Video Metadata</p></div></summary>


width

number

Video width in pixels


height

number

Video height in pixels


duration

number

Video duration in seconds


fps

number

Frames per second (optional)

</details>


createdAt

string

ISO 8601 timestamp when the project was created


updatedAt

string

ISO 8601 timestamp when the project was last updated


words

array

Array of transcribed words and silence segments with timing information (available when transcription is completed)

<details open="" class="expandable mt-4 border-standard rounded-xl" data-testid="undefined-children"><summary class="not-prose text-sm flex flex-row items-center content-center w-full cursor-pointer text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-gray-200 py-3 px-3.5 hover:bg-gray-50/50 dark:hover:bg-white/5 rounded-t-xl list-none [&::-webkit-details-marker]:hidden" aria-controls="Children attributes" aria-expanded="true" data-component-part="expandable-button"><svg class="h-2.5 w-2.5 bg-zinc-400 transition-transform rotate-90"></svg><div class="ml-3 leading-tight text-left"><p class="m-0" contenteditable="false">Hide<span> </span>Word Object</p></div></summary>


id

string

Unique identifier for the word or silence segment


text

string

The transcribed text content (empty string for silence segments)


type

string

Type of segment: `word` for spoken words, `silence` for silent periods, or `punctuation` for punctuation marks


startTime

number

Start time of the word/silence in seconds


endTime

number

End time of the word/silence in seconds

</details>


magicClips

array

Array of generated Magic Clips (only present for Magic Clips projects)

<details open="" class="expandable mt-4 border-standard rounded-xl" data-testid="undefined-children"><summary class="not-prose text-sm flex flex-row items-center content-center w-full cursor-pointer text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-gray-200 py-3 px-3.5 hover:bg-gray-50/50 dark:hover:bg-white/5 rounded-t-xl list-none [&::-webkit-details-marker]:hidden" aria-controls="Children attributes" aria-expanded="true" data-component-part="expandable-button"><svg class="h-2.5 w-2.5 bg-zinc-400 transition-transform rotate-90"></svg><div class="ml-3 leading-tight text-left"><p class="m-0" contenteditable="false">Hide<span> </span>Magic Clip Object</p></div></summary>


id

string

Unique identifier for the Magic Clip (UUID format)


title

string

AI-generated title for the clip


duration

number

Duration of the clip in seconds


status

string

Processing status of the clip: `processing`, `completed`, or `failed`


previewUrl

string

URL to preview the Magic Clip (available when status is `completed`)


downloadUrl

string

Direct download URL for the Magic Clip (available when status is `completed`)


directUrl

string

Direct URL that can be embedded on your website or used to play the Magic Clip directly (available when status is `completed`)

</details>

[Upload Project](https://docs.submagic.co/api-reference/upload-project)[Update Project](https://docs.submagic.co/api-reference/update-project)

[ ]

[Powered by Mintlify](https://www.mintlify.com/?utm_campaign=poweredBy&utm_medium=referral&utm_source=submagic)

Get Project - Submagic API


# Update Project

Update an existing video project with new settings, features, or media insertions

PUT

/

v1

/

projects

/

{id}

Try it

Update Project

Update an existing video project with new settings, AI features, or user media (B-roll) insertions. This endpoint allows you to modify project parameters and enhance your video with additional features or custom media content from your library.

This endpoint requires authentication and has a rate limit of 100 requests per hour. After modifying a video, you’ll need to re-export to see the changes using the export endpoint. When using `removeBadTakes`, the response may take 1-2 minutes as our AI processes the video.

Authentication


x-api-key

string

required

Your Submagic API key starting with `sk-`

Path Parameters


id

string

required

The unique identifier (UUID) of the project to update

Request Body

All fields are optional. Only provide the fields you want to update. If a field is provided with a different value from the current project settings, it will be updated.

removeSilencePace

string

Automatically remove silence from the video at the specified pace. Allowed values: `natural`, `fast`, `extra-fast`. - `extra-fast`: 0.1-0.2 seconds of silence removal - `fast`: 0.2-0.6 seconds of silence removal - `natural`: 0.6+ seconds of silence removal


removeBadTakes

boolean

Automatically detect and remove bad takes and silence from the video using AI analysis. **Note: This process may take 1-2 minutes to complete.**


items

array

Array of user media items to insert into the video

<details open="" class="expandable mt-4 border-standard rounded-xl" data-testid="undefined-children"><summary class="not-prose text-sm flex flex-row items-center content-center w-full cursor-pointer text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-gray-200 py-3 px-3.5 hover:bg-gray-50/50 dark:hover:bg-white/5 rounded-t-xl list-none [&::-webkit-details-marker]:hidden" aria-controls="Children attributes" aria-expanded="true" data-component-part="expandable-button"><svg class="h-2.5 w-2.5 bg-zinc-400 transition-transform rotate-90"></svg><div class="ml-3 leading-tight text-left"><p class="m-0" contenteditable="false">Hide<span> </span>Item Object</p></div></summary>


startTime

number

required

Start time in seconds where the user media should begin (must be ≥ 0)


endTime

number

required

End time in seconds where the user media should end (must be greater than startTime)


userMediaId

string

required

UUID of the user media from your library. You can find this ID in the editor’s ‘B-roll’ tab → ‘My videos’ section under each video.

</details>

Finding User Media ID

To find your `userMediaId`:1. Go to the Submagic editor

1. Navigate to the **‘B-roll’** tab
2. Add a B-roll to access your media library
3. Go to the **‘My videos’** tab
4. Each video will display its unique media ID that you can use with this API

![Example.png](https://mintcdn.com/submagic/eEPiypbnZT0UxgbH/images/Example.png?fit=max&auto=format&n=eEPiypbnZT0UxgbH&q=85&s=34f0653da7f63c569ba15cf48d679871)## 

Response


message

string

Success message confirming the project update


id

string

The unique identifier of the updated project


status

string

Updated processing status of the project

Error Responses


error

string

Error code: `NOT_FOUND` or `VALIDATION_ERROR`


message

string

Detailed error message explaining what went wrong

**Important:** After updating a project, you must re-export the project to see the changes in the final video. Use the export endpoint to generate the updated video with your modifications. **Processing Time:** When using `removeBadTakes`, the API response may take 1-2 minutes as our AI analyzes and processes the video to detect and remove bad takes and silence.


# Export Project

Trigger the rendering/export process for a completed project to generate the final video

POST

/

v1

/

projects

/

{id}

/

export

Try it

Export Project

Triggers the rendering/export process for a completed project. This starts the video generation process asynchronously with customizable output parameters.

This endpoint requires authentication and has enhanced rate limits for API-generated projects. The export process is asynchronous - use webhooks or polling to track completion.

Authentication


x-api-key

string

required

Your Submagic API key starting with `sk-`

Path Parameters


id

string

required

The unique identifier (UUID) of the project to export

Request Body (Optional)

All parameters are optional. If not provided, the system uses optimal defaults based on the project’s original video metadata.

fps

number

Frames per second for the exported video (1-60). Defaults to project’s original fps or 30.


width

number

Video width in pixels (100-4000). Defaults to project’s original width or 1080.


height

number

Video height in pixels (100-4000). Defaults to project’s original height or 1920.


webhookUrl

string

URL to receive notification when export is complete. Must be a valid URL format.

Prerequisites

Before exporting a project, ensure:*  **Project is transcribed** : Must have words data available

* **Project is not uploading** : Cannot be in “uploading” status
* **Project ownership** : Must belong to the authenticated user
* **API-generated project** : Must be created via API

Response


message

string

Success message confirming the export has started


projectId

string

The unique identifier of the project being exported


status

string

Current status of the project after export trigger

Error Responses


error

string

Error code: `NOT_FOUND`, `BAD_REQUEST`, or `INTERNAL_SERVER_ERROR`


message

string

Detailed error message explaining the issue

Webhook Notifications

If you provide a `webhookUrl`, the system will send a POST request to your URL when export completes, including export details and download URL in the notification.## 

Export Status Tracking

After triggering an export:1.  **Monitor Progress** : Call `GET /v1/projects/{id}` to check export progress

1. **Check Download URL** : The `downloadUrl` and `directUrl` fields will be populated once rendering is complete

 **Tip** : After triggering an export, use the [Get Project](https://docs.submagic.co/api-reference/get-project) endpoint to monitor the export progress. The `downloadUrl` and `directUrl` fields will be populated once the rendering is complete.

 **Important** : The export process is asynchronous. The API will return immediately after starting the export, but the actual video rendering happens in the background. Use webhooks or polling to track completion status.

[](https://docs.submagic.co/api-reference/update-project)
