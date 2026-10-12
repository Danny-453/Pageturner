import { lessons } from '../data/lessons';
import { API_ENABLED, apiGet } from './api';

function toLesson(lesson, courseId, topicNames, progress) {
  const completed = progress.find((item) => item.lesson_id === lesson.id)?.completed ?? false;
  return {
    ...lesson,
    courseId: courseId ?? lesson.course_id,
    topic: topicNames.get(lesson.topic_id) ?? 'Lesson',
    duration: `${lesson.estimated_minutes} min`,
    completed,
  };
}

export async function getLessons(courseId) {
  if (!API_ENABLED) return lessons.filter((lesson) => !courseId || lesson.courseId === courseId);

  const [items, progress] = await Promise.all([
    apiGet(`/lessons${courseId ? `?course_id=${encodeURIComponent(courseId)}` : ''}`),
    apiGet('/progress'),
  ]);
  const topicNames = new Map();
  if (courseId) {
    const topics = await apiGet(`/courses/${encodeURIComponent(courseId)}/topics`);
    topics.forEach((topic) => topicNames.set(topic.id, topic.title));
  }
  return items.map((lesson) => toLesson(lesson, courseId, topicNames, progress));
}

export async function getLessonById(id, courseId) {
  if (!API_ENABLED) return lessons.find((lesson) => lesson.id === id);
  const [lesson, progress] = await Promise.all([
    apiGet(`/lessons/${encodeURIComponent(id)}`),
    apiGet('/progress'),
  ]);
  if (!courseId) throw new Error('Course ID is required to load this lesson.');
  const topics = await apiGet(`/courses/${encodeURIComponent(courseId)}/topics`);
  const topicNames = new Map(topics.map((topic) => [topic.id, topic.title]));
  return toLesson(lesson, courseId, topicNames, progress);
}
