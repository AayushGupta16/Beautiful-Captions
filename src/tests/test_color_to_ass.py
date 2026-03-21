import pytest

from beautiful_captions.utils.subtitles import color_to_ass


class TestColorToAss:
    @pytest.mark.parametrize("color,expected", [
        ("white", "&HFFFFFF&"),
        ("yellow", "&H00FFFF&"),
        ("red", "&H0000FF&"),
        ("blue", "&HFF0000&"),
        ("green", "&H00FF00&"),
        ("purple", "&H800080&"),
        ("black", "&H000000&"),
    ])
    def test_known_colors(self, color: str, expected: str):
        assert color_to_ass(color) == expected

    def test_case_insensitive(self):
        assert color_to_ass("White") == "&HFFFFFF&"
        assert color_to_ass("RED") == "&H0000FF&"

    def test_unknown_color_defaults_to_white(self):
        assert color_to_ass("magenta") == "&HFFFFFF&"
