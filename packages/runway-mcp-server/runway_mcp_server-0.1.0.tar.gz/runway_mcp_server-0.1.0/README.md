# 🎬 Runway MCP Server

<!-- mcp-name: io.github.sidart10/runway-mcp-server -->

A Model Context Protocol (MCP) server for **Runway AI** - featuring Gen-4 models, Aleph video editing, and comprehensive video generation tools.

**MCP Registry Name:** `io.github.sidart10/runway-mcp-server`

## ✨ Features

- **🎥 Aleph Video Editing** - Add/remove objects, change camera angles, transform lighting
- **🎨 Gen-4 Image Generation** - High-fidelity images with reference support
- **📹 Gen-4 Video Generation** - Text-to-video, image-to-video, keyframe control
- **🎭 Advanced Tools** - Video extension, 4K upscaling, style transfer

## 📦 Installation

> **⚠️ Note:** The root-level `runway_mcp_server.py` file is kept for backward compatibility. New installations should use the PyPI package below.

### Option 1: Install from PyPI (Recommended)

```bash
# Install with uvx (automatically manages dependencies)
uvx runway-mcp-server

# Or install globally with pip
pip install runway-mcp-server
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/sidart10/runway-mcp-server.git
cd runway-mcp-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux (or venv\Scripts\activate on Windows)

# Install in development mode
pip install -e .
```

## 🚀 Quick Start

### 1. Configure API Key

Create a `.env` file in the project root:

```bash
# .env file
RUNWAY_API_KEY=your_api_key_here
```

Get your API key from [dev.runwayml.com](https://dev.runwayml.com)

### 2. Add to MCP Config

**For Cursor:** Edit `~/.cursor/mcp.json`

**For Claude Desktop:** Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "runway": {
      "command": "uvx",
      "args": ["runway-mcp-server"],
      "env": {
        "RUNWAY_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Note:** Replace `your_api_key_here` with your actual Runway API key from [dev.runwayml.com](https://dev.runwayml.com)

### 3. Restart Your Client

Restart Cursor or Claude Desktop to load the server.

## 🛠️ Available Tools

| Tool | Description |
|------|-------------|
| `generate_image_gen4` | Create high-quality images with Gen-4 |
| `generate_video_text_to_video` | Generate videos from text descriptions |
| `generate_video_image_to_video` | Animate images with motion |
| `generate_video_first_last_frame` | Precise start/end frame control |
| `edit_video_with_aleph` | ⭐ Advanced video editing & transformation |
| `restyle_video` | Apply artistic styles to videos |
| `extend_video` | Extend videos by 5-10 seconds |
| `upscale_video_4k` | Upscale to 4K resolution |
| `get_task_status` | Check generation progress |
| `cancel_task` | Cancel running tasks |
| `list_available_models` | List all available models |
| `get_api_info` | Server configuration info |

## 📚 Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get running in 5 minutes
- **[Aleph Guide](docs/ALEPH_GUIDE.md)** - Video editing deep dive
- **[Features Guide](docs/FEATURES.md)** - All capabilities explained
- **[Architecture](docs/ARCHITECTURE.md)** - Technical details
- **[Examples](examples/)** - Working code samples

## 📁 Project Structure

```
runway-mcp-server/
├── runway_mcp_server.py    # Main server code
├── requirements.txt         # Python dependencies
├── .env                     # API key (create this)
├── README.md               # This file
├── .gitignore              # Git ignore rules
├── venv/                   # Virtual environment
├── docs/                   # Documentation
│   ├── QUICKSTART.md
│   ├── ALEPH_GUIDE.md
│   ├── FEATURES.md
│   ├── ARCHITECTURE.md
│   └── ...
├── examples/               # Code examples
│   └── example_usage.py
└── config/                 # Configuration templates
    └── mcp_config_example.json
```

## 💡 Usage Examples

### Generate a Video
```
"Generate a 10-second video of an eagle soaring over mountains at sunset"
```

### Edit with Aleph
```
"Edit this video to remove the person in the background: [video URL]"
```

### Create an Image
```
"Create a Gen-4 image of a futuristic cyberpunk city at night, 1920x1080"
```

## 🔒 Rate Limits

- API calls are rate-limited based on your Runway plan
- Gen-4 Turbo: ~5 credits per second
- Aleph editing: ~15 credits per second
- Check usage at [dev.runwayml.com](https://dev.runwayml.com)

## 🐛 Troubleshooting

**API Key Not Loading:**
```bash
# Verify .env file exists
ls -la .env

# Check if key loads
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅' if os.getenv('RUNWAY_API_KEY') else '❌')"
```

**Server Won't Start:**
- Ensure Python 3.10+ is installed: `python3 --version`
- Verify virtual environment is activated
- Check all dependencies installed: `pip list`

**Task Timeouts:**
- Video generation takes 2-10 minutes depending on length
- Use `get_task_status()` to check progress
- Increase wait time if needed

## 🤝 Contributing

This is an MCP server implementation following the Model Context Protocol specification.

## 📄 License

This MCP server is provided as-is for use with the Runway API. Runway API usage is subject to [Runway's terms of service](https://runwayml.com/terms).

## 🔗 Resources

- **Runway Developer Portal**: [dev.runwayml.com](https://dev.runwayml.com)
- **API Documentation**: [docs.dev.runwayml.com](https://docs.dev.runwayml.com)
- **MCP Specification**: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **Help Center**: [help.runwayml.com](https://help.runwayml.com)

---

**Built for the Runway AI community** 🚀

For issues or questions, refer to the [Runway Developer Portal](https://dev.runwayml.com) or check the [documentation](docs/).
