import sys
import traceback
from TTS.api import TTS
import torch

original_load = torch.load
torch.load = lambda *args, **kwargs: original_load(*args, **{**kwargs, "weights_only": False})

try:
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
    gpt_cond_latent, speaker_embedding = tts.synthesizer.tts_model.get_conditioning_latents(
        audio_path=["dylan_ref.wav"],
        gpt_cond_len=30,
        max_ref_length=60,
    )
    out = tts.synthesizer.tts_model.inference(
        text="Test",
        language="en",
        gpt_cond_latent=gpt_cond_latent,
        speaker_embedding=speaker_embedding,
        temperature=0.7,
        length_penalty=1.0,
        repetition_penalty=10.0,
        top_k=50,
        top_p=0.85,
    )
    print("Success")
except Exception as e:
    traceback.print_exc()
