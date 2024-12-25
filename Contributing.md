# Contributing to Beautiful Captions

First off, thank you for considering contributing to Beautiful Captions! This document provides guidelines and instructions for contributing.

## Code Organization

The project is organized into several key modules:

```
beautiful_captions/
├── transcription/          # Transcription service integrations
│   ├── base.py            # Base transcription interface
│   ├── assemblyai.py      # AssemblyAI implementation
│   ├── deepgram.py        # Deepgram implementation
│   └── openai.py          # OpenAI implementation
├── styles/                # Caption styling
│   ├── base.py           # Base style interface
│   └── presets.py        # Preset style definitions
├── animations/           # Caption animations
│   ├── base.py          # Base animation interface
│   └── bounce.py        # Bounce animation implementation
└── core/                # Core functionality
    ├── caption.py       # Main captioning logic
    ├── video.py         # Video handling
    └── utils.py         # Utility functions
```

## Adding a New Transcription Service

1. Create a new file in `transcription/` directory
2. Implement the base transcription interface
3. Add tests in `tests/transcription/`

Example:

```python
from .base import TranscriptionService

class NewService(TranscriptionService):
    def __init__(self, api_key):
        self.api_key = api_key

    def transcribe(self, video_path):
        # Implementation here
        pass

    def to_srt(self, transcription):
        # Convert to SRT format
        pass
```

## Adding a New Style

1. Create your style in `styles/presets.py`
2. Add documentation and examples
3. Add tests in `tests/styles/`

## Development Process

1. Fork the repository
2. Create a feature branch
3. Write your changes
4. Write or update tests
5. Run the test suite
6. Push your branch and submit a pull request

### Setting Up Development Environment

```bash
# Clone your fork
git clone https://github.com/your-username/beautiful-captions.git
cd beautiful-captions

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_transcription.py

# Run with coverage
pytest --cov=beautiful_captions tests/
```

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the documentation if you're adding new features
3. Add tests for new functionality
4. Ensure all tests pass
5. Update the CHANGELOG.md

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

### Python Styleguide

* Use meaningful variable names
* Add docstrings to all functions and classes
* Comment complex algorithms or business logic

## Community

* Join our [GitHub Discussions](https://github.com/yourusername/beautiful-captions/discussions)
* Follow our [Code of Conduct](CODE_OF_CONDUCT.md)