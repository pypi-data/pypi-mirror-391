"""
OpenAI Server-Sent Events TTS plugin for LiveKit Agents.

This plugin provides real-time streaming text-to-speech using OpenAI's TTS API
with Server-Sent Events (SSE) for low-latency audio generation.

Key Features:
- Real-time streaming audio synthesis
- Low-latency audio delivery using SSE
- Support for multiple voices and models
- Both streaming and chunked audio modes
- Built-in latency measurement capabilities

Example:
    ```python
    from livekit.plugins.openai_sse import TTS
    
    # Create TTS instance
    tts = TTS(
        voice="alloy",
        model="gpt-4o-mini-tts",
        speed=1.0,
        response_format="pcm"
    )
    
    # Use in streaming mode
    stream = tts.stream()
    # ... use stream with LiveKit agents
    ```
"""

from .tts import (
    TTS,
    SynthesizeStream,
    ChunkedStream,
    OpenAIAPIClient,
)

__all__ = [
    "TTS",
    "SynthesizeStream", 
    "ChunkedStream",
    "OpenAIAPIClient",
]

# Version information
from .version import __version__

__version__ = __version__
