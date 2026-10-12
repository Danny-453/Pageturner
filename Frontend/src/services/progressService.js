import { API_ENABLED, apiRequest } from './api';

export async function markLessonComplete(courseId, lessonId) {
  if (!API_ENABLED) return { completed: true };
  return apiRequest('/progress', {
    method: 'PUT',
    body: JSON.stringify({
      course_id: courseId,
      lesson_id: lessonId,
      completed: true,
      percent: 100,
    }),
  });
}