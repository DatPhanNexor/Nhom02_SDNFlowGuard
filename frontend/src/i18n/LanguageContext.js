import React, { createContext, useContext, useState, useCallback } from 'react';
import { vi } from './vi';
import { en } from './en';

const STORAGE_KEY = 'sdnflowguard_locale';
const DEFAULT_LANGUAGE = 'vi';

const translations = {
  vi,
  en,
};

const LanguageContext = createContext({
  language: DEFAULT_LANGUAGE,
  setLanguage: () => {},
  t: (key) => key,
});

export const LanguageProvider = ({ children }) => {
  const [language, setLanguageState] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved === 'vi' || saved === 'en') {
        return saved;
      }
    } catch (e) {
      // localStorage may fail in restricted sandbox
    }
    return DEFAULT_LANGUAGE;
  });

  const setLanguage = useCallback((newLang) => {
    if (newLang === 'vi' || newLang === 'en') {
      setLanguageState(newLang);
      try {
        localStorage.setItem(STORAGE_KEY, newLang);
      } catch (e) {
        // Ignore storage write errors
      }
    }
  }, []);

  const t = useCallback(
    (keyPath, params = {}) => {
      if (!keyPath || typeof keyPath !== 'string') return '';

      const keys = keyPath.split('.');
      let current = translations[language];

      // Navigate path in current language
      for (const k of keys) {
        if (current && typeof current === 'object' && k in current) {
          current = current[k];
        } else {
          current = undefined;
          break;
        }
      }

      // Fallback to English if missing
      if (current === undefined && language !== 'en') {
        let fallback = translations.en;
        for (const k of keys) {
          if (fallback && typeof fallback === 'object' && k in fallback) {
            fallback = fallback[k];
          } else {
            fallback = undefined;
            break;
          }
        }
        current = fallback;
      }

      // If still not found, return key path
      if (current === undefined || typeof current !== 'string') {
        return current !== undefined ? current : keyPath;
      }

      // Interpolate parameters if any
      let result = current;
      if (params && typeof params === 'object') {
        Object.entries(params).forEach(([paramKey, paramVal]) => {
          result = result.replace(new RegExp(`\\{${paramKey}\\}`, 'g'), String(paramVal));
        });
      }

      return result;
    },
    [language]
  );

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);

export default LanguageContext;
