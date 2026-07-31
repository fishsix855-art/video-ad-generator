"""
Subtitle Generator - Uses faster-whisper for speech-to-text SRT generation
"""
import os
import logging

logger = logging.getLogger(__name__)


def generate_srt(audio_path: str, output_srt: str = None, language: str = "zh") -> dict:
    """
    Generate SRT subtitle file from audio/video using faster-whisper.
    
    Args:
        audio_path: Path to audio or video file
        output_srt: Output SRT path (auto-generated if None)
        language: Language code (default: zh)
    
    Returns:
        {"success": bool, "srt_path": str, "segments": list, "message": str}
    """
    if output_srt is None:
        output_srt = os.path.splitext(audio_path)[0] + ".srt"
    
    try:
        from faster_whisper import WhisperModel
        
        model_size = "small"
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        
        segments, info = model.transcribe(audio_path, language=language, beam_size=5)
        
        srt_lines = []
        idx = 1
        for segment in segments:
            start = segment.start
            end = segment.end
            text = segment.text.strip()
            
            start_ts = _format_timestamp(start)
            end_ts = _format_timestamp(end)
            
            srt_lines.append(str(idx))
            srt_lines.append(f"{start_ts} --> {end_ts}")
            srt_lines.append(text)
            srt_lines.append("")
            idx += 1
        
        with open(output_srt, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_lines))
        
        logger.info(f"Subtitle generated: {output_srt} ({idx-1} segments)")
        return {
            "success": True,
            "srt_path": output_srt,
            "segments_count": idx - 1,
            "message": f"Generated {idx-1} subtitle segments",
        }
    
    except ImportError:
        logger.warning("faster-whisper not installed, using fallback dummy SRT")
        return _generate_dummy_srt(output_srt)
    except Exception as e:
        logger.error(f"Subtitle generation failed: {e}")
        return {"success": False, "error": str(e)}


def _generate_dummy_srt(output_srt: str) -> dict:
    """Generate a placeholder SRT when whisper is unavailable."""
    dummy = """1
00:00:00,000 --> 00:00:05,000
[Subtitle placeholder - install faster-whisper for real transcription]

"""
    with open(output_srt, "w", encoding="utf-8") as f:
        f.write(dummy)
    return {
        "success": True,
        "srt_path": output_srt,
        "segments_count": 1,
        "message": "Dummy subtitle generated (faster-whisper not available)",
    }


def _format_timestamp(seconds: float) -> str:
    """Convert float seconds to SRT timestamp format: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def add_subtitle_to_video(video_path: str, output_path: str = None) -> dict:
    """
    Full pipeline: extract audio -> generate SRT -> burn subtitles into video.
    Returns the path to the subtitled video.
    """
    if output_path is None:
        base = os.path.splitext(video_path)[0]
        output_path = base + "_subtitled.mp4"
    
    # Step 1: Generate SRT from video audio
    srt_path = os.path.splitext(video_path)[0] + ".srt"
    srt_result = generate_srt(video_path, srt_path)
    
    if not srt_result["success"]:
        return srt_result
    
    # Step 2: Burn subtitles using FFmpeg (via video_editor)
    try:
        from app.services.video_editor import VideoEditor
        editor = VideoEditor()
        editor.add_subtitle(video_path=video_path, srt_path=srt_path, output_path=output_path)
        return {
            "success": True,
            "output_path": output_path,
            "srt_path": srt_path,
            "segments_count": srt_result.get("segments_count", 0),
            "message": f"Subtitled video saved to {output_path}",
        }
    except Exception as e:
        return {
            "success": False,
            "srt_path": srt_path,
            "error": f"FFmpeg subtitle burning failed: {e}",
            "message": "SRT generated but FFmpeg burning failed",
        }
