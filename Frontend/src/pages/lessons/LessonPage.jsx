import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import Icon from '../../components/common/Icon';
import MarkdownContent from '../../components/common/MarkdownContent';
import PageHeader from '../../components/common/PageHeader';
import LessonVideo from '../../components/lessons/LessonVideo';
import { getLessonById, getLessons } from '../../services/lessonService';
import { markLessonComplete } from '../../services/progressService';

export default function LessonPage() {
  const { courseId, lessonId } = useParams();
  const [lesson, setLesson] = useState(null);
  const [related, setRelated] = useState([]);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let active = true;
    Promise.all([getLessonById(lessonId, courseId), getLessons(courseId)])
      .then(([item, items]) => {
        if (active) {
          setLesson(item);
          setRelated(items);
        }
      })
      .catch((loadError) => {
        if (active) setError(loadError.message);
      });
    return () => {
      active = false;
    };
  }, [courseId, lessonId]);

  async function completeLesson() {
    setSaving(true);
    setError('');
    try {
      await markLessonComplete(courseId, lessonId);
      setLesson((current) => ({ ...current, completed: true }));
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSaving(false);
    }
  }

  if (error && !lesson) {
    return <div className="page-container"><div className="notice" style={{ color: 'var(--color-error)' }}>{error}</div></div>;
  }
  if (!lesson) {
    return <div className="page-container"><div className="card empty">Loading lesson…</div></div>;
  }

  return (
    <div className="page-container">
      <PageHeader
        eyebrow={`${lesson.topic} · ${lesson.duration}`}
        title={lesson.title}
        description="Read the lesson notes, watch the video if one is available, capture the key concepts and continue when you are ready."
        actions={<Link to={`/courses/${courseId}`} className="btn btn-secondary">Back to course</Link>}
      />
      {error && <div className="notice" style={{ color: 'var(--color-error)', marginBottom: 16 }}>{error}</div>}
      <div className="grid-2">
        <article className="card card-pad" style={{ maxWidth: 860 }}>
          <div className="notice notice-info">
            <strong>Study note</strong>
            <div className="muted" style={{ marginTop: 4 }}>
              Focus on the physical property being measured, field procedure and interpretation before moving to practice.
            </div>
          </div>
          <LessonVideo url={lesson.video_url} title={lesson.title} />
          <div style={{ marginTop: 28, fontSize: 17, lineHeight: 1.85 }}>
            <h2>Lesson notes</h2>
            <MarkdownContent>{lesson.content}</MarkdownContent>
          </div>
          <div className="row space-between" style={{ borderTop: '1px solid var(--color-border)', paddingTop: 20, marginTop: 30 }}>
            <span className="muted">Lesson {lesson.order} of {related.length}</span>
            <div className="row">
              {!lesson.completed && (
                <button className="btn btn-secondary" onClick={completeLesson} disabled={saving} aria-busy={saving}>
                  {saving ? 'Saving…' : 'Mark complete'}
                </button>
              )}
              <Link to="/practice" className="btn btn-primary">Practice this topic <Icon name="target" /></Link>
            </div>
          </div>
        </article>
        <aside className="card card-pad" style={{ alignSelf: 'start' }}>
          <div className="eyebrow">Course lessons</div>
          <div className="stack" style={{ gap: 0, marginTop: 12 }}>
            {related.map((item) => (
              <Link
                key={item.id}
                to={`/courses/${courseId}/lessons/${item.id}`}
                className="row"
                style={{
                  padding: '12px 0',
                  borderBottom: '1px solid var(--color-border)',
                  color: item.id === lesson.id ? 'var(--color-primary)' : 'inherit',
                }}
              >
                <span style={{ flex: 1, fontWeight: item.id === lesson.id ? 800 : 600 }}>{item.title}</span>
                {item.completed && <span className="badge badge-success">Complete</span>}
                <Icon name="chevron" size={15} />
              </Link>
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
}
