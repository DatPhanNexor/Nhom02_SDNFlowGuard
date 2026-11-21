import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, useTheme } from '../theme/ThemeContext';
import { LanguageProvider } from '../i18n/LanguageContext';
import ThemeToggle from '../components/ThemeToggle';

// Test consumer component
const TestConsumer = () => {
  const { selectedTheme, theme, resolvedTheme, setTheme, isDark, isLight, isSystem } = useTheme();
  return (
    <div>
      <span data-testid="selected-theme">{selectedTheme}</span>
      <span data-testid="resolved-theme">{resolvedTheme}</span>
      <span data-testid="theme-alias">{theme}</span>
      <span data-testid="is-dark">{isDark ? 'yes' : 'no'}</span>
      <span data-testid="is-light">{isLight ? 'yes' : 'no'}</span>
      <span data-testid="is-system">{isSystem ? 'yes' : 'no'}</span>
      <button onClick={() => setTheme('light')} data-testid="btn-light">Set Light</button>
      <button onClick={() => setTheme('dark')} data-testid="btn-dark">Set Dark</button>
      <button onClick={() => setTheme('system')} data-testid="btn-system">Set System</button>
    </div>
  );
};

describe('SDNFlowGuard 3-Mode Theme Management System (V7)', () => {
  beforeEach(() => {
    window.localStorage.clear();
    document.documentElement.removeAttribute('data-theme');
    document.documentElement.removeAttribute('data-theme-mode');
    if (document.body) {
      document.body.removeAttribute('data-theme');
      document.body.removeAttribute('data-theme-mode');
    }
  });

  afterEach(() => {
    window.localStorage.clear();
  });

  test('defaults to system theme when localStorage is empty and sets DOM attribute', () => {
    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>
    );

    expect(screen.getByTestId('selected-theme').textContent).toBe('system');
    expect(screen.getByTestId('is-system').textContent).toBe('yes');
    expect(document.documentElement.getAttribute('data-theme-mode')).toBe('system');
    expect(['light', 'dark']).toContain(document.documentElement.getAttribute('data-theme'));
  });

  test('restores dark theme from localStorage on initial render', () => {
    window.localStorage.setItem('sdnflowguard_theme', 'dark');

    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>
    );

    expect(screen.getByTestId('selected-theme').textContent).toBe('dark');
    expect(screen.getByTestId('is-dark').textContent).toBe('yes');
    expect(screen.getByTestId('is-light').textContent).toBe('no');
    expect(screen.getByTestId('is-system').textContent).toBe('no');
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    expect(document.documentElement.getAttribute('data-theme-mode')).toBe('dark');
  });

  test('restores light theme from localStorage on initial render', () => {
    window.localStorage.setItem('sdnflowguard_theme', 'light');

    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>
    );

    expect(screen.getByTestId('selected-theme').textContent).toBe('light');
    expect(screen.getByTestId('is-dark').textContent).toBe('no');
    expect(screen.getByTestId('is-light').textContent).toBe('yes');
    expect(screen.getByTestId('is-system').textContent).toBe('no');
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    expect(document.documentElement.getAttribute('data-theme-mode')).toBe('light');
  });

  test('setTheme switches between light, dark, and system updating localStorage and DOM', () => {
    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>
    );

    // Switch to Dark
    fireEvent.click(screen.getByTestId('btn-dark'));
    expect(screen.getByTestId('selected-theme').textContent).toBe('dark');
    expect(screen.getByTestId('is-dark').textContent).toBe('yes');
    expect(window.localStorage.getItem('sdnflowguard_theme')).toBe('dark');
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');

    // Switch to Light
    fireEvent.click(screen.getByTestId('btn-light'));
    expect(screen.getByTestId('selected-theme').textContent).toBe('light');
    expect(screen.getByTestId('is-light').textContent).toBe('yes');
    expect(window.localStorage.getItem('sdnflowguard_theme')).toBe('light');
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');

    // Switch to System
    fireEvent.click(screen.getByTestId('btn-system'));
    expect(screen.getByTestId('selected-theme').textContent).toBe('system');
    expect(screen.getByTestId('is-system').textContent).toBe('yes');
    expect(window.localStorage.getItem('sdnflowguard_theme')).toBe('system');
    expect(document.documentElement.getAttribute('data-theme-mode')).toBe('system');
  });

  test('ThemeToggle segmented pill renders 3 modes with correct accessibility roles and attributes', () => {
    render(
      <ThemeProvider>
        <LanguageProvider>
          <ThemeToggle />
        </LanguageProvider>
      </ThemeProvider>
    );

    const radiogroup = screen.getByRole('radiogroup');
    expect(radiogroup).toBeInTheDocument();
    expect(radiogroup).toHaveAttribute('aria-label');

    const lightOption = screen.getByTestId('theme-option-light');
    const darkOption = screen.getByTestId('theme-option-dark');
    const systemOption = screen.getByTestId('theme-option-system');

    expect(lightOption).toHaveAttribute('role', 'radio');
    expect(darkOption).toHaveAttribute('role', 'radio');
    expect(systemOption).toHaveAttribute('role', 'radio');

    // System is default
    expect(systemOption).toHaveAttribute('aria-checked', 'true');
    expect(systemOption).toHaveAttribute('tabIndex', '0');
    expect(lightOption).toHaveAttribute('aria-checked', 'false');
    expect(lightOption).toHaveAttribute('tabIndex', '-1');

    // Click light option
    fireEvent.click(lightOption);
    expect(lightOption).toHaveAttribute('aria-checked', 'true');
    expect(lightOption).toHaveAttribute('tabIndex', '0');
    expect(systemOption).toHaveAttribute('aria-checked', 'false');
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');

    // Click dark option
    fireEvent.click(darkOption);
    expect(darkOption).toHaveAttribute('aria-checked', 'true');
    expect(darkOption).toHaveAttribute('tabIndex', '0');
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });

  test('ThemeToggle supports keyboard navigation (ArrowRight, ArrowLeft, Home, End)', () => {
    render(
      <ThemeProvider>
        <LanguageProvider>
          <ThemeToggle />
        </LanguageProvider>
      </ThemeProvider>
    );

    const lightOption = screen.getByTestId('theme-option-light');
    const darkOption = screen.getByTestId('theme-option-dark');
    const systemOption = screen.getByTestId('theme-option-system');

    // Set to light first
    fireEvent.click(lightOption);
    expect(lightOption).toHaveAttribute('aria-checked', 'true');

    // ArrowRight from light -> dark
    fireEvent.keyDown(lightOption, { key: 'ArrowRight' });
    expect(darkOption).toHaveAttribute('aria-checked', 'true');

    // ArrowRight from dark -> system
    fireEvent.keyDown(darkOption, { key: 'ArrowRight' });
    expect(systemOption).toHaveAttribute('aria-checked', 'true');

    // ArrowLeft from system -> dark
    fireEvent.keyDown(systemOption, { key: 'ArrowLeft' });
    expect(darkOption).toHaveAttribute('aria-checked', 'true');

    // Home -> light
    fireEvent.keyDown(darkOption, { key: 'Home' });
    expect(lightOption).toHaveAttribute('aria-checked', 'true');

    // End -> system
    fireEvent.keyDown(lightOption, { key: 'End' });
    expect(systemOption).toHaveAttribute('aria-checked', 'true');
  });
});
