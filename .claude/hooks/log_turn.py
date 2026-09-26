#!/usr/bin/env python3
"""Session log hook: mirrors the conversation into sessions/YYYY-MM-DD.md
so every session is readable (and searchable) in Obsidian.

Usage (from .claude/settings.json):
    log_turn.py prompt     <- UserPromptSubmit event (what you typed)
    log_turn.py response   <- Stop event (Claude's reply)

Must never print anything: UserPromptSubmit stdout would be injected as context.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "sessions"


def last_assistant_text(transcript_path: str) -> str:
    """Fallback: read the transcript JSONL and return the last assistant text."""
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8").splitlines()
    except Exception:
        return ""
    for raw in reversed(lines):
        try:
            entry = json.loads(raw)
        except Exception:
            continue
        msg = entry.get("message") or {}
        if entry.get("type") != "assistant" and msg.get("role") != "assistant":
            continue
        content = msg.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
        if isinstance(content, list):
            texts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
            text = "\n\n".join(t for t in texts if t.strip())
            if text.strip():
                return text.strip()
    return ""


def main() -> None:
    kind = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8") or "{}")
    except Exception:
        return

    if kind == "prompt":
        text = (data.get("prompt") or "").strip()
        block = f"> [!quote] YOU · {datetime.now().strftime('%H:%M')}\n> " + text.replace("\n", "\n> ")
    elif kind == "response":
        text = (data.get("last_assistant_message") or "").strip()
        if not text:
            text = last_assistant_text(data.get("transcript_path", ""))
        block = f"**CLAUDE · {datetime.now().strftime('%H:%M')}**\n\n{text}"
    else:
        return
    if not text:
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    day = datetime.now().strftime("%Y-%m-%d")
    path = LOG_DIR / f"{day}.md"
    new_file = not path.exists()
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        if new_file:
            f.write(f"---\ntype: session-log\ndate: {day}\n---\n# Session log {day}\n\n"
                    "*Raw transcript, written automatically. The clean version is in the lesson notes.*\n")
        f.write("\n" + block + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # logging must never break the session
