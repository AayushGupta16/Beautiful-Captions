from beautiful_captions import (
    StyleConfig,
)


class TestStyleConfig:
    def test_defaults(self):
        s = StyleConfig()
        assert s.font == "Montserrat"
        assert s.verticle_position == 0.5
        assert s.outline_thickness == 10
        assert s.max_words_per_line == 1
        assert s.auto_scale_font is True
        assert s.censor_subtitles is False
        assert s.custom_censored_words is None

    def test_censoring_populates_defaults(self):
        s = StyleConfig(censor_subtitles=True)
        assert s.custom_censored_words is not None
        assert "fuck" in s.custom_censored_words

    def test_custom_censored_words(self):
        s = StyleConfig(censor_subtitles=True, custom_censored_words={"darn": "d*rn"})
        assert s.custom_censored_words == {"darn": "d*rn"}
