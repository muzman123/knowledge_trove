# Cards: Technical Interview Prep

### [ivp-001] What are the three groups of clarifying questions, in order?
node: approach
type: explain
Input → Output → Edge cases. Input: size, sorted?, negatives/duplicates. Output: values or indices, ties, always one answer? Edge cases: empty, one element, no answer.
Metaphor: a builder asks "how many floors?" before pouring concrete.

### [ivp-002] Why say the slow brute-force idea out loud before optimizing?
node: approach
type: explain
1) The interviewer sees your thinking. 2) It's the starting point: optimizing means finding what it wastes. 3) It's your safety net if time runs out, and a working slow answer beats a blank screen.
Metaphor: a climber clipping into the rope before the hard route.

### [ivp-003] How do you find the optimization in a brute-force solution?
node: approach
type: explain
Find the question the slow inner loop keeps asking, then pick the tool that answers it fast. Two-sum: fix x, and the inner loop is really asking "is target − x in the list?" → hash set → O(n).
Example table: "seen it?" → set · "how many?" → map · sorted pairs → two pointers · "smallest right now?" → heap.

### [ivp-004] Hash set vs hash map: which one for "how many times does each letter appear?"
node: approach
type: spot
Hash map. A set only stores yes/no ("have I seen it?", like a hand stamp). A map stores key → value ("how many?" or "at which index?", like a coat-check ticket).
"First unique letter" and "valid anagram" both need counts → map.

### [ivp-005] Is it true that using a Python dict is an "optimization" over a hash map? Why not?
node: approach
type: explain
No, they're the same thing. A Python `dict` IS a hash map, and a `set` IS a hash set. In the interview, say "hash map" so the interviewer hears the right term.
Valid anagram: counting with dicts is already the O(n) answer. The real brute force is O(n²) (cross out letters) or O(n log n) (sort both).

### [ivp-006] Before saying "done", what two things do you do?
node: approach
type: explain
1) Test: dry run (trace by hand) on the normal example, then edge cases (empty, one element, no answer). 2) Say time AND space complexity out loud with a "because", e.g. "O(n) time because each lookup is O(1); O(n) space for the set."
Metaphor: a pilot's pre-takeoff checklist.
