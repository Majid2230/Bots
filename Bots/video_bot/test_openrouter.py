"""
Make ONE video clip with OpenRouter.   (For a long film, use make_film.py)

OpenRouter is a website that gives you ONE account and ONE API key to use many
AI models from many companies. You pay per second of video.

Before you run this:
  1. Make an account at https://openrouter.ai and add a little credit ($5 is plenty to test).
  2. Create an API key at https://openrouter.ai/settings/keys
  3. Put the key in your terminal:   export OPENROUTER_API_KEY="sk-or-..."
     (Windows PowerShell:            $env:OPENROUTER_API_KEY="sk-or-...")

Examples:
  python test_openrouter.py --list                         # show video models + prices
  python test_openrouter.py                                # MiniMax H3, AlUla prompt
  python test_openrouter.py --prompt red_sea --duration 5
  python test_openrouter.py --model alibaba/wan-2.7 --prompt riyadh_night --resolution 720p
"""

import argparse
import os
import sys
import time
from pathlib import Path

import requests

from prompts import DEFAULT, get_prompt

API = "https://openrouter.ai/api/v1"
# MiniMax H3 is the best-ranked OPEN-WEIGHTS video model (Nov 2026).
DEFAULT_MODEL = "minimax/hailuo-3"
OUT_DIR = Path(__file__).parent / "outputs"


class RequestRefused(Exception):
    """OpenRouter said no to the request (bad settings, no credit, blocked prompt...)."""


def headers() -> dict:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        sys.exit("Missing OPENROUTER_API_KEY. See the instructions at the top of test_openrouter.py.")
    return {"Authorization": f"Bearer {key}"}


def get_models() -> dict:
    """All OpenRouter video models, as {model_id: details}. Free, no key needed."""
    data = requests.get(f"{API}/videos/models", timeout=60).json()["data"]
    return {m["id"]: m for m in data}


def list_models() -> None:
    """Print every video model OpenRouter offers, with price per second."""
    for m in get_models().values():
        price = m.get("pricing_skus") or {}
        price_txt = ", ".join(f"{k}=${v}" for k, v in price.items()) or "?"
        print(f"{m['id']:<40} durations={m.get('supported_durations')} "
              f"res={m.get('supported_resolutions')} audio={m.get('generate_audio')}  price/s: {price_txt}")


def run_job(body: dict, out: Path) -> float | None:
    """Send one video request, wait until it is done, save the .mp4 to `out`. Returns the cost in $."""
    # Step 1: ask for a video. OpenRouter answers right away with a job id.
    r = requests.post(f"{API}/videos", json=body, headers=headers(), timeout=120)
    if r.status_code >= 400:
        raise RequestRefused(f"{r.status_code}: {r.text}")
    job = r.json()
    print(f"  job {job['id']} started (usually 1-5 minutes)")

    # Step 2: check every 10 seconds until the video is ready.
    started = time.time()
    while True:
        time.sleep(10)
        job = requests.get(job["polling_url"], headers=headers(), timeout=60).json()
        status = job.get("status")
        print(f"  {int(time.time() - started):>4}s  {status}")
        if status == "completed":
            break
        if status in ("failed", "cancelled", "expired"):
            raise RequestRefused(f"job {status}: {job.get('error')}")

    # Step 3: download the finished video.
    out.parent.mkdir(parents=True, exist_ok=True)
    video = requests.get(job["unsigned_urls"][0], headers=headers(), timeout=300)
    video.raise_for_status()
    out.write_bytes(video.content)
    return (job.get("usage") or {}).get("cost")


def main() -> None:
    p = argparse.ArgumentParser(description="Generate one video clip with OpenRouter")
    p.add_argument("--list", action="store_true", help="list video models and prices, then exit")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--prompt", default=DEFAULT, help="a short name from prompts.py, or your own text")
    p.add_argument("--duration", type=int, default=5, help="seconds (check --list for allowed values)")
    p.add_argument("--resolution", default=None, help="e.g. 480p, 720p, 1080p (default: model's default)")
    p.add_argument("--aspect-ratio", default="16:9", help="16:9 for YouTube, 9:16 for TikTok/Reels/Shorts")
    p.add_argument("--no-audio", action="store_true", help="make a silent video")
    a = p.parse_args()

    if a.list:
        list_models()
        return

    body = {"model": a.model, "prompt": get_prompt(a.prompt), "duration": a.duration,
            "aspect_ratio": a.aspect_ratio, "generate_audio": not a.no_audio}
    if a.resolution:
        body["resolution"] = a.resolution
    print(f"Model : {body['model']}\nPrompt: {body['prompt']}\n")

    out = OUT_DIR / f"openrouter_{a.model.replace('/', '_')}_{int(time.time())}.mp4"
    try:
        cost = run_job(body, out)
    except RequestRefused as e:
        sys.exit(f"Request refused: {e}")
    print(f"\nSaved: {out}  ({out.stat().st_size / 1e6:.1f} MB)  cost: ${cost}")


if __name__ == "__main__":
    main()
