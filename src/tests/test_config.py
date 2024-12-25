"""Tests for configuration system."""

from src.core.config import (
    StyleConfig,
    AnimationConfig,
    DiarizationConfig,
    CaptionConfig
)

def test_style_config_defaults():
    """Test StyleConfig default values."""
    config = StyleConfig()
    
    assert config.font == "Montserrat"
    assert config.position == 0.7
    assert config.color == "white"
    assert config.outline_color == "black"
    assert config.outline_thickness == 2

def test_style_config_custom():
    """Test StyleConfig with custom values."""
    config = StyleConfig(
        font="Rubik",
        position=0.8,
        color="yellow",
        outline_color="blue",
        outline_thickness=3
    )
    
    assert config.font == "Rubik"
    assert config.position == 0.8
    assert config.color == "yellow"
    assert config.outline_color == "blue"
    assert config.outline_thickness == 3

def test_animation_config_defaults():
    """Test AnimationConfig default values."""
    config = AnimationConfig()
    
    assert config.enabled is True
    assert config.type == "bounce"
    assert config.keyframes == 10

def test_diarization_config_defaults():
    """Test DiarizationConfig default values."""
    config = DiarizationConfig()
    
    assert config.enabled is True
    assert config.colors == ["white", "yellow", "blue"]
    assert config.max_speakers == 3

def test_diarization_config_custom_colors():
    """Test DiarizationConfig with custom colors."""
    config = DiarizationConfig(
        colors=["red", "green", "blue"],
        max_speakers=5
    )
    
    assert config.colors == ["red", "green", "blue"]
    assert config.max_speakers == 5

def test_caption_config_defaults():
    """Test CaptionConfig default initialization."""
    config = CaptionConfig()
    
    assert isinstance(config.style, StyleConfig)
    assert isinstance(config.animation, AnimationConfig)
    assert isinstance(config.diarization, DiarizationConfig)
    
    # Check nested defaults
    assert config.style.font == "Montserrat"
    assert config.animation.type == "bounce"
    assert config.diarization.max_speakers == 3

def test_caption_config_custom():
    """Test CaptionConfig with custom nested configs."""
    config = CaptionConfig(
        style=StyleConfig(font="Rubik", position=0.8),
        animation=AnimationConfig(enabled=False),
        diarization=DiarizationConfig(max_speakers=5)
    )
    
    assert config.style.font == "Rubik"
    assert config.style.position == 0.8
    assert config.animation.enabled is False
    assert config.diarization.max_speakers == 5