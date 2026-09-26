---
name: review
description: Run the due spaced-repetition review cards. The learner answers from memory (usually in their own words), Claude grades against the reference answer and records the result with the FSRS review engine. Used at the start of /learn and /quick, or on its own via /review.
---

# Review the due cards

Goal: pull each idea back out of memory (that's what makes it stick), fast. ~5 minutes,
max ~15 cards. Anything left over rolls to tomorrow automatically.

## Steps

1. Run `bash .claude/bin/srs due --limit 15`.
   - 0 due → say "Nothing due today ✅" and move on (in `/quick`, do the no-cards fallback below).
2. Tell me in one line: "🃏 N cards today, mixed subjects. Answer in your own words."
3. For each card, ask it based on its `type`:
   - `explain` → plain-text question: "In your own words: …". I type an answer.
   - `choose` → `AskUserQuestion` with 3 options + "I don't know" (build options with the
     rules in the `teach` skill; run `srs answer` first *silently* only if you need the answer
     to build the options — never show it).
   - `code` → ask me to write the small snippet in the terminal.
   - `spot` → "What's the difference between X and Y?" in plain text.
4. **After** I answer, run `bash .claude/bin/srs answer <id>` and compare.
5. Grade it and tell me the grade in one short line:
   - **again** — wrong, blank, "I don't know", or the core idea is missing
   - **hard** — right idea but shaky, incomplete, or needed a hint
   - **good** — correct and in my own words
   - **easy** — instant, precise, maybe even added something extra
   Be honest, not generous: the schedule only works with true grades.
6. Feedback, 1–2 lines max:
   - good/easy → "✓" + one line that adds a connection (what it links to).
   - again/hard → re-explain in 2 lines with a **different metaphor** than the card uses.
     Don't just paste the reference answer.
7. Run `bash .claude/bin/srs grade <id> <rating>`. Next card.
8. End: "Reviews done: X good/easy, Y to redo." Mention which idea was weakest.

Keep the rhythm quick: no long explanations here — deep re-teaching happens in lessons.
If the same card keeps coming back as `again`, note it: the lesson probably needs redoing,
and `/learn` should revisit that node.

## No-cards fallback (for `/quick` when nothing is due)

Pick the most recent lesson note, ask me 2 "explain it back" questions from it (no grading,
just feedback). That's still retrieval practice and still counts as the session.
