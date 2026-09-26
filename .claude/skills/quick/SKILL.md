---
name: quick
description: Bad-day mode (~10 min) - just the due reviews, then log the session and commit/push so the daily streak and Beeminder goal stay alive. Use when the learner types /quick or says they're tired / short on time.
---

# Quick session (~10 min)

For days with no energy. Doing this beats skipping — the habit is what matters.

1. One line: "Low-energy day, no problem. Reviews only, then we commit. 🔥 streak stays alive."
2. Run the `review` skill, capped at 10 cards. If nothing is due, use its no-cards fallback.
3. Run the `wrap` skill steps 4–6 only (no new cards, no map changes unless reviews showed a
   node is now solid). Commit message: `review: <n> cards (quick session)`.
4. If I seem up for more after reviews, offer (once, no pressure) to do a 10-minute lesson.
