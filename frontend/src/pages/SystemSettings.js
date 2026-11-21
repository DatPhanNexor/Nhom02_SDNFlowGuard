import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  API_BASE_URL,
  getApiHeaders,
  isValidIpAddress,
} from '../config/apiConfig';
import { useLanguage } from '../i18n/LanguageContext';
import './SystemSettings.css';

function SystemSettings() {
  const { language, t } = useLanguage();
  const [mode, setMode] = useState('balanced');
  const [sdnControllerIp, setSdnControllerIp] = useState('');
  const [elkIp, setElkIp] = useState('');
  const [honeypotIp, setHoneypotIp] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [healthSummary, setHealthSummary] = useState(null);
  const [copiedJson, setCopiedJson] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    axios
      .get(`${API_BASE_URL}/api/get-settings`)
      .then((response) => {
        const settings = response.data?.data || {};
        setMode(settings['Mode'] || 'balanced');
        setSdnControllerIp(settings['SDN Controller IP'] || '');
        setElkIp(settings['ELK IP Address'] || '');
        setHoneypotIp(settings['Honeypot IP Address'] || '');
      })
      .catch(() => {
        setStatusMessage(t('settings.fetchError'));
      });

    axios
      .get(`${API_BASE_URL}/api/health`)
      .then((response) => setHealthSummary(response.data?.config || null))
      .catch(() => setHealthSummary(null));
  }, [language, t]);

  const handleSaveSettings = () => {
    if (
      !isValidIpAddress(sdnControllerIp) ||
      !isValidIpAddress(elkIp) ||
      !isValidIpAddress(honeypotIp)
    ) {
      setStatusMessage(t('settings.validationError'));
      return;
    }

    setIsSaving(true);
    setStatusMessage('');

    const settings = {
      Mode: mode,
      'SDN Controller IP': sdnControllerIp.trim(),
      'ELK IP Address': elkIp.trim(),
      'Honeypot IP Address': honeypotIp.trim(),
    };

    axios
      .post(`${API_BASE_URL}/api/save-settings`, settings, {
        headers: getApiHeaders(),
      })
      .then((response) => {
        setStatusMessage(response.data.message || t('settings.saveSuccess'));
      })
      .catch((error) => {
        setStatusMessage(error.response?.data?.error || t('settings.saveFailed'));
      })
      .finally(() => {
        setIsSaving(false);
      });
  };

  const handleCopyJson = () => {
    if (!healthSummary) return;
    const jsonStr = JSON.stringify(healthSummary, null, 2);
    if (navigator?.clipboard?.writeText) {
      navigator.clipboard.writeText(jsonStr)
        .then(() => {
          setCopiedJson(true);
          setTimeout(() => setCopiedJson(false), 2500);
        })
        .catch(() => {
          setCopiedJson(false);
        });
    }
  };

  const modeDescriptions = {
    strict: t('settings.strict'),
    balanced: t('settings.balanced'),
    loose: t('settings.loose'),
  };

  return (
    <div className="system-settings">
      <div className="settings-container" data-testid="settings-container">
        {/* Page Header */}
        <div className="settings-header">
          <h2>{t('settings.title')}</h2>
          <p>{t('settings.subtitle')}</p>
        </div>

        {/* Runtime Precedence Notice */}
        <div className="settings-notice-card" role="note" aria-label="Runtime Precedence Notice">
          <span className="notice-icon" aria-hidden="true">ℹ️</span>
          <div>
            <strong>{t('settings.runtimeNoticeLabel')}</strong>{' '}
            {t('settings.runtimeNotice')}
          </div>
        </div>

        {/* Status Message Banner */}
        {statusMessage && (
          <div
            className={`settings-status-banner ${
              statusMessage.toLowerCase().includes('lỗi') ||
              statusMessage.toLowerCase().includes('error') ||
              statusMessage.toLowerCase().includes('thất bại') ||
              statusMessage.toLowerCase().includes('failed')
                ? 'error'
                : 'success'
            }`}
            role="alert"
          >
            {statusMessage}
          </div>
        )}

        {/* 1. Detection Mode */}
        <div className="settings-group">
          <h3>{t('settings.detectionMode')}</h3>
          <p className="card-description">{t('settings.detectionDescription')}</p>

          <div className="detection-mode-options" role="radiogroup" aria-label={t('settings.detectionMode')}>
            {[
              { id: 'strict', badge: 'High Sensitivity' },
              { id: 'balanced', badge: 'Recommended' },
              { id: 'loose', badge: 'Low Sensitivity' },
            ].map(({ id: option, badge }) => (
              <label
                key={option}
                htmlFor={`mode-${option}`}
                className={`mode-option-card ${mode === option ? 'selected' : ''}`}
              >
                <input
                  type="radio"
                  id={`mode-${option}`}
                  name="mode"
                  value={option}
                  checked={mode === option}
                  onChange={(e) => setMode(e.target.value)}
                />
                <div className="mode-label-wrap">
                  <span className="mode-title">
                    {option.charAt(0).toUpperCase() + option.slice(1)}
                  </span>
                  <span className="mode-badge">{badge}</span>
                </div>
              </label>
            ))}
          </div>

          <div className="mode-description-box">
            <strong>{t('settings.selectedModeDesc')}</strong> {modeDescriptions[mode]}
          </div>
        </div>

        {/* 2. Application Variables */}
        <div className="settings-group">
          <h3>{t('settings.appVariables')}</h3>
          <p className="card-description">
            {language === 'vi'
              ? 'Cấu hình địa chỉ IP các thành phần hạ tầng SDN, hệ thống SIEM và máy chủ Honeypot'
              : 'Configure network endpoints for SDN Controller, SIEM infrastructure, and Honeypot hosts'}
          </p>

          <div className="settings-form-grid">
            {[
              {
                label: t('settings.controllerIp'),
                id: 'sdn-ctrl-ip',
                value: sdnControllerIp,
                set: setSdnControllerIp,
                placeholder: '127.0.0.1',
                hint: 'ONOS REST API (Default port: 8181)',
              },
              {
                label: t('settings.siemIp'),
                id: 'siem-ip',
                value: elkIp,
                set: setElkIp,
                placeholder: '127.0.0.1',
                hint: 'Elasticsearch Cluster (Default port: 9200)',
              },
              {
                label: t('settings.honeypotIp'),
                id: 'honeypot-ip',
                value: honeypotIp,
                set: setHoneypotIp,
                placeholder: '10.0.0.6',
                hint: 'Internal Honeypot / Decoy host',
              },
            ].map(({ label, id, value, set, placeholder, hint }) => (
              <div className="form-field" key={id}>
                <label htmlFor={id}>{label}</label>
                <input
                  type="text"
                  id={id}
                  value={value}
                  onChange={(e) => set(e.target.value)}
                  placeholder={placeholder}
                />
                <span className="field-hint">{hint}</span>
              </div>
            ))}
          </div>

          <div className="settings-actions">
            <button
              type="button"
              className="btn-save-settings"
              onClick={handleSaveSettings}
              disabled={isSaving}
            >
              {isSaving ? t('settings.saving') : t('settings.btnSave')}
            </button>
          </div>
        </div>

        {/* 3. Effective Runtime Configuration & Safety Gate */}
        {healthSummary && (
          <div className="settings-group">
            <div className="runtime-header-row">
              <div>
                <h3>{t('settings.runtimeSummaryTitle')}</h3>
                <p className="card-description" style={{ marginBottom: 0 }}>
                  {t('settings.runtimeNoticeSub')}
                </p>
              </div>
              <button
                type="button"
                className="btn-copy-json"
                onClick={handleCopyJson}
                title="Copy active configuration JSON"
              >
                {copiedJson ? `✓ ${t('settings.copied')}` : `📋 ${t('settings.copyJson')}`}
              </button>
            </div>

            <pre className="settings-code-viewer" data-testid="runtime-config-viewer">
              {JSON.stringify(healthSummary, null, 2)}
            </pre>

            <div className="safety-gate-notice">
              <span className="safety-icon" aria-hidden="true">🛡️</span>
              <div>
                <strong>{t('settings.safetyGateTitle')}:</strong> {t('settings.safetyGateDesc')}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default SystemSettings;
