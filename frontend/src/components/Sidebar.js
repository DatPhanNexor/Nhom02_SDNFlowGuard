import React from 'react';
import { NavLink } from 'react-router-dom';
import { useLanguage } from '../i18n/LanguageContext';
import './Sidebar.css';

const navClass = ({ isActive }) => (isActive ? 'nav-link active' : 'nav-link');

const Sidebar = () => {
  const { t } = useLanguage();

  return (
    <div className="sidebar">
      <div className="sidebar-title">
        <img
          src={`${process.env.PUBLIC_URL}/sdnflowguard-logo.png`}
          alt="SDNFlowGuard logo"
          className="sidebar-brand-logo"
        />
        <span className="sidebar-brand-text">SDNFlowGuard</span>
      </div>
      <ul className="sidebar-menu">
        <li>
          <NavLink to="/" end className={navClass}>
            {t('nav.dashboard')}
          </NavLink>
        </li>
        <li>
          <NavLink to="/traffic-overview" className={navClass}>
            {t('nav.trafficOverview')}
          </NavLink>
        </li>
        <li>
          <NavLink to="/anomaly-detection" className={navClass}>
            {t('nav.anomalyDetection')}
          </NavLink>
        </li>
        <li>
          <NavLink to="/manual-traffic-control" className={navClass}>
            {t('nav.manualTrafficControl')}
          </NavLink>
        </li>
        <li>
          <NavLink to="/decision-logs" className={navClass}>
            {t('nav.decisionLogs')}
          </NavLink>
        </li>
        <li>
          <NavLink to="/reports" className={navClass}>
            {t('nav.reports')}
          </NavLink>
        </li>
        <li>
          <NavLink to="/system-settings" className={navClass}>
            {t('nav.systemSettings')}
          </NavLink>
        </li>
      </ul>
    </div>
  );
};

export default Sidebar;
