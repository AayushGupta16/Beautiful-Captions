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
        
 