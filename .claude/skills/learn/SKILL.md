---
name: learn
description: The full daily learning session (~25 min) - reviews first, then the next lesson on the subject's roadmap (with a short prerequisite check), a build/apply exercise, then /wrap. Use when the learner types /learn or says they want to study.
---

# Daily session (~25 min)

Use the session-start status block (streak, due cards, subjects). Follow the `teach` skill for
all teaching and my profile for all language.

## 0. Open (30 sec)
- One line: streak + cards due + today's plan. E.g. "🔥 Day 4. 7 cards due, then *Order books* 📘".
- If there are no subjects → suggest `/new-subject` and stop.
- If there's more than one active subject and I didn't name one, ask which (`AskUserQuestion`),
  recommending the one I've neglected longest.
- If the subject's roadmap isn't approved yet (`status: draft` in `_map.md`), finish that first
  (see `new-subject` step 4).
- If today's if-then trigger in my profile is still blank, ask me to fill it in (one question).

## 1. Reviews (~5 min)
Run the `review` skill.

## 2. Pick the lesson (~1 min)
- Open `subjects/<subject>/_map.md`. The lesson is `next_node`, or the first ⬜/🟨 node whose
  prerequisites (incoming arrows) are all done.
- If a card for an earlier node came back `again` repeatedly, re-teach that node instead.
- Tell me the lesson title and, in one line, why it's next ("you need this before X").

## 3. Quick prerequisite check (~2 min)
Two quick graded questions on the node(s) this lesson rests on.
- Both right → go.
- One wrong → a 2-minute fix of that prerequisite first (mini teach loop), then go.
- Both wrong → the foundation is weak: re-teach that prerequisite as today's lesson instead,
  and add a note in `_map.md` if the map is missing a step.

## 4. Teach the node (~12 min)
- Create the lesson note from the template in the `teach` skill.
- Split the node into 2–4 small ideas. Run the teach loop for each: **Why → Guess → Explain
  simply → Check**. Write each part into the note as you go; the terminal gets one-line
  pointers + questions.
- Record each quick check in the note (question · my answer · ✓/✗).
- If I'm clearly tired (short answers, "idk" streak, asks to stop), cut the lesson short,
  write what we covered, and go to wrap. A shorter session beats a skipped one.

## 5. Build / apply (~5 min)
Make me *use* the idea once, alone:
- design subjects → a small design problem: "sketch how you'd…" — I describe it (or a
  mermaid diagram), you critique it. Save it to `subjects/<subject>/exercises/YYYY-MM-DD <topic>.md`
  (my answer + your feedback + a corrected version).
- coding subjects → a small exercise with a test in `exercises/<topic>/`. I write the code,
  you run the test and review.
- math → one worked example together, then one I do alone.
Early in a subject, show a worked example first (see `teach` skill).

## 6. Wrap
Finish the note's Recap, set `status: done`, then run the `wrap` skill.
Don't end a session without wrapping — the commit is what Beeminder counts.
