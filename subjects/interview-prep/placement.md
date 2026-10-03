---
type: placement
subject: interview-prep
date: 2026-10-02
---
# Placement quiz — Technical Interview Prep

## Summary by strand

### 1. Data structures
- **Floor (solid):** hash sets for O(1) average lookup; recognizes the two-pointer concept by name.
- **Ceiling (gap):** binary heaps / priority queues — picked hash map instead of heap for O(log n) min/max access.

### 2. Algorithmic patterns
- **Floor (solid):** can define the two-pointer technique correctly.
- **Ceiling (gap):** doesn't always pick the *optimal* technique under pressure — for a sorted-array two-sum, chose "binary search per element" (O(n log n)) over two-pointer (O(n)). Knows the tool exists but doesn't always reach for the best one.

### 3. Complexity analysis
- **Floor (solid):** correctly analyzes iterative nested loops (O(n²)).
- **Ceiling (gap):** recursive/branching complexity — called naive recursive Fibonacci O(n²) instead of O(2ⁿ). Recursion-tree counting is the specific weak spot, not complexity analysis overall.

### 4. System design fundamentals
- **Floor (solid):** caching to reduce DB read load, load balancer purpose, cache invalidation/consistency problem across replicas.
- **Ceiling (gap):** CAP theorem / consistency vs. availability trade-off in replication — picked "caching" instead.

### 5. Networking & distributed systems
- **Floor (solid):** TCP vs UDP, CDN purpose, WebSockets for real-time bidirectional comms, forward vs. reverse proxy — all correct, higher floor than expected.
- **Ceiling (gap):** consistent hashing for distributed cache rebalancing — picked LRU eviction instead.

## Overall read
Floor is well above beginner — real working knowledge of networking and basic system design from practical experience. The gaps are specifically the "interview vocabulary / pattern recognition" layer: naming and reaching for the right technique (heaps, two-pointer vs. alternatives, recursion-tree Big-O, CAP theorem, consistent hashing) rather than foundational misunderstanding. Roadmap should skip basic definitions (what is Big-O, what is a hash map, what is a load balancer) and start at pattern selection + the specific named gaps.

## Questions asked

| # | Question (short) | Answer | Result |
|---|---|---|---|
| 1 | Best avg lookup structure | B (hash set O(1)) | ✓ |
| 2 | Sorted array two-sum, most efficient | D (binary search/elem) | ✗ (optimal was two-pointer) |
| 3 | Naive recursive Fibonacci complexity | B (O(n²)) | ✗ (correct: O(2ⁿ)) |
| 4 | First fix for DB read overload | A (cache) | ✓ |
| 5 | What load balancer solves | A (distributes requests) | ✓ |
| 6 | Structure for O(log n) min/max | D (hash map) | ✗ (correct: binary heap) |
| 7 | Definition of two-pointer technique | B | ✓ |
| 8 | Fix for exponential Fibonacci blowup | A (memoization) | ✓ |
| 9 | Stale cache across replicas = ? | B (cache invalidation/consistency) | ✓ |
| 10 | TCP vs UDP difference | B | ✓ |
| 11 | Nested loop (n × n) complexity | C (O(n²)) | ✓ |
| 12 | Replication latency vs. freshness trade-off | D (caching) | ✗ (correct: CAP theorem) |
| 13 | What a CDN is for | B | ✓ |
| 14 | Tech for real-time bidirectional comms | B (WebSockets) | ✓ |
| 15 | Forward vs. reverse proxy | B | ✓ |
| 16 | Avoiding cache remap on server add/remove | D (LRU eviction) | ✗ (correct: consistent hashing) |
