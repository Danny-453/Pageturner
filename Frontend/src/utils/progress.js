import { learningLevels } from '../data/learningLevels.js';
export function getLearningLevel(correctAnswers){let current=learningLevels[0]; for(const level of learningLevels){if(correctAnswers>=level.threshold)current=level;} return current;}
export function percentage(value,total){return total?Math.round((value/total)*100):0;}
export function courseProgress(lessons, progress) {
  const lessonIds = new Set(lessons.map((lesson) => lesson.id));
  if (!lessonIds.size) return 0;

  const completedLessonIds = new Set(
    progress
      .filter((item) => item.completed && lessonIds.has(item.lesson_id))
      .map((item) => item.lesson_id),
  );
  return percentage(completedLessonIds.size, lessonIds.size);
}
