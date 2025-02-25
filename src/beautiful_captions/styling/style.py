"""Style processing for captions."""

import os
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class FontManager:
    """Manages font availability and paths."""
    
    def __init__(self):
        """Initialize font manager."""
        self.font_dir = Path(__file__).parent.parent / "fonts"
        self.font_map = self._load_fonts()
        
    def _load_fonts(self) -> Dict[str, str]:
        """Load available fonts and their display names.
        
        Returns:
            Dictionary mapping display names to font files
        """
        fonts = {}
        font_lookup = {
            "CheGuevaraBarry-Brown": "CheGuevara Barry",
            "FiraSansCondensed-ExtraBoldItalic": "Fira Sans Condensed",
            "Gabarito-Black": "Gabarito",
            "KOMIKAX_": "Komika Axis",
            "Montserrat-Bold": "Montserrat",
            "Proxima-Nova-Semibold": "Proxima Nova",
            "Rubik-ExtraBold": "Rubik"
        }
        
        # Load bundled fonts
        for font_file in self.font_dir.glob("*.ttf"):
            base_name = font_file.stem
            display_name = font_lookup.get(base_name, base_name)
            fonts[display_name] = str(font_file)
            
        return fonts
        
    def get_font_path(self, font_name: str) -> Optional[str]:
        """Get path to font file.
        
        Args:
            font_name: Display name of font
            
        Returns:
            Path to font file or None if not found
        """
        return self.font_map.get(font_name)
        
    def list_fonts(self) -> list[str]:
        """List available font display names.
        
        Returns:
            List of available font names
        """
        return list(self.font_map.keys())

class StyleManager:
    """Manages caption styling."""
    
    def __init__(self):
        """Initialize style manager."""
        self.font_manager = FontManager()
        
    def _validate_color(self, color: str, default: str = "&HFFFFFF&") -> str:
        """Validate ASS color format."""
        if not (color.startswith("&H") and color.endswith("&") and len(color) == 10):
            logger.warning(f"Invalid color format '{color}', using default")
            return default
        return color
        
    def create_ass_style(
        self,
        font_name: str = "Montserrat",
        font_size: int = 140,
        primary_color: str = "&HFFFFFF&",
        outline_color: str = "&H000000&",
        outline_thickness: float = 2.0,
        vertical_position: float = 0.5,
        horizontal_position: float = 0.5,
        video_width: int = 1920,
        video_height: int = 1080,
        bold: bool = False,
        italic: bool = False
    ) -> str:
        # Validate font
        if not self.font_manager.get_font_path(font_name):
            logger.warning(f"Font '{font_name}' not found, using default Montserrat")
            font_name = "Montserrat"
            
        # Validate colors
        primary_color = self._validate_color(primary_color)
        outline_color = self._validate_color(outline_color, "&H000000&")
        
        # Validate numeric ranges
        font_size = max(1, min(font_size, 300))  # Reasonable limits
        outline_thickness = max(0, min(outline_thickness, 10.0))
        vertical_position = max(0, min(vertical_position, 1.0))
        horizontal_position = max(0, min(horizontal_position, 1.0))
        
        # Calculate margins based on positions and actual video dimensions
        margin_v = int(video_height * vertical_position)
        margin_l = int(video_width * horizontal_position)
        margin_r = int(video_width * (1 - horizontal_position))
        
        # Use center alignment (2) and let margins control the position
        alignment = 2  # Center alignment
        
        style = (
            f"Style: Default,{font_name},{font_size},"
            f"{primary_color},"  # Primary color
            f"&H000000FF,"  # Secondary color (unused)
            f"{outline_color},"  # Outline color
            f"&H00000000,"  # Shadow color
            f"{1 if bold else 0},{1 if italic else 0},0,0,"  # Bold, italic, etc.
            f"100,100,0,0,1,"  # Scale and spacing
            f"{outline_thickness},0,"  # Outline and shadow
            f"{alignment},{margin_l},{margin_r},{margin_v},1"  # Alignment and margins
        )
        
        return style
