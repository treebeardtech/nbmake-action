import os

if os.name == "nt":
    try:
        import sys
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding="utf-8")
    except:
        pass
