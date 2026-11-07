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
        setStatusMessage(
          language === 'vi'
            ? 'Không thể tải cấu hình từ backend.'
            : 'Unable to fetch settings from backend.'
        );
      });

    axios
      .get(`${API_BASE_URL}/api/health`)
      .then((response) => setHealthSummary(response.data?.config || null))
      .catch(() => setHealthSummary(null));
  }, [language]);

  const handleSaveSettings = () => {
    if (
      !isValidIpAddress(sdnControllerIp) ||
      !isValidIpAddress(elkIp) ||
      !isValidIpAddress(honeypotIp)
    ) {
      setStatusMessage(
        language === 'vi'
          ? 'Lỗi xác thực: Địa chỉ IP Controller, SIEM và Honeypot phải là địa chỉ IP hợp lệ.'
          : 'Validation Error: SDN Controller IP, SIEM IP Address, and Honeypot IP Address must be valid IP addresses.'
      );
      return;
    }

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
        setStatusMessage(
          response.data.message || (language === 'vi' ? 'Đã lưu cấu hình thành công' : 'Settings saved successfully')
        );
      })
      .catch((error) => {
        setStatusMessage(
          error.response?.data?.error || (language === 'vi' ? 'Lưu cấu hình thất bại' : 'Failed to save settings')
        );
      });
  };

  const modeDescriptions = {
    strict: t('settings.strict'),
    balanced: t('settings.balanced'),
    loose: t('settings.loose'),
  };

  return (
    <div className="system-settings">
      <div style={{ marginBottom: 20 }}>
        <h2 style={{ margin: 0, color: '#0f172a', fontSize: '1.6rem', fontWeight: 700 }}>
          {t('settings.title')}
        </h2>
        <p style={{ margin: '4px 0 0 0', color: '#64748b', fontSize: 14 }}>
          {language === 'vi'
            ? 'Quản lý tham số dịch vụ mạng, chế độ phát hiện bất thường và cơ chế bảo vệ Safety Gate'
            : 'Manage network service endpoints, detection sensitivity modes, and Safety Gate policy'}
        </p>
      </div>

      {/* Runtime Precedence Notice */}
      <div
        style={{
          background: '#f8fafc',
          border: '1px solid #cbd5e1',
          borderLeft: '4px solid #0284c7',
          padding: '14px 18px',
          borderRadius: 8,
          marginBottom: 20,
          fontSize: 13,
          color: '#334155',
          lineHeight: 1.5,
        }}
      >
        <strong>{language === 'vi' ? 'Lưu ý về thứ tự ưu tiên cấu hình:' : 'Runtime Precedence Notice:'}</strong>{' '}
        {t('settings.runtimeNotice')}
      </div>

      {statusMessage && (
        <div
          style={{
            background: '#e0f2fe',
            color: '#0369a1',
            padding: '10px 14px',
            borderRadius: 6,
            marginBottom: 18,
            fontWeight: 600,
            border: '1px solid #bae6fd',
            fontSize: 13,
          }}
        >
          {statusMessage}
        </div>
      )}

      {/* 1. Detection Mode */}
      <div className="settings-group" style={{ background: '#fff', padding: 22, borderRadius: 10, border: '1px solid #e2e8f0', marginBottom: 22, boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
        <h3 style={{ margin: '0 0 8px 0', color: '#0f172a', fontSize: '1.15rem', fontWeight: 700 }}>
          {t('settings.detectionMode')}
        </h3>
        <p style={{ fontSize: 13, color: '#64748b', marginBottom: 14 }}>
          {t('settings.detectionDescription')}
        </p>

        <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap', marginBottom: 14 }}>
          {['strict', 'balanced', 'loose'].map((option) => (
            <label key={option} style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontSize: 14, fontWeight: 600, color: '#334155' }}>
              <input
                type="radio"
                id={option}
                name="mode"
                value={option}
                checked={mode === option}
                onChange={(e) => setMode(e.target.value)}
                style={{ cursor: 'pointer' }}
              />
              <span>{option.charAt(0).toUpperCase() + option.slice(1)}</span>
            </label>
          ))}
        </div>

        <div style={{ background: '#f8fafc', padding: 12, borderRadius: 6, border: '1px solid #e2e8f0', fontSize: 13, color: '#475569' }}>
          <strong>{t('settings.selectedModeDesc')}</strong> {modeDescriptions[mode]}
        </div>
      </div>

      {/* 2. Application Variables */}
      <div className="settings-group" style={{ background: '#fff', padding: 22, borderRadius: 10, border: '1px solid #e2e8f0', marginBottom: 22, boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
        <h3 style={{ margin: '0 0 16px 0', color: '#0f172a', fontSize: '1.15rem', fontWeight: 700 }}>
          {t('settings.appVariables')}
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {[
            {
              label: t('settings.controllerIp'),
              id: 'sdn-ctrl-ip',
              value: sdnControllerIp,
              set: setSdnControllerIp,
              placeholder: '127.0.0.1',
            },
            {
              label: t('settings.siemIp'),
              id: 'siem-ip',
              value: elkIp,
              set: setElkIp,
              placeholder: '127.0.0.1',
            },
            {
              label: t('settings.honeypotIp'),
              id: 'honeypot-ip',
              value: honeypotIp,
              set: setHoneypotIp,
              placeholder: '10.0.0.6',
            },
          ].map(({ label, id, value, set, placeholder }) => (
            <div className="form-field" key={id} style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              <label htmlFor={id} style={{ fontWeight: 600, fontSize: 13, color: '#334155' }}>
                {label}
              </label>
              <input
                type="text"
                id={id}
                value={value}
                onChange={(e) => set(e.target.value)}
                placeholder={placeholder}
                style={{ width: '100%', maxWidth: '420px', padding: '8px 12px', borderRadius: 6, border: '1px solid #cbd5e1', fontSize: 13 }}
              />
            </div>
          ))}
        </div>

        <div style={{ marginTop: 20 }}>
          <button
            onClick={handleSaveSettings}
            style={{
              padding: '10px 22px',
              background: '#0284c7',
              color: '#fff',
              border: 'none',
              borderRadius: 6,
              fontWeight: 700,
              fontSize: 14,
              cursor: 'pointer',
              boxShadow: '0 1px 3px rgba(2, 132, 199, 0.3)'
            }}
          >
            {t('settings.btnSave')}
          </button>
        </div>
      </div>

      {/* 3. Effective Runtime Configuration & Safety Gate */}
      {healthSummary && (
        <div className="settings-group" style={{ background: '#fff', padding: 22, borderRadius: 10, border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
          <h3 style={{ margin: '0 0 6px 0', color: '#0f172a', fontSize: '1.15rem', fontWeight: 700 }}>
            {t('settings.runtimeSummaryTitle')}
          </h3>
          <p style={{ fontSize: 13, color: '#64748b', marginBottom: 14 }}>
            {t('settings.runtimeNoticeSub')}
          </p>
          <pre
            style={{
              background: '#0f172a',
              color: '#f8fafc',
              padding: 16,
              borderRadius: 8,
              fontSize: 12,
              overflowX: 'auto',
              lineHeight: 1.4,
              margin: 0
            }}
          >
            {JSON.stringify(healthSummary, null, 2)}
          </pre>
          <p style={{ margin: '14px 0 0 0', fontSize: 12, color: '#94a3b8' }}>
            ℹ️ {t('settings.safetyGateDesc')}
          </p>
        </div>
      )}
    </div>
  );
}

export default SystemSettings;
