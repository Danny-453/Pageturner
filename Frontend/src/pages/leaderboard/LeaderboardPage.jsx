import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import Avatar from '../../components/common/Avatar';
import PageHeader from '../../components/common/PageHeader';
import { getCourses } from '../../services/courseService';
import { getLeaderboard } from '../../services/leaderboardService';
import { getCurrentProfile } from '../../services/profileService';

export default function LeaderboardPage() {
  const { courseId } = useParams();
  const [scope, setScope] = useState(courseId ? 'course' : 'department');
  const [selectedCourseId, setSelectedCourseId] = useState(courseId ?? '');
  const [courses, setCourses] = useState([]);
  const [rows, setRows] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [rank, setRank] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    getCourses()
      .then((items) => {
        if (!active) return;
        setCourses(items);
        setSelectedCourseId((selected) => selected || items[0]?.id || '');
      })
      .catch((err) => {
        if (active) setError(err.message);
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    const activeCourseId = courseId ?? selectedCourseId;
    if (scope === 'course' && !activeCourseId) return undefined;

    let active = true;
    setError('');
    Promise.all([
      getLeaderboard({ scope, courseId: scope === 'course' ? activeCourseId : undefined }),
      getCurrentProfile(),
    ])
      .then(([result, profile]) => {
        const entries = Array.isArray(result) ? result : result.entries;
        if (!active) return;
        setRows(entries);
        setRank(
          Array.isArray(result)
            ? entries.find((item) => item.id === profile.id)?.rank
            : result.current_user_rank,
        );
        setCurrentUser(profile);
      })
      .catch((err) => {
        if (active) setError(err.message);
      });
    return () => {
      active = false;
    };
  }, [scope, courseId, selectedCourseId]);

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Academic community"
        title="Leaderboard"
        description="A study-oriented view of points, progress and current standing."
        actions={
          <div className="row">
            <button className={scope === 'course' ? 'btn btn-primary' : 'btn btn-secondary'} onClick={() => setScope('course')}>Course</button>
            <button className={scope === 'level' ? 'btn btn-primary' : 'btn btn-secondary'} onClick={() => setScope('level')}>My level</button>
            <button className={scope === 'department' ? 'btn btn-primary' : 'btn btn-secondary'} onClick={() => setScope('department')}>Department</button>
          </div>
        }
      />
      {scope === 'course' && (
        <div style={{ marginBottom: 16 }}>
          <select
            className="select"
            value={courseId ?? selectedCourseId}
            onChange={(event) => setSelectedCourseId(event.target.value)}
            disabled={Boolean(courseId)}
          >
            {courses.map((course) => (
              <option key={course.id} value={course.id}>{course.code} · {course.title}</option>
            ))}
          </select>
        </div>
      )}
      {error && <div className="notice" style={{ color: 'var(--color-error)', marginBottom: 16 }}>{error}</div>}
      {currentUser && (
        <div className="card card-pad" style={{ marginBottom: 20 }}>
          <div className="row space-between">
            <div>
              <div className="eyebrow">Your standing</div>
              <h2 style={{ marginTop: 6 }}>
                {rank ? `#${rank} in ${scope}` : 'Not ranked yet'} · {currentUser.academicLevel}
              </h2>
            </div>
            <Link to="/profile" className="btn btn-secondary">View profile</Link>
          </div>
        </div>
      )}
      <div className="card table-wrap">
        <table>
          <thead>
            <tr><th>Rank</th><th>Student</th><th>Academic level</th><th>Questions</th><th>Accuracy</th><th>Points</th></tr>
          </thead>
          <tbody>
            {rows.map((student, index) => (
              <tr key={student.id} style={student.id === currentUser?.id ? { background: 'var(--color-primary-light)' } : {}}>
                <td><strong>#{student.rank ?? index + 1}</strong></td>
                <td><div className="row"><Avatar name={student.name} size={34}/><strong>{student.name}{student.id === currentUser?.id ? ' (You)' : ''}</strong></div></td>
                <td>{student.academicLevel}</td>
                <td>{student.answered}</td>
                <td>{student.accuracy}%</td>
                <td><strong>{student.points}</strong></td>
              </tr>
            ))}
          </tbody>
        </table>
        {!rows.length && !error && <div className="empty">Loading leaderboard…</div>}
        {!rows.length && error && <div className="empty">Leaderboard could not be loaded.</div>}
      </div>
    </div>
  );
}
