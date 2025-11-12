"""
Runway MCP Server - AI Video Generation & Editing
Comprehensive MCP server for Runway ML featuring Gen-4, Veo 3, Aleph video editing, and more
"""

# Package metadata - this helps Python identify your package
__version__ = "0.1.0"
__author__ = "Sid"
__description__ = "MCP server for Runway ML video generation with Gen-4, Veo, and Aleph support"

# Import the main server components so they can be accessed as:
# from runway_mcp_server import mcp, main
from .server import mcp, main

# This tells Python what to export when someone does: from runway_mcp_server import *
__all__ = ["mcp", "main", "__version__"]

