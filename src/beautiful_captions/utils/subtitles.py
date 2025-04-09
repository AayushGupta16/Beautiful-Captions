"""Subtitle format utilities and conversions."""

import logging
import re
from pathlib import Path
from typing import Union, List, Optional
import pysrt
from ..core.config import StyleConfig, AnimationConfig
from ..utils.ffmpeg import get_video_dimensions
from ..styling.style import FontManager

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
        font_manage = FontManager()
        font = font_manage.get_font_mapping(style.font)
        
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
            
            margin_v = int(height * (1 - style.verticle_position))  # Convert relative position to pixels
            
            # Write default style
            f.write(
                f"Style: Default,{font},{style.font_size},"  # Use font_size from StyleConfig
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
                    
                    # Process text - keep any speaker labels but remove font tags
                    text = sub.text
                    
                    # Extract color information from font tags if present
                    color_match = re.search(r'<font color="([^"]+)">', text)
                    color = color_match.group(1) if color_match else style.color
                    
                    # Remove font tags but keep the content
                    text = re.sub(r'<font[^>]*>', '', text)
                    text = re.sub(r'</font>', '', text)
                    text = re.sub(r'<[^>]+>', '', text)  # Remove any other HTML-style tags
                    text = text.replace('\n', '\\N')
                    
                    # Apply color override if different from default
                    if color.lower() != style.color.lower():
                        text = f"{{\\c{color_to_ass(color)}}}{text}"
                    
                    # Auto-scale font size based on text length if enabled
                    font_scale = 100
                    if style.auto_scale_font:
                        # Calculate a scaling factor based on text length
                        # More characters = smaller font
                        char_count = len(text.replace('\\N', ''))
                        if char_count > 5:  # Only scale if more than 5 characters
                            # Scale down to 70% for long text (20+ chars)
                            font_scale = max(70, 100 - (char_count - 5) * 1.5)
                            text = f"{{\\fscx{font_scale:.0f}\\fscy{font_scale:.0f}}}{text}"
                    
                    if animation.enabled and animation.type == "bounce":
                        # Add bounce animation
                        duration = sub.duration.seconds + sub.duration.milliseconds / 1000
                        animated_text = ""
                        
                        for j in range(animation.keyframes - 1):
                            t1 = j * duration / (animation.keyframes - 1)
                            t2 = (j + 1) * duration / (animation.keyframes - 1)
                            scale = max(80, 100 - 90 * (t1 / duration))
                            if style.auto_scale_font and font_scale < 100:
                                scale = scale * font_scale / 100
                            animated_text += f"{{\\t({t1:.2f},{t2:.2f},\\fscx{scale:.0f}\\fscy{scale:.0f})}}"
                        
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

def style_srt_content(
    srt_content: str, 
    colors: Optional[List[str]] = None, 
    encode_speaker_colors: bool = True,
    keep_speaker_labels: bool = False,
    max_words_per_line: int = 1
) -> str:
    """Apply styling and color encoding to plain SRT content.
    
    Args:
        srt_content: Plain SRT content
        colors: List of colors to use for styling text (defaults to ["white", "yellow", "blue"])
        encode_speaker_colors: Whether to encode speaker colors in the output
        keep_speaker_labels: Whether to keep speaker labels in the output (default: False)
        max_words_per_line: Maximum number of words per line (default: 1)
        
    Returns:
        Styled SRT content with font and color tags as requested
    """    
    # Default colors if none provided
    if colors is None:
        colors = ["white", "yellow", "blue"]
    
    # Parse the SRT content
    subs = pysrt.from_string(srt_content)
    
    if max_words_per_line > 1:
        # Process subtitles by speaker to potentially combine them
        subs = _optimize_subtitles_for_max_words(subs, max_words_per_line)
    
    styled_content = ""
    
    # Track speakers and their assigned colors
    speaker_colors = {}
    subtitle_to_speaker = {}  # Map subtitle indices to speakers
    
    # First pass: Identify all speakers and assign colors
    for i, sub in enumerate(subs):
        text = sub.text
        speaker_match = re.match(r'^(Speaker [A-Z]+):\s*(.*)', text)
        
        if speaker_match:
            speaker_label = speaker_match.group(1)
            if speaker_label not in speaker_colors:
                speaker_colors[speaker_label] = colors[len(speaker_colors) % len(colors)]
            # Store which speaker this subtitle belongs to
            subtitle_to_speaker[i] = speaker_label
    
    # Second pass: Apply colors and format text
    for i, sub in enumerate(subs):
        text = sub.text
        speaker_label = ""
        speaker_match = re.match(r'^(Speaker [A-Z]+):\s*(.*)', text)
        
        if speaker_match:
            speaker_label = speaker_match.group(1)
            text = speaker_match.group(2)
            
            # Get the color assigned to this speaker
            color = speaker_colors.get(speaker_label, colors[0])
        else:
            # If no speaker label in this subtitle, see if we know which speaker it belongs to
            speaker_label = subtitle_to_speaker.get(i)
            if speaker_label and speaker_label in speaker_colors:
                color = speaker_colors[speaker_label]
            else:
                # Default to first color if we can't determine the speaker
                color = colors[0]
        
        # Apply color formatting if enabled
        if encode_speaker_colors:
            text = f'<font color="{color}">{text}</font>'
        
        # Add speaker label back only if requested
        if keep_speaker_labels and speaker_label:
            text = f"{speaker_label}: {text}"
        
        # Create a new subtitle with the styled text
        new_sub = pysrt.SubRipItem(
            index=sub.index,
            start=sub.start,
            end=sub.end,
            text=text
        )
        
        styled_content += str(new_sub) + "\n"
    
    return styled_content


def _optimize_subtitles_for_max_words(subs, max_words_per_line: int):
    """Optimize subtitle segmentation based on max_words_per_line.
    
    This function looks at adjacent subtitles from the same speaker and combines them
    if needed to approach the max_words_per_line limit.
    
    Args:
        subs: List of subtitles from pysrt
        max_words_per_line: Maximum words per line target
        
    Returns:
        Optimized list of subtitles
    """
    if not subs or len(subs) <= 1:
        return subs
    
    result = []
    current_batch = []
    current_speaker = None
    current_word_count = 0
    
    # Helper to create a new subtitle from a batch
    def create_subtitle_from_batch(batch):
        if not batch:
            return None
        
        combined_text = ' '.join([re.sub(r'^(Speaker [A-Z]+):\s*', '', sub.text) for sub in batch])
        # Keep the speaker label from the first subtitle
        first_sub_match = re.match(r'^(Speaker [A-Z]+):\s*', batch[0].text)
        if first_sub_match:
            speaker_prefix = first_sub_match.group(1) + ": "
            combined_text = speaker_prefix + combined_text
        
        # Create new subtitle with the combined text and spanning time
        return pysrt.SubRipItem(
            index=batch[0].index,
            start=batch[0].start,
            end=batch[-1].end,
            text=combined_text
        )
    
    for i, sub in enumerate(subs):
        # Extract speaker and text
        speaker_match = re.match(r'^(Speaker [A-Z]+):\s*', sub.text)
        current_sub_speaker = speaker_match.group(1) if speaker_match else None
        text_without_speaker = re.sub(r'^(Speaker [A-Z]+):\s*', '', sub.text)
        word_count = len(text_without_speaker.split())
        
        # If we're starting a new batch or changing speakers
        if (current_speaker is None or 
            current_speaker != current_sub_speaker or 
            current_word_count + word_count > max_words_per_line or
            # Time gap check (e.g., >500ms between subtitles)
            (current_batch and 
             (sub.start.ordinal - current_batch[-1].end.ordinal) > 500)):
            
            # Process the current batch if it exists
            if current_batch:
                result.append(create_subtitle_from_batch(current_batch))
            
            # Start a new batch
            current_batch = [sub]
            current_speaker = current_sub_speaker
            current_word_count = word_count
        else:
            # Continue the current batch
            current_batch.append(sub)
            current_word_count += word_count
        
        # If we've reached max_words_per_line or this is the last subtitle
        if current_word_count >= max_words_per_line or i == len(subs) - 1:
            if current_batch:
                result.append(create_subtitle_from_batch(current_batch))
                current_batch = []
                current_speaker = None
                current_word_count = 0
    
    # Process any remaining batch
    if current_batch:
        result.append(create_subtitle_from_batch(current_batch))
    
    # Re-index the subtitles
    for i, sub in enumerate(result, 1):
        sub.index = i
    
    return result

def group_words_into_lines(
    words: List[str],
    max_words_per_line: int = 1,
    respect_punctuation: bool = True
) -> List[str]:
    """Group words into lines based on max_words_per_line setting.
    
    Args:
        words: List of words to group
        max_words_per_line: Maximum number of words per line
        respect_punctuation: Whether to start a new line after sentence-ending punctuation
        
    Returns:
        List of lines with grouped words
    """
    if max_words_per_line <= 0:
        max_words_per_line = 1
        
    lines = []
    current_line = []
    word_count = 0
    
    for word in words:
        current_line.append(word)
        word_count += 1
        
        # Check if we need to start a new line
        if word_count >= max_words_per_line or (
            respect_punctuation and 
            word.rstrip()[-1] in ['.', '!', '?', ':', ';'] and 
            word_count > 0
        ):
            lines.append(' '.join(current_line))
            current_line = []
            word_count = 0
            
    # Add any remaining words
    if current_line:
        lines.append(' '.join(current_line))
        
    return lines