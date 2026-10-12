import { leaderboard } from '../data/leaderboard';
import { API_ENABLED, apiGet } from './api';

export async function getLeaderboard({ scope = 'department', courseId } = {}) {
  if (!API_ENABLED) {
    return leaderboard
      .filter((student) => scope !== 'level' || student.academicLevel === '300 Level')
      .map((student, index) => ({ ...student, rank: index + 1, courseId }));
  }
  const query = new URLSearchParams({ scope });
  if (courseId) query.set('course_id', courseId);
  const response = await apiGet(`/leaderboard?${query}`);
  return {
    ...response,
    entries: response.entries.map((entry) => ({
      ...entry,
      id: entry.user_id,
      academicLevel: entry.academic_level,
      answered: entry.questions_answered,
    })),
  };
}
