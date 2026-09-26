# 🧠 Learning

My AI-tutored learning system. I talk to **Claude Code** in a terminal. It teaches me, quizzes me, and writes everything into this folder, which I read in **Obsidian**. Every daily session ends with a **git commit**, and **Beeminder** checks those commits, so skipping a day costs money.

One commit here = one day I actually studied.

---

## How it works

```
 Terminal                          Obsidian
┌──────────────────┐   writes    ┌───────────────────────┐
│ claude           │ ──────────► │ 📘 lessons             │
│ > /learn         │             │ 🗺️ roadmap per subject │
│ quizzes + chat   │             │ 🃏 review cards        │
└────────┬─────────┘             │ 📊 dashboard           │
         │ /wrap                 └───────────────────────┘
         ▼
  git commit + push ──► GitHub ──► Beeminder
```

### Built on the science of learning
| Research finding | How the system uses it |
|---|---|
| Testing yourself beats rereading | Constant questions; lessons end in review cards |
| Spacing reviews out beats cramming | FSRS scheduler brings each card back at the right time |
| Guessing before being taught helps memory | Every idea starts with "take a guess" |
| Explaining in your own words helps a lot | Most cards are "explain it back", graded by Claude |
| Beginners learn from worked examples, then solo | Build step: example first, then a fresh one alone |
| Plain, chunked, jargon-free material | Plain-language rules in `_system/learner-profile.md` |
| If-then plans + commitment devices | Daily trigger + Beeminder on this repo |

### Two levels of planning
1. **Once per subject (`/new-subject`)**: a placement quiz finds where my knowledge runs out, a few questions pin down my real goal, a researcher checks the field, and Claude draws a **roadmap**: a dependency graph of lessons from basics to goal.
2. **Every day (`/learn`)**: reviews → a 2-question check of what the next lesson builds on → the lesson (Why → Guess → Explain simply → Check, for each idea) → a small build exercise → `/wrap`.

A lesson only counts as ✅ **solid** when its review cards have stuck for 3+ weeks. The map shows what I *know*, not just what I've *seen*.

---

## Daily commands

| Command | Time | What it does |
|---|---|---|
| `/learn` | ~25 min | Full session: reviews, next lesson, build, wrap |
| `/quick` | ~10 min | Bad-day mode: reviews + commit. Keeps the streak alive. |
| `/review` | ~5 min | Just the due cards |
| `/new-subject` | ~20 min | Placement quiz, goal, research, roadmap |
| `/wrap` | ~2 min | Make cards, update map, log session, commit + push |

## Folder layout

```
Learning/
├── CLAUDE.md                 tutor instructions (read by Claude Code)
├── setup.ps1                 one-time setup (Windows)
├── _system/
│   ├── Dashboard.md          open this in Obsidian
│   ├── learner-profile.md    how I learn (rules the tutor follows + its notes on me)
│   ├── stats.md              streak / due cards (auto)
│   └── srs-state.json        review schedule (auto)
├── subjects/<subject>/
│   ├── _map.md               roadmap
│   ├── placement.md          placement quiz results
│   ├── cards.md              review cards
│   ├── lessons/              one note per lesson
│   └── exercises/            my designs and code
├── sessions/                 raw chat log per day (auto)
└── .claude/                  skills, hooks, review engine (hidden in Obsidian)
```

## Setup (once)

1. Put this folder in the Obsidian vault (it lives at `Davault/Learning`).
2. In PowerShell, inside this folder:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\setup.ps1
   ```
   This moves the tutor files from `_setup/claude` into `.claude`, creates the review engine's Python environment, makes the git repo, and creates the public GitHub repo (with the GitHub CLI `gh`).
3. Obsidian → Settings → Community plugins → Browse → **Dataview** → Install + Enable. Open `_system/Dashboard.md`.
4. Beeminder: make a **GitHub** goal tracking commits to this repo (see below).
5. `claude` → `/new-subject`.

## Beeminder notes

- Beeminder's GitHub integration tracks **one specific repo** per goal, which is why everything lives in this single repo.
- It counts commits on **main** by default. `/wrap` always commits to `main`.
- Commits count only if the **git email matches an email on your GitHub account**. `setup.ps1` checks this.
- GitHub data can lag **up to ~6 hours**. Don't leave the session until 11:55 pm.

## Credits

The teaching method (solid foundations first, "how could I have discovered this?", probe → plan → teach) is adapted from Amos Blomqvist's [`learn`](https://github.com/amosblomqvist/learn) system. Review scheduling uses [FSRS](https://github.com/open-spaced-repetition/py-fsrs).
