# PageTurners Backend Content Guide

Educational content is stored in PostgreSQL in Phase 2.

## Courses

Use `POST /api/v1/courses` as an administrator.

Required fields:

- `code`
- `title`
- `description`
- `academic_level_id`
- `is_published`

## Topics

Use `POST /api/v1/courses/{course_id}/topics`.

## Lesson notes

Use `POST /api/v1/lessons` and supply:

```json
{
  "topic_id": "...",
  "title": "Introduction to Geophysical Methods",
  "content": "Lesson notes...",
  "order": 1,
  "estimated_minutes": 20
}
```

## Questions

Use `POST /api/v1/questions`.

A question contains:

- question text
- question type
- difficulty
- explanation
- points
- correct answer
- options
- publication status

The correct answer is stored server-side and is never included in ordinary question retrieval responses.

## Achievements

Use `POST /api/v1/achievements` as an administrator.

## Learning levels

Learning levels are database records and should be managed through a controlled migration/admin workflow rather than hardcoded in React components.
