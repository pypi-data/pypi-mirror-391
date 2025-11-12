import os, sys

_ALREADY = False

def run():
    global _ALREADY
    if _ALREADY:
        return
    if str(os.getenv("SINQ_AUTO_PATCH","1")).lower() in ("0","false","no","off",""):
        return
    try:
        from .hf_io import patch_hf_pretrained_io
        patch_hf_pretrained_io()
        os.environ["SINQ_PTH_LOADED"] = "1"  # debug marker (optional)
        _ALREADY = True
    except Exception as e:
        sys.stderr.write(f"[SINQ] autopatch failed: {e}\n")
