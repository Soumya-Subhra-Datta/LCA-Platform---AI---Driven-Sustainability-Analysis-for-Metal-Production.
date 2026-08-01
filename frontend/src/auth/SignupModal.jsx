import { useEffect, useRef, useState } from 'react';
import logo from '../assets/logo.png';
import authService from './authService.js';
import { validateSignup } from './validators.js';

function ModalPasswordField({ id, label, value, onChange, error, autoComplete }) {
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
          aria-label={visible ? `Hide ${label.toLowerCase()}` : `Show ${label.toLowerCase()}`}
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

export default function SignupModal({ onClose, onSignIn, onSuccess }) {
  const [form, setForm] = useState({ name: '', email: '', password: '', confirmPassword: '' });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [serverError, setServerError] = useState('');
  const modalRef = useRef(null);
  const closeButtonRef = useRef(null);

  useEffect(() => {
    const previouslyFocused = document.activeElement;
    closeButtonRef.current?.focus();

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };

    document.addEventListener('keydown', handleKeyDown);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
      if (previouslyFocused && typeof previouslyFocused.focus === 'function') {
        previouslyFocused.focus();
      }
    };
  }, [onClose]);

  const setField = (key) => (value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    setErrors((prev) => ({ ...prev, [key]: undefined }));
    setServerError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setServerError('');

    const validationErrors = validateSignup(form);
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length > 0) return;

    setIsSubmitting(true);
    try {
      await authService.signup({
        name: form.name,
        email: form.email,
        password: form.password,
      });
      if (onSuccess) {
        onSuccess();
      } else {
        onClose();
      }
    } catch (err) {
      setServerError(err.message || 'Unable to create your account. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose} role="presentation">
      <div
        className="signup-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="signup-title"
        ref={modalRef}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          ref={closeButtonRef}
          type="button"
          className="modal-close"
          aria-label="Close sign up dialog"
          onClick={onClose}
        >
          &times;
        </button>

        <div className="signup-modal-header">
          <img src={logo} alt="LCA Platform logo" className="signup-logo" />
          <h2 id="signup-title" className="signup-heading">
            Create Account
          </h2>
          <p className="signup-subtitle">Create your account to get started.</p>
        </div>

        <div className="signup-modal-body">
          {serverError && (
            <div className="alert alert-error" role="alert">
              {serverError}
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate>
            <div className="form-field">
              <label htmlFor="signup-name">Name</label>
              <input
                id="signup-name"
                type="text"
                value={form.name}
                autoComplete="name"
                placeholder="Your full name"
                aria-invalid={Boolean(errors.name)}
                aria-describedby={errors.name ? 'signup-name-error' : undefined}
                onChange={(e) => setField('name')(e.target.value)}
              />
              {errors.name && (
                <span id="signup-name-error" className="field-error" role="alert">
                  {errors.name}
                </span>
              )}
            </div>

            <div className="form-field">
              <label htmlFor="signup-email">Email</label>
              <input
                id="signup-email"
                type="email"
                value={form.email}
                autoComplete="email"
                placeholder="you@example.com"
                aria-invalid={Boolean(errors.email)}
                aria-describedby={errors.email ? 'signup-email-error' : undefined}
                onChange={(e) => setField('email')(e.target.value)}
              />
              {errors.email && (
                <span id="signup-email-error" className="field-error" role="alert">
                  {errors.email}
                </span>
              )}
            </div>

            <ModalPasswordField
              id="signup-password"
              label="Password"
              value={form.password}
              onChange={setField('password')}
              error={errors.password}
              autoComplete="new-password"
            />

            <ModalPasswordField
              id="signup-confirm-password"
              label="Confirm Password"
              value={form.confirmPassword}
              onChange={setField('confirmPassword')}
              error={errors.confirmPassword}
              autoComplete="new-password"
            />

            <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
              {isSubmitting ? 'Creating Account...' : 'Sign Up'}
            </button>
          </form>

          <p className="auth-switch">
            Already have an account?{' '}
            <button type="button" className="link-button" onClick={onSignIn}>
              Sign In
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
