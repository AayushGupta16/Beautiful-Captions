"""Tests for animation system."""

import pytest
from src.styling.animation import BounceAnimation, AnimationFactory, create_animation_for_subtitle

def test_bounce_animation_keyframes():
    """Test bounce animation keyframe generation."""
    animation = BounceAnimation(duration=2.0, num_keyframes=5)
    keyframes = animation.generate_keyframes()
    
    assert len(keyframes) == 5
    
    # First keyframe should be at t=0
    assert keyframes[0].time == 0
    assert keyframes[0].scale_x == 100
    assert keyframes[0].scale_y == 100
    
    # Last keyframe should be at t=duration
    assert keyframes[-1].time == 2.0
    assert 80 <= keyframes[-1].scale_x <= 100
    assert 80 <= keyframes[-1].scale_y <= 100

def test_bounce_animation_ass_commands():
    """Test ASS command generation for bounce animation."""
    animation = BounceAnimation(duration=1.0, num_keyframes=3)
    commands = animation.to_ass_commands()
    
    assert commands.startswith("{\\t(")
    assert commands.endswith(")}")
    assert "\\fscx" in commands
    assert "\\fscy" in commands

def test_animation_factory_bounce():
    """Test animation factory with bounce animation."""
    commands = AnimationFactory.create("bounce", duration=1.0, num_keyframes=3)
    assert commands.startswith("{\\t(")
    assert "\\fscx" in commands

def test_animation_factory_invalid():
    """Test animation factory with invalid animation type."""
    with pytest.raises(ValueError):
        AnimationFactory.create("invalid_type", duration=1.0)

def test_create_animation_for_subtitle():
    """Test creating animated subtitle text."""
    text = "Hello, world!"
    duration = 1.0
    
    result = create_animation_for_subtitle(
        text=text,
        duration=duration,
        animation_type="bounce",
        num_keyframes=3
    )
    
    assert text in result
    assert result.startswith("{\\t(")
    assert result.endswith(text)