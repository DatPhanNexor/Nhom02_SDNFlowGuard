import React from 'react';
import { useLanguage } from '../i18n/LanguageContext';
import './LanguageSwitcher.css';

const LanguageSwitcher = () => {
  const { language, setLanguage, t } = useLanguage();

  return (
    <div
      className="sdn-lang-switcher"
      role="group"
      aria-label="Language selection"
      title={t('header.languageTooltip')}
    >
      <button
        type="button"
        className={`sdn-lang-btn ${language === 'vi' ? 'active' : ''}`}
        onClick={() => setLanguage('vi')}
        aria-pressed={language === 'vi'}
        title="Tiếng Việt (Mặc định)"
      >
        VI
      </button>
      <span className="sdn-lang-divider">|</span>
      <button
        type="button"
        className={`sdn-lang-btn ${language === 'en' ? 'active' : ''}`}
        onClick={() => setLanguage('en')}
        aria-pressed={language === 'en'}
        title="English"
      >
        EN
      </button>
    </div>
  );
};

export default LanguageSwitcher;
