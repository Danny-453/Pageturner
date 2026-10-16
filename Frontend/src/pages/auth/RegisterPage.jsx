import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import Logo from '../../components/common/Logo';
import { useAuth } from '../../context/AuthContext';
import { ACADEMIC_LEVELS } from '../../config/app';
import { API_ENABLED, apiGet } from '../../services/api';

export default function RegisterPage() {
    const { register, loading } = useAuth();
    const nav = useNavigate();

    const [form, setForm] = useState({
        fullName: '',
        nickname: '',
        email: '',
        password: '',
        confirmPassword: '',
        studentId: '',
        academicLevel: API_ENABLED ? '' : '300 Level',
    });

    const [error, setError] = useState('');
    const [academicLevels, setAcademicLevels] = useState(
        API_ENABLED ? [] : ACADEMIC_LEVELS.map((name) => ({ id: name, name })),
    );

    useEffect(() => {
        if (!API_ENABLED) return;
        apiGet('/academic-levels')
            .then((levels) => {
                setAcademicLevels(levels);
                setForm((current) => ({
                    ...current,
                    academicLevel: levels.find((level) => level.name === '300 Level')?.id ?? levels[0]?.id ?? '',
                }));
            })
            .catch((err) => setError(err.message));
    }, []);

    const set = (key, value) => {
        setForm((formData) => ({
            ...formData,
            [key]: value,
        }));
    };

    async function submit(e) {
        e.preventDefault();
        setError('');

        if (form.password !== form.confirmPassword) {
            setError('Passwords do not match.');
            return;
        }

        try {
            const selectedLevel = academicLevels.find((level) => level.id === form.academicLevel);
            await register({
                ...form,
                academicLevel: selectedLevel?.name ?? form.academicLevel,
                academicLevelId: API_ENABLED ? form.academicLevel : undefined,
            });
            nav('/dashboard');
        } catch (err) {
            setError(err.message);
        }
    }

    return (
        <div className="auth-page">
            <div className="auth-brand">
                <Logo className="auth-brand-logo" />

                <div
                    className="eyebrow"
                    style={{ color: 'var(--color-secondary)' }}
                >
                    Join PageTurners
                </div>

                <h2
                    style={{
                        fontFamily: 'var(--font-serif)',
                        fontSize: 42,
                        marginTop: 12,
                    }}
                >
                    Build a learning habit that compounds.
                </h2>

                <p
                    style={{
                        color: 'rgba(255,255,255,.72)',
                        maxWidth: 520,
                    }}
                >
                    Create a student profile and explore a structured geology
                    learning environment.
                </p>
            </div>

            <div className="auth-form-wrap">
                <div className="card auth-card">
                    <div className="eyebrow">
                        Student registration
                    </div>

                    <h1>Create account</h1>

                    <p className="muted">
                        Create an account to save your learning progress.
                    </p>

                    {error && (
                        <div
                            className="notice"
                            style={{
                                color: 'var(--color-error)',
                                marginBottom: 16,
                            }}
                        >
                            {error}
                        </div>
                    )}

                    <form
                        onSubmit={submit}
                        className="form-grid"
                    >
                        <div className="form-field full">
                            <label htmlFor="fullName">
                                Full name
                            </label>

                            <input
                                className="input"
                                id="fullName"
                                value={form.fullName}
                                onChange={(e) =>
                                    set('fullName', e.target.value)
                                }
                                required
                            />
                        </div>

                        <div className="form-field">
                            <label htmlFor="nickname">
                                Nickname
                            </label>

                            <input
                                className="input"
                                id="nickname"
                                value={form.nickname}
                                onChange={(e) =>
                                    set('nickname', e.target.value)
                                }
                                minLength={2}
                                maxLength={40}
                                required
                            />

                            <span className="muted">This is the name shown on the leaderboard.</span>
                        </div>

                        <div className="form-field">
                            <label htmlFor="email">
                                Email
                            </label>

                            <input
                                className="input"
                                id="email"
                                type="email"
                                value={form.email}
                                onChange={(e) =>
                                    set('email', e.target.value)
                                }
                                required
                            />
                        </div>

                        <div className="form-field">
                            <label htmlFor="studentId">
                                Student ID
                            </label>

                            <input
                                className="input"
                                id="studentId"
                                value={form.studentId}
                                onChange={(e) =>
                                    set('studentId', e.target.value)
                                }
                                required
                            />
                        </div>

                        <div className="form-field">
                            <label htmlFor="password">
                                Password
                            </label>

                            <input
                                className="input"
                                id="password"
                                type="password"
                                value={form.password}
                                onChange={(e) =>
                                    set('password', e.target.value)
                                }
                                required
                            />
                        </div>

                        <div className="form-field">
                            <label htmlFor="confirmPassword">
                                Confirm password
                            </label>

                            <input
                                className="input"
                                id="confirmPassword"
                                type="password"
                                value={form.confirmPassword}
                                onChange={(e) =>
                                    set('confirmPassword', e.target.value)
                                }
                                required
                            />
                        </div>

                        <div className="form-field full">
                            <label htmlFor="academicLevel">
                                Academic level
                            </label>

                            <select
                                className="select"
                                id="academicLevel"
                                value={form.academicLevel}
                                onChange={(e) =>
                                    set('academicLevel', e.target.value)
                                }
                            >
                                {academicLevels.map((level) => (
                                    <option key={level.id} value={level.id}>
                                        {level.name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className="full">
                            <button
                                className="btn btn-primary"
                                style={{ width: '100%' }}
                                disabled={loading || !academicLevels.length}
                                aria-busy={loading}
                            >
                                {loading
                                    ? 'Creating…'
                                    : 'Create account'}
                            </button>
                        </div>
                    </form>

                    <p
                        className="muted"
                        style={{
                            textAlign: 'center',
                            marginTop: 20,
                            marginBottom: 0,
                        }}
                    >
                        Already registered?{' '}
                        <Link
                            to="/login"
                            style={{
                                color: 'var(--color-primary)',
                                fontWeight: 800,
                            }}
                        >
                            Sign in
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}