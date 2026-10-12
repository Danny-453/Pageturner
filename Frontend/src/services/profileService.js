import { currentStudent } from '../data/students';
import { API_ENABLED, apiGet } from './api';

export async function getCurrentProfile() {
  if (!API_ENABLED) return currentStudent;
  const [user, levels, learningLevels] = await Promise.all([
    apiGet('/users/me'),
    apiGet('/academic-levels'),
    apiGet('/learning-levels'),
  ]);
  const academicLevel = levels.find((level) => level.id === user.academic_level_id)?.name ?? '';
  const learningLevel = learningLevels
    .filter((level) => level.required_correct_answers <= user.correct_answers)
    .at(-1);
  return {
    ...user,
    name: user.full_name,
    studentId: user.student_id,
    academicLevel,
    learningLevel: learningLevel?.level ?? 1,
    learningTitle: learningLevel?.name ?? learningLevels[0]?.name ?? 'Beginner',
    points: user.total_points,
    streak: user.current_streak,
    answered: user.questions_answered,
    correct: user.correct_answers,
    accuracy: user.accuracy,
  };
}
