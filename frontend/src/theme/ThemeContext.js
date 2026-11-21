import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';

const STORAGE_KEY = 'sdnflowguard_theme';

const getSystemPreference = () => {
  if (typeof window !== 'undefined' && window.matchMedia) {
    try {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    } catch (err) {
      // media query not supported
    }
  }
  return 'light';
};

const getInitialSelectedTheme = () => {
  try {
    if (typeof window !== 'undefined' && window.localStorage) {
      const saved = window.localStorage.getItem(STORAGE_KEY);
      if (saved === 'light' || saved === 'dark' || saved === 'system') {
        return saved;
      }
    }
  } catch (err) {
    // localStorage restricted / sandboxed
  }
  return 'system';
};

const ThemeContext = createContext({
  selectedTheme: 'system',
  theme: 'light',
  resolvedTheme: 'light',
  setTheme: () => {},
  toggleTheme: () => {},
  isDark: false,
  isLight: true,
  isSystem: true,
});

export const ThemeProvider = ({ children }) => {
  const [selectedTheme, setSelectedThemeState] = useState(getInitialSelectedTheme);
  const [systemPreference, setSystemPreference] = useState(getSystemPreference);

  // Compute resolved theme: if 'system', follow systemPreference; otherwise use selectedTheme
  const resolvedTheme = useMemo(() => {
    if (selectedTheme === 'system') {
      return systemPreference;
    }
    return selectedTheme === 'dark' ? 'dark' : 'light';
  }, [selectedTheme, systemPreference]);

  const applyThemeToDom = useCallback((activeResolved, activeMode) => {
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-theme', activeResolved);
      document.documentElement.setAttribute('data-theme-mode', activeMode);
      if (document.body) {
        document.body.setAttribute('data-theme', activeResolved);
        document.body.setAttribute('data-theme-mode', activeMode);
      }
    }
  }, []);

  const setTheme = useCallback(
    (mode) => {
      const validMode = mode === 'dark' ? 'dark' : mode === 'light' ? 'light' : 'system';
      setSelectedThemeState(validMode);
      try {
        if (typeof window !== 'undefined' && window.localStorage) {
          window.localStorage.setItem(STORAGE_KEY, validMode);
        }
      } catch (err) {
        // storage quota or sandboxed
      }
    },
    []
  );

  const toggleTheme = useCallback(() => {
    setSelectedThemeState((prev) => {
      let nextMode = 'light';
      if (prev === 'light') nextMode = 'dark';
      else if (prev === 'dark') nextMode = 'system';
      else nextMode = 'light';
      try {
        if (typeof window !== 'undefined' && window.localStorage) {
          window.localStorage.setItem(STORAGE_KEY, nextMode);
        }
      } catch (err) {
        // ignore
      }
      return nextMode;
    });
  }, []);

  // Listen to OS preference changes
  useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return;
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleChange = (e) => {
      setSystemPreference(e.matches ? 'dark' : 'light');
    };

    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    } else if (mediaQuery.addListener) {
      mediaQuery.addListener(handleChange);
      return () => mediaQuery.removeListener(handleChange);
    }
  }, []);

  // Sync with DOM attribute on resolvedTheme or selectedTheme change
  useEffect(() => {
    applyThemeToDom(resolvedTheme, selectedTheme);
  }, [resolvedTheme, selectedTheme, applyThemeToDom]);

  const value = useMemo(
    () => ({
      selectedTheme,
      theme: resolvedTheme, // alias for backwards compatibility
      resolvedTheme,
      setTheme,
      toggleTheme,
      isDark: resolvedTheme === 'dark',
      isLight: resolvedTheme === 'light',
      isSystem: selectedTheme === 'system',
    }),
    [selectedTheme, resolvedTheme, setTheme, toggleTheme]
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

export const useTheme = () => useContext(ThemeContext);

export default ThemeContext;
