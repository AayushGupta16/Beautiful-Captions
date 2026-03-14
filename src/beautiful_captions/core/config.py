from dataclasses import dataclass, field
from typing import Dict, List, Optional


def default_censored_words() -> Dict[str, str]:
    """Default dictionary of words to censor."""
    return {
        # Mild censoring
        "sex": "s*x",
        "kill": "k*ll",
        "death": "d*ath",
        "idiot": "id*ot",
        "moron": "m*ron",
        "pathetic": "path*tic",
        "scum": "sc*m",
        "dead": "d*ad",
        "pissed": "p*ssed",
        "gun": "g*n",
        # Strong censoring
        "asshole": "a**hole",
        "assholes": "a**holes",
        "bullshitter": "bullsh**ter",
        "bullshit": "bulls**t",
        "penis": "p**is",
        "vagina": "v**ina",
        "sexual": "s**ual",
        "sexuality": "s**uality",
        "retard": "r**ard",
        "retarded": "r**arded",
        "shit": "sh**",
        "bastard": "b**tard",
        "pussy": "p**sy",
        "dick": "d**k",
        "cock": "c**k",
        "bitch": "b**ch",
        "whore": "wh**e",
        "slut": "sl*t",
        "fuck": "f**k",
        "fucking": "f**king",
        "fucker": "f**ker",
    }


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
    censor_subtitles: bool = False
    custom_censored_words: Optional[Dict[str, str]] = None

    def __post_init__(self):
        # Initialize with default censored words if censorship is enabled but no custom words provided
        if self.censor_subtitles and self.custom_censored_words is None:
            self.custom_censored_words = default_censored_words()


@dataclass
class AnimationConfig:
    enabled: bool = True
    type: str = "bounce"
    keyframes: int = 10


@dataclass
class DiarizationConfig:
    enabled: bool = True
    colors: List[str] = field(default_factory=lambda: ["white", "yellow", "red"])
    max_speakers: int = 3
    keep_speaker_labels: bool = False


@dataclass
class CaptionConfig:
    style: StyleConfig = field(default_factory=StyleConfig)
    animation: AnimationConfig = field(default_factory=AnimationConfig)
    diarization: DiarizationConfig = field(default_factory=DiarizationConfig)

    def __post_init__(self):
        if isinstance(self.style, dict):
            self.style = StyleConfig(**self.style)
        if isinstance(self.animation, dict):
            self.animation = AnimationConfig(**self.animation)
        if isinstance(self.diarization, dict):
            self.diarization = DiarizationConfig(**self.diarization)
