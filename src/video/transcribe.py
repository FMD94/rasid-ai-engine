from pathlib import Path
from moviepy import VideoFileClip

# MVP: we extract audio to a .wav file.
# Speech-to-text will be Phase 1.5/Phase 3 depending on what API you choose.
def extract_audio(video_path: str, out_wav_path: str) -> str:
    out = Path(out_wav_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    clip = VideoFileClip(video_path)
    if clip.audio is None:
        return ""

    clip.audio.write_audiofile(str(out), logger=None)
    clip.close()
    return str(out)

