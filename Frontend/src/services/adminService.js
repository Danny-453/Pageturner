import { apiPost } from './api';

export function generateLessonQuestions(lessonId) {
  return apiPost(`/admin/lessons/${encodeURIComponent(lessonId)}/generate-questions`, {});
}

export function saveLessonQuestions(lessonId, questions) {
  return apiPost(`/admin/lessons/${encodeURIComponent(lessonId)}/questions`, { questions });
}
