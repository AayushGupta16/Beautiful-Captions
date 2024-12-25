"""Beautiful Captions - Fast and elegant video captioning library."""

from .core.config import CaptionConfig, StyleConfig, AnimationConfig, DiarizationConfig
from .core.caption import add_captions, process_video, extract_subtitles, caption_stream
from .core.video import Video
from .styling.style import StyleManager, FontManager
from .styling.animation import AnimationFactory, create_animation_for_subtitle

__version__ = "0.1.0"

__all__ = [
    # Main functions
    "add_captions",
    "process_video",
    "extract_subtitles",
    "caption_stream",
    
    # Classes
    "Video",
    "CaptionConfig",
    "StyleConfig",
    "AnimationConfig",
    "DiarizationConfig",
    
    # Styling
    "StyleManager",
    "FontManager",
    "AnimationFactory",
    "create_animation_for_subtitle",
]