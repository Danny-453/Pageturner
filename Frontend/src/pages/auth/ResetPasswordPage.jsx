import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import Logo from '../../components/common/Logo';
import { confirmPasswordReset } from '../../services/authService';

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') ?? '';
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [complete, setComplete] = useState(false);
  const [loading, setLoading] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setError('');
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setLoading(true);
    try {
      await confirmPasswordReset(token, password);
      setComplete(true);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-brand">
        <Logo className="auth-brand-logo" />
        <div className="eyebrow" style={{ color: 'var(--color-secondary)' }}>Account recovery</div>
        <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 42, marginTop: 12 }}>Choose a new password.</h2>
        <p style={{ color: 'rgba(255,255,255,.72)', maxWidth: 520 }}>Use at least 8 characters to protect your account.</p>
      </div>
      <div className="auth-form-wrap">
        <div className="card auth-card">
          <div className="eyebrow">New password</div>
          <h1>Set a new password</h1>
          {complete ? (
            <div className="notice" role="status">
              Your password has been reset. <Link to="/login">Sign in</Link> with your new password.
            </div>
          ) : !token ? (
            <div className="notice" role="alert" style={{ color: 'var(--color-error)' }}>
              This reset link is missing its token. Request a new link from <Link to="/forgot-password">Forgot password</Link>.
            </div>
          ) : (
            <>
              {error && <div className="notice" role="alert" style={{ color: 'var(--color-error)', marginBottom: 16 }}>{error}</div>}
              <form onSubmit={submit} className="stack" style={{ gap: 16 }}>
                <div className="form-field">
                  <label htmlFor="password">New password</label>
                  <input className="input" id="password" type="password" autoComplete="new-password" minLength={8} maxLength={128} value={password} onChange={(event) => setPassword(event.target.value)} required />
                </div>
                <div className="form-field">
                  <label htmlFor="confirm-password">Confirm new password</label>
                  <input className="input" id="confirm-password" type="password" autoComplete="new-password" minLength={8} maxLength={128} value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} required />
                </div>
                <button className="btn btn-primary" type="submit" disabled={loading} aria-busy={loading}>
                  {loading ? 'Updating…' : 'Change password'}
                </button>
              </form>
            </>
          )}
          <p className="muted" style={{ textAlign: 'center', marginTop: 22, marginBottom: 0 }}>
            <Link to="/login" style={{ color: 'var(--color-primary)', fontWeight: 800 }}>Back to sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
