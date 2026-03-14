# Beautiful Captions 🎬

A fast and elegant Python library for adding beautiful captions to videos. Combines the speed of FFmpeg with the beauty of custom styling.

## Features

- ⚡ Lightning-fast caption rendering
- 🎨 Beautiful default styling with customization options
- 💃 Engaging bounce animation for captions
- 🤖 Built-in support for AssemblyAI
- 📝 Support for SRT files
- 🛠️ Simple, intuitive API

## Installation

```bash
pip install beautiful-captions
```

## Quick Start

Beautiful Captions provides two API styles to suit your needs:

### Functional API

```python
from beautiful_captions import add_captions, transcribe, process_video

# Using an existing SRT file
subtitles_from_srt("input.mp4", "subtitles.srt", style="default")

# Transcribe and caption
transcribe("video.mp4", service="assemblyai", api_key="YOUR_KEY")
subtitles_from_srt("video.mp4", "generated.srt", style="default")

# All-in-one process
add_subtitles("input.mp4", 
    transcribe_with="assemblyai",
    api_key="YOUR_KEY",
    style="default"
)
```

### Object-Oriented API

```python
from beautiful_captions import Video

# Using an existing SRT file
video = Video("input.mp4")
video.subtitles_from_srt("subtitles.srt", style="default")
video.save("output.mp4")

# Transcribe and caption
video = Video("input.mp4")
video.transcribe(service="assemblyai", api_key="YOUR_KEY")
video.subtitles_from_srt(style="default", animation="bounce")
video.save("output.mp4")
```

## Styling Options

Customize your captions with these options:

```python
from beautiful_captions import Style

style = Style(
    font="Arial",          # Font family
    color="white",         # Text color
    outline_color="black", # Outline color
    outline_width=2,       # Outline thickness
    position="bottom",     # Vertical position
    animation="bounce"     # Animation type
)

add_captions("input.mp4", "subtitles.srt", style=style)
```

## Transcription Services

Beautiful Captions supports multiple transcription services out of the box:

```python
# Using AssemblyAI
video.transcribe(service="assemblyai", api_key="YOUR_ASSEMBLYAI_KEY")
```

## Performance

Beautiful Captions is optimized for speed while maintaining high-quality output. Here's how it compares to MoviePy:

| Operation | Beautiful Captions | MoviePy |
|-----------|-------------------|---------|
| Caption Rendering | [Benchmark] | [Benchmark] |
| Memory Usage | [Benchmark] | [Benchmark] |

*Benchmarks coming soon*

## Contributing

We welcome contributions of all sizes! Beautiful Captions is designed to be modular and easy to extend. Here are some ways you can contribute:

### Areas for Contribution

1. **Transcription Services**: Add support for new transcription services by implementing the transcription interface
2. **Caption Styles**: Create new preset styles that others can use
3. **Animations**: Develop new caption animation types
4. **Performance Improvements**: Help optimize the caption rendering pipeline
5. **Documentation**: Improve docs, add examples, or fix typos
6. **Bug Reports**: Submit detailed bug reports and feature requests

### Getting Started

1. Check our [Contributing Guide](CONTRIBUTING.md) for detailed instructions
2. Look for issues labeled `good-first-issue` or `help-wanted`
3. Join discussions in GitHub Discussions to share ideas
4. Read our [Code of Conduct](CODE_OF_CONDUCT.md)

See [CONTRIBUTING.md](CONTRIBUTING.md) for full details on our development process.

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/aayushgupta16/beautiful-captions.git
cd beautiful-captions
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

## Future Features

Vote on upcoming features in our [GitHub Discussions](https://github.com/yourusername/beautiful-captions/discussions/categories/ideas):

- Additional preset styles (TikTok-style, Hormozi-style, etc.)
- Support for VTT format
- More animation types
- Additional transcription services

## Configuration Reference

`CaptionConfig` accepts three nested configs: `style`, `animation`, and `diarization`. You can pass them as dict literals or as config objects.

```python
from beautiful_captions import Video, CaptionConfig
```

### CaptionConfig

The top-level config that wraps everything:

```python
# Using dicts (recommended)
config = CaptionConfig(
    style={...},
    animation={...},
    diarization={...},
)

# Using config objects
from beautiful_captions.core.config import StyleConfig, AnimationConfig, DiarizationConfig

config = CaptionConfig(
    style=StyleConfig(...),
    animation=AnimationConfig(...),
    diarization=DiarizationConfig(...),
)
```

---

### StyleConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `font` | `str` | `"Montserrat"` | Font family name |
| `font_size` | `int` | `140` | Font size in pixels |
| `color` | `str` | `"white"` | Text color (`white`, `yellow`, `red`, `blue`, `green`, `purple`, `black`) |
| `outline_color` | `str` | `"black"` | Outline color |
| `outline_thickness` | `int` | `10` | Outline thickness in pixels |
| `verticle_position` | `float` | `0.5` | Vertical position (0.0 = bottom, 1.0 = top) |
| `max_words_per_line` | `int` | `1` | Max words per subtitle line (only works with word-level SRT input) |
| `auto_scale_font` | `bool` | `True` | Auto-scale font size based on text length |
| `censor_subtitles` | `bool` | `False` | Enable profanity censoring |
| `custom_censored_words` | `dict` | `None` | Custom word replacements (e.g. `{"damn": "d*mn"}`) |

### AnimationConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | `bool` | `True` | Enable/disable animation |
| `type` | `str` | `"bounce"` | Animation type |
| `keyframes` | `int` | `10` | Number of animation keyframes |

### DiarizationConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | `bool` | `True` | Enable/disable speaker diarization colors |
| `colors` | `list[str]` | `["white", "yellow", "red"]` | Colors assigned to speakers in order |
| `max_speakers` | `int` | `3` | Maximum number of speakers to detect |
| `keep_speaker_labels` | `bool` | `False` | Show "Speaker A:" labels in output |

---

### Config Examples

**Minimal — all defaults:**
```python
video = Video("input.mp4")
video.add_captions(srt_content=srt, output_path="output.mp4")
```

**No animation, no scaling — plain constant-size text:**
```python
video = Video("input.mp4", config=CaptionConfig(
    animation={"enabled": False},
    style={"auto_scale_font": False},
))
```

**Animation on, scaling off — constant size with no flicker:**
```python
video = Video("input.mp4", config=CaptionConfig(
    animation={"enabled": True},
    style={"auto_scale_font": False},
))
```

**Animation off, scaling on — static size adapts to text length:**
```python
video = Video("input.mp4", config=CaptionConfig(
    animation={"enabled": False},
    style={"auto_scale_font": True},
))
```

**Bounce animation with auto-scaling:**
```python
video = Video("input.mp4", config=CaptionConfig(
    animation={"enabled": True, "type": "bounce", "keyframes": 10},
    style={"auto_scale_font": True},
))
```

**Multi-word lines (2 words per line):**
```python
video = Video("input.mp4", config=CaptionConfig(
    style={"max_words_per_line": 2},
))
```

**Speaker diarization with custom colors:**
```python
video = Video("input.mp4", config=CaptionConfig(
    diarization={"enabled": True, "colors": ["yellow", "white"]},
))
```

**Speaker labels visible:**
```python
video = Video("input.mp4", config=CaptionConfig(
    diarization={"enabled": True, "colors": ["red", "green"], "keep_speaker_labels": True},
))
```

**Large font, no animation:**
```python
video = Video("input.mp4", config=CaptionConfig(
    style={"font_size": 200, "auto_scale_font": False},
    animation={"enabled": False},
))
```

**Small font with bounce:**
```python
video = Video("input.mp4", config=CaptionConfig(
    style={"font_size": 80, "auto_scale_font": True},
    animation={"enabled": True},
))
```

**Custom outline:**
```python
video = Video("input.mp4", config=CaptionConfig(
    style={"outline_thickness": 20, "outline_color": "blue"},
    animation={"enabled": False},
))
```

**Bottom position:**
```python
video = Video("input.mp4", config=CaptionConfig(
    style={"verticle_position": 0.15},
))
```

**Top position:**
```python
video = Video("input.mp4", config=CaptionConfig(
    style={"verticle_position": 0.85},
))
```

**Profanity censoring:**
```python
video = Video("input.mp4", config=CaptionConfig(
    style={"censor_subtitles": True},
))
```

**Custom censored words:**
```python
video = Video("input.mp4", config=CaptionConfig(
    style={
        "censor_subtitles": True,
        "custom_censored_words": {"damn": "d*mn", "hell": "h*ll"},
    },
))
```

**Kitchen sink — everything combined:**
```python
video = Video("input.mp4", config=CaptionConfig(
    animation={"enabled": True, "type": "bounce", "keyframes": 15},
    style={
        "font": "Montserrat",
        "font_size": 120,
        "color": "white",
        "outline_color": "black",
        "outline_thickness": 10,
        "verticle_position": 0.5,
        "auto_scale_font": True,
        "max_words_per_line": 2,
        "censor_subtitles": False,
    },
    diarization={
        "enabled": True,
        "colors": ["yellow", "white", "red"],
        "max_speakers": 3,
        "keep_speaker_labels": False,
    },
))
video.add_captions(
    srt_content=subtitle_content,
    output_path="output.mp4",
    add_styling=True,
    cuda=False,  # Set True for NVIDIA GPU acceleration
)
```

**Using with SRT file path:**
```python
video = Video("input.mp4", config=CaptionConfig(
    style={"auto_scale_font": False},
    animation={"enabled": False},
))
video.add_captions(srt_input_path="subtitles.srt", output_path="output.mp4")
```

**Using with inline SRT content:**
```python
srt = """
1
00:00:00,000 --> 00:00:02,500
Speaker A: Hello world.

2
00:00:02,500 --> 00:00:05,000
Speaker B: How are you?
"""

video = Video("input.mp4", config=CaptionConfig(
    diarization={"enabled": True, "colors": ["yellow", "white"]},
    animation={"enabled": False},
    style={"auto_scale_font": False},
))
video.add_captions(srt_content=srt, output_path="output.mp4", add_styling=True)
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📫 For bug reports and feature requests, use [GitHub Issues](https://github.com/aayushgupta16/beautiful-captions/issues)
- 💬 For questions and discussions, join our [GitHub Discussions](https://github.com/aayushgupta16/beautiful-captions/discussions)
- 🗳️ Vote on new features in our [Ideas section](https://github.com/aayushgupta16/beautiful-captions/discussions/categories/ideas)