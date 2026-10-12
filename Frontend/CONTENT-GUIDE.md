# PageTurners Content Editing Guide

## LESSON NOTES
File: `src/data/lessons/index.js`

Add a lesson object with `id`, `courseId`, `topicId`, `title`, `topic`, `order`, `duration`, `completed`, and `content`.

## QUIZ QUESTIONS
File: `src/data/questions/index.js`

Add `question`, `options`, `correctAnswer`, `explanation`, `courseId`, `topicId`, `difficulty`, `points`, and `type`.

## COURSES
File: `src/data/courses.js`

Add the course object with its code, title, level, description and learning metadata.

## ACHIEVEMENTS
File: `src/data/achievements.js`

Modify the achievement title, description, icon marker, unlocked state and date.

## LEARNING LEVELS
File: `src/data/learningLevels.js`

Modify names and correct-answer thresholds. Keep thresholds as data because the future backend will become authoritative.

## MOCK STUDENTS
File: `src/data/students.js`

Use this file only for Phase 1 demonstration data. Do not place real student personal data in source control.
