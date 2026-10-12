import { currentStudent } from '../data/students';
import { API_ENABLED, AUTH_TOKEN_KEY, apiGet, apiPost } from './api';

function normalizeUser(user) {
  return {
    ...user,
    name: user.full_name ?? user.name,
    studentId: user.student_id ?? user.studentId,
    academicLevelId: user.academic_level_id ?? user.academicLevelId,
    points: user.total_points ?? user.points ?? 0,
    streak: user.current_streak ?? user.streak ?? 0,
    answered: user.questions_answered ?? user.answered ?? 0,
    correct: user.correct_answers ?? user.correct ?? 0,
    accuracy: user.accuracy ?? 0,
  };
}

function saveToken(token) {
  if (token) localStorage.setItem(AUTH_TOKEN_KEY, token);
  else localStorage.removeItem(AUTH_TOKEN_KEY);
}

export async function login(email, password) {
  if (!email || !password) throw new Error('Email and password are required.');
  if (!API_ENABLED) {
    await new Promise((resolve) => setTimeout(resolve, 250));
    return { token: 'mock-jwt-token', user: normalizeUser({ ...currentStudent, email }) };
  }

  const result = await apiPost('/auth/login', { email, password });
  saveToken(result.access_token);
  return { token: result.access_token, user: normalizeUser(result.user) };
}

export async function register(payload) {
  if (!API_ENABLED) {
    await new Promise((resolve) => setTimeout(resolve, 250));
    return {
      token: 'mock-jwt-token',
      user: normalizeUser({
        ...currentStudent,
        name: payload.fullName,
        email: payload.email,
        academicLevel: payload.academicLevel,
        studentId: payload.studentId,
      }),
    };
  }

  let academicLevelId = payload.academicLevelId;
  if (!academicLevelId) {
    const levels = await apiGet('/academic-levels');
    academicLevelId = levels.find((level) => level.name === payload.academicLevel)?.id;
  }
  if (!academicLevelId) throw new Error('Select a valid academic level.');

  const result = await apiPost('/auth/register', {
    full_name: payload.fullName,
    email: payload.email,
    password: payload.password,
    student_id: payload.studentId || null,
    academic_level_id: academicLevelId,
  });
  saveToken(result.access_token);
  return { token: result.access_token, user: normalizeUser(result.user) };
}

export async function getCurrentUser() {
  const user = await apiGet('/auth/me');
  return normalizeUser(user);
}

export function requestPasswordReset(email) {
  return apiPost('/auth/password-reset/request', { email });
}

export function confirmPasswordReset(token, newPassword) {
  return apiPost('/auth/password-reset/confirm', { token, new_password: newPassword });
}

export function logout() {
  saveToken(null);
  return Promise.resolve();
}
