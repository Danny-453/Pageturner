import { courses } from '../data/courses';
import { courseProgress as courseProgressPercentage } from '../utils/progress';
import { API_ENABLED, apiGet } from './api';

function toCourse(course, levels, progress, lessons) {
  const level = levels.find((item) => item.id === course.academic_level_id);
  return {
    ...course,
    level: level?.name ?? '',
    category: course.code.split(/[-\s]/)[0],
    progress: courseProgressPercentage(
      lessons,
      progress.filter((item) => item.course_id === course.id),
    ),
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
  const courseLessons = await Promise.all(
    items.map(async (course) => [
      course.id,
      await apiGet(`/lessons?course_id=${encodeURIComponent(course.id)}`),
    ]),
  );
  const lessonsByCourse = new Map(courseLessons);
  return items.map((course) => toCourse(course, levels, progress, lessonsByCourse.get(course.id) ?? []));
}

export async function getCourseById(id) {
  if (!API_ENABLED) return courses.find((course) => course.id === id);
  const [course, levels, progress, lessons] = await Promise.all([
    apiGet(`/courses/${encodeURIComponent(id)}`),
    apiGet('/academic-levels'),
    apiGet('/progress'),
    apiGet(`/lessons?course_id=${encodeURIComponent(id)}`),
  ]);
  return toCourse(course, levels, progress, lessons);
}
