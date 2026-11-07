import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config/apiConfig';
import { useLanguage } from '../i18n/LanguageContext';
import LanguageSwitcher from './LanguageSwitcher';
import './Header.css';

const Header = () => {
  const { t } = useLanguage();
  const [defenseMode, setDefenseMode] = useState('DRY_RUN');
  const [backendOnline, setBackendOnline] = useState(false);

  useEffect(() => {
    let mounted = true;
    axios
      .get(`${API_BASE_URL}/api/health`, { timeout: 4000 })
      .then((res) => {
        if (mounted && res.data) {
          setDefenseMode(res.data.defense_mode || 'DRY_RUN');
          setBackendOnline(true);
        }
      })
      .catch(() => {
        if (mounted) {
          setBackendOnline(false);
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="header">
      <div className="header-brand">
        <img
          src={`${process.env.PUBLIC_URL}/sdnflowguard-logo.png`}
          alt="SDNFlowGuard logo"
          className="header-brand-logo"
        />
        <h1 className="header-brand-text">{t('header.title')}</h1>
      </div>
      <div className="user-info">
        <LanguageSwitcher />
        <span
          className="header-badge header-badge-defense"
          style={{
            backgroundColor: defenseMode === 'DRY_RUN' ? '#0d9488' : '#e11d48',
          }}
          title={
            defenseMode === 'DRY_RUN'
              ? t('status.dryRun')
              : t('status.liveEnforcement')
          }
        >
          {t('header.defenseMode')}: {defenseMode}
        </span>
        <span
          className="header-badge header-badge-api"
          style={{
            backgroundColor: backendOnline ? '#16a34a' : '#64748b',
          }}
          title={`Backend API: ${backendOnline ? 'ONLINE' : 'OFFLINE'}`}
        >
          {t('header.api')}: {backendOnline ? t('status.online') : t('status.offline')}
        </span>
      </div>
    </div>
  );
};

export default Header;
