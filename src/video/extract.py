from pathlib import Path
import cv2
import math
import os


def extract_frames(video_path: str, out_dir: str, fps: float = 1.0, max_frames: int = 30) -> list[str]:
    """
    Extract frames from a video at `fps` frames per second (approx).
    Returns list of saved frame paths.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    video_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_interval = max(1, int(math.floor(video_fps / fps)))

    frame_paths = []
    idx = 0
    saved = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if idx % frame_interval == 0:
            frame_file = out / f"frame_{saved:04d}.jpg"
            cv2.imwrite(str(frame_file), frame)
            frame_paths.append(str(frame_file))
            saved += 1
            if saved >= max_frames:
                break

        idx += 1

    cap.release()
    return frame_paths
