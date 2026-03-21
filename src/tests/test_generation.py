import os
from typing import Any

import pytest

from beautiful_captions import CaptionConfig, Video
from tests.base_config import CONFIGS, INPUT_VIDEO, SUBTITLE_CONTENT


class TestGeneration:
    """Parameterized video generation tests using all CONFIGS entries."""

    @pytest.mark.parametrize("name,kwargs", list(CONFIGS.items()), ids=list(CONFIGS.keys()))
    def test_generate_video(self, name: str, kwargs: dict[str, Any]):
        os.makedirs("./output", exist_ok=True)
        output = f"./output/{name}.mp4"
        video = Video(INPUT_VIDEO, config=CaptionConfig(**kwargs))
        _ = video.add_captions(
            srt_content=SUBTITLE_CONTENT,
            output_path=output,
            add_styling=True,
            cuda=False,
        )
        assert os.path.exists(output)
        assert os.path.getsize(output) > 0
