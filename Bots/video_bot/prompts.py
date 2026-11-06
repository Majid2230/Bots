"""
Ready-made prompts for videos about Saudi Arabia.

A "prompt" is the text description you give the AI model. The model reads it
and tries to make a video that matches. Good prompts describe:
  1. the subject   (what is in the shot)
  2. the place     (where, what it looks like)
  3. the camera    (drone shot, close-up, slow pan...)
  4. the light     (golden hour, night, soft morning light...)
  5. the mood/style (cinematic, documentary, calm...)

Run `python prompts.py` to print the list with their short names.
"""

PROMPTS = {
    "alula": (
        "Cinematic drone shot slowly circling Elephant Rock in AlUla, Saudi Arabia, "
        "at golden hour. Warm orange sandstone, long soft shadows across the desert "
        "floor, a few people sitting on rugs near small lanterns. Calm, majestic, "
        "documentary style, 4K film look."
    ),
    "hegra": (
        "Slow forward dolly shot towards the ancient Nabataean tomb of Qasr al-Farid "
        "in Hegra, AlUla, Saudi Arabia, carved into a single sandstone boulder. "
        "Early morning light, clear blue sky, fine sand drifting in the wind. "
        "Documentary, highly detailed."
    ),
    "riyadh_night": (
        "Aerial night time-lapse over the Riyadh skyline, Saudi Arabia, with the "
        "Kingdom Centre tower glowing and car light trails flowing along King Fahd "
        "Road. Modern city, deep blue sky, cinematic."
    ),
    "edge_of_world": (
        "Epic drone shot flying off the edge of the towering Tuwaiq escarpment cliffs "
        "known as the Edge of the World near Riyadh, Saudi Arabia. Vast flat desert "
        "plain far below, hazy sunset, dramatic scale."
    ),
    "jeddah_albalad": (
        "Steady walking shot through a narrow lane of Al-Balad, the historic old town "
        "of Jeddah, Saudi Arabia. Tall coral-stone houses with carved wooden roshan "
        "balconies, warm late-afternoon light, a small shop selling spices. "
        "Authentic, documentary."
    ),
    "red_sea": (
        "Underwater shot gliding over a vibrant coral reef in the Red Sea off the coast "
        "of Saudi Arabia. Clear turquoise water, colorful fish, sunbeams shining "
        "through the surface. Calm, nature documentary."
    ),
    "camels_dunes": (
        "Wide shot of a camel caravan walking in a line across the red sand dunes of "
        "the Empty Quarter (Rub' al Khali), Saudi Arabia, at sunset. Long shadows, "
        "wind blowing sand off the dune crests. Cinematic, slow motion."
    ),
    "diriyah": (
        "Slow pan across the restored mud-brick palaces of At-Turaif in Diriyah, "
        "Saudi Arabia, at blue hour. Warm lights glowing in the windows, palm trees, "
        "elegant and peaceful."
    ),
    "qahwa": (
        "Close-up of a hand pouring Saudi Arabic coffee from a brass dallah into a "
        "small finjan cup, next to a plate of dates on a traditional rug. Steam "
        "rising, soft warm light, shallow depth of field. Welcoming, hospitality."
    ),
    "asir_mountains": (
        "Drone shot over the green terraced mountains of Asir near Abha, Saudi Arabia, "
        "revealing the colorful stone towers of Rijal Almaa village. Clouds drifting "
        "through the valleys, morning light, cinematic."
    ),
}

DEFAULT = "alula"


def get_prompt(name_or_text: str) -> str:
    """Return a saved prompt by its short name, or the text itself if it is not a name."""
    return PROMPTS.get(name_or_text, name_or_text)


if __name__ == "__main__":
    for key, text in PROMPTS.items():
        print(f"[{key}]\n  {text}\n")
