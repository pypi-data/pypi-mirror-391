# -*- coding: utf-8 -*-
"""
Video editing tool using FFmpeg.

This tool provides video editing capabilities including speed adjustment, trimming,
format conversion, and more using FFmpeg.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import List, Optional

from massgen.tool._result import ExecutionResult, TextContent


def _validate_path_access(path: Path, allowed_paths: Optional[List[Path]] = None) -> None:
    """
    Validate that a path is within allowed directories.

    Args:
        path: Path to validate
        allowed_paths: List of allowed base paths (optional)

    Raises:
        ValueError: If path is not within allowed directories
    """
    if not allowed_paths:
        return  # No restrictions

    for allowed_path in allowed_paths:
        try:
            path.relative_to(allowed_path)
            return  # Path is within this allowed directory
        except ValueError:
            continue

    raise ValueError(f"Path not in allowed directories: {path}")


def _check_ffmpeg_installed() -> bool:
    """
    Check if FFmpeg is installed.

    Returns:
        True if FFmpeg is installed, False otherwise
    """
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


async def speed_up_video(
    input_video: str,
    speed_factor: float = 2.0,
    output_filename: Optional[str] = None,
    allowed_paths: Optional[List[str]] = None,
    agent_cwd: Optional[str] = None,
) -> ExecutionResult:
    """
    Speed up a video by a specified factor.

    This tool uses FFmpeg to increase video playback speed while maintaining audio pitch.
    Useful for condensing long recordings into shorter, faster-paced demos.

    Args:
        input_video: Path to input video file
                    - Relative path: Resolved relative to workspace
                    - Absolute path: Must be within allowed directories
        speed_factor: Speed multiplier (default: 2.0)
                     - 2.0 = 2x speed (twice as fast)
                     - 4.0 = 4x speed
                     - 0.5 = 0.5x speed (slow motion)
                     - For 10min → 1.5min: use speed_factor=6.67
        output_filename: Output filename (default: "{input}_speed{factor}x.mp4")
        allowed_paths: List of allowed base paths for validation (optional)
        agent_cwd: Agent's current working directory (automatically injected, optional)

    Returns:
        ExecutionResult containing:
        - success: Whether operation succeeded
        - operation: "speed_up_video"
        - input_video: Path to input video
        - output_video: Path to output video
        - speed_factor: Speed multiplier used
        - original_duration: Original video duration in seconds
        - new_duration: New video duration in seconds
        - file_size_bytes: Output file size

    Examples:
        # Speed up video 2x
        speed_up_video("demo.mp4", speed_factor=2.0)
        → Creates demo_speed2x.mp4

        # Condense 10min video to 1.5min
        speed_up_video("long_demo.mp4", speed_factor=6.67)
        → Creates long_demo_speed6.67x.mp4 (~1.5 minutes)

    Prerequisites:
        - FFmpeg must be installed: brew install ffmpeg (macOS)

    Note:
        - Audio is sped up using atempo filter (maintains pitch quality)
        - Maximum atempo is 2.0 per filter, so we chain filters for higher speeds
        - Video uses setpts filter for smooth playback
    """
    try:
        # Convert allowed_paths from strings to Path objects
        allowed_paths_list = [Path(p) for p in allowed_paths] if allowed_paths else None

        # Resolve base directory
        base_dir = Path(agent_cwd) if agent_cwd else Path.cwd()

        # Resolve input video path
        if Path(input_video).is_absolute():
            input_path = Path(input_video).resolve()
        else:
            input_path = (base_dir / input_video).resolve()

        # Validate input path
        _validate_path_access(input_path, allowed_paths_list)

        if not input_path.exists():
            result = {
                "success": False,
                "operation": "speed_up_video",
                "error": f"Input video does not exist: {input_path}",
            }
            return ExecutionResult(
                output_blocks=[TextContent(data=json.dumps(result, indent=2))],
            )

        # Check FFmpeg
        if not _check_ffmpeg_installed():
            result = {
                "success": False,
                "operation": "speed_up_video",
                "error": "FFmpeg is not installed. Install with: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)",
            }
            return ExecutionResult(
                output_blocks=[TextContent(data=json.dumps(result, indent=2))],
            )

        # Validate speed factor
        if speed_factor <= 0:
            result = {
                "success": False,
                "operation": "speed_up_video",
                "error": f"Invalid speed factor: {speed_factor}. Must be > 0",
            }
            return ExecutionResult(
                output_blocks=[TextContent(data=json.dumps(result, indent=2))],
            )

        # Generate output filename
        if output_filename:
            output_path = base_dir / output_filename
        else:
            output_path = base_dir / f"{input_path.stem}_speed{speed_factor}x.mp4"

        # Build FFmpeg command
        # Video speed: setpts filter
        video_filter = f"setpts={1/speed_factor}*PTS"

        # Audio speed: atempo filter (chain multiple for speeds > 2x)
        # atempo supports 0.5 to 2.0, so we chain filters for higher speeds
        audio_filters = []
        remaining_speed = speed_factor

        while remaining_speed > 2.0:
            audio_filters.append("atempo=2.0")
            remaining_speed /= 2.0

        if remaining_speed > 1.0:
            audio_filters.append(f"atempo={remaining_speed:.2f}")

        audio_filter = ",".join(audio_filters) if audio_filters else f"atempo={speed_factor:.2f}"

        # FFmpeg command
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", str(input_path),
            "-filter:v", video_filter,
            "-filter:a", audio_filter,
            "-y",  # Overwrite output
            str(output_path),
        ]

        # Run FFmpeg
        try:
            result_proc = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result_proc.returncode != 0:
                result = {
                    "success": False,
                    "operation": "speed_up_video",
                    "error": f"FFmpeg failed with exit code {result_proc.returncode}",
                    "ffmpeg_stderr": result_proc.stderr,
                }
                return ExecutionResult(
                    output_blocks=[TextContent(data=json.dumps(result, indent=2))],
                )

            # Get output video duration
            probe_cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(output_path),
            ]

            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=10)
            new_duration = float(probe_result.stdout.strip()) if probe_result.returncode == 0 else 0

            # Compile result
            result = {
                "success": True,
                "operation": "speed_up_video",
                "input_video": str(input_path),
                "output_video": str(output_path),
                "speed_factor": speed_factor,
                "original_duration_seconds": round(duration, 2),
                "new_duration_seconds": round(new_duration, 2) if new_duration > 0 else round(duration / speed_factor, 2),
                "file_size_bytes": os.path.getsize(output_path),
            }

            return ExecutionResult(
                output_blocks=[TextContent(data=json.dumps(result, indent=2))],
            )

        except subprocess.TimeoutExpired:
            result = {
                "success": False,
                "operation": "speed_up_video",
                "error": "FFmpeg processing timed out after 300 seconds",
            }
            return ExecutionResult(
                output_blocks=[TextContent(data=json.dumps(result, indent=2))],
            )

    except Exception as e:
        result = {
            "success": False,
            "operation": "speed_up_video",
            "error": f"Failed to speed up video: {str(e)}",
        }
        return ExecutionResult(
            output_blocks=[TextContent(data=json.dumps(result, indent=2))],
        )
