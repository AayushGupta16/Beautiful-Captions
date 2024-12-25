"""Tests for style system."""

import pytest
from pathlib import Path
from src.styling.style import FontManager, StyleManager

def test_font_manager_initialization():
    """Test FontManager initialization and font loading."""
    manager = FontManager()
    fonts = manager.list_fonts()
    
    # Check that default fonts are loaded
    assert "Montserrat" in fonts
    assert len(fonts) > 0

def test_font_manager_get_font_path():
    """Test getting font path."""
    manager = FontManager()
    
    # Test valid font
    path = manager.get_font_path("Montserrat")
    assert path is not None
    assert Path(path).exists()
    assert Path(path).suffix == ".ttf"
    
    # Test invalid font
    path = manager.get_font_path("NonexistentFont")
    assert path is None

def test_style_manager_create_style():
    """Test creating ASS style."""
    manager = StyleManager()
    
    style = manager.create_ass_style(
        font_name="Montserrat",
        font_size=140,
        primary_color="&HFFFFFF&",
        outline_color="&H000000&",
        outline_thickness=2.0,
        vertical_position=0.7
    )
    
    # Check style string format
    assert style.startswith("Style: Default,Montserrat,140")
    assert "&HFFFFFF&" in style  # Primary color
    assert "&H000000&" in style  # Outline color
    assert "2" in style  # Outline thickness

def test_style_manager_invalid_font():
    """Test creating style with invalid font."""
    manager = StyleManager()
    
    with pytest.raises(ValueError):
        manager.create_ass_style(font_name="NonexistentFont")

def test_style_manager_create_header():
    """Test creating complete ASS header."""
    manager = StyleManager()
    
    style = manager.create_ass_style(
        font_name="Montserrat",
        vertical_position=0.7
    )
    header = manager.create_ass_header(style)
    
    # Check header sections
    assert "[Script Info]" in header
    assert "PlayResX: 1080" in header
    assert "PlayResY: 1920" in header
    assert "[V4+ Styles]" in header
    assert "[Events]" in header
    assert style in header

def test_style_vertical_position():
    """Test vertical position calculation."""
    manager = StyleManager()
    
    # Test different vertical positions
    style_top = manager.create_ass_style(vertical_position=0.0)
    style_middle = manager.create_ass_style(vertical_position=0.5)
    style_bottom = manager.create_ass_style(vertical_position=1.0)
    
    # Extract MarginV values
    def get_margin_v(style: str) -> int:
        parts = style.split(",")
        return int(parts[-2])
    
    margin_top = get_margin_v(style_top)
    margin_middle = get_margin_v(style_middle)
    margin_bottom = get_margin_v(style_bottom)
    
    assert margin_top < margin_middle < margin_bottom
    assert margin_middle == 960  # 1920 * 0.5