import { useEffect, useState } from 'react';
import PageHeader from '../../components/common/PageHeader';
import { useAuth } from '../../context/AuthContext';
import { students } from '../../data/students';
import { API_ENABLED, apiGet, apiPost, apiRequest } from '../../services/api';
import { getCourses } from '../../services/courseService';
import { getLessons } from '../../services/lessonService';
import { getQuestions } from '../../services/questionService';

const fieldStyle = { marginTop: 14 };
const inputStyle = { width: '100%' };

function FormField({ label, children }) {
  return (
    <div className="form-field" style={fieldStyle}>
      <label>{label}</label>
      {children}
    </div>
  );
}

export default function AdminPage() {
  const { user } = useAuth();
  const [counts, setCounts] = useState(null);
  const [levels, setLevels] = useState([]);
  const [courses, setCourses] = useState([]);
  const [topics, setTopics] = useState([]);
  const [contentLessons, setContentLessons] = useState([]);
  const [contentQuestions, setContentQuestions] = useState([]);
  const [courseId, setCourseId] = useState('');
  const [topicId, setTopicId] = useState('');
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(null);
  const [courseForm, setCourseForm] = useState({ code: '', title: '', description: '', academic_level_id: '' });
  const [topicForm, setTopicForm] = useState({ title: '', description: '', order: 1 });
  const [lessonForm, setLessonForm] = useState({ title: '', content: '', order: 1, estimated_minutes: 15 });
  const [questionForm, setQuestionForm] = useState({
    question_text: '',
    difficulty: 'medium',
    explanation: '',
    points: 10,
    correct_answer: 'a',
    options: [
      { option_key: 'a', text: '', order: 1 },
      { option_key: 'b', text: '', order: 2 },
      { option_key: 'c', text: '', order: 3 },
      { option_key: 'd', text: '', order: 4 },
    ],
  });

  async function refreshContent() {
    const [courseItems, lessonItems, questionItems, users] = await Promise.all([
      getCourses(),
      getLessons(),
      getQuestions(),
      apiGet('/users'),
    ]);
    setCourses(courseItems);
    setCounts({
      students: users.length,
      courses: courseItems.length,
      lessons: lessonItems.length,
      questions: questionItems.length,
    });
    return courseItems;
  }

  useEffect(() => {
    if (API_ENABLED && user?.role !== 'admin') return undefined;
    let active = true;
    const load = async () => {
      try {
        if (API_ENABLED) {
          const [levelItems, courseItems] = await Promise.all([
            apiGet('/academic-levels'),
            getCourses(),
          ]);
          const [lessonItems, questionItems, users] = await Promise.all([
            getLessons(),
            getQuestions(),
            apiGet('/users'),
          ]);
          if (!active) return;
          setLevels(levelItems);
          setCourses(courseItems);
          setCounts({
            students: users.length,
            courses: courseItems.length,
            lessons: lessonItems.length,
            questions: questionItems.length,
          });
          setCourseForm((current) => ({
            ...current,
            academic_level_id: current.academic_level_id || levelItems[0]?.id || '',
          }));
          setCourseId((current) => current || courseItems[0]?.id || '');
        } else {
          const [courseItems, lessonItems, questionItems] = await Promise.all([
            getCourses(),
            getLessons(),
            getQuestions(),
          ]);
          if (!active) return;
          setCounts({
            students: students.length,
            courses: courseItems.length,
            lessons: lessonItems.length,
            questions: questionItems.length,
          });
        }
      } catch (loadError) {
        if (active) setError(loadError.message);
      }
    };
    load();
    return () => {
      active = false;
    };
  }, [user]);

  useEffect(() => {
    if (!API_ENABLED || !courseId || user?.role !== 'admin') return undefined;
    let active = true;
    Promise.all([
      apiGet(`/courses/${encodeURIComponent(courseId)}/topics`),
      getLessons(courseId),
      getQuestions(courseId),
    ])
      .then(([items, lessonItems, questionItems]) => {
        if (!active) return;
        setTopics(items);
        setContentLessons(lessonItems);
        setContentQuestions(questionItems);
        setTopicId((current) => items.some((item) => item.id === current) ? current : items[0]?.id || '');
      })
      .catch((loadError) => {
        if (active) setError(loadError.message);
      });
    return () => {
      active = false;
    };
  }, [courseId, user]);

  async function deleteContent(type, id, label) {
    const messages = {
      course: `Delete "${label}" and all its topics, lessons, quiz questions, and related progress? This cannot be undone.`,
      topic: `Delete topic "${label}" and all its lessons and quiz questions? This cannot be undone.`,
      lesson: `Delete lesson "${label}"? This cannot be undone.`,
      question: `Delete quiz question "${label}" and its attempt history? This cannot be undone.`,
    };
    if (!window.confirm(messages[type])) return;

    setError('');
    setNotice('');
    setSaving(true);
    try {
      const path = type === 'topic'
        ? `/courses/topics/${encodeURIComponent(id)}`
        : `/${type === 'course' ? 'courses' : type === 'lesson' ? 'lessons' : 'questions'}/${encodeURIComponent(id)}`;
      await apiRequest(path, { method: 'DELETE' });
      const updatedCourses = await refreshContent();
      if (type === 'course') {
        setCourseId((current) => current === id ? updatedCourses[0]?.id || '' : current);
      } else if (type === 'topic') {
        const updatedTopics = await apiGet(`/courses/${encodeURIComponent(courseId)}/topics`);
        setTopics(updatedTopics);
        setTopicId((current) => current === id ? updatedTopics[0]?.id || '' : current);
        setContentLessons((current) => current.filter((lesson) => lesson.topic_id !== id));
        setContentQuestions((current) => current.filter((question) => question.topic_id !== id));
      } else if (type === 'lesson') {
        setContentLessons((current) => current.filter((lesson) => lesson.id !== id));
      } else {
        setContentQuestions((current) => current.filter((question) => question.id !== id));
      }
      setNotice(`${type[0].toUpperCase()}${type.slice(1)} deleted.`);
    } catch (deleteError) {
      setError(deleteError.message);
    } finally {
      setSaving(false);
    }
  }

  async function beginEdit(type, item) {
    setError('');
    setNotice('');
    try {
      const form = type === 'question'
        ? await apiGet(`/questions/${encodeURIComponent(item.id)}/admin`)
        : { ...item };
      setEditing({ type, id: item.id, form });
    } catch (editError) {
      setError(editError.message);
    }
  }

  async function saveEdit(event) {
    event.preventDefault();
    if (!editing) return;
    setError('');
    setNotice('');
    setSaving(true);
    try {
      const { type, id, form } = editing;
      const path = type === 'topic'
        ? `/courses/topics/${encodeURIComponent(id)}`
        : `/${type === 'course' ? 'courses' : type === 'lesson' ? 'lessons' : 'questions'}/${encodeURIComponent(id)}`;
      const body = type === 'question'
        ? {
          question_text: form.question_text,
          question_type: form.question_type,
          difficulty: form.difficulty,
          explanation: form.explanation,
          points: Number(form.points),
          correct_answer: form.correct_answer,
          is_published: form.is_published,
          options: form.options.map((option, index) => ({
            option_key: option.option_key,
            text: option.text,
            order: Number(option.order ?? index + 1),
          })),
        }
        : type === 'course'
          ? { code: form.code, title: form.title, description: form.description, academic_level_id: form.academic_level_id }
          : type === 'lesson'
            ? { title: form.title, content: form.content, order: Number(form.order), estimated_minutes: Number(form.estimated_minutes) }
            : { title: form.title, description: form.description, order: Number(form.order) };
      await apiRequest(path, { method: 'PATCH', body: JSON.stringify(body) });
      await refreshContent();
      const [updatedTopics, updatedLessons, updatedQuestions] = await Promise.all([
        apiGet(`/courses/${encodeURIComponent(courseId)}/topics`),
        getLessons(courseId),
        getQuestions(courseId),
      ]);
      setTopics(updatedTopics);
      setContentLessons(updatedLessons);
      setContentQuestions(updatedQuestions);
      setEditing(null);
      setNotice(`${type[0].toUpperCase()}${type.slice(1)} updated.`);
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSaving(false);
    }
  }

  function updateEditForm(field, value) {
    setEditing((current) => ({ ...current, form: { ...current.form, [field]: value } }));
  }

  async function submitContent(event, path, body, onSuccess) {
    event.preventDefault();
    setError('');
    setNotice('');
    setSaving(true);
    try {
      const created = await apiPost(path, body);
      onSuccess?.(created);
      await refreshContent();
      if (path === '/courses') setCourseId(created.id);
      if (path.endsWith('/topics')) {
        const updatedTopics = await apiGet(`/courses/${encodeURIComponent(courseId)}/topics`);
        setTopics(updatedTopics);
        setTopicId(created.id);
      }
      setNotice('Saved successfully.');
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSaving(false);
    }
  }

  if (API_ENABLED && user?.role !== 'admin') {
    return (
      <div className="page-container">
        <div className="notice" style={{ color: 'var(--color-error)' }}>
          Administrator access is required to manage courses and learning content.
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Administration"
        title="Manage learning content"
        description="Add a course for an academic level, organize it into topics, then add lessons and quiz questions."
      />
      {error && <div className="notice" role="alert" style={{ color: 'var(--color-error)', marginBottom: 16 }}>{error}</div>}
      {notice && <div className="notice" role="status" style={{ marginBottom: 16 }}>{notice}</div>}

      <div className="grid-4">
        {[
          ['Students', counts?.students],
          ['Courses', counts?.courses],
          ['Lessons', counts?.lessons],
          ['Questions', counts?.questions],
        ].map(([label, count]) => (
          <div className="card card-pad" key={label}>
            <div className="eyebrow">{label}</div>
            <div style={{ fontSize: 34, fontWeight: 850, marginTop: 6 }}>{count ?? '—'}</div>
          </div>
        ))}
      </div>

      {!API_ENABLED ? (
        <div className="notice" style={{ marginTop: 20 }}>
          Set <code>VITE_API_BASE_URL</code> and connect as an administrator to add content.
        </div>
      ) : (
        <>
          <section className="card card-pad" style={{ marginTop: 20 }}>
            <div className="eyebrow">Existing content</div>
            <h2 style={{ marginTop: 6 }}>Edit or delete learning content</h2>
            <p className="muted">
              Edit a course, topic, lesson, or question here. Deleting a course or topic also deletes its nested learning content.
            </p>
            <FormField label="Choose a course to manage">
              <select className="select" style={inputStyle} value={courseId} onChange={(event) => setCourseId(event.target.value)}>
                <option value="">Select a course</option>
                {courses.map((course) => <option key={course.id} value={course.id}>{course.code} · {course.title}</option>)}
              </select>
            </FormField>
            {courseId && (
              <div className="notice" style={{ marginTop: 16 }}>
                <div className="row space-between" style={{ flexWrap: 'wrap' }}>
                  <strong>{courses.find((course) => course.id === courseId)?.code} · {courses.find((course) => course.id === courseId)?.title}</strong>
                  <div className="row">
                    <button type="button" className="btn btn-ghost" disabled={saving} onClick={() => beginEdit('course', courses.find((course) => course.id === courseId))}>Edit course</button>
                    <button
                      type="button"
                      className="btn btn-ghost"
                      style={{ color: 'var(--color-error)' }}
                      disabled={saving}
                      onClick={() => deleteContent('course', courseId, courses.find((course) => course.id === courseId)?.title)}
                    >Delete course</button>
                  </div>
                </div>
                <div className="stack" style={{ marginTop: 12 }}>
                  {topics.map((topic) => (
                    <div className="card card-pad" key={topic.id}>
                      <div className="row space-between" style={{ flexWrap: 'wrap' }}>
                        <strong>{topic.title}</strong>
                        <div className="row">
                          <button type="button" className="btn btn-ghost" disabled={saving} onClick={() => beginEdit('topic', topic)}>Edit topic</button>
                          <button
                            type="button"
                            className="btn btn-ghost"
                            style={{ color: 'var(--color-error)' }}
                            disabled={saving}
                            onClick={() => deleteContent('topic', topic.id, topic.title)}
                          >Delete topic</button>
                        </div>
                      </div>
                      <div className="stack" style={{ gap: 8, marginTop: 10 }}>
                        {contentLessons.filter((lesson) => lesson.topic_id === topic.id).map((lesson) => (
                          <div className="row space-between" key={lesson.id} style={{ flexWrap: 'wrap' }}>
                            <span>Lesson: {lesson.title}</span>
                            <div className="row">
                              <button type="button" className="btn btn-ghost" disabled={saving} onClick={() => beginEdit('lesson', lesson)}>Edit lesson</button>
                              <button
                                type="button"
                                className="btn btn-ghost"
                                style={{ color: 'var(--color-error)' }}
                                disabled={saving}
                                onClick={() => deleteContent('lesson', lesson.id, lesson.title)}
                              >Delete lesson</button>
                            </div>
                          </div>
                        ))}
                        {contentQuestions.filter((question) => question.topic_id === topic.id).map((question) => (
                          <div className="row space-between" key={question.id} style={{ flexWrap: 'wrap' }}>
                            <span>Quiz: {question.question}</span>
                            <div className="row">
                              <button type="button" className="btn btn-ghost" disabled={saving} onClick={() => beginEdit('question', question)}>Edit question</button>
                              <button
                                type="button"
                                className="btn btn-ghost"
                                style={{ color: 'var(--color-error)' }}
                                disabled={saving}
                                onClick={() => deleteContent('question', question.id, question.question)}
                              >Delete question</button>
                            </div>
                          </div>
                        ))}
                        {!contentLessons.some((lesson) => lesson.topic_id === topic.id)
                          && !contentQuestions.some((question) => question.topic_id === topic.id)
                          && <span className="muted">No lessons or questions in this topic yet.</span>}
                      </div>
                    </div>
                  ))}
                  {!topics.length && <span className="muted">This course has no topics yet.</span>}
                </div>
              </div>
            )}
            {editing && (
              <form className="card card-pad" style={{ marginTop: 16 }} onSubmit={saveEdit}>
                <div className="row space-between" style={{ flexWrap: 'wrap' }}>
                  <h3 style={{ margin: 0 }}>Edit {editing.type}</h3>
                  <button type="button" className="btn btn-ghost" disabled={saving} onClick={() => setEditing(null)}>Cancel</button>
                </div>
                {editing.type === 'course' && (
                  <>
                    <div className="grid-2">
                      <FormField label="Course code"><input className="input" style={inputStyle} value={editing.form.code || ''} onChange={(event) => updateEditForm('code', event.target.value)} required maxLength={30} /></FormField>
                      <FormField label="Course title"><input className="input" style={inputStyle} value={editing.form.title || ''} onChange={(event) => updateEditForm('title', event.target.value)} required minLength={2} /></FormField>
                    </div>
                    <FormField label="Academic level">
                      <select className="select" style={inputStyle} value={editing.form.academic_level_id || ''} onChange={(event) => updateEditForm('academic_level_id', event.target.value)} required>
                        {levels.map((level) => <option key={level.id} value={level.id}>{level.name}</option>)}
                      </select>
                    </FormField>
                    <FormField label="Course description"><textarea className="input" style={{ ...inputStyle, minHeight: 90 }} value={editing.form.description || ''} onChange={(event) => updateEditForm('description', event.target.value)} required /></FormField>
                  </>
                )}
                {editing.type === 'topic' && (
                  <>
                    <FormField label="Topic title"><input className="input" style={inputStyle} value={editing.form.title || ''} onChange={(event) => updateEditForm('title', event.target.value)} required /></FormField>
                    <FormField label="Topic description"><textarea className="input" style={{ ...inputStyle, minHeight: 70 }} value={editing.form.description || ''} onChange={(event) => updateEditForm('description', event.target.value)} /></FormField>
                    <FormField label="Topic order"><input className="input" style={inputStyle} type="number" min="1" value={editing.form.order ?? 1} onChange={(event) => updateEditForm('order', Number(event.target.value))} required /></FormField>
                  </>
                )}
                {editing.type === 'lesson' && (
                  <>
                    <FormField label="Lesson title"><input className="input" style={inputStyle} value={editing.form.title || ''} onChange={(event) => updateEditForm('title', event.target.value)} required /></FormField>
                    <FormField label="Lesson content"><textarea className="input" style={{ ...inputStyle, minHeight: 180 }} value={editing.form.content || ''} onChange={(event) => updateEditForm('content', event.target.value)} required /></FormField>
                    <div className="grid-2">
                      <FormField label="Lesson order"><input className="input" style={inputStyle} type="number" min="1" value={editing.form.order ?? 1} onChange={(event) => updateEditForm('order', Number(event.target.value))} required /></FormField>
                      <FormField label="Estimated minutes"><input className="input" style={inputStyle} type="number" min="1" value={editing.form.estimated_minutes ?? 15} onChange={(event) => updateEditForm('estimated_minutes', Number(event.target.value))} required /></FormField>
                    </div>
                  </>
                )}
                {editing.type === 'question' && (
                  <>
                    <FormField label="Question"><textarea className="input" style={{ ...inputStyle, minHeight: 80 }} value={editing.form.question_text || ''} onChange={(event) => updateEditForm('question_text', event.target.value)} required /></FormField>
                    <div className="grid-2">
                      <FormField label="Difficulty">
                        <select className="select" style={inputStyle} value={editing.form.difficulty} onChange={(event) => updateEditForm('difficulty', event.target.value)}>
                          <option value="easy">Easy</option><option value="medium">Medium</option><option value="hard">Hard</option>
                        </select>
                      </FormField>
                      <FormField label="Points"><input className="input" style={inputStyle} type="number" min="0" value={editing.form.points} onChange={(event) => updateEditForm('points', Number(event.target.value))} required /></FormField>
                    </div>
                    <div className="stack" style={{ gap: 10, marginTop: 16 }}>
                      {editing.form.options.map((option, index) => (
                        <FormField key={option.option_key} label={`Option ${option.option_key.toUpperCase()}${editing.form.correct_answer === option.option_key ? ' (correct answer)' : ''}`}>
                          <div className="row">
                            <input type="radio" name="edit-correct-answer" aria-label={`Mark option ${option.option_key} as correct`} checked={editing.form.correct_answer === option.option_key} onChange={() => updateEditForm('correct_answer', option.option_key)} />
                            <input className="input" style={inputStyle} value={option.text} onChange={(event) => updateEditForm('options', editing.form.options.map((item, itemIndex) => itemIndex === index ? { ...item, text: event.target.value } : item))} required />
                          </div>
                        </FormField>
                      ))}
                    </div>
                    <FormField label="Explanation shown after answering"><textarea className="input" style={{ ...inputStyle, minHeight: 80 }} value={editing.form.explanation || ''} onChange={(event) => updateEditForm('explanation', event.target.value)} required /></FormField>
                  </>
                )}
                <button className="btn btn-primary" style={{ marginTop: 16 }} disabled={saving}>{saving ? 'Saving…' : `Save ${editing.type}`}</button>
              </form>
            )}
            {!courses.length && <p className="muted">No courses have been created yet.</p>}
          </section>

          <section className="card card-pad" style={{ marginTop: 20 }}>
            <div className="eyebrow">Step 1</div>
            <h2 style={{ marginTop: 6 }}>Create a course</h2>
            <p className="muted">Choose the academic level this course belongs to.</p>
            <form onSubmit={(event) => submitContent(event, '/courses', courseForm, () => {
              setCourseForm((current) => ({ ...current, code: '', title: '', description: '' }));
            })}>
              <div className="grid-2">
                <FormField label="Course code">
                  <input className="input" style={inputStyle} value={courseForm.code} onChange={(event) => setCourseForm({ ...courseForm, code: event.target.value })} required maxLength={30} placeholder="e.g. GEO-201" />
                </FormField>
                <FormField label="Course title">
                  <input className="input" style={inputStyle} value={courseForm.title} onChange={(event) => setCourseForm({ ...courseForm, title: event.target.value })} required minLength={2} placeholder="e.g. Structural Geology" />
                </FormField>
              </div>
              <FormField label="Academic level">
                <select className="select" style={inputStyle} value={courseForm.academic_level_id} onChange={(event) => setCourseForm({ ...courseForm, academic_level_id: event.target.value })} required>
                  <option value="" disabled>Select a level</option>
                  {levels.map((level) => <option key={level.id} value={level.id}>{level.name}</option>)}
                </select>
              </FormField>
              <FormField label="Course description">
                <textarea className="input" style={{ ...inputStyle, minHeight: 90 }} value={courseForm.description} onChange={(event) => setCourseForm({ ...courseForm, description: event.target.value })} required />
              </FormField>
              <button className="btn btn-primary" style={{ marginTop: 16 }} disabled={saving}>{saving ? 'Saving…' : 'Create course'}</button>
            </form>
          </section>

          <section className="card card-pad" style={{ marginTop: 20 }}>
            <div className="eyebrow">Step 2</div>
            <h2 style={{ marginTop: 6 }}>Add a topic to a course</h2>
            <FormField label="Choose course">
              <select className="select" style={inputStyle} value={courseId} onChange={(event) => setCourseId(event.target.value)} required>
                <option value="" disabled>Select a course</option>
                {courses.map((course) => <option key={course.id} value={course.id}>{course.code} · {course.title}</option>)}
              </select>
            </FormField>
            <form onSubmit={(event) => submitContent(event, `/courses/${encodeURIComponent(courseId)}/topics`, topicForm, () => {
              setTopicForm({ title: '', description: '', order: topics.length + 1 });
            })}>
              <FormField label="Topic title">
                <input className="input" style={inputStyle} value={topicForm.title} onChange={(event) => setTopicForm({ ...topicForm, title: event.target.value })} required placeholder="e.g. Stress and strain" />
              </FormField>
              <FormField label="Topic description">
                <textarea className="input" style={{ ...inputStyle, minHeight: 70 }} value={topicForm.description} onChange={(event) => setTopicForm({ ...topicForm, description: event.target.value })} />
              </FormField>
              <FormField label="Topic order">
                <input className="input" style={inputStyle} type="number" min="1" value={topicForm.order} onChange={(event) => setTopicForm({ ...topicForm, order: Number(event.target.value) })} required />
              </FormField>
              <button className="btn btn-primary" style={{ marginTop: 16 }} disabled={saving || !courseId}>{saving ? 'Saving…' : 'Add topic'}</button>
            </form>
          </section>

          <section className="card card-pad" style={{ marginTop: 20 }}>
            <div className="eyebrow">Step 3</div>
            <h2 style={{ marginTop: 6 }}>Add a lesson</h2>
            <FormField label="Choose topic">
              <select className="select" style={inputStyle} value={topicId} onChange={(event) => setTopicId(event.target.value)} required>
                <option value="" disabled>Select a topic</option>
                {topics.map((topic) => <option key={topic.id} value={topic.id}>{topic.title}</option>)}
              </select>
            </FormField>
            <form onSubmit={(event) => submitContent(event, '/lessons', { ...lessonForm, topic_id: topicId }, () => {
              setLessonForm({ title: '', content: '', order: 1, estimated_minutes: 15 });
            })}>
              <FormField label="Lesson title">
                <input className="input" style={inputStyle} value={lessonForm.title} onChange={(event) => setLessonForm({ ...lessonForm, title: event.target.value })} required />
              </FormField>
              <FormField label="Lesson content">
                <textarea className="input" style={{ ...inputStyle, minHeight: 180 }} value={lessonForm.content} onChange={(event) => setLessonForm({ ...lessonForm, content: event.target.value })} required />
              </FormField>
              <div className="grid-2">
                <FormField label="Lesson order">
                  <input className="input" style={inputStyle} type="number" min="1" value={lessonForm.order} onChange={(event) => setLessonForm({ ...lessonForm, order: Number(event.target.value) })} required />
                </FormField>
                <FormField label="Estimated minutes">
                  <input className="input" style={inputStyle} type="number" min="1" value={lessonForm.estimated_minutes} onChange={(event) => setLessonForm({ ...lessonForm, estimated_minutes: Number(event.target.value) })} required />
                </FormField>
              </div>
              <button className="btn btn-primary" style={{ marginTop: 16 }} disabled={saving || !topicId}>{saving ? 'Saving…' : 'Add lesson'}</button>
            </form>
          </section>

          <section className="card card-pad" style={{ marginTop: 20 }}>
            <div className="eyebrow">Step 4</div>
            <h2 style={{ marginTop: 6 }}>Add a multiple-choice quiz question</h2>
            <FormField label="Choose topic">
              <select className="select" style={inputStyle} value={topicId} onChange={(event) => setTopicId(event.target.value)} required>
                <option value="" disabled>Select a topic</option>
                {topics.map((topic) => <option key={topic.id} value={topic.id}>{topic.title}</option>)}
              </select>
            </FormField>
            <form onSubmit={(event) => submitContent(event, '/questions', {
              topic_id: topicId,
              question_text: questionForm.question_text,
              question_type: 'multiple_choice',
              difficulty: questionForm.difficulty,
              explanation: questionForm.explanation,
              points: Number(questionForm.points),
              correct_answer: questionForm.correct_answer,
              options: questionForm.options.map((option) => ({ ...option, order: Number(option.order) })),
            }, () => {
              setQuestionForm((current) => ({ ...current, question_text: '', explanation: '', options: current.options.map((option) => ({ ...option, text: '' })) }));
            })}>
              <FormField label="Question">
                <textarea className="input" style={{ ...inputStyle, minHeight: 80 }} value={questionForm.question_text} onChange={(event) => setQuestionForm({ ...questionForm, question_text: event.target.value })} required />
              </FormField>
              <div className="grid-2">
                <FormField label="Difficulty">
                  <select className="select" style={inputStyle} value={questionForm.difficulty} onChange={(event) => setQuestionForm({ ...questionForm, difficulty: event.target.value })}>
                    <option value="easy">Easy</option><option value="medium">Medium</option><option value="hard">Hard</option>
                  </select>
                </FormField>
                <FormField label="Points">
                  <input className="input" style={inputStyle} type="number" min="0" value={questionForm.points} onChange={(event) => setQuestionForm({ ...questionForm, points: Number(event.target.value) })} required />
                </FormField>
              </div>
              <div className="stack" style={{ gap: 10, marginTop: 16 }}>
                {questionForm.options.map((option, index) => (
                  <FormField key={option.option_key} label={`Option ${option.option_key.toUpperCase()}${questionForm.correct_answer === option.option_key ? ' (correct answer)' : ''}`}>
                    <div className="row">
                      <input type="radio" name="correct-answer" aria-label={`Mark option ${option.option_key} as correct`} checked={questionForm.correct_answer === option.option_key} onChange={() => setQuestionForm({ ...questionForm, correct_answer: option.option_key })} />
                      <input className="input" style={inputStyle} value={option.text} onChange={(event) => setQuestionForm({
                        ...questionForm,
                        options: questionForm.options.map((item, itemIndex) => itemIndex === index ? { ...item, text: event.target.value } : item),
                      })} required placeholder={`Answer option ${option.option_key.toUpperCase()}`} />
                    </div>
                  </FormField>
                ))}
              </div>
              <FormField label="Explanation shown after answering">
                <textarea className="input" style={{ ...inputStyle, minHeight: 80 }} value={questionForm.explanation} onChange={(event) => setQuestionForm({ ...questionForm, explanation: event.target.value })} required />
              </FormField>
              <button className="btn btn-primary" style={{ marginTop: 16 }} disabled={saving || !topicId}>{saving ? 'Saving…' : 'Add quiz question'}</button>
            </form>
          </section>
        </>
      )}
    </div>
  );
}
