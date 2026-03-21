from beautiful_captions.utils.subtitles import group_words_into_lines


class TestGroupWordsIntoLines:
    def test_single_word_per_line(self):
        lines = group_words_into_lines(["hello", "world"], max_words_per_line=1)
        assert lines == ["hello", "world"]

    def test_two_words_per_line(self):
        lines = group_words_into_lines(["a", "b", "c", "d"], max_words_per_line=2)
        assert lines == ["a b", "c d"]

    def test_odd_count(self):
        lines = group_words_into_lines(["a", "b", "c"], max_words_per_line=2)
        assert lines == ["a b", "c"]

    def test_punctuation_breaks_line(self):
        lines = group_words_into_lines(
            ["hello.", "world", "foo"], max_words_per_line=3, respect_punctuation=True
        )
        assert lines == ["hello.", "world foo"]

    def test_no_punctuation_respect(self):
        lines = group_words_into_lines(
            ["hello.", "world", "foo"], max_words_per_line=3, respect_punctuation=False
        )
        assert lines == ["hello. world foo"]

    def test_empty_list(self):
        assert group_words_into_lines([]) == []

    def test_zero_max_words_defaults_to_one(self):
        lines = group_words_into_lines(["a", "b"], max_words_per_line=0)
        assert lines == ["a", "b"]
