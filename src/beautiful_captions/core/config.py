from dataclasses import dataclass
from typing import List, Optional

@dataclass
class StyleConfig:
    font: str = "Montserrat"
    verticle_position: float = 0.5
    color: str = "white"
    outline_color: str = "black"
    outline_thickness: int = 10
    font_size: int = 140
    max_words_per_line: int = 1  
    auto_scale_font: bool = True  

@dataclass
class AnimationConfig:
    enabled: bool = True
    type: str = "bounce"
    keyframes: int = 10

@dataclass
class DiarizationConfig:
    enabled: bool = True
    colors: List[str] = None
    max_speakers: int = 3
    keep_speaker_labels: bool = False

    def __post_init__(self):
        if self.colors is None:
            self.colors = ["white", "yellow", "blue"]

@dataclass
class CaptionConfig:
    style: StyleConfig = None
    animation: AnimationConfig = None
    diarization: DiarizationConfig = None

    def __post_init__(self):
        if self.style is None:
            self.style = StyleConfig()
        if self.animation is None:
            self.animation = AnimationConfig()
        if self.diarization is None:
            self.diarization = DiarizationConfig()
