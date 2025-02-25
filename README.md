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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📫 For bug reports and feature requests, use [GitHub Issues](https://github.com/aayushgupta16/beautiful-captions/issues)
- 💬 For questions and discussions, join our [GitHub Discussions](https://github.com/aayushgupta16/beautiful-captions/discussions)
- 🗳️ Vote on new features in our [Ideas section](https://github.com/aayushgupta16/beautiful-captions/discussions/categories/ideas)