---
type: exercise
subject: interview-prep
node: approach
date: 2026-10-05
---
# Valid anagram: run the full interview method

**Problem:** given two strings, return true if one is an anagram of the other (`"listen"` / `"silent"` → true).

## My answer
> Do we worry about case sensitivity? Can input strings be empty? Lowercase everything if needed. Brute force: loop through each word, count letter usage in one dictionary, do the same for the other word in another dictionary, and if both dictionaries have the same letters and counts → true, otherwise false. Edge cases: if either string is empty, return false instantly. To optimize, I think we can use hash maps to count letter usage in both strings to reach a faster complexity.

## Feedback

| Step | Verdict | Notes |
|---|---|---|
| Clarify | ✓ good | Case + empty are both good questions. Could add: **spaces / punctuation?** (`"dormitory"` / `"dirty room"`) |
| Edge cases | 🟨 | Don't *decide* the empty-string answer yourself. **Ask** it: "two empty strings, true or false?" (Usually true.) Missed the best quick check: **different lengths → return false immediately.** |
| Brute force | 🟨 | Your "brute force" was actually the **optimal** solution already! A Python `dict` **is** a hash map. The real brute force is slower (see below). |
| Optimize | ✗ | Repeated your step 2, because dict = hash map. No Big-O stated. |
| State Big-O | ✗ | Missing. Always give time + space with a "because". |

> [!warning] Vocabulary trap
> **Python `dict` = hash map.** **Python `set` = hash set.** Same thing, different names. In the interview, say "hash map" and the interviewer hears the right thing.

## Corrected version

**1. Clarify:** case-sensitive? spaces/punctuation count? empty strings → true or false? only a–z, or any characters?

**2. Example:** `"listen"` / `"silent"`: both have l, i, s, t, e, n once each → true.

**3. Brute force:** for each letter in `s`, find a matching letter in `t` and cross it out. If one is missing → false.
Each search scans `t`, so $O(n^2)$ time.
*(Middle option: sort both strings and compare: $O(n \log n)$ time.)*

**4. Optimize:** repeated question = *"How many times does each letter appear?"* → **hash map**.
- Quick exit: `len(s) != len(t)` → false.
- One map: `+1` for each letter in `s`, `−1` for each letter in `t`. All counts are 0 → true.

```python
def is_anagram(s, t):
    if len(s) != len(t):
        return False
    count = {}
    for a, b in zip(s, t):
        count[a] = count.get(a, 0) + 1
        count[b] = count.get(b, 0) - 1
    return all(v == 0 for v in count.values())
```

**5. Test:** dry run on `"ab"`/`"ba"` → `{a: 0, b: 0}` → true. Edge cases: `""`/`""` → true · `"a"`/`"ab"` → false (length).

**6. Big-O:** time $O(n)$ because we walk each string once and every map update is $O(1)$ on average.
Space $O(k)$ for $k$ different letters. With only lowercase a–z, $k \le 26$, so effectively $O(1)$.
