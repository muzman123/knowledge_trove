#!/usr/bin/env python3
"""SessionStart hook: prints a status block that Claude sees before you say anything.
Also refreshes _system/stats.md so the Obsidian dashboard is current."""
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

try:
    import srs  # noqa: E402

    print(srs.build_summary(srs.load_state()))
except SystemExit:
    pass
except Exception as e:  # never block the session because of the status script
    print(f"(learning status unavailable: {e}. Did you run setup.ps1?)")
