---
type: dashboard
---
# 🎯 Learning Dashboard

![[stats#Stats]]

## 📚 Subjects

```dataview
TABLE WITHOUT ID
  link(file.link, title) AS "Subject",
  goal AS "Goal",
  nodes_solid + " / " + nodes_total AS "Solid",
  next_node AS "Next lesson",
  status AS "Status",
  updated AS "Updated"
FROM "Learning/subjects"
WHERE type = "map"
SORT updated DESC
```

## 📘 Recent lessons

```dataview
TABLE WITHOUT ID
  file.link AS "Lesson",
  subject AS "Subject",
  status AS "Status"
FROM "Learning/subjects"
WHERE type = "lesson"
SORT date DESC
LIMIT 10
```

## 🗓️ Last 7 sessions

```dataview
LIST
FROM "Learning/sessions"
WHERE type = "session-log"
SORT date DESC
LIMIT 7
```

---
*The tables need the free **Dataview** community plugin (Settings → Community plugins → Browse → "Dataview" → Install → Enable). The stats block above works without it.*
