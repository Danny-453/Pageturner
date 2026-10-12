import { questions } from '../data/questions';
import { API_ENABLED, apiGet, apiPost } from './api';

function toQuestion(question, courseId) {
  return {
    ...question,
    courseId: courseId ?? question.course_id,
    question: question.question_text ?? question.question,
    options: question.options.map((option) => ({
      id: option.option_key ?? option.id,
      text: option.text,
    })),
  };
}

export async function getQuestions(courseId) {
  if (!API_ENABLED) return questions.filter((question) => !courseId || question.courseId === courseId);
  const items = await apiGet(`/questions${courseId ? `?course_id=${encodeURIComponent(courseId)}` : ''}`);
  if (courseId) return items.map((question) => toQuestion(question, courseId));

  const courses = await apiGet('/courses');
  const topicCourses = await Promise.all(courses.map(async (course) => {
    const topics = await apiGet(`/courses/${encodeURIComponent(course.id)}/topics`);
    return topics.map((topic) => [topic.id, course.id]);
  }));
  const courseByTopic = new Map(topicCourses.flat());
  return items.map((question) => toQuestion(question, courseByTopic.get(question.topic_id)));
}

export async function getQuestionById(id) {
  if (!API_ENABLED) return questions.find((question) => question.id === id);
  return toQuestion(await apiGet(`/questions/${encodeURIComponent(id)}`));
}

export async function evaluateAnswer(question, answerId) {
  if (!API_ENABLED) {
    const correct = question.correctAnswer === answerId;
    return {
      correct,
      points: correct ? question.points : 0,
      explanation: question.explanation,
    };
  }
  return apiPost(`/questions/${encodeURIComponent(question.id)}/answer`, { answer_id: answerId });
}
