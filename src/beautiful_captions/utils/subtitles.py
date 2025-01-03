"""Subtitle format utilities and conversions."""

import logging
import re
from pathlib import Path
from typing import Union, List
import pysrt
from ..core.config import StyleConfig, AnimationConfig
from ..utils.ffmpeg import get_video_dimensions

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
    video_path: Union[str, Path],
    output_path: Union[str, Path],
    style: StyleConfig,
    animation: AnimationConfig
) -> None:
    """Create ASS subtitle file from SRT content with styling.
    
    Args:
        srt_content: Input SRT content
        video_path: Input video file path
        output_path: Output ASS file path
        style: Caption style configuration
        animation: Animation configuration
    """
    try:
        # Get video dimensions
        width, height = get_video_dimensions(video_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write ASS header
            f.write("[Script Info]\n")
            f.write("ScriptType: v4.00+\n")
            f.write(f"PlayResX: {width}\n")
            f.write(f"PlayResY: {height}\n")
            f.write("ScaledBorderAndShadow: yes\n\n")
            
            # Write style section
            f.write("[V4+ Styles]\n")
            f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
            
            margin_v = int(height * style.position)  # Convert relative position to pixels
            
            # Write default style
            f.write(
                f"Style: Default,{style.font},{style.font_size},"  # Use font_size from StyleConfig
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
                    
                    # Strip font and color tags
                    text = sub.text
                    text = re.sub(r'<font[^>]*>', '', text)  # Remove opening font tags
                    text = re.sub(r'</font>', '', text)      # Remove closing font tags
                    text = re.sub(r'<[^>]+>', '', text)      # Remove any other HTML-style tags
                    text = re.sub(r'^[^:]+:\s*', '', text)   # Remove speaker tags (both "Speaker:" and "Speaker X:" formats)
                    text = text.replace('\n', '\\N')
                    
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

def style_srt_content(srt_content: str, speaker_colors: List[str]) -> str:
    """Apply styling and color encoding to plain SRT content.
    
    Args:
        srt_content: Plain SRT content
        speaker_colors: List of colors to use for different speakers
        
    Returns:
        Styled SRT content with font and color tags
    """
    import pysrt
    from io import StringIO
    
    # Parse the SRT content
    subs = pysrt.from_string(srt_content)
    styled_content = ""
    speaker_color_map = {}
    
    # Process each subtitle
    for sub in subs:
        # Extract speaker from text (assumes format "Speaker: text")
        if ': ' in sub.text:
            speaker, text = sub.text.split(': ', 1)
            
            # Assign color to speaker if not already assigned
            if speaker not in speaker_color_map:
                color_index = len(speaker_color_map) % len(speaker_colors)
                speaker_color_map[speaker] = speaker_colors[color_index]
            
            color = speaker_color_map[speaker]
            
            # Format with styling
            styled_text = f'<font color="{color}">{speaker}: {text}</font>'
            
            # Create new subtitle entry
            styled_content += f"{sub.index}\n"
            styled_content += f"{sub.start} --> {sub.end}\n"
            styled_content += f"{styled_text}\n\n"
        else:
            # If no speaker found, keep original
            styled_content += str(sub)
            
    return styled_content