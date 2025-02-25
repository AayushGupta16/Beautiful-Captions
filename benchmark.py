import os
import time
import psutil
import pysrt
import threading
import statistics
from pathlib import Path
from typing import Dict, List
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, VideoClip
from beautiful_captions import add_captions, CaptionConfig, StyleConfig, AnimationConfig

class ResourceMonitor:
    def __init__(self, interval: float = 0.1):
        self.interval = interval
        self.cpu_percentages: List[float] = []
        self.memory_usages: List[float] = []
        self.is_running = False
        self.process = psutil.Process()
        
    def start(self):
        self.is_running = True
        self.cpu_percentages = []
        self.memory_usages = []
        self.monitor_thread = threading.Thread(target=self._monitor)
        self.monitor_thread.start()
        
    def stop(self):
        self.is_running = False
        self.monitor_thread.join()
        
    def _monitor(self):
        # Initial CPU measurement (first call returns 0)
        self.process.cpu_percent()
        
        while self.is_running:
            # CPU usage as percentage
            cpu = self.process.cpu_percent()
            # Memory usage in MB
            memory = self.process.memory_info().rss / (1024 * 1024)
            
            self.cpu_percentages.append(cpu)
            self.memory_usages.append(memory)
            
            time.sleep(self.interval)
    
    def get_stats(self) -> Dict:
        if not self.cpu_percentages or not self.memory_usages:
            return {
                "avg_cpu_percent": 0,
                "peak_cpu_percent": 0,
                "avg_memory_mb": 0,
                "peak_memory_mb": 0
            }
            
        # Remove the first few measurements as they might be inaccurate
        cpu_samples = self.cpu_percentages[5:]
        mem_samples = self.memory_usages[5:]
        
        return {
            "avg_cpu_percent": statistics.mean(cpu_samples),
            "peak_cpu_percent": max(cpu_samples),
            "avg_memory_mb": statistics.mean(mem_samples),
            "peak_memory_mb": max(mem_samples)
        }

def benchmark_function(func, *args, **kwargs) -> Dict:
    """
    Measures execution time, CPU, and memory usage of a function.
    """
    monitor = ResourceMonitor()
    
    # Start monitoring
    monitor.start()
    start_time = time.time()
    
    # Run the function
    func(*args, **kwargs)
    
    # Stop monitoring
    end_time = time.time()
    monitor.stop()
    
    # Get stats
    stats = monitor.get_stats()
    stats["time_seconds"] = end_time - start_time
    
    return stats

def bounce_scale(t, total_duration, min_scale=80, max_scale=100):
    """
    Very rough replication of "bounce" scaling by interpolating scale over time
    """
    half_duration = total_duration / 2
    if t < half_duration:
        # Scale down
        progress = t / half_duration
        return max_scale - (max_scale - min_scale) * progress
    else:
        # Scale up
        progress = (t - half_duration) / half_duration
        return min_scale + (max_scale - min_scale) * progress

def run_beautiful_captions(test_video, output_path, animation_enabled):
    """
    Runs beautiful_captions package with animation toggled on/off
    """
    caption_config = CaptionConfig(
        style=StyleConfig(font_size=100),
        animation=AnimationConfig(enabled=animation_enabled, type="bounce", keyframes=10),
    )

    add_captions(
        video_path=test_video,
        srt_path="subtitles.srt",
        output_path=output_path,
        config=caption_config
    )

def run_moviepy(test_video, output_video, animation_enabled):
    """
    Creates subtitles in MoviePy using the SRT file, with or without a simple "bounce" effect.
    """
    clip = VideoFileClip(test_video)
    
    # Read SRT file
    subs = pysrt.open("subtitles.srt")
    subtitle_clips = []
    
    for sub in subs:
        start_time = sub.start.ordinal / 1000  # Convert to seconds
        end_time = sub.end.ordinal / 1000
        duration = end_time - start_time
        
        if animation_enabled:
            def make_frame(t):
                scale_factor = bounce_scale(t % duration, duration, 80, 100)
                txt_clip = (TextClip(sub.text, font="Montserrat", fontsize=scale_factor, 
                                   color="white", stroke_color="black", stroke_width=2,
                                   method='caption', size=(clip.w, None))
                          .set_position(('center', 'center')))
                return txt_clip.get_frame(0)
            
            animated_txt = VideoClip(make_frame, duration=duration)
            animated_txt = animated_txt.set_start(start_time)
            subtitle_clips.append(animated_txt)
        else:
            txt = (TextClip(sub.text, font="Montserrat", fontsize=100, 
                          color="white", stroke_color="black", stroke_width=2,
                          method='caption', size=(clip.w, None))
                  .set_start(start_time)
                  .set_duration(duration)
                  .set_position(('center', 'center')))
            subtitle_clips.append(txt)
    
    # Combine video with all subtitle clips
    final = CompositeVideoClip([clip] + subtitle_clips)
    final.write_videofile(output_video, codec="libx264", audio_codec="aac")

def run_ffmpeg(test_video, output_video):
    """
    Creates subtitles using FFmpeg's built-in subtitle filter.
    Note: animation_enabled is ignored as FFmpeg doesn't support animation.
    """
    import subprocess
    
    # First convert SRT to ASS format as FFmpeg handles ASS better
    srt_path = "subtitles.srt"
    ass_path = "temp_subtitles.ass"
    
    cmd_convert = [
        "ffmpeg", "-i", srt_path,
        "-y",  # Overwrite output file
        ass_path
    ]
    
    # Then combine video with subtitles
    cmd_subtitle = [
        "ffmpeg",
        "-i", test_video,
        "-vf", f"ass={ass_path}",
        "-c:a", "copy",
        "-y",
        output_video
    ]
    
    try:
        # Convert SRT to ASS
        subprocess.run(cmd_convert, check=True, capture_output=True)
        
        # Add subtitles to video
        subprocess.run(cmd_subtitle, check=True, capture_output=True)
    finally:
        # Clean up temporary ASS file
        if os.path.exists(ass_path):
            os.remove(ass_path)

def format_stats(stats: Dict) -> str:
    """Format benchmark stats for display"""
    return (
        f"Time: {stats['time_seconds']:.1f}s, "
        f"Avg CPU: {stats['avg_cpu_percent']:.1f}%, "
        f"Peak CPU: {stats['peak_cpu_percent']:.1f}%, "
        f"Avg RAM: {stats['avg_memory_mb']:.0f}MB, "
        f"Peak RAM: {stats['peak_memory_mb']:.0f}MB"
    )

def print_comparison_table(results: Dict[str, Dict]):
    """Print a formatted comparison table of benchmark results"""
    # Find Beautiful Captions stats for relative comparison
    bc_stats = results["Beautiful Captions"]
    bc_time = bc_stats['time_seconds']
    bc_ram = bc_stats['avg_memory_mb']
    
    # Table headers
    headers = [
        "Method",
        "Time (s)",
        "vs FFmpeg",
        "vs BC",
        "RAM (MB)",
        "vs FFmpeg RAM",
        "vs BC RAM"
    ]
    
    # Calculate maximum width for each column
    rows = []
    for method, stats in results.items():
        vs_ffmpeg_time = stats['time_seconds'] / results['FFmpeg']['time_seconds']
        vs_bc_time = stats['time_seconds'] / bc_time
        vs_ffmpeg_ram = stats['avg_memory_mb'] / results['FFmpeg']['avg_memory_mb']
        vs_bc_ram = stats['avg_memory_mb'] / bc_ram
        
        rows.append([
            method,
            f"{stats['time_seconds']:.1f}",
            f"{vs_ffmpeg_time:.1f}x",
            f"{vs_bc_time:.1f}x",
            f"{stats['avg_memory_mb']:.0f}",
            f"{vs_ffmpeg_ram:.1f}x",
            f"{vs_bc_ram:.1f}x"
        ])
    
    # Get maximum width for each column
    widths = [max(len(str(row[i])) for row in [headers] + rows) for i in range(len(headers))]
    
    # Print table
    separator = "-" * (sum(widths) + len(widths) * 3 + 1)
    
    print("\n" + separator)
    print("| " + " | ".join(f"{header:<{widths[i]}}" for i, header in enumerate(headers)) + " |")
    print(separator)
    
    for row in rows:
        print("| " + " | ".join(f"{cell:<{widths[i]}}" for i, cell in enumerate(row)) + " |")
    
    print(separator + "\n")

def run_all_benchmarks():
    test_video = "input.mp4"
    
    # Create output directory if it doesn't exist
    output_dir = "benchmark_outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Define output paths
    bc_out_anim = os.path.join(output_dir, "bc_anim.mp4")
    moviepy_out_noanim = os.path.join(output_dir, "moviepy_noanim.mp4")
    moviepy_out_anim = os.path.join(output_dir, "moviepy_anim.mp4")
    ffmpeg_out = os.path.join(output_dir, "ffmpeg.mp4")

    print("\nRunning FFmpeg (Basic Subtitles)...")
    res_ffmpeg = benchmark_function(
        run_ffmpeg, test_video, ffmpeg_out
    )

    print("\nRunning Beautiful Captions (With Animation)...")
    res_bc_anim = benchmark_function(
        run_beautiful_captions, test_video, bc_out_anim, True
    )

    print("\nRunning MoviePy (No Animation)...")
    res_moviepy_noanim = benchmark_function(
        run_moviepy, test_video, moviepy_out_noanim, False
    )

    print("\nRunning MoviePy (With Animation)...")
    res_moviepy_anim = benchmark_function(
        run_moviepy, test_video, moviepy_out_anim, True
    )

    print("\n======== BENCHMARK RESULTS ========\n")
    print(f"FFmpeg              : {format_stats(res_ffmpeg)}")
    print(f"Beautiful Captions (Bounce)   : {format_stats(res_bc_anim)}")
    print(f"MoviePy (No Anim)            : {format_stats(res_moviepy_noanim)}")
    print(f"MoviePy (Bounce)             : {format_stats(res_moviepy_anim)}")
    print("\n===================================")
    print(f"\nOutput videos saved in: {output_dir}/")

if __name__ == "__main__":
    run_all_benchmarks()
