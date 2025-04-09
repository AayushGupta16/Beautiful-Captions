"""Beautiful Captions - Fast and elegant video captioning library."""

from .core.config import CaptionConfig, StyleConfig, AnimationConfig, DiarizationConfig
from .core.caption import subtitles_from_srt, add_subtitles, extract_subtitles, caption_stream
from .core.video import Video
from .styling.style import StyleManager, FontManager
from .styling.animation import AnimationFactory, create_animation_for_subtitle
from .utils.subtitles import style_srt_content

__version__ = "0.1.55"

__all__ = [
    # Main functions
    "subtitles_from_srt",
    "add_subtitles",
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
    "style_srt_content",
]