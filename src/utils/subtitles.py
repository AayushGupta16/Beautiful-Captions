"""Subtitle format utilities and conversions."""

import logging
from pathlib import Path
from typing import Union
import pysrt
from ..core.config import StyleConfig, AnimationConfig

logger = logging.getLogger(__name__)

def color_to_ass(color: str) -> str:
    """Convert common color names to ASS color codes."""
    color_map = {
        "white": "&HFFFFFF&",
        "yellow": "&H00FFFF&",
        "red": "&H0000FF&",
        "blue": "&HFF0000&",
        "green": "&H00FF00&",
        "purple": "&H800080&",
        "black": "&H000000&"
    }
    return color_map.get(color.lower(), "&HFFFFFF&")

def create_ass_subtitles(
    srt_content: str,
    output_path: Union[str, Path],
    style: StyleConfig,
    animation: AnimationConfig
) -> None:
    """Create ASS subtitle file from SRT content with styling.
    
    Args:
        srt_content: Input SRT content
        output_path: Output ASS file path
        style: Caption style configuration
        animation: Animation configuration
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write ASS header
            f.write("[Script Info]\n")
            f.write("ScriptType: v4.00+\n")
            f.write("PlayResX: 1080\n")
            f.write("PlayResY: 1920\n")
            f.write("ScaledBorderAndShadow: yes\n\n")
            
            # Write style section
            f.write("[V4+ Styles]\n")
            f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
            
            margin_v = int(1920 * style.position)  # Convert relative position to pixels
            
            # Write default style
            f.write(
                f"Style: Default,{style.font},140,"
                f"{color_to_ass(style.color)},"  # Primary color
                f"&H000000FF,"  # Secondary color
                f"{color_to_ass(style.outline_color)},"  # Outline color
                f"&H00000000,"  # Background color
                f"0,0,0,0,"  # No bold, italic, underline, strikeout
                f"100,100,0,0,1,"  # Default scaling and spacing
                f"{style.outline_thickness},0,"  # Outline thickness, no shadow
                f"2,10,10,{margin_v},1\n\n"  # Alignment and margins
            )
            
            # Write events section
            f.write("[Events]\n")
            f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
            
            # Convert SRT to ASS events
            subs = pysrt.from_string(srt_content)
            
            for i, sub in enumerate(subs, 1):
                try:
                    start = f"{sub.start.hours:01d}:{sub.start.minutes:02d}:{sub.start.seconds:02d}.{sub.start.milliseconds // 10:02d}"
                    end = f"{sub.end.hours:01d}:{sub.end.minutes:02d}:{sub.end.seconds:02d}.{sub.end.milliseconds // 10:02d}"
                    
                    text = sub.text.replace('\n', '\\N')
                    
                    if animation.enabled and animation.type == "bounce":
                        # Add bounce animation
                        duration = sub.duration.seconds + sub.duration.milliseconds / 1000
                        animated_text = ""
                        
                        for j in range(animation.keyframes):
                            t = j * duration / (animation.keyframes - 1)
                            scale = max(80, 100 - 90 * (t / duration))
                            animated_text += f"{{\\t({t:.2f},{t:.2f},\\fscx{scale:.0f}\\fscy{scale:.0f})}}"
                        
                        animated_text += text
                        text = animated_text
                    
                    f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n")
                    
                except Exception as e:
                    logger.error(f"Error processing subtitle {i}: {str(e)}")
                    continue
                    
        logger.info(f"ASS subtitles created successfully at: {output_path}")
        
    except Exception as e:
        logger.error(f"Error creating ASS subtitles: {str(e)}")
        raise