"""
Make a LONG film from a story file.

AI video models can only make short clips (about 5-30 seconds each). To make a
long film, this script:
  1. reads your story file: a list of scenes (see stories/saudi_journey.txt),
  2. makes one clip per scene with OpenRouter or Hugging Face,
  3. joins all the clips into one film with ffmpeg (a free video tool),
  4. optionally puts background music under the whole film.

It saves every clip as it goes. If something fails, or you don't like one
scene, just run the same command again: finished scenes are skipped, so you
don't pay for them twice. Use --redo 3 to make scene 3 again.

Examples:
  python make_film.py stories/saudi_journey.txt --dry-run       # show plan + cost, make nothing
  python make_film.py stories/saudi_journey.txt                 # make the film
  python make_film.py stories/saudi_journey.txt --redo 2,5      # remake scenes 2 and 5
  python make_film.py stories/saudi_journey.txt --music oud.mp3 # add background music

You need ffmpeg installed:  https://ffmpeg.org/download.html
(Windows: `winget install ffmpeg`, Mac: `brew install ffmpeg`).
"""

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).parent
FILMS_DIR = HERE / "films"
FPS = 24


# ---------------------------------------------------------------- story file

@dataclass
class Scene:
    number: int
    seconds: int
    text: str
    continue_shot: bool  # start from the last frame of the previous scene


@dataclass
class Story:
    title: str = "My Film"
    backend: str = "openrouter"          # openrouter or huggingface
    model: str = "minimax/hailuo-3"
    style: str = ""
    aspect: str = "16:9"
    resolution: str | None = None
    audio: bool = True
    references: list[str] = field(default_factory=list)
    scenes: list[Scene] = field(default_factory=list)

    @property
    def slug(self) -> str:
        return re.sub(r"[^a-z0-9]+", "_", self.title.lower()).strip("_") or "film"


SCENE_RE = re.compile(r"^\[\s*(\d+)\s*(?:s|sec|seconds)?\s*(continue)?\s*\]\s*(.*)$", re.I)


def read_story(path: Path) -> Story:
    story = Story()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = SCENE_RE.match(line)
        if m:
            story.scenes.append(Scene(len(story.scenes) + 1, int(m.group(1)), m.group(3), bool(m.group(2))))
        elif not story.scenes and ":" in line:
            key, value = (s.strip() for s in line.split(":", 1))
            key = key.upper()
            if key == "TITLE":
                story.title = value
            elif key == "BACKEND":
                story.backend = value.lower()
            elif key == "MODEL":
                story.model = value
            elif key == "STYLE":
                story.style = value
            elif key == "ASPECT":
                story.aspect = value
            elif key == "RESOLUTION":
                story.resolution = value or None
            elif key == "AUDIO":
                story.audio = value.lower() in ("yes", "true", "on", "1")
            elif key == "REFERENCE":
                story.references.append(value)
            else:
                sys.exit(f"Unknown setting '{key}' in {path}")
        elif story.scenes:
            story.scenes[-1].text += " " + line  # a scene can continue on the next lines
        else:
            sys.exit(f"Don't understand this line in {path}:\n  {raw}")
    if not story.scenes:
        sys.exit(f"No scenes found in {path}. Scenes look like:  [8] A drone shot over ...")
    if story.backend not in ("openrouter", "huggingface"):
        sys.exit("BACKEND must be 'openrouter' or 'huggingface'")
    return story


def full_prompt(story: Story, scene: Scene) -> str:
    return f"{scene.text.rstrip('. ')}. {story.style}".strip() if story.style else scene.text


# ---------------------------------------------------------------- ffmpeg helpers

def need_ffmpeg() -> None:
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        sys.exit("ffmpeg is not installed. See https://ffmpeg.org/download.html")


def ff(*args: str) -> None:
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams",
                          "-show_format", str(path)], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def last_frame(video: Path, jpg: Path) -> Path:
    ff("-sseof", "-0.5", "-i", str(video), "-update", "1", "-q:v", "2", str(jpg))
    return jpg


def image_as_url(path_or_url: str) -> str:
    """Web links are sent as they are; files on your computer are packed into the request."""
    if path_or_url.startswith(("http://", "https://", "data:")):
        return path_or_url
    p = Path(path_or_url)
    if not p.is_absolute():
        p = HERE / p
    mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def stitch(clips: list[Path], work: Path, out: Path, music: Path | None, music_volume: float) -> None:
    """Make all clips the same size/speed/sound format, then glue them together."""
    first = next(s for s in probe(clips[0])["streams"] if s["codec_type"] == "video")
    w, h = int(first["width"]) // 2 * 2, int(first["height"]) // 2 * 2
    vf = (f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
          f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,fps={FPS},setsar=1,format=yuv420p")
    norm_dir = work / "normalized"
    norm_dir.mkdir(exist_ok=True)
    parts = []
    for clip in clips:
        norm = norm_dir / clip.name
        has_audio = any(s["codec_type"] == "audio" for s in probe(clip)["streams"])
        audio_in = [] if has_audio else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        audio_map = ["-map", "0:v:0", "-map", "0:a:0" if has_audio else "1:a:0", "-shortest"]
        ff("-i", str(clip), *audio_in, *audio_map, "-vf", vf,
           "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k", str(norm))
        parts.append(norm)

    concat_list = work / "concat.txt"
    concat_list.write_text("".join(f"file '{p.resolve()}'\n" for p in parts), encoding="utf-8")
    joined = work / "joined.mp4" if music else out
    ff("-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", "-movflags", "+faststart", str(joined))

    if music:
        ff("-i", str(joined), "-stream_loop", "-1", "-i", str(music), "-filter_complex",
           f"[1:a]volume={music_volume}[m];[0:a][m]amix=inputs=2:duration=first:dropout_transition=0[a]",
           "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", str(out))


# ---------------------------------------------------------------- planning & cost

def plan_openrouter(story: Story) -> float | None:
    """Check the story against what the model supports. Returns estimated cost in $."""
    from test_openrouter import get_models

    models = get_models()
    if story.model not in models:
        sys.exit(f"Model '{story.model}' not found on OpenRouter. Run: python test_openrouter.py --list")
    info = models[story.model]

    allowed = info.get("supported_durations")
    if allowed:
        for s in story.scenes:
            if s.seconds not in allowed:
                fixed = min(allowed, key=lambda d: (abs(d - s.seconds), -d))
                print(f"  note: scene {s.number}: {s.seconds}s not allowed for this model -> using {fixed}s")
                s.seconds = fixed
    if info.get("supported_aspect_ratios") and story.aspect not in info["supported_aspect_ratios"]:
        sys.exit(f"ASPECT {story.aspect} not supported. Choose one of {info['supported_aspect_ratios']}")
    if story.resolution and info.get("supported_resolutions") and story.resolution not in info["supported_resolutions"]:
        sys.exit(f"RESOLUTION {story.resolution} not supported. Choose one of {info['supported_resolutions']}")
    if any(s.continue_shot for s in story.scenes) and "first_frame" not in (info.get("supported_frame_images") or []):
        print("  note: this model can't continue from a previous frame; 'continue' scenes become normal cuts")
        for s in story.scenes:
            s.continue_shot = False

    skus = info.get("pricing_skus") or {}
    per_sec = skus.get(f"duration_seconds_{story.resolution}") or skus.get("duration_seconds")
    if per_sec is None:  # price depends on resolution and we don't know the default -> assume the highest
        res_prices = [float(v) for k, v in skus.items() if k.startswith("duration_seconds_")]
        per_sec = max(res_prices) if res_prices else None
    if per_sec is None:
        return None
    total = sum(s.seconds for s in story.scenes) * float(per_sec)
    if story.references and skus.get("reference_images"):
        uses = sum(1 for s in story.scenes if not s.continue_shot)
        total += uses * len(story.references) * float(skus["reference_images"])
    return total


# ---------------------------------------------------------------- making clips

def make_clip_openrouter(story: Story, scene: Scene, prev_clip: Path | None, out: Path) -> float | None:
    from test_openrouter import RequestRefused, run_job

    body = {"model": story.model, "prompt": full_prompt(story, scene), "duration": scene.seconds,
            "aspect_ratio": story.aspect, "generate_audio": story.audio}
    if story.resolution:
        body["resolution"] = story.resolution
    if scene.continue_shot and prev_clip:
        frame = last_frame(prev_clip, out.with_suffix(".start.jpg"))
        body["frame_images"] = [{"type": "image_url", "image_url": {"url": image_as_url(str(frame))},
                                 "frame_type": "first_frame"}]
    elif story.references:
        body["input_references"] = [{"type": "image_url", "image_url": {"url": image_as_url(r)}}
                                    for r in story.references]
    try:
        return run_job(body, out)
    except RequestRefused as e:
        if "frame_images" not in body and "input_references" not in body:
            raise
        print(f"  images were refused ({e}); trying again with text only")
        body.pop("frame_images", None)
        body.pop("input_references", None)
        return run_job(body, out)


def make_clip_huggingface(story: Story, scene: Scene, prev_clip: Path | None, out: Path) -> None:
    from huggingface_hub import InferenceClient

    token = os.environ.get("HF_TOKEN")
    if not token:
        sys.exit("Missing HF_TOKEN. See the instructions at the top of test_huggingface.py.")
    client = InferenceClient(provider="auto", api_key=token, timeout=900)
    prompt = full_prompt(story, scene)
    if scene.continue_shot and prev_clip:
        frame = last_frame(prev_clip, out.with_suffix(".start.jpg"))
        try:
            video = client.image_to_video(str(frame), model=story.model, prompt=prompt)
        except ValueError:  # this model only does text-to-video
            video = client.text_to_video(prompt, model=story.model)
    else:
        video = client.text_to_video(prompt, model=story.model)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(video)


# ---------------------------------------------------------------- main

def main() -> None:
    p = argparse.ArgumentParser(description="Make a long film from a story file")
    p.add_argument("story", type=Path, help="your story file, e.g. stories/saudi_journey.txt")
    p.add_argument("--dry-run", action="store_true", help="only show the plan and the cost")
    p.add_argument("--yes", action="store_true", help="don't ask for confirmation")
    p.add_argument("--redo", default="", help="scene numbers to make again, e.g. 2,5")
    p.add_argument("--music", type=Path, help="mp3/wav to play under the whole film")
    p.add_argument("--music-volume", type=float, default=0.25, help="0.0 - 1.0 (default 0.25)")
    a = p.parse_args()

    need_ffmpeg()
    story = read_story(a.story)
    work = FILMS_DIR / story.slug
    clips_dir = work / "clips"

    print(f"\nFilm : {story.title}\nModel: {story.model} (via {story.backend})")
    cost = plan_openrouter(story) if story.backend == "openrouter" else None
    total_s = sum(s.seconds for s in story.scenes)
    print(f"\n{len(story.scenes)} scenes, about {total_s // 60}m {total_s % 60}s in total:")
    for s in story.scenes:
        done = " (already made)" if (clips_dir / f"scene_{s.number:02d}.mp4").exists() else ""
        how = "continues previous shot" if s.continue_shot else "new shot"
        print(f"  {s.number:>2}. [{s.seconds:>2}s, {how}] {s.text[:70]}{'...' if len(s.text) > 70 else ''}{done}")
    if story.backend == "huggingface":
        print("\n  note: on Hugging Face the model decides the clip length (often ~5s), and the price "
              "depends on the provider.")
    print(f"\nEstimated cost: {'$%.2f' % cost if cost is not None else 'unknown'} "
          "(scenes already made are free)")
    if a.dry_run:
        return
    if not a.yes and input("\nMake this film? [y/N] ").strip().lower() not in ("y", "yes"):
        return

    for n in filter(None, (x.strip() for x in a.redo.split(","))):
        (clips_dir / f"scene_{int(n):02d}.mp4").unlink(missing_ok=True)

    clips: list[Path] = []
    spent = 0.0
    for s in story.scenes:
        out = clips_dir / f"scene_{s.number:02d}.mp4"
        if out.exists():
            print(f"\nScene {s.number}: already made, skipping")
        else:
            print(f"\nScene {s.number}/{len(story.scenes)}: {s.text[:80]}")
            started = time.time()
            try:
                if story.backend == "openrouter":
                    spent += make_clip_openrouter(story, s, clips[-1] if clips else None, out) or 0
                else:
                    make_clip_huggingface(story, s, clips[-1] if clips else None, out)
            except Exception as e:
                sys.exit(f"\nScene {s.number} failed: {e}\nFix the problem and run the same command "
                         "again: finished scenes will be skipped.")
            print(f"  saved {out.name} in {int(time.time() - started)}s")
        clips.append(out)

    print("\nJoining all scenes into one film...")
    final = work / f"{story.slug}.mp4"
    stitch(clips, work, final, a.music, a.music_volume)
    length = float(probe(final)["format"]["duration"])
    print(f"\nDone! {final}\nLength: {int(length // 60)}m {int(length % 60)}s"
          + (f"   Spent this run: ${spent:.2f}" if spent else ""))


if __name__ == "__main__":
    main()
