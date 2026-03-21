from beautiful_captions.utils.subtitles import style_srt_content
from tests.base_config import SUBTITLE_CONTENT


class TestStyleSrtContent:
    def test_speaker_colors_assigned(self):
        result = style_srt_content(SUBTITLE_CONTENT, colors=["yellow", "white"])
        assert '<font color="yellow">' in result
        assert '<font color="white">' in result

    def test_speaker_labels_removed_by_default(self):
        result = style_srt_content(SUBTITLE_CONTENT)
        assert "Speaker A:" not in result
        assert "Speaker B:" not in result

    def test_speaker_labels_kept(self):
        result = style_srt_content(SUBTITLE_CONTENT, keep_speaker_labels=True)
        assert "Speaker A:" in result
        assert "Speaker B:" in result

    def test_max_words_per_line(self):
        result = style_srt_content(SUBTITLE_CONTENT, max_words_per_line=4)
        assert result  # should not crash

    def test_font_face_applied(self):
        result = style_srt_content(SUBTITLE_CONTENT, font="Arial")
        assert 'face="Arial"' in result
