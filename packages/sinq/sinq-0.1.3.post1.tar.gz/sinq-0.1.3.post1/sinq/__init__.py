from .hf_io import patch_hf_pretrained_io as patch  # manual opt-in

def is_patched() -> bool:
    try:
        import transformers
        f = getattr(transformers.PreTrainedModel.from_pretrained, "__func__",
                    transformers.PreTrainedModel.from_pretrained)
        return bool(getattr(f, "_sinq_wrapped", False))
    except Exception:
        return False