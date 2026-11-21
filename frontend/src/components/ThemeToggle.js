import React, { useRef } from 'react';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../i18n/LanguageContext';
import './ThemeToggle.css';

const MODES = ['light', 'dark', 'system'];

const ThemeToggle = () => {
  const { selectedTheme, setTheme } = useTheme();
  const { t } = useLanguage();
  const groupRef = useRef(null);

  const getLabel = (mode) => {
    switch (mode) {
      case 'light':
        return t('header.themeLight');
      case 'dark':
        return t('header.themeDark');
      case 'system':
      default:
        return t('header.themeSystem');
    }
  };

  const handleKeyDown = (e, currentMode) => {
    const currentIndex = MODES.indexOf(currentMode);
    let nextIndex = currentIndex;

    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
      e.preventDefault();
      nextIndex = (currentIndex + 1) % MODES.length;
    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
      e.preventDefault();
      nextIndex = (currentIndex - 1 + MODES.length) % MODES.length;
    } else if (e.key === 'Home') {
      e.preventDefault();
      nextIndex = 0;
    } else if (e.key === 'End') {
      e.preventDefault();
      nextIndex = MODES.length - 1;
    }

    if (nextIndex !== currentIndex) {
      const nextMode = MODES[nextIndex];
      setTheme(nextMode);
      if (groupRef.current) {
        const buttons = groupRef.current.querySelectorAll('button[role="radio"]');
        if (buttons[nextIndex]) {
          buttons[nextIndex].focus();
        }
      }
    }
  };

  return (
    <div
      className="theme-segmented-pill"
      role="radiogroup"
      aria-label={t('header.themeModeLabel')}
      ref={groupRef}
      data-testid="theme-segmented-control"
    >
      {/* Light Option */}
      <button
        type="button"
        role="radio"
        className={`theme-segment-btn ${selectedTheme === 'light' ? 'is-active' : ''}`}
        aria-checked={selectedTheme === 'light'}
        tabIndex={selectedTheme === 'light' ? 0 : -1}
        onClick={() => setTheme('light')}
        onKeyDown={(e) => handleKeyDown(e, 'light')}
        aria-label={getLabel('light')}
        title={getLabel('light')}
        data-testid="theme-option-light"
      >
        <svg
          viewBox="0 0 24 24"
          width="17"
          height="17"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
          className="theme-svg-icon"
        >
          <circle cx="12" cy="12" r="4.5" />
          <line x1="12" y1="1.5" x2="12" y2="3.5" />
          <line x1="12" y1="20.5" x2="12" y2="22.5" />
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
          <line x1="1.5" y1="12" x2="3.5" y2="12" />
          <line x1="20.5" y1="12" x2="22.5" y2="12" />
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
        </svg>
      </button>

      {/* Dark Option */}
      <button
        type="button"
        role="radio"
        className={`theme-segment-btn ${selectedTheme === 'dark' ? 'is-active' : ''}`}
        aria-checked={selectedTheme === 'dark'}
        tabIndex={selectedTheme === 'dark' ? 0 : -1}
        onClick={() => setTheme('dark')}
        onKeyDown={(e) => handleKeyDown(e, 'dark')}
        aria-label={getLabel('dark')}
        title={getLabel('dark')}
        data-testid="theme-option-dark"
      >
        <svg
          viewBox="0 0 24 24"
          width="17"
          height="17"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
          className="theme-svg-icon"
        >
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
        </svg>
      </button>

      {/* System Option */}
      <button
        type="button"
        role="radio"
        className={`theme-segment-btn ${selectedTheme === 'system' ? 'is-active' : ''}`}
        aria-checked={selectedTheme === 'system'}
        tabIndex={selectedTheme === 'system' ? 0 : -1}
        onClick={() => setTheme('system')}
        onKeyDown={(e) => handleKeyDown(e, 'system')}
        aria-label={getLabel('system')}
        title={getLabel('system')}
        data-testid="theme-option-system"
      >
        <svg
          viewBox="0 0 24 24"
          width="17"
          height="17"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
          className="theme-svg-icon"
        >
          {/* Outer circle with left half filled, right half hollow */}
          <circle cx="12" cy="12" r="9" />
          <path d="M12 3a9 9 0 0 0 0 18z" fill="currentColor" />
        </svg>
      </button>
    </div>
  );
};

export default ThemeToggle;
