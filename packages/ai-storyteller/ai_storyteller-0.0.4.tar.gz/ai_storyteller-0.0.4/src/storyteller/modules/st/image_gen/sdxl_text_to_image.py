from __future__ import annotations

import os
import time
from pathlib import Path
import urllib.parse

import torch
from diffusers import StableDiffusionXLPipeline

from storyteller.modules.st.option_choices import artistic_styles

__all__ = ("generate_sdxl_text_to_image",)


def _pick_device() -> str:
    """Pick best available device."""
    # Prefer MPS on Apple Silicon, then CUDA, then CPU.
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def _ensure_pipeline(
    model_id: str,
    device: str,
    torch_dtype: torch.dtype | None = None,
) -> StableDiffusionXLPipeline:
    """Load and configure SDXL pipeline with sensible defaults."""
    if torch_dtype is None:
        # Use float16 on GPU/MPS, float32 on CPU.
        torch_dtype = torch.float16 if device in {"cuda", "mps"} else torch.float32

    pipe = StableDiffusionXLPipeline.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        use_safetensors=True,
    )

    # Enable inference optimizations appropriate for the device.
    pipe.enable_attention_slicing()
    if device == "cuda":
        pipe.enable_model_cpu_offload()  # Keeps VRAM usage in check on CUDA.
    pipe.to(device)

    return pipe


# Simple in-memory singleton cache to avoid reloading the model repeatedly.
_PIPELINE_CACHE: dict[tuple[str, str], StableDiffusionXLPipeline] = {}


def _get_pipeline(model_id: str, device: str) -> StableDiffusionXLPipeline:
    """Get cached pipeline for (model_id, device)."""
    key = (model_id, device)
    pipe = _PIPELINE_CACHE.get(key)
    if pipe is None:
        pipe = _ensure_pipeline(model_id=model_id, device=device)
        _PIPELINE_CACHE[key] = pipe
    return pipe


def generate_sdxl_text_to_image(
    prompt: str,
    artistic_style: str | None = None,
    guidance_scale: float = 7.0,
    num_inference_steps: int = 30,
    negative_prompt: str | None = None,
    width: int = 1024,
    height: int = 1024,
    seed: int | None = 1_000_000,
    model_id: str = "stabilityai/stable-diffusion-xl-base-1.0",
    # model_id: str = "sd-community/sdxl-flash-mini",
    # model_id: str = "segmind/SSD-1B",
    output_dir: str | Path = "media",
    filename_prefix: str = "sdxl",
) -> tuple[str, str, bool]:
    """Generate an image locally using SDXL 1.0 (Diffusers).

    :param prompt: The positive prompt.
    :param artistic_style: Optional artistic style key (looked up in `artistic_styles`).
    :param guidance_scale: Guidance scale (CFG). Typical range 5.0–9.0 for SDXL.
    :param num_inference_steps: Diffusion steps. 20–40 is a good balance on MPS.
    :param negative_prompt: Optional negative prompt.
    :param width: Output width (multiples of 64 are safest).
    :param height: Output height (multiples of 64 are safest).
    :param seed: Optional seed for reproducibility.
    :param model_id: HF model ID or a local path to an SDXL model.
    :param output_dir: Directory to save images into.
    :param filename_prefix: Prefix for the saved file name.
    :return: (file_url_or_error, final_prompt, success_bool)

    Usage example:

        from storyteller.modules.st.image_gen.sdxl_text_to_image import generate_sdxl_text_to_image
        image_url, final_prompt, success = generate_sdxl_text_to_image("A fox cub on the moon.")
    """
    # Compose final prompt with optional style expansion.
    style_hint = artistic_styles.get(artistic_style) if artistic_style else None
    if style_hint:
        final_prompt = (
            f"{prompt}\nCreate an image in the style of {artistic_style}: {style_hint}"
        )
    else:
        final_prompt = prompt

    # Resolve media config
    media_root = Path(output_dir or os.environ.get("MEDIA_ROOT", "media")).resolve()
    media_url_base = os.environ.get(
        "MEDIA_URL", "/media/"
    )  # can be "/media/" or "https://host/media/"
    if not media_url_base.endswith("/"):
        media_url_base += "/"

    try:
        device = _pick_device()
        pipe = _get_pipeline(model_id=model_id, device=device)

        # Prepare RNG.
        generator = None
        if seed is not None:
            # Generator must be on CPU for MPS/CUDA compatibility in diffusers.
            generator = torch.Generator(device="cpu").manual_seed(int(seed))

        # SDXL prefers sizes divisible by 64.
        width = (width // 64) * 64
        height = (height // 64) * 64

        # Run inference.
        result = pipe(
            prompt=final_prompt,
            negative_prompt=negative_prompt,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            width=width,
            height=height,
            generator=generator,
        )
        image = result.images[0]

        # Save to disk.
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        ts = int(time.time() * 1000)
        fname = f"{filename_prefix}_{ts}.png"
        fpath = media_root / fname
        image.save(fpath)

        # Return a file:// URL to keep parity with your (url, prompt, bool) contract.
        # Build public URL from MEDIA_URL. Works for both absolute and relative bases.
        image_url = urllib.parse.urljoin(media_url_base, fname)
        return image_url, final_prompt, True

    except Exception as err:  # noqa: BLE001
        # Return the error string and the prompt for tracing, False for failure.
        return str(err), final_prompt, False
