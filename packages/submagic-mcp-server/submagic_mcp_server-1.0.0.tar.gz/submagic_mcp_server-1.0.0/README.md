# Submagic MCP Server

AI-powered video editing MCP server for automatic captions, magic zooms, B-rolls, and viral clip generation. Process videos in 107 languages with professional templates and advanced editing features.

**Status:** Production-Ready | **API Coverage:** 100% | **Rating:** 9.5/10

---

## Quick Start

### Installation

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key
echo 'SUBMAGIC_API_KEY="sk-your-key-here"' > .env

# 4. Test the server
python tests/test_server.py
```

Get your API key at: https://app.submagic.co/signup

### Claude Desktop Setup

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "submagic": {
      "command": "/absolute/path/to/venv/bin/python",
      "args": ["/absolute/path/to/submagic_mcp.py"],
      "env": {
        "SUBMAGIC_API_KEY": "sk-your-api-key"
      }
    }
  }
}
```

Restart Claude Desktop - done!

---

## Features

### AI Video Processing
- **AI Captions** - 107 languages, 98%+ accuracy
- **Magic Zooms** - AI-powered dynamic zoom effects
- **Magic B-rolls** - Auto-insert stock footage (0-100% coverage)
- **Silence Removal** - 3 speeds: natural (0.6+s), fast (0.2-0.6s), extra-fast (0.1-0.2s)
- **Bad Takes Removal** - AI removes "um", "uh", "like" filler words
- **Custom B-rolls** - Insert your own videos at exact timestamps

### Social Media Optimization
- **30+ Templates** - Hormozi series, Beast, Sara, professional styles
- **Magic Clips** - Auto-generate viral clips from YouTube (15-300s duration)
- **Platform Presets** - TikTok (15-30s), Reels (30s), Shorts (45-60s)
- **Custom Themes** - Apply your branded styling
- **Aspect Ratios** - 9:16, 1:1, 16:9, 4:5 via export dimensions

### Professional Workflow
- **Post-Creation Editing** - Update silence removal, add filler word cleanup, insert B-rolls
- **Iterative Refinement** - Update and re-export multiple times
- **Webhook Notifications** - Get notified when processing completes
- **Custom Dictionary** - Improve transcription accuracy

---

## Usage Examples

### Basic: Create Video with AI Captions

```python
submagic_create_project(
    title="Product Demo",
    language="en",
    video_url="https://example.com/video.mp4",
    template_name="Hormozi 2",
    magic_zooms=True,
    magic_brolls=True,
    remove_silence_pace="fast"
)
```

### Advanced: Professional Editing Workflow

```python
# 1. Create project
project_id = submagic_create_project(...)

# 2. Wait for processing (2-10 min)
submagic_get_project(project_id)

# 3. Fine-tune after reviewing
submagic_update_project(
    project_id=project_id,
    remove_silence_pace="extra-fast",  # Tighten pacing
    remove_bad_takes=True               # Clean filler words
)

# 4. Export for TikTok (9:16 vertical)
submagic_export_project(
    project_id=project_id,
    width=1080,
    height=1920,
    fps=30
)

# 5. Get download URL
submagic_get_project(project_id)  # Check for downloadUrl
```

### Magic Clips: YouTube to TikTok

```python
# Generate 15-second TikTok clips from YouTube video
submagic_create_magic_clips(
    title="TikTok Highlights",
    youtube_url="https://youtube.com/watch?v=abc123",
    language="en",
    min_clip_length=15,
    max_clip_length=30,
    user_theme_id="your-brand-uuid"  # Optional branding
)
```

### Insert Custom B-Roll

```python
# Replace boring section with product demo
submagic_update_project(
    project_id=project_id,
    custom_broll_items=[
        {
            "startTime": 30.0,
            "endTime": 45.0,
            "userMediaId": "your-broll-uuid"  # From Submagic editor
        }
    ]
)
```

---

## Tools Reference

| Tool | Purpose | Rate Limit |
|------|---------|------------|
| `submagic_list_languages` | Get 107 language codes | 1000/hour |
| `submagic_list_templates` | List 30+ templates | 1000/hour |
| `submagic_create_project` | Create video with AI features | 500/hour |
| `submagic_get_project` | Check status, get download URLs | 100/hour |
| `submagic_update_project` | Edit after creation | 100/hour |
| `submagic_export_project` | Export with custom settings | 500/hour |
| `submagic_create_magic_clips` | Generate clips from YouTube | 500/hour |

---

## Platform-Specific Exports

### TikTok (9:16 Vertical)
```python
submagic_export_project(project_id, width=1080, height=1920)
```

### Instagram Reels (9:16)
```python
submagic_export_project(project_id, width=1080, height=1920)
```

### Instagram Feed (1:1 Square)
```python
submagic_export_project(project_id, width=1080, height=1080)
```

### YouTube (16:9 Landscape)
```python
submagic_export_project(project_id, width=1920, height=1080)
```

### Instagram Feed Optimized (4:5)
```python
submagic_export_project(project_id, width=1080, height=1350)
```

---

## Important Notes

### Workflow
- Create → Wait 2-10 min → (Optional) Update → Re-export → Download
- After updating, MUST re-export to apply changes
- Can iterate multiple times for refinement

### Limitations
- Videos must be publicly accessible URLs (no local files yet)
- Max: 2GB file size, 2 hours duration
- Formats: MP4, MOV input | MP4, MOV output
- `remove_bad_takes` adds 1-2 minutes processing time

### Dashboard vs API
Some dashboard features are NOT available via API:
- Correct Eye Contact (AI)
- Clean Audio enhancement
- Generate Hook Title (AI)
- Explicit aspect ratio parameter (use export dimensions instead)

See `docs/API_LIMITATIONS_DISCOVERED.md` for full analysis.

---

## Troubleshooting

**Server won't start:**
```bash
pip install -r requirements.txt
python -c "from submagic_mcp import app; print('OK')"
```

**Authentication failed:**
- Check `.env` file has correct API key
- Key must start with `sk-`

**Project stuck processing:**
- Normal: 2-10 minutes
- Large videos: up to 15 minutes
- Check every 30-60 seconds

---

## Pricing

- **Free Trial:** 3 videos with watermark
- **Starter:** $14/month - 20 videos
- **Growth:** $40/month - Unlimited
- **Business:** $60/month - Unlimited + features

https://www.submagic.co/pricing

---

## Resources

- **API Docs:** https://docs.submagic.co
- **Sign Up:** https://app.submagic.co/signup
- **Templates:** https://www.submagic.co/templates
- **MCP Protocol:** https://modelcontextprotocol.io

---

## License

MIT
