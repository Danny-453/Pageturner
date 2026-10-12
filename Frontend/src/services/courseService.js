import { courses } from '../data/courses';
import { API_ENABLED, apiGet } from './api';

function toCourse(course, levels, progress) {
  const courseProgress = progress.filter((item) => item.course_id === course.id);
  const level = levels.find((item) => item.id === course.academic_level_id);
  return {
    ...course,
    level: level?.name ?? '',
    category: course.code.split(/[-\s]/)[0],
    progress: courseProgress.length
      ? Math.round(courseProgress.reduce((sum, item) => sum + item.percent, 0) / courseProgress.length)
      : 0,
    averageScore: API_ENABLED ? null : course.averageScore,
    topics: undefined,
    questions: undefined,
    color: 'purple',
  };
}

export async function getCourses() {
  if (!API_ENABLED) return courses;
  const [items, levels, progress] = await Promise.all([
    apiGet('/courses'),
    apiGet('/academic-levels'),
    apiGet('/progress'),
  ]);
  return items.map((course) => toCourse(course, levels, progress));
}

export async function getCourseById(id) {
  if (!API_ENABLED) return courses.find((course) => course.id === id);
  const [course, levels, progress] = await Promise.all([
    apiGet(`/courses/${encodeURIComponent(id)}`),
    apiGet('/academic-levels'),
    apiGet('/progress'),
  ]);
  return toCourse(course, levels, progress);
}
