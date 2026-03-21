import pytest

from beautiful_captions import (
    AnimationConfig,
    CaptionConfig,
    DiarizationConfig,
    StyleConfig,
)

from .base_config import CONFIGS

# -- CaptionConfig tests --------------------------------------------------

class TestCaptionConfigCreation:
    """Test that every CONFIGS entry produces a valid CaptionConfig."""

    @pytest.mark.parametrize("name,kwargs", list(CONFIGS.items()), ids=list(CONFIGS.keys()))
    def test_config_creates_successfully(self, name, kwargs):
        config = CaptionConfig(**kwargs)
        assert isinstance(config.style, StyleConfig)
        assert isinstance(config.animation, AnimationConfig)
        assert isinstance(config.diarization, DiarizationConfig)

    def test_default_config(self):
        config = CaptionConfig()
        assert config.style.font == "Montserrat"
        assert config.style.font_size == 140
        assert config.style.color == "white"
        assert config.animation.enabled is True
        assert config.animation.type == "bounce"
        assert config.diarization.enabled is True

    def test_config_with_dict_style(self):
        config = CaptionConfig(style={"font_size": 200, "color": "yellow"})
        assert config.style.font_size == 200
        assert config.style.color == "yellow"

    def test_config_with_dict_animation(self):
        config = CaptionConfig(animation={"enabled": False})
        assert config.animation.enabled is False

    def test_config_with_dict_diarization(self):
        config = CaptionConfig(diarization={"colors": ["red", "blue"], "max_speakers": 5})
        assert config.diarization.colors == ["red", "blue"]
        assert config.diarization.max_speakers == 5

    def test_config_with_dataclass_objects(self):
        config = CaptionConfig(
            style=StyleConfig(font_size=80),
            animation=AnimationConfig(enabled=False),
            diarization=DiarizationConfig(colors=["green"]),
        )
        assert config.style.font_size == 80
        assert config.animation.enabled is False
        assert config.diarization.colors == ["green"]
