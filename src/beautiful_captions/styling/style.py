"""Style processing for captions."""

import os
from pathlib import Path
from typing import Dict, Optional

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
        
    def create_ass_style(
        self,
        font_name: str = "Montserrat",
        font_size: int = 140,
        primary_color: str = "&HFFFFFF&",
        outline_color: str = "&H000000&",
        outline_thickness: float = 2.0,
        vertical_position: float = 0.7,
        bold: bool = False,
        italic: bool = False
    ) -> str:
        """Create ASS style definition.
        
        Args:
            font_name: Name of font to use
            font_size: Font size in pixels
            primary_color: Primary text color in ASS format
            outline_color: Outline color in ASS format
            outline_thickness: Outline thickness in pixels
            vertical_position: Vertical position (0-1, from top)
            bold: Whether to use bold style
            italic: Whether to use italic style
            
        Returns:
            ASS style definition string
            
        Raises:
            ValueError: If font is not available
        """
        if not self.font_manager.get_font_path(font_name):
            raise ValueError(f"Font not available: {font_name}")
            
        margin_v = int(1920 * vertical_position)
        
        style = (
            f"Style: Default,{font_name},{font_size},"
            f"{primary_color},"  # Primary color
            f"&H000000FF,"  # Secondary color (unused)
            f"{outline_color},"  # Outline color
            f"&H00000000,"  # Shadow color
            f"{1 if bold else 0},{1 if italic else 0},0,0,"  # Bold, italic, etc.
            f"100,100,0,0,1,"  # Scale and spacing
            f"{outline_thickness},0,"  # Outline and shadow
            f"2,10,10,{margin_v},1"  # Alignment and margins
        )
        
        return style
    
    def create_ass_header(self, style: str) -> str:
        """Create complete ASS header with style.
        
        Args:
            style: ASS style definition
            
        Returns:
            Complete ASS header section
        """
        header = [
            "[Script Info]",
            "ScriptType: v4.00+",
            "PlayResX: 1080",
            "PlayResY: 1920",
            "ScaledBorderAndShadow: yes",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            style,
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        ]
        
        return "\n".join(header)