import { achievements } from '../data/achievements';
import { API_ENABLED, apiGet } from './api';

export async function getAchievements() {
  if (!API_ENABLED) return achievements;
  const [all, earned] = await Promise.all([
    apiGet('/achievements'),
    apiGet('/achievements/mine'),
  ]);
  const earnedById = new Map(earned.map((item) => [item.id, item]));
  return all.map((item) => {
    const award = earnedById.get(item.id);
    return {
      ...item,
      title: item.name,
      icon: String(item.threshold).padStart(2, '0'),
      unlocked: Boolean(award),
      date: award?.awarded_at ? new Date(award.awarded_at).toLocaleDateString() : undefined,
    };
  });
}
