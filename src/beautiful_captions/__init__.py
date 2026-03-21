"""Beautiful Captions - Fast and elegant video captioning library."""

from .core.caption import (
    add_subtitles,
    caption_stream,
    extract_subtitles,
    subtitles_from_srt,
)
from .core.config import AnimationConfig, CaptionConfig, DiarizationConfig, StyleConfig
from .core.video import Video
from .styling.animation import AnimationFactory, create_animation_for_subtitle
from .styling.style import FontManager, StyleManager
from .utils.subtitles import style_srt_content

__version__ = "0.1.71"

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
