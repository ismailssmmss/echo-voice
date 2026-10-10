from __future__ import annotations

import hashlib
import os
import threading
from pathlib import Path


MODEL_NAME = "SILMA TTS v1"
SUPPORTED_LANGUAGES = {"ar", "en", "ar-en"}


class ModelNotReadyError(RuntimeError):
    """Raised when the model cannot be initialized."""


class SilmaRuntime:
    """Lazy, process-local inference runtime for SILMA's zero-shot voice cloning."""

    def __init__(self) -> None:
        self.model = None
        self._lock = threading.RLock()
        self.cache_dir = Path(os.getenv("MODEL_CACHE_DIR", os.getenv("HF_HOME", "/models/huggingface")))
        self.device = "cpu"

    @property
    def loaded(self) -> bool:
        return self.model is not None

    def load(self):
        with self._lock:
            if self.model is not None:
                return self.model

            try:
                import torch
                from silma_tts.api import SilmaTTS

                self.cache_dir.mkdir(parents=True, exist_ok=True)
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
                self.model = SilmaTTS(
                    model="SilmaTTS_V1_Small",
                    device=self.device,
                    hf_cache_dir=str(self.cache_dir),
                    enable_normalizer=True,
                    force_tashkeel=False,
                )
            except Exception as exc:
                self.model = None
                raise ModelNotReadyError(
                    "SILMA TTS could not initialize. Verify model download access, cache disk space, and available RAM/GPU memory."
                ) from exc
            return self.model

    @staticmethod
    def _clear_reference_cache(audio_hash: str, source_audio: Path) -> None:
        """Remove SILMA's own temporary, preprocessed reference clip after each request."""
        try:
            from silma_tts.infer import utils_infer

            cached_audio = utils_infer._ref_audio_cache.pop(audio_hash, None)
            utils_infer._ref_text_cache.pop(audio_hash, None)
            if cached_audio:
                cached_path = Path(cached_audio)
                if cached_path.resolve() != source_audio.resolve():
                    cached_path.unlink(missing_ok=True)
        except Exception:
            # Best effort cleanup must not mask the original inference error.
            pass

    def generate(
        self,
        reference_audio: Path,
        reference_text: str,
        text: str,
        language: str,
        output_path: Path,
        speed: float = 1.0,
        seed: int | None = None,
    ) -> None:
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError("Supported language values are ar, en, and ar-en.")
        if not text.strip() or len(text) > 5000:
            raise ValueError("Text must contain between 1 and 5000 characters.")
        if not reference_text.strip() or len(reference_text) > 2000:
            raise ValueError("Reference transcription must contain between 1 and 2000 characters.")
        if not 0.75 <= speed <= 1.25:
            raise ValueError("Speed must be between 0.75 and 1.25.")

        # SILMA internally uses the MD5 of the supplied clip as its in-process cache key.
        # Clear that entry afterwards so reference audio isn't retained in a global cache.
        audio_hash = hashlib.md5(reference_audio.read_bytes()).hexdigest()
        with self._lock:
            model = self.load()
            try:
                model.infer(
                    ref_file=str(reference_audio),
                    ref_text=reference_text.strip(),
                    gen_text=text.strip(),
                    file_wave=str(output_path),
                    speed=speed,
                    seed=seed,
                    force_tashkeel=False,
                )
            except Exception as exc:
                raise RuntimeError(
                    "Speech generation failed. Verify the reference transcription and available memory, then retry."
                ) from exc
            finally:
                self._clear_reference_cache(audio_hash, reference_audio)

        if not output_path.is_file() or output_path.stat().st_size < 1024:
            raise RuntimeError("The model completed without producing a valid audio file.")


runtime = SilmaRuntime()
