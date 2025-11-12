"""
Runway MCP Server - Comprehensive AI Video Generation & Editing
Supports all latest Runway features including Gen-4, Aleph video editing, Act-One, and more
"""

import os
import json
import time
import asyncio
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env file
# This reads your .env file and makes the variables available to the program
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("Runway AI Video Generation")

# Configuration
# Check for both uppercase and lowercase versions of the API key
# This way it works with either "RUNWAY_API_KEY" or "runway_api_key" in your .env file
RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY") or os.getenv("runway_api_key") or ""
RUNWAY_API_BASE = "https://api.dev.runwayml.com/v1"  # Development API endpoint
RUNWAY_API_VERSION = "2024-11-06"

# Type definitions
# Updated with correct API model names from Runway docs (Nov 2024)
VideoRatio = Literal["1280:720", "720:1280", "1104:832", "832:1104", "960:960", "1584:672"]
ImageRatio = Literal["1920:1080", "1080:1920", "1024:1024"]
TextToVideoModel = Literal["veo3.1", "veo3.1_fast", "veo3"]  # For text_to_video endpoint
ImageToVideoModel = Literal["gen4_turbo", "gen3a_turbo", "veo3.1", "veo3.1_fast", "veo3"]  # For image_to_video
VideoEditingModel = Literal["gen4_aleph"]  # For video_to_video (Aleph)
ImageModel = Literal["gen4_image", "gen4_image_turbo"]
Duration = Literal[4, 6, 8]  # Valid durations for Veo models


class RunwayAPIClient:
    """HTTP client for Runway API with authentication and error handling"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = RUNWAY_API_BASE
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "X-Runway-Version": RUNWAY_API_VERSION,
            "Content-Type": "application/json"
        }
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated API request"""
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
    
    async def create_task(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new generation task"""
        return await self._request("POST", endpoint, json=data)
    
    async def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get task status and results"""
        return await self._request("GET", f"/tasks/{task_id}")
    
    async def wait_for_task(
        self, 
        task_id: str, 
        max_wait: int = 300,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """Wait for task completion with polling"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            task = await self.get_task(task_id)
            status = task.get("status")
            
            if status == "SUCCEEDED":
                return task
            elif status == "FAILED":
                raise Exception(f"Task failed: {task.get('failure', 'Unknown error')}")
            elif status in ["CANCELLED", "EXPIRED"]:
                raise Exception(f"Task {status.lower()}")
            
            await asyncio.sleep(poll_interval)
        
        raise TimeoutError(f"Task did not complete within {max_wait} seconds")


def get_client() -> RunwayAPIClient:
    """Get authenticated Runway API client"""
    if not RUNWAY_API_KEY:
        raise ValueError("RUNWAY_API_KEY environment variable not set")
    return RunwayAPIClient(RUNWAY_API_KEY)


# ============================================================================
# GEN-4 IMAGE GENERATION
# ============================================================================

@mcp.tool()
async def generate_image_gen4(
    prompt_text: str,
    model: ImageModel = "gen4_image",
    ratio: ImageRatio = "1920:1080",
    reference_images: Optional[List[Dict[str, str]]] = None,
    seed: Optional[int] = None,
    wait_for_completion: bool = True
) -> str:
    """
    Generate high-quality images using Gen-4 Image models with reference image support.
    
    Gen-4 Image provides unprecedented stylistic control and visual fidelity.
    Supports reference images with tags for consistent characters, locations, and styles.
    
    Args:
        prompt_text: Text description of the image to generate. Use @tags to reference images.
        model: Model to use - gen4_image (high quality) or gen4_image_turbo (faster)
        ratio: Image aspect ratio (1920:1080, 1080:1920, 1024:1024)
        reference_images: List of reference images with uri and tag fields
            Example: [{"uri": "https://...", "tag": "Character"}]
        seed: Random seed for reproducible results
        wait_for_completion: Wait for task to complete before returning
    
    Returns:
        Task result with image URL or task ID if not waiting
    
    Example:
        generate_image_gen4(
            prompt_text="@Hero standing on a mountaintop at sunset",
            reference_images=[{"uri": "https://example.com/hero.jpg", "tag": "Hero"}]
        )
    """
    client = get_client()
    
    data = {
        "model": model,
        "promptText": prompt_text,
        "ratio": ratio
    }
    
    if reference_images:
        data["referenceImages"] = reference_images
    if seed is not None:
        data["seed"] = seed
    
    task = await client.create_task("/images", data)
    task_id = task["id"]
    
    if wait_for_completion:
        result = await client.wait_for_task(task_id)
        return json.dumps({
            "status": "success",
            "image_url": result["output"][0] if result.get("output") else None,
            "task_id": task_id,
            "model": model
        }, indent=2)
    
    return json.dumps({"task_id": task_id, "status": "processing"}, indent=2)


# ============================================================================
# GEN-4 VIDEO GENERATION - TEXT TO VIDEO
# ============================================================================

@mcp.tool()
async def generate_video_text_to_video(
    prompt_text: str,
    model: TextToVideoModel = "veo3.1",
    ratio: VideoRatio = "1280:720",
    duration: Duration = 4,
    wait_for_completion: bool = True
) -> str:
    """
    Generate videos from text descriptions using Google's Veo 3 models.
    
    Veo 3.1 provides high-quality cinematic video generation from text prompts.
    Produces realistic videos with excellent motion, consistency, and understanding.
    
    Args:
        prompt_text: Detailed text description of the video to generate (max 1000 characters)
        model: Video model to use:
            - veo3.1: High quality, best results
            - veo3.1_fast: Faster generation with good quality
            - veo3: Standard quality
        ratio: Video aspect ratio (1280:720, 720:1280, 1104:832, 832:1104, 960:960, 1584:672)
        duration: Video length in seconds (4, 6, or 8)
        wait_for_completion: Wait for generation to complete
    
    Returns:
        Task result with video URL or task ID
    
    Example:
        generate_video_text_to_video(
            prompt_text="A golden retriever and orange cat sitting together on a cozy couch, warm lighting, cinematic shot",
            duration=6,
            model="veo3.1"
        )
    """
    client = get_client()
    
    # Build request data according to Runway API docs
    data = {
        "model": model,
        "promptText": prompt_text,
        "ratio": ratio,
        "duration": duration
    }
    
    task = await client.create_task("/text_to_video", data)
    task_id = task["id"]
    
    if wait_for_completion:
        result = await client.wait_for_task(task_id, max_wait=600)
        return json.dumps({
            "status": "success",
            "video_url": result["output"][0] if result.get("output") else None,
            "task_id": task_id,
            "model": model,
            "duration": duration
        }, indent=2)
    
    return json.dumps({"task_id": task_id, "status": "processing"}, indent=2)


# ============================================================================
# GEN-4 IMAGE TO VIDEO
# ============================================================================

@mcp.tool()
async def generate_video_image_to_video(
    prompt_image: str,
    prompt_text: Optional[str] = None,
    model: ImageToVideoModel = "gen4_turbo",
    ratio: VideoRatio = "1280:720",
    duration: int = 5,
    seed: Optional[int] = None,
    wait_for_completion: bool = True
) -> str:
    """
    Generate videos from images using Gen-4, Gen-3, or Veo models.
    
    Transform static images into dynamic videos. Supports multiple models for different
    quality/speed tradeoffs.
    
    Args:
        prompt_image: URL or base64 data URI of the input image
        prompt_text: Optional text prompt for additional guidance (max 1000 characters)
        model: Video model to use (gen4_turbo, gen3a_turbo, veo3.1, veo3.1_fast, veo3)
        ratio: Video aspect ratio
        duration: Video length in seconds (2-10)
        seed: Random seed for reproducibility
        wait_for_completion: Wait for completion
    
    Returns:
        Task result with video URL
    
    Example:
        generate_video_image_to_video(
            prompt_image="https://example.com/sunset.jpg",
            prompt_text="Time-lapse of clouds moving across the sky",
            duration=6
        )
    """
    client = get_client()
    
    # Build request according to Runway API docs
    data = {
        "model": model,
        "promptImage": prompt_image,
        "ratio": ratio,
        "duration": duration
    }
    
    if prompt_text:
        data["promptText"] = prompt_text
    if seed is not None:
        data["seed"] = seed
    
    task = await client.create_task("/image_to_video", data)
    task_id = task["id"]
    
    if wait_for_completion:
        result = await client.wait_for_task(task_id, max_wait=600)
        return json.dumps({
            "status": "success",
            "video_url": result["output"][0] if result.get("output") else None,
            "task_id": task_id,
            "model": model
        }, indent=2)
    
    return json.dumps({"task_id": task_id, "status": "processing"}, indent=2)


# ============================================================================
# FIRST-LAST FRAME TO VIDEO
# ============================================================================

@mcp.tool()
async def generate_video_first_last_frame(
    first_frame: str,
    last_frame: str,
    prompt_text: Optional[str] = None,
    model: ImageToVideoModel = "gen3a_turbo",
    ratio: VideoRatio = "1280:720",
    duration: int = 5,
    seed: Optional[int] = None,
    wait_for_completion: bool = True
) -> str:
    """
    Generate video with precise control over first and last frames.
    
    Create smooth transitions between two frames with AI-generated motion.
    Perfect for precise storytelling and controlled animations.
    
    Args:
        first_frame: URL or data URI of the first frame
        last_frame: URL or data URI of the last frame
        prompt_text: Optional guidance for the transition
        model: Video model to use
        ratio: Video aspect ratio
        duration: Video length in seconds
        seed: Random seed
        wait_for_completion: Wait for completion
    
    Returns:
        Task result with video URL
    """
    client = get_client()
    
    data = {
        "model": model,
        "firstFrame": first_frame,
        "lastFrame": last_frame,
        "ratio": ratio,
        "duration": duration
    }
    
    if prompt_text:
        data["promptText"] = prompt_text
    if seed is not None:
        data["seed"] = seed
    
    task = await client.create_task("/first_last_frame_to_video", data)
    task_id = task["id"]
    
    if wait_for_completion:
        result = await client.wait_for_task(task_id, max_wait=600)
        return json.dumps({
            "status": "success",
            "video_url": result["output"][0] if result.get("output") else None,
            "task_id": task_id
        }, indent=2)
    
    return json.dumps({"task_id": task_id, "status": "processing"}, indent=2)


# ============================================================================
# VIDEO TO VIDEO WITH ALEPH (Video Editing)
# ============================================================================

@mcp.tool()
async def edit_video_with_aleph(
    input_video: str,
    prompt_text: str,
    ratio: VideoRatio = "1280:720",
    reference_image: Optional[str] = None,
    seed: Optional[int] = None,
    wait_for_completion: bool = True
) -> str:
    """
    ⭐ ALEPH VIDEO EDITING - Transform and edit existing videos with AI ⭐
    
    Runway Gen-4 Aleph is the most advanced video editing model, enabling:
    - Add, remove, or replace objects in videos
    - Change camera angles and generate novel views
    - Transform lighting, style, and environments
    - Generate next shots and shot continuations
    - Restyle videos with reference images
    
    This is Runway's breakthrough video-to-video editing technology!
    
    Args:
        input_video: URL or data URI of the input video to edit
        prompt_text: Editing instruction (max 1000 characters)
            Examples: "Add fireworks to the sky", "Remove the car from the scene",
            "Change to nighttime lighting"
        ratio: Video aspect ratio for output
        reference_image: Optional reference image for style/lighting guidance
        seed: Random seed for reproducibility
        wait_for_completion: Wait for processing to complete
    
    Returns:
        Task result with edited video URL
    
    Examples:
        # Remove objects
        edit_video_with_aleph(
            input_video="https://example.com/video.mp4",
            prompt_text="Remove all people from the scene"
        )
        
        # Add elements
        edit_video_with_aleph(
            input_video="https://example.com/video.mp4",
            prompt_text="Add fireworks exploding in the night sky"
        )
        
        # Change camera angle
        edit_video_with_aleph(
            input_video="https://example.com/video.mp4",
            prompt_text="Generate a reverse angle shot of this scene"
        )
        
        # Style transfer with reference
        edit_video_with_aleph(
            input_video="https://example.com/video.mp4",
            prompt_text="Restyle the video using the aesthetic from the reference image",
            reference_image="https://example.com/style.jpg"
        )
    """
    client = get_client()
    
    # Build request according to Runway API docs for gen4_aleph
    data = {
        "model": "gen4_aleph",  # Only model supported for video_to_video
        "videoUri": input_video,
        "promptText": prompt_text,
        "ratio": ratio
    }
    
    # Add optional reference image for style guidance
    if reference_image:
        data["references"] = [{"type": "image", "uri": reference_image}]
    if seed is not None:
        data["seed"] = seed
    
    # Aleph uses video-to-video endpoint
    task = await client.create_task("/video_to_video", data)
    task_id = task["id"]
    
    if wait_for_completion:
        result = await client.wait_for_task(task_id, max_wait=600)
        return json.dumps({
            "status": "success",
            "edited_video_url": result["output"][0] if result.get("output") else None,
            "task_id": task_id,
            "model": "gen4_aleph",
            "prompt": prompt_text
        }, indent=2)
    
    return json.dumps({"task_id": task_id, "status": "processing"}, indent=2)


# ============================================================================
# VIDEO TO VIDEO - STYLE TRANSFER
# ============================================================================

@mcp.tool()
async def restyle_video(
    input_video: str,
    style_prompt: Optional[str] = None,
    style_image: Optional[str] = None,
    model: ImageToVideoModel = "gen3a_turbo",
    duration: int = 10,
    structure_transformation: float = 0.5,
    seed: Optional[int] = None,
    wait_for_completion: bool = True
) -> str:
    """
    Restyle existing videos with new aesthetic styles using Gen-3 models.
    
    Transform the visual style of your videos while preserving motion and structure.
    Use text prompts, reference images, or both for style guidance.
    
    Args:
        input_video: URL of the input video to restyle
        style_prompt: Text description of desired style
        style_image: Optional reference image for style transfer
        model: Video model (gen3a_turbo or gen3_alpha)
        duration: Video duration (up to 20s for Gen-3)
        structure_transformation: How much to transform structure (0.0-1.0)
        seed: Random seed
        wait_for_completion: Wait for completion
    
    Returns:
        Task result with restyled video URL
    
    Example:
        restyle_video(
            input_video="https://example.com/video.mp4",
            style_prompt="Transform to a vibrant watercolor painting style",
            structure_transformation=0.3
        )
    """
    client = get_client()
    
    data = {
        "model": model,
        "promptVideo": input_video,
        "duration": min(duration, 20)  # Gen-3 supports up to 20s
    }
    
    if style_prompt:
        data["promptText"] = style_prompt
    if style_image:
        data["promptImage"] = style_image
    if structure_transformation is not None:
        data["structureTransformation"] = structure_transformation
    if seed is not None:
        data["seed"] = seed
    
    task = await client.create_task("/video_to_video", data)
    task_id = task["id"]
    
    if wait_for_completion:
        result = await client.wait_for_task(task_id, max_wait=600)
        return json.dumps({
            "status": "success",
            "video_url": result["output"][0] if result.get("output") else None,
            "task_id": task_id,
            "style": style_prompt or "image-based"
        }, indent=2)
    
    return json.dumps({"task_id": task_id, "status": "processing"}, indent=2)


# ============================================================================
# VIDEO EXTENSION
# ============================================================================

@mcp.tool()
async def extend_video(
    input_video: str,
    extension_duration: Literal[5, 10] = 10,
    prompt_text: Optional[str] = None,
    seed: Optional[int] = None,
    wait_for_completion: bool = True
) -> str:
    """
    Extend videos by generating continuation footage (Gen-3 feature).
    
    Seamlessly extend your videos by 5 or 10 seconds, creating up to 40s total.
    The AI continues the motion and action naturally.
    
    Args:
        input_video: URL of the video to extend
        extension_duration: How many seconds to add (5 or 10)
        prompt_text: Optional guidance for the extension
        seed: Random seed
        wait_for_completion: Wait for completion
    
    Returns:
        Task result with extended video URL
    """
    client = get_client()
    
    data = {
        "promptVideo": input_video,
        "duration": extension_duration
    }
    
    if prompt_text:
        data["promptText"] = prompt_text
    if seed is not None:
        data["seed"] = seed
    
    task = await client.create_task("/extend_video", data)
    task_id = task["id"]
    
    if wait_for_completion:
        result = await client.wait_for_task(task_id, max_wait=600)
        return json.dumps({
            "status": "success",
            "extended_video_url": result["output"][0] if result.get("output") else None,
            "task_id": task_id,
            "extension_seconds": extension_duration
        }, indent=2)
    
    return json.dumps({"task_id": task_id, "status": "processing"}, indent=2)


# ============================================================================
# UPSCALE TO 4K
# ============================================================================

@mcp.tool()
async def upscale_video_4k(
    input_video: str,
    wait_for_completion: bool = True
) -> str:
    """
    Upscale videos to 4K resolution for production-ready quality.
    
    Enhanced detail and clarity for professional outputs. Available for Gen-3 videos.
    
    Args:
        input_video: URL of the video to upscale
        wait_for_completion: Wait for upscaling to complete
    
    Returns:
        Task result with 4K video URL
    """
    client = get_client()
    
    data = {
        "promptVideo": input_video
    }
    
    task = await client.create_task("/upscale", data)
    task_id = task["id"]
    
    if wait_for_completion:
        result = await client.wait_for_task(task_id, max_wait=600)
        return json.dumps({
            "status": "success",
            "upscaled_video_url": result["output"][0] if result.get("output") else None,
            "task_id": task_id,
            "resolution": "4K"
        }, indent=2)
    
    return json.dumps({"task_id": task_id, "status": "processing"}, indent=2)


# ============================================================================
# TASK MANAGEMENT
# ============================================================================

@mcp.tool()
async def get_task_status(task_id: str) -> str:
    """
    Check the status of any Runway generation task.
    
    Args:
        task_id: The task ID returned from any generation function
    
    Returns:
        Current task status and output if completed
    """
    client = get_client()
    task = await client.get_task(task_id)
    
    return json.dumps({
        "task_id": task_id,
        "status": task.get("status"),
        "progress": task.get("progress"),
        "output": task.get("output"),
        "failure": task.get("failure"),
        "created_at": task.get("createdAt"),
        "updated_at": task.get("updatedAt")
    }, indent=2)


@mcp.tool()
async def cancel_task(task_id: str) -> str:
    """
    Cancel a running generation task.
    
    Args:
        task_id: The task ID to cancel
    
    Returns:
        Cancellation confirmation
    """
    client = get_client()
    await client._request("POST", f"/tasks/{task_id}/cancel")
    
    return json.dumps({
        "task_id": task_id,
        "status": "cancelled"
    }, indent=2)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

@mcp.tool()
async def list_available_models() -> str:
    """
    List all available Runway models and their capabilities.
    
    Returns:
        Comprehensive list of models and features
    """
    models = {
        "image_generation": {
            "gen4_image": {
                "description": "Gen-4 Image - Highest quality image generation",
                "features": ["Reference images", "Tag-based composition", "1920:1080 resolution"],
                "use_cases": ["Consistent characters", "Styled imagery", "High-fidelity art"]
            },
            "gen4_image_turbo": {
                "description": "Gen-4 Image Turbo - Faster image generation",
                "features": ["Quick generation", "Multiple ratios", "Cost-efficient"],
                "use_cases": ["Rapid prototyping", "Batch generation", "Iterations"]
            }
        },
        "video_generation": {
            "gen4_turbo": {
                "description": "Gen-4 Turbo - Fastest and most efficient video model",
                "features": ["5-10s duration", "Multiple ratios", "High consistency"],
                "use_cases": ["Quick video creation", "Text-to-video", "Image-to-video"]
            },
            "gen3a_turbo": {
                "description": "Gen-3 Alpha Turbo - Fast Gen-3 variant",
                "features": ["Up to 20s duration", "Advanced controls", "Video-to-video"],
                "use_cases": ["Style transfer", "Extended videos", "Quick iterations"]
            },
            "gen3_alpha": {
                "description": "Gen-3 Alpha - Highest quality Gen-3",
                "features": ["Superior fidelity", "Expressive characters", "Complex scenes"],
                "use_cases": ["Premium content", "Character animation", "Cinematic shots"]
            }
        },
        "video_editing": {
            "aleph": {
                "description": "⭐ Aleph - Advanced video-to-video editing (Gen-4)",
                "features": [
                    "Add/remove/replace objects",
                    "Generate new camera angles",
                    "Transform lighting and style",
                    "Shot continuation",
                    "Novel view synthesis"
                ],
                "use_cases": [
                    "Professional video editing",
                    "Object manipulation",
                    "Scene transformation",
                    "Creative restyles"
                ]
            }
        },
        "special_features": {
            "extend_video": "Extend videos by 5-10 seconds (Gen-3)",
            "upscale_4k": "Upscale to 4K resolution",
            "first_last_frame": "Precise control with start/end frames",
            "keyframe_control": "Image as first or last frame",
            "reference_images": "Consistent characters with @tags"
        }
    }
    
    return json.dumps(models, indent=2)


@mcp.tool()
async def get_api_info() -> str:
    """
    Get information about the Runway MCP server and API configuration.
    
    Returns:
        Server info and setup instructions
    """
    info = {
        "server": "Runway MCP Server",
        "version": "1.0.0",
        "api_version": RUNWAY_API_VERSION,
        "features": [
            "Gen-4 Image & Video Generation",
            "Gen-3 Alpha & Turbo Models",
            "⭐ Aleph Video Editing (video-to-video)",
            "Text-to-Video",
            "Image-to-Video",
            "First-Last Frame Control",
            "Video Extension",
            "4K Upscaling",
            "Style Transfer",
            "Reference Images",
            "Keyframe Control"
        ],
        "setup": {
            "required_env": "RUNWAY_API_KEY",
            "get_api_key": "https://dev.runwayml.com",
            "documentation": "https://docs.dev.runwayml.com"
        },
        "api_configured": bool(RUNWAY_API_KEY)
    }
    
    return json.dumps(info, indent=2)


def main():
    """
    Main entry point for the Runway MCP server.
    This function is called when you run: uvx runway-mcp-server
    """
    # Run the MCP server
    mcp.run()


if __name__ == "__main__":
    # This allows running the server directly with: python server.py
    main()
