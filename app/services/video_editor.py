"""
Video Editor - FFmpeg trim/concat/subtitle
"""
import os, subprocess, logging

logger = logging.getLogger(__name__)


def _get_ffmpeg():
    try:
        from app.config import config
        return config.app.get('ffmpeg_path', 'ffmpeg')
    except:
        return 'ffmpeg'


class VideoEditor:
    def trim(self, input_path: str, output_path: str, start: float, end: float = None):
        cmd = [_get_ffmpeg(), '-y', '-i', input_path, '-ss', str(start)]
        if end:
            cmd += ['-to', str(end)]
        cmd += ['-c', 'copy', output_path]
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path

    def concat(self, inputs: list[str], output_path: str):
        list_file = output_path + '.txt'
        with open(list_file, 'w') as f:
            for inp in inputs:
                f.write(f"file '{inp}'\n")
        cmd = [_get_ffmpeg(), '-y', '-f', 'concat', '-safe', '0', '-i', list_file, '-c', 'copy', output_path]
        subprocess.run(cmd, capture_output=True, check=True)
        os.remove(list_file)
        return output_path

    def add_subtitle(self, video_path: str, srt_path: str, output_path: str):
        cmd = [_get_ffmpeg(), '-y', '-i', video_path, '-vf', f"subtitles={srt_path}", '-c:a', 'copy', output_path]
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path
