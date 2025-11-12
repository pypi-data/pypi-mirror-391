# sitecustomize.py
try:
    from sinq._autopatch import run as _sinq_autopatch_run
    _sinq_autopatch_run()
except Exception as e:
    import sys
    sys.stderr.write(f"[SINQ] autopatch failed: {e}\n")