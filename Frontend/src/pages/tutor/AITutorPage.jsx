import { useEffect, useRef, useState } from 'react';
import PageHeader from '../../components/common/PageHeader';
import MarkdownContent from '../../components/common/MarkdownContent';
import { API_ENABLED, apiPost } from '../../services/api';
import { getCourses } from '../../services/courseService';

const starterPrompts = [
  'Explain the main ideas in this course.',
  'Can you give me a simple geology example?',
  'What should I review before a quiz?',
];

export default function AITutorPage() {
  const [courses, setCourses] = useState([]);
  const [courseId, setCourseId] = useState('');
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState('');
  const [loadingCourses, setLoadingCourses] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const conversationEnd = useRef(null);

  useEffect(() => {
    let active = true;
    getCourses()
      .then((items) => {
        if (!active) return;
        setCourses(items);
        setCourseId((current) => current || items[0]?.id || '');
      })
      .catch((loadError) => {
        if (active) setError(loadError.message);
      })
      .finally(() => {
        if (active) setLoadingCourses(false);
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    conversationEnd.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, sending]);

  function chooseCourse(id) {
    if (id === courseId) return;
    setCourseId(id);
    setMessages([]);
    setError('');
  }

  async function sendQuestion(event) {
    event.preventDefault();
    const content = question.trim();
    if (!content || !courseId || sending) return;

    setError('');
    setSending(true);
    try {
      const recentMessages = [...messages, { role: 'user', content }].slice(-12);
      const result = await apiPost('/ai/tutor', {
        course_id: courseId,
        messages: recentMessages,
      });
      setMessages((current) => [
        ...current,
        { role: 'user', content },
        { role: 'assistant', content: result.answer },
      ]);
      setQuestion('');
    } catch (sendError) {
      setError(sendError.message);
    } finally {
      setSending(false);
    }
  }

  const selectedCourse = courses.find((course) => course.id === courseId);
  const disabled = !API_ENABLED || loadingCourses || !courseId || sending;

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Personal study support"
        title="AI study tutor"
        description="Ask questions about your course and get clear explanations grounded in its lesson notes."
      />

      {!API_ENABLED && (
        <div className="notice" role="alert" style={{ color: 'var(--color-error)', marginBottom: 16 }}>
          Connect the frontend to the backend to use the AI tutor.
        </div>
      )}
      {error && (
        <div className="notice" role="alert" style={{ color: 'var(--color-error)', marginBottom: 16 }}>
          {error}
        </div>
      )}

      <section className="card card-pad" aria-label="AI study tutor">
        <div className="grid-2" style={{ alignItems: 'end' }}>
          <div className="form-field">
            <label htmlFor="tutor-course">Course context</label>
            <select
              id="tutor-course"
              className="select"
              value={courseId}
              onChange={(event) => chooseCourse(event.target.value)}
              disabled={loadingCourses || sending || !courses.length}
            >
              <option value="" disabled>
                {loadingCourses ? 'Loading courses…' : 'Select a course'}
              </option>
              {courses.map((course) => (
                <option key={course.id} value={course.id}>{course.code} · {course.title}</option>
              ))}
            </select>
          </div>
          {messages.length > 0 && (
            <button
              type="button"
              className="btn btn-secondary"
              style={{ justifySelf: 'end' }}
              disabled={sending}
              onClick={() => { setMessages([]); setError(''); }}
            >
              Clear conversation
            </button>
          )}
        </div>

        <div
          aria-live="polite"
          aria-label="Tutor conversation"
          style={{
            display: 'grid',
            gap: 14,
            minHeight: 240,
            maxHeight: 'min(55vh, 560px)',
            overflowY: 'auto',
            padding: '20px 2px',
            marginTop: 12,
            borderTop: '1px solid var(--color-border)',
            borderBottom: '1px solid var(--color-border)',
          }}
        >
          {messages.length === 0 ? (
            <div style={{ alignSelf: 'center', maxWidth: 640 }}>
              <h2>Hello{selectedCourse ? `! Let’s study ${selectedCourse.title}.` : ', ready to study?'}</h2>
              <p className="muted">I can explain course concepts, give examples, and help you review. Choose a prompt or ask your own question.</p>
              <div className="row" style={{ flexWrap: 'wrap' }}>
                {starterPrompts.map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    className="btn btn-secondary"
                    disabled={!courseId || sending}
                    onClick={() => setQuestion(prompt)}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          ) : messages.map((message, index) => (
            <article
              key={`${index}-${message.role}`}
              className="notice"
              style={{
                justifySelf: message.role === 'user' ? 'end' : 'start',
                width: 'min(90%, 720px)',
                background: message.role === 'user' ? 'var(--color-primary-light)' : 'var(--color-background)',
              }}
            >
              <strong>{message.role === 'user' ? 'You' : 'AI Tutor'}</strong>
              {message.role === 'assistant' ? (
                <MarkdownContent className="tutor-answer">{message.content}</MarkdownContent>
              ) : (
                <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.7, marginTop: 8 }}>{message.content}</div>
              )}
            </article>
          ))}
          {sending && <div className="muted" role="status">Your tutor is thinking…</div>}
          <div ref={conversationEnd} />
        </div>

        <form onSubmit={sendQuestion} style={{ marginTop: 16 }}>
          <label className="form-field" htmlFor="tutor-question">
            <span className="eyebrow">Your question</span>
            <textarea
              id="tutor-question"
              className="textarea"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask about a concept from your course…"
              maxLength={2000}
              required
              disabled={disabled}
            />
          </label>
          <div className="row space-between" style={{ marginTop: 12, flexWrap: 'wrap' }}>
            <small className="muted">The tutor can make mistakes. Check important details against your lesson notes.</small>
            <button className="btn btn-primary" type="submit" disabled={disabled || !question.trim()} aria-busy={sending}>
              {sending ? 'Thinking…' : 'Ask tutor'}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
