#!/usr/bin/env python3
"""
srs.py — the review engine (spaced repetition with FSRS).

Cards live in plain markdown so you can read them in Obsidian:
    subjects/<subject>/cards.md

Card format (one card = one H3 heading with an id in square brackets):

    ### [sd-001] In plain words, what is latency?
    node: latency-basics
    type: explain
    The time between asking for something and getting the answer back.
    Example: you click "buy", the order reaches the exchange 2 ms later.

  - `node:`  which roadmap node this card belongs to (used for mastery)
  - `type:`  explain | choose | code | spot  (how Claude should ask it)
  - everything else under the heading is the reference answer

Scheduling data lives in _system/srs-state.json (never edit by hand).

Commands (run via:  bash .claude/bin/srs <command>):
    sync                       register new cards found in cards.md files
    due [--limit N] [--subject S]
                               list due cards: id + question only (no answers)
    answer <id>                show the reference answer for one card
    grade <id> <again|hard|good|easy>
                               record how the recall went, schedule next review
    stats [--write]            totals, due today, streak (--write updates _system/stats.md)
    mastery <subject>          per-node status: learning / solid
    log-session                mark today as a completed session (streak)
    summary                    short status block (used by the session-start hook)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
except Exception:
    pass

try:
    from fsrs import Card, Rating, Scheduler
except ImportError:  # pragma: no cover
    print("ERROR: the 'fsrs' package is not installed. Run setup.ps1 (or: pip install fsrs).")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[2]  # .../Learning
SUBJECTS = ROOT / "subjects"
SYSTEM = ROOT / "_system"
STATE_FILE = SYSTEM / "srs-state.json"
STATS_FILE = SYSTEM / "stats.md"

# Daily sessions -> no intra-day learning steps. A card graded today comes back
# on a later day. "again" brings it back tomorrow.
SCHEDULER = Scheduler(learning_steps=(), relearning_steps=(), desired_retention=0.9)

SOLID_STABILITY_DAYS = 21  # a node is "solid" when all its cards reach this
SOLID_MIN_REVIEWS = 2

RATINGS = {"again": Rating.Again, "hard": Rating.Hard, "good": Rating.Good, "easy": Rating.Easy}

HEADING_RE = re.compile(r"^###\s*\[([A-Za-z0-9_\-]+)\]\s*(.+?)\s*$")
FIELD_RE = re.compile(r"^(node|type)\s*:\s*(.*?)\s*$", re.IGNORECASE)


# ---------------------------------------------------------------- utilities

def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def today_local() -> date:
    return datetime.now().astimezone().date()


def end_of_today_utc() -> datetime:
    local_now = datetime.now().astimezone()
    end = local_now.replace(hour=23, minute=59, second=59, microsecond=0)
    return end.astimezone(timezone.utc)


def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE, encoding="utf-8") as f:
            state = json.load(f)
    else:
        state = {}
    state.setdefault("version", 1)
    state.setdefault("cards", {})
    state.setdefault("sessions", [])
    return state


def save_state(state: dict) -> None:
    SYSTEM.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, STATE_FILE)


def parse_frontmatter(path: Path) -> dict:
    """Tiny YAML-frontmatter reader (flat key: value only, no dependency)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    out = {}
    for line in text[3:end].splitlines():
        if ":" in line and not line.startswith((" ", "\t", "-")):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


# ---------------------------------------------------------------- card files

def parse_card_file(path: Path) -> list[dict]:
    subject = path.parent.name
    cards, cur = [], None
    for raw in path.read_text(encoding="utf-8").splitlines():
        m = HEADING_RE.match(raw)
        if m:
            if cur:
                cards.append(cur)
            cur = {"id": m.group(1), "question": m.group(2), "subject": subject,
                   "node": "", "type": "explain", "answer_lines": []}
            continue
        if cur is None:
            continue
        if raw.startswith("## ") or raw.startswith("# "):  # a new section ends the card
            cards.append(cur)
            cur = None
            continue
        fm = FIELD_RE.match(raw)
        if fm and not cur["answer_lines"]:
            cur[fm.group(1).lower()] = fm.group(2)
            continue
        cur["answer_lines"].append(raw)
    if cur:
        cards.append(cur)
    for c in cards:
        c["answer"] = "\n".join(c.pop("answer_lines")).strip()
    return cards


def all_file_cards() -> tuple[dict, list[str]]:
    found, dupes = {}, []
    if SUBJECTS.exists():
        for path in sorted(SUBJECTS.glob("*/cards.md")):
            for c in parse_card_file(path):
                if c["id"] in found:
                    dupes.append(c["id"])
                found[c["id"]] = c
    return found, dupes


def sync(state: dict, quiet: bool = False) -> dict:
    found, dupes = all_file_cards()
    added = []
    for cid, c in found.items():
        entry = state["cards"].get(cid)
        if entry is None:
            state["cards"][cid] = {
                "subject": c["subject"], "node": c["node"],
                "created": today_local().isoformat(),
                "fsrs": Card().to_dict(), "reviews": [], "orphan": False,
            }
            added.append(cid)
        else:
            entry["subject"], entry["node"], entry["orphan"] = c["subject"], c["node"], False
    orphans = []
    for cid, entry in state["cards"].items():
        if cid not in found and not entry.get("orphan"):
            entry["orphan"] = True
            orphans.append(cid)
    save_state(state)
    if not quiet:
        print(f"sync: {len(added)} new card(s), {len(found)} total in files.")
        if added:
            print("  added: " + ", ".join(added))
        if orphans:
            print("  WARNING: these ids are no longer in any cards.md (paused): " + ", ".join(orphans))
        if dupes:
            print("  WARNING: duplicate ids (fix these, ids must be unique): " + ", ".join(sorted(set(dupes))))
    return found


def due_cards(state: dict, subject: str | None = None) -> list[tuple[str, dict]]:
    cutoff = end_of_today_utc()
    out = []
    for cid, e in state["cards"].items():
        if e.get("orphan"):
            continue
        if subject and e["subject"] != subject:
            continue
        due = datetime.fromisoformat(e["fsrs"]["due"])
        if due <= cutoff:
            out.append((cid, e, due))
    out.sort(key=lambda t: t[2])  # most overdue first
    # interleave subjects (round-robin) so reviews are mixed
    by_subj: dict[str, list] = {}
    for cid, e, _ in out:
        by_subj.setdefault(e["subject"], []).append((cid, e))
    mixed = []
    while any(by_subj.values()):
        for s in sorted(by_subj):
            if by_subj[s]:
                mixed.append(by_subj[s].pop(0))
    return mixed


# ---------------------------------------------------------------- stats

def streak(sessions: list[str]) -> int:
    days = {date.fromisoformat(d) for d in sessions}
    d = today_local()
    if d not in days:
        d -= timedelta(days=1)  # today not done yet: streak still alive from yesterday
    n = 0
    while d in days:
        n += 1
        d -= timedelta(days=1)
    return n


def compute_stats(state: dict) -> dict:
    active = {k: v for k, v in state["cards"].items() if not v.get("orphan")}
    today = today_local().isoformat()
    reviewed_today = sum(
        1 for v in active.values() for r in v["reviews"] if r["date"].startswith(today)
    )
    return {
        "cards_total": len(active),
        "cards_due": len(due_cards(state)),
        "reviewed_today": reviewed_today,
        "streak": streak(state["sessions"]),
        "sessions_total": len(set(state["sessions"])),
        "last_session": max(state["sessions"]) if state["sessions"] else "never",
        "done_today": today in state["sessions"],
    }


def write_stats_file(st: dict) -> None:
    body = f"""---
type: stats
cards_due: {st['cards_due']}
cards_total: {st['cards_total']}
reviewed_today: {st['reviewed_today']}
streak: {st['streak']}
sessions_total: {st['sessions_total']}
last_session: {st['last_session']}
done_today: {str(st['done_today']).lower()}
updated: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M')}
---
# Stats

*Written automatically by the review engine. Don't edit.*

- 🔥 Streak: **{st['streak']} day(s)**
- 🃏 Cards due today: **{st['cards_due']}**
- ✅ Reviewed today: **{st['reviewed_today']}**
- 📚 Total cards: **{st['cards_total']}**
- 📅 Sessions so far: **{st['sessions_total']}** (last: {st['last_session']})
- Today done: **{'yes' if st['done_today'] else 'not yet'}**
"""
    with open(STATS_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)


def mastery(state: dict, subject: str) -> list[dict]:
    nodes: dict[str, list] = {}
    for cid, e in state["cards"].items():
        if e.get("orphan") or e["subject"] != subject:
            continue
        nodes.setdefault(e["node"] or "(no node)", []).append((cid, e))
    rows = []
    for node, cards in sorted(nodes.items()):
        stabs = [c[1]["fsrs"].get("stability") or 0 for c in cards]
        reviews = [len(c[1]["reviews"]) for c in cards]
        solid = all(s >= SOLID_STABILITY_DAYS for s in stabs) and all(r >= SOLID_MIN_REVIEWS for r in reviews)
        rows.append({
            "node": node, "cards": len(cards), "min_stability_days": round(min(stabs), 1),
            "min_reviews": min(reviews), "status": "solid" if solid else "learning",
        })
    return rows


def subject_summaries() -> list[dict]:
    out = []
    if SUBJECTS.exists():
        for d in sorted(p for p in SUBJECTS.iterdir() if p.is_dir()):
            fm = parse_frontmatter(d / "_map.md")
            out.append({
                "subject": d.name,
                "goal": fm.get("goal", "?"),
                "nodes_total": fm.get("nodes_total", "?"),
                "nodes_solid": fm.get("nodes_solid", "?"),
                "next_node": fm.get("next_node", "?"),
                "status": fm.get("status", "?"),
            })
    return out


# ---------------------------------------------------------------- commands

def cmd_due(args, state):
    sync(state, quiet=True)
    items = due_cards(state, args.subject)
    total = len(items)
    items = items[: args.limit] if args.limit else items
    found, _ = all_file_cards()
    print(f"{total} card(s) due" + (f" (showing {len(items)})" if len(items) < total else "") + ".")
    for cid, e in items:
        c = found.get(cid, {})
        print(f"- [{cid}] ({e['subject']} / {c.get('type', 'explain')}) {c.get('question', '?')}")


def cmd_answer(args, state):
    found, _ = all_file_cards()
    c = found.get(args.id)
    if not c:
        print(f"No card with id {args.id}")
        sys.exit(1)
    print(f"[{c['id']}] {c['question']}\nnode: {c['node']}\ntype: {c['type']}\n---\n{c['answer']}")


def cmd_grade(args, state):
    sync(state, quiet=True)
    e = state["cards"].get(args.id)
    if not e:
        print(f"No card with id {args.id}")
        sys.exit(1)
    card = Card.from_dict(e["fsrs"])
    card, _ = SCHEDULER.review_card(card, RATINGS[args.rating], review_datetime=now_utc())
    e["fsrs"] = card.to_dict()
    e["reviews"].append({"date": datetime.now().astimezone().isoformat(timespec="seconds"),
                         "rating": args.rating})
    save_state(state)
    days = (card.due - now_utc()).total_seconds() / 86400
    print(f"graded {args.id}: {args.rating}. Next review in ~{max(1, round(days))} day(s) "
          f"(memory strength ~{card.stability:.1f} days).")


def cmd_stats(args, state):
    sync(state, quiet=True)
    st = compute_stats(state)
    if args.write:
        write_stats_file(st)
    for k, v in st.items():
        print(f"{k}: {v}")


def cmd_mastery(args, state):
    sync(state, quiet=True)
    rows = mastery(state, args.subject)
    if not rows:
        print(f"No cards yet for subject '{args.subject}'.")
        return
    print("node | cards | weakest memory (days) | min reviews | status")
    for r in rows:
        print(f"{r['node']} | {r['cards']} | {r['min_stability_days']} | {r['min_reviews']} | {r['status']}")
    print(f"(solid = every card reviewed >= {SOLID_MIN_REVIEWS}x and remembered >= {SOLID_STABILITY_DAYS} days)")


def cmd_log_session(args, state):
    d = today_local().isoformat()
    if d not in state["sessions"]:
        state["sessions"].append(d)
        state["sessions"].sort()
    save_state(state)
    st = compute_stats(state)
    write_stats_file(st)
    print(f"Session logged for {d}. Streak: {st['streak']} day(s).")


def build_summary(state: dict) -> str:
    sync(state, quiet=True)
    st = compute_stats(state)
    write_stats_file(st)
    due = due_cards(state)
    per_subj: dict[str, int] = {}
    for _, e in due:
        per_subj[e["subject"]] = per_subj.get(e["subject"], 0) + 1
    lines = [
        "=== LEARNING SYSTEM STATUS (auto-generated at session start) ===",
        f"Date: {today_local().isoformat()} ({datetime.now().astimezone().strftime('%A %H:%M')})",
        f"Streak: {st['streak']} day(s). Today's session done: {'YES' if st['done_today'] else 'NOT YET'}.",
        f"Cards due: {st['cards_due']}"
        + (" (" + ", ".join(f"{k}: {v}" for k, v in sorted(per_subj.items())) + ")" if per_subj else ""),
    ]
    subs = subject_summaries()
    if subs:
        lines.append("Subjects:")
        for s in subs:
            lines.append(f"  - {s['subject']}: goal = {s['goal']}; {s['nodes_solid']}/{s['nodes_total']} nodes solid; "
                         f"next node = {s['next_node']}; status = {s['status']}")
    else:
        lines.append("Subjects: none yet. Suggest /new-subject.")
    lines.append("Commands: /learn (full session), /quick (bad-day: reviews + commit), /review, /new-subject, /wrap")
    return "\n".join(lines)


def cmd_summary(args, state):
    print(build_summary(state))


def main():
    p = argparse.ArgumentParser(description="FSRS review engine for the Learning vault")
    sp = p.add_subparsers(dest="cmd", required=True)
    sp.add_parser("sync")
    d = sp.add_parser("due")
    d.add_argument("--limit", type=int, default=0)
    d.add_argument("--subject")
    a = sp.add_parser("answer")
    a.add_argument("id")
    g = sp.add_parser("grade")
    g.add_argument("id")
    g.add_argument("rating", choices=list(RATINGS))
    s = sp.add_parser("stats")
    s.add_argument("--write", action="store_true")
    m = sp.add_parser("mastery")
    m.add_argument("subject")
    sp.add_parser("log-session")
    sp.add_parser("summary")
    args = p.parse_args()

    state = load_state()
    {
        "sync": lambda a, s: sync(s),
        "due": cmd_due, "answer": cmd_answer, "grade": cmd_grade, "stats": cmd_stats,
        "mastery": cmd_mastery, "log-session": cmd_log_session, "summary": cmd_summary,
    }[args.cmd](args, state)


if __name__ == "__main__":
    main()
