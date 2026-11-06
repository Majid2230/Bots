"""
Make a video with Hugging Face "Inference Providers".

Hugging Face (huggingface.co) is the biggest website for open AI models: it is
where companies upload the model files ("weights"). You usually do NOT run the
model on your own computer (video models need a very expensive GPU). Instead,
Hugging Face sends your request to a partner company (fal, Replicate,
WaveSpeed...) that runs the model for you, and bills your Hugging Face account.

Before you run this:
  1. Make an account at https://huggingface.co
  2. Add credit: either buy credits, or get PRO ($9/month, includes $2 of credit/month).
     https://huggingface.co/settings/billing
  3. Create a token (type "Fine-grained", tick "Make calls to Inference Providers"):
     https://huggingface.co/settings/tokens
  4. Put it in your terminal:   export HF_TOKEN="hf_..."
     (Windows PowerShell:       $env:HF_TOKEN="hf_...")

Examples:
  python test_huggingface.py --list                        # which models are ready to use
  python test_huggingface.py                               # Wan 2.2, AlUla prompt
  python test_huggingface.py --model tencent/HunyuanVideo-1.5 --prompt camels_dunes
  # image-to-video (bring your own photo, the model animates it):
  python test_huggingface.py --model Lightricks/LTX-2 --image my_photo.jpg --prompt "slow drone push-in"

Note: MiniMax H3 (the best open model) cannot be called from this library yet.
Try it in the browser: https://huggingface.co/spaces/MiniMaxAI/MiniMax-H3-Turbo-Lora
or with test_openrouter.py (model minimax/hailuo-3).
"""

import argparse
import os
import sys
import time
from pathlib import Path

import requests
from huggingface_hub import InferenceClient

from prompts import DEFAULT, get_prompt

# Wan 2.2 (Alibaba): open weights, Apache-2.0 licence (the most permissive one).
DEFAULT_MODEL = "Wan-AI/Wan2.2-T2V-A14B"
OUT_DIR = Path(__file__).parent / "outputs"


def list_models() -> None:
    """Show the video models that a provider is running right now (ready to use)."""
    for task in ("text-to-video", "image-to-video"):
        print(f"\n=== {task} ===")
        url = (f"https://huggingface.co/api/models?pipeline_tag={task}&inference_provider=all"
               f"&sort=trendingScore&direction=-1&limit=25&expand[]=inferenceProviderMapping")
        for m in requests.get(url, timeout=60).json():
            live = [p["provider"] for p in (m.get("inferenceProviderMapping") or [])
                    if p.get("status") == "live"]
            print(f"{m['id']:<55} providers={live}")


def main() -> None:
    p = argparse.ArgumentParser(description="Generate a video with Hugging Face Inference Providers")
    p.add_argument("--list", action="store_true", help="list ready-to-use video models, then exit")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--provider", default="auto", help="fal-ai, replicate, wavespeed ... or auto")
    p.add_argument("--prompt", default=DEFAULT, help="a short name from prompts.py, or your own text")
    p.add_argument("--image", help="path to a photo -> image-to-video instead of text-to-video")
    p.add_argument("--seed", type=int, default=None, help="same seed + same prompt = similar video")
    a = p.parse_args()

    if a.list:
        list_models()
        return

    token = os.environ.get("HF_TOKEN")
    if not token:
        sys.exit("Missing HF_TOKEN. See the instructions at the top of this file.")

    client = InferenceClient(provider=a.provider, api_key=token, timeout=900)
    prompt = get_prompt(a.prompt)
    print(f"Model : {a.model}  (provider: {a.provider})\nPrompt: {prompt}\n"
          "Working... this usually takes 1-5 minutes, please wait.")

    started = time.time()
    if a.image:
        video = client.image_to_video(a.image, model=a.model, prompt=prompt, seed=a.seed)
    else:
        video = client.text_to_video(prompt, model=a.model, seed=a.seed)

    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / f"hf_{a.model.replace('/', '_')}_{int(time.time())}.mp4"
    out.write_bytes(video)
    print(f"\nSaved: {out}  ({len(video) / 1e6:.1f} MB) in {int(time.time() - started)}s")


if __name__ == "__main__":
    main()
