#TODO: update readme to get rid of openai and deepgram for now
#TODO: add moviepy comparison to the readme
#TODO: what happens if i dont pass in an animation?
#TODO: What happens if i pass in a bad animation, color, font, etc?
#TODO: need to figure out how to stop generating the Speaker labels because they're not needed probably
#TODO: I should have a configurable output path
#TODO: I should generate all temp files in a temp directory
#TODO: Need to fix benchmarking so that the moviepy captions are correct and not wack

import asyncio
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from beautiful_captions import process_video, add_captions, Video
from beautiful_captions import StyleConfig, AnimationConfig, CaptionConfig, DiarizationConfig
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip 

load_dotenv()

async def demo_transcription():
    # Configuration

    style = StyleConfig(
        font="Montserrat",
        color="white",
        font_size=140,
        outline_color="black",
        outline_thickness=2,
        verticle_position=0.5,  
        max_words_per_line=1,
        auto_scale_font=True,
    )
    
    animation = AnimationConfig(
        enabled=True,
        type="bounce",
        keyframes=10
    )
    
    diarization = DiarizationConfig(
        enabled=True,
        colors=["white", "yellow", "blue"],
        keep_speaker_labels=False  
    )
    
    config = CaptionConfig(style=style, animation=animation, diarization=diarization)

    # Method 1: Process video with automatic transcription
    output_path = await process_video(
        video_path="input.mp4",
        output_path="output.mp4",
        transcribe_with="assemblyai",
        api_key=os.getenv("ASSEMBLYAI_API_KEY"),
        config=config
    )
    print(f"Processed video saved to: {output_path}")

    # Method 2: Using existing SRT file with Beautiful Captions
    start_time = time.time()
    output_path = add_captions(
        video_path="input.mp4",
        srt_path="subtitles.srt",
        config=config
    )
    bc_time = time.time() - start_time
    print(f"Beautiful Captions processing time: {bc_time:.2f} seconds")
    print(f"Captioned video saved to: {output_path}")

    # MoviePy comparison
    start_time = time.time()
    video = VideoFileClip("input.mp4")
    generator = lambda txt: TextClip(txt, font='Montserrat', fontsize=200, color='white', stroke_color='black', stroke_width=2)
    subtitles = SubtitlesClip("subtitles.srt", generator)
    final = CompositeVideoClip([video, subtitles.set_position(('center', 'bottom'))])
    final.write_videofile("output_moviepy.mp4")
    moviepy_time = time.time() - start_time
    print(f"MoviePy processing time: {moviepy_time:.2f} seconds")
    
    # Print comparison
    print("\nSpeed Comparison:")
    print(f"Beautiful Captions: {bc_time:.2f}s")
    print(f"MoviePy: {moviepy_time:.2f}s")
    print(f"Beautiful Captions is {moviepy_time/bc_time:.1f}x faster than MoviePy")

    # # Method 3: Using existing SRT content
    # output_path = add_captions(
    #     video_path="input.mp4",
    #     srt_path="subtitles.srt",
    #     config=config
    # )
    # print(f"Captioned video saved to: {output_path}")

    # # Method 4: Object-oriented approach
    # video = Video("input.mp4", config=config)
    # await video.transcribe(
    #     service="assemblyai",
    #     api_key=os.getenv("ASSEMBLYAI_API_KEY")
    # )
    # output_path = video.add_captions()
    # print(f"Video with captions saved to: {output_path}")

if __name__ == "__main__":
    asyncio.run(demo_transcription())
