import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import logo from '../assets/logo.png';
import heroImage from '../assets/log.jpg';
import authService from './authService.js';
import { validateLogin } from './validators.js';
import SignupModal from './SignupModal.jsx';

const PROJECT_TITLE = 'AI-Powered Life Cycle Assessment (LCA) Platform';

function PasswordField({ id, label, value, onChange, error, autoComplete }) {
  const [visible, setVisible] = useState(false);
  return (
    <div className="form-field">
      <label htmlFor={id}>{label}</label>
      <div className="password-wrapper">
        <input
          id={id}
          type={visible ? 'text' : 'password'}
          value={value}
          autoComplete={autoComplete}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? `${id}-error` : undefined}
          onChange={(e) => onChange(e.target.value)}
        />
        <button
          type="button"
          className="password-toggle"
          aria-label={visible ? 'Hide password' : 'Show password'}
          onClick={() => setVisible((v) => !v)}
        >
          {visible ? 'Hide' : 'Show'}
        </button>
      </div>
      {error && (
        <span id={`${id}-error`} className="field-error" role="alert">
          {error}
        </span>
      )}
    </div>
  );
}

export default function LoginPage({ onAuthenticated }) {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});
  const [showSignup, setShowSignup] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [serverError, setServerError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setServerError('');
    setSuccessMessage('');

    const validationErrors = validateLogin({ email, password });
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length > 0) return;

    setIsSubmitting(true);
    try {
      await authService.login({ email, password });
      setSuccessMessage('Signed in successfully.');
      onAuthenticated();
      navigate('/', { replace: true });
    } catch (err) {
      setServerError(err.message || 'Unable to sign in. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-hero" aria-hidden="true">
          <img src={heroImage} alt="" />
        </div>
        <div className="auth-panel">
          <div className="auth-brand">
            <img src={logo} alt="LCA Platform logo" className="auth-logo" />
            <h1 className="auth-title">{PROJECT_TITLE}</h1>
          </div>

          <div className="auth-body">
            <h2 className="auth-heading">Sign In</h2>
            <p className="auth-subtitle">The key to happiness is to sign in.</p>

            {serverError && (
              <div className="alert alert-error" role="alert">
                {serverError}
              </div>
            )}
            {successMessage && (
              <div className="alert alert-success" role="status">
                {successMessage}
              </div>
            )}

            <form onSubmit={handleSubmit} noValidate>
              <div className="form-field">
                <label htmlFor="login-email">Email</label>
                <input
                  id="login-email"
                  type="email"
                  value={email}
                  autoComplete="email"
                  placeholder="you@example.com"
                  aria-invalid={Boolean(errors.email)}
                  aria-describedby={errors.email ? 'login-email-error' : undefined}
                  onChange={(e) => setEmail(e.target.value)}
                />
                {errors.email && (
                  <span id="login-email-error" className="field-error" role="alert">
                    {errors.email}
                  </span>
                )}
              </div>

              <PasswordField
                id="login-password"
                label="Password"
                value={password}
                onChange={setPassword}
                error={errors.password}
                autoComplete="current-password"
              />

              <div className="auth-row">
                <button
                  type="button"
                  className="link-button"
                  onClick={() => setSuccessMessage('Password reset is not available yet.')}
                >
                  Forgot Password?
                </button>
              </div>

              <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                {isSubmitting ? 'Signing In...' : 'Sign In'}
              </button>
            </form>

            <p className="auth-switch">
              Don&apos;t have an account?{' '}
              <button type="button" className="link-button" onClick={() => setShowSignup(true)}>
                Sign Up
              </button>
            </p>
          </div>
        </div>
      </div>

      {showSignup && (
        <SignupModal
          onClose={() => setShowSignup(false)}
          onSignIn={() => setShowSignup(false)}
          onSuccess={() => {
            setShowSignup(false);
            setSuccessMessage('Account created successfully. Please sign in.');
          }}
        />
      )}
    </div>
  );
}
