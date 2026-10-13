import { useState } from 'react';
import { Link } from 'react-router-dom';
import Logo from '../../components/common/Logo';
import { requestPasswordReset } from '../../services/authService';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  async function sendResetRequest() {
    setError('');
    setLoading(true);
    try {
      await requestPasswordReset(email);
      setSent(true);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  async function submit(event) {
    event.preventDefault();
    await sendResetRequest();
  }

  return (
    <div className="auth-page">
      <div className="auth-brand">
        <Logo className="auth-brand-logo" />
        <div className="eyebrow" style={{ color: 'var(--color-secondary)' }}>Account recovery</div>
        <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 42, marginTop: 12 }}>Get back to learning.</h2>
        <p style={{ color: 'rgba(255,255,255,.72)', maxWidth: 520 }}>
          We’ll send a secure, one-time password reset link to your account email.
        </p>
      </div>
      <div className="auth-form-wrap">
        <div className="card auth-card">
          <div className="row space-between">
            <div><div className="eyebrow">Forgot password</div><h1>Reset your password</h1></div>
            <Link to="/" className="muted" style={{ fontSize: 13 }}>Home</Link>
          </div>
          {sent ? (
            <>
              <div className="notice" role="status">
                If an account exists for that email, a reset link will be sent. Check your inbox and spam folder.
              </div>
              {error && <div className="notice" role="alert" style={{ color: 'var(--color-error)', marginTop: 16 }}>{error}</div>}
              <button
                className="btn btn-primary"
                type="button"
                style={{ width: '100%', marginTop: 16 }}
                disabled={loading}
                aria-busy={loading}
                onClick={sendResetRequest}
              >
                {loading ? 'Sending…' : 'Resend reset email'}
              </button>
            </>
          ) : (
            <>
              <p className="muted">Enter the email address associated with your account.</p>
              {error && <div className="notice" role="alert" style={{ color: 'var(--color-error)', marginBottom: 16 }}>{error}</div>}
              <form onSubmit={submit} className="stack" style={{ gap: 16 }}>
                <div className="form-field">
                  <label htmlFor="email">Email</label>
                  <input className="input" id="email" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
                </div>
                <button className="btn btn-primary" type="submit" disabled={loading} aria-busy={loading}>
                  {loading ? 'Sending…' : 'Send reset link'}
                </button>
              </form>
            </>
          )}
          <p className="muted" style={{ textAlign: 'center', marginTop: 22, marginBottom: 0 }}>
            Remember your password? <Link to="/login" style={{ color: 'var(--color-primary)', fontWeight: 800 }}>Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
