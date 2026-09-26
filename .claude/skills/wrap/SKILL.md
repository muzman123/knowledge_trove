---
name: wrap
description: End a learning session - finish the lesson note, turn the key ideas into review cards, update the roadmap from the mastery report, log the session, then git commit and push to main (the commit is what Beeminder tracks). Use at the end of /learn or /new-subject, or when the learner types /wrap.
---

# Wrap up the session (~2 min)

## 1. Finish the lesson note
If there's a lesson note from today: make sure the Recap is there and `status: done`.

## 2. Make review cards
Add 3–6 cards per lesson to `subjects/<subject>/cards.md` (format in CLAUDE.md).
- Next free id = highest existing number for that prefix + 1. Never reuse an id.
- Set `node:` to the lesson's node id.
- Mostly `explain` cards, especially **"why"** questions ("Why does X need Y?") — they build
  connections. Add a `spot` card when two ideas are easy to confuse, a `code` card for code.
- One idea per card. Question ≤ 1 line. Answer ≤ 4 lines, plain language, with a metaphor or
  example.
- Also add a card for any misconception I showed today ("Is it true that …? Why not?").
- Then run `bash .claude/bin/srs sync` and check it reports the new ids with no warnings.

## 3. Update the roadmap
- Run `bash .claude/bin/srs mastery <subject>`.
- In `_map.md`: set each node's status from the report (🟨 learning / ✅ solid; ⬜ = no cards
  yet), link today's lesson note in the table (`[[YYYY-MM-DD Title]]`), update `nodes_solid`,
  `next_node`, and `updated` in the frontmatter.
- If today revealed a missing step, add a node (and a change-log line saying why).

## 4. Learn about the learner
If you noticed something about how I learn (a metaphor style that clicked, where I got lost,
energy level), add one dated line to section 5 of `_system/learner-profile.md`.

## 5. Log + commit
```bash
bash .claude/bin/srs log-session
git add -A
git commit -m "<type>(<subject>): <what happened>"
git push origin main
```
Commit message examples:
- `learn(system-design-hft): latency basics — 5 new cards, 8 reviews`
- `placement(system-design-hft): placement quiz + goal`
- `review: 12 cards (quick session)`

If the push fails, tell me plainly what failed (no internet? auth?) and how to fix it —
the day only counts on Beeminder once it's pushed to GitHub.

## 6. Close
One or two lines: streak, what we learned today in one sentence, and what's next tomorrow.
Something like: "🔥 Day 5 done. Today: why tail latency matters. Tomorrow: what the CPU does with data."
