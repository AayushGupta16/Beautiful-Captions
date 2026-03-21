INPUT_VIDEO = "src/tests/input.mp4"

SUBTITLE_CONTENT = """
1
00:00:00,000 --> 00:00:02,500
Speaker A: Welcome to the demo video.

2
00:00:02,500 --> 00:00:05,000
Speaker B: These subtitles are provided as a sample.

3
00:00:05,000 --> 00:00:08,000
Speaker A: They work without any API key.

4
00:00:08,000 --> 00:00:11,000
Speaker B: You can style them however you like.
"""

# All test configs: (name, CaptionConfig kwargs)
CONFIGS = {
    # 1. Defaults — animation on, auto_scale on, 1 word per line
    "defaults": {},
    # 2. Animation off, auto_scale off — plain constant-size text
    "no_animation_no_scale": {
        "animation": {"enabled": False},
        "style": {"auto_scale_font": False},
    },
    # 3. Animation on, auto_scale off — should show constant size (no flicker)
    "animation_on_scale_off": {
        "animation": {"enabled": True},
        "style": {"auto_scale_font": False},
    },
    # 4. Animation off, auto_scale on — static size based on text length
    "animation_off_scale_on": {
        "animation": {"enabled": False},
        "style": {"auto_scale_font": True},
    },
    # 5. Animation on, auto_scale on — bounce animation with length scaling
    "animation_on_scale_on": {
        "animation": {"enabled": True},
        "style": {"auto_scale_font": True},
    },
    # 6. Multi-word lines (2 words per line)
    "max_words_2": {
        "style": {"max_words_per_line": 2},
    },
    # 7. Multi-word lines (4 words per line), no animation
    "max_words_4_no_anim": {
        "animation": {"enabled": False},
        "style": {"max_words_per_line": 4, "auto_scale_font": False},
    },
    # 8. Diarization with custom colors
    "diarization_colors": {
        "diarization": {"enabled": True, "colors": ["yellow", "white"]},
        "style": {"auto_scale_font": False},
        "animation": {"enabled": False},
    },
    # 9. Diarization with speaker labels kept
    "diarization_labels_kept": {
        "diarization": {
            "enabled": True,
            "colors": ["red", "green"],
            "keep_speaker_labels": True,
        },
        "animation": {"enabled": False},
        "style": {"auto_scale_font": False},
    },
    # 10. Diarization with speaker labels hidden
    "diarization_labels_hidden": {
        "diarization": {
            "enabled": True,
            "colors": ["red", "green"],
            "keep_speaker_labels": False,
        },
        "animation": {"enabled": False},
        "style": {"auto_scale_font": False},
    },
    # 11. Large font, no animation
    "large_font": {
        "style": {"font_size": 200, "auto_scale_font": False},
        "animation": {"enabled": False},
    },
    # 12. Small font with animation
    "small_font_animated": {
        "style": {"font_size": 80, "auto_scale_font": True},
        "animation": {"enabled": True},
    },
    # 13. Custom outline
    "thick_outline": {
        "style": {
            "outline_thickness": 20,
            "outline_color": "blue",
            "auto_scale_font": False,
        },
        "animation": {"enabled": False},
    },
    # 14. Bottom position
    "bottom_position": {
        "style": {"verticle_position": 0.85, "auto_scale_font": False},
        "animation": {"enabled": False},
    },
    # 15. Top position
    "top_position": {
        "style": {"verticle_position": 0.15, "auto_scale_font": False},
        "animation": {"enabled": False},
    },
    # 16. Everything combined — animation, scaling, 2 words, diarization
    "kitchen_sink": {
        "animation": {"enabled": True, "keyframes": 15},
        "style": {"font_size": 120, "auto_scale_font": True, "max_words_per_line": 2},
        "diarization": {"enabled": True, "colors": ["yellow", "white", "red"]},
    },
}
