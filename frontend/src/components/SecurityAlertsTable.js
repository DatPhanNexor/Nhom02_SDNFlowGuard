import React, { useEffect, useState } from 'react';
import { API_BASE_URL } from '../config/apiConfig';
import { useLanguage } from '../i18n/LanguageContext';

const API_URL = `${API_BASE_URL}/api/elk/security-alerts`;

function formatTime(value, language) {
  if (!value) return '-';

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return String(value);

  return date.toLocaleString(language === 'vi' ? 'vi-VN' : 'en-US', {
    timeZone: 'Asia/Ho_Chi_Minh',
    hour12: false
  });
}

function formatNumber(value) {
  const number = Number(value);

  return Number.isFinite(number)
    ? number.toFixed(3)
    : '-';
}

function SecurityAlertsTable() {
  const { language, t } = useLanguage();
  const [minutes, setMinutes] = useState(1440);
  const [filter, setFilter] = useState('all');
  const [alerts, setAlerts] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);
  const [lastLoaded, setLastLoaded] = useState(null);

  useEffect(() => {
    let active = true;

    const loadAlerts = async () => {
      try {
        const response = await fetch(
          `${API_URL}?minutes=${minutes}&limit=100`,
          { cache: 'no-store' }
        );

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const result = await response.json();

        if (!active) return;

        setAlerts(
          Array.isArray(result.alerts)
            ? result.alerts
            : []
        );

        setTotal(Number(result.total) || 0);
        setLastLoaded(new Date());
        setError('');
      } catch (err) {
        if (!active) return;

        console.error('Security Alerts API:', err);
        setError(
          language === 'vi'
            ? 'Không thể tải cảnh báo từ Flask/Elasticsearch.'
            : 'Unable to load security alerts from Flask/Elasticsearch.'
        );
      } finally {
        if (active) setLoading(false);
      }
    };

    setLoading(true);
    loadAlerts();

    const timer = setInterval(loadAlerts, 30000);

    return () => {
      active = false;
      clearInterval(timer);
    };
  }, [minutes, refreshKey, language]);

  const visibleAlerts = alerts.filter((alert) => {
    if (filter === 'test') return alert.test_only === true;
    if (filter === 'unverified') return alert.test_only !== true;
    return true;
  });

  const selectStyle = {
    padding: '7px 12px',
    border: '1px solid #cbd5e1',
    borderRadius: 6,
    background: '#fff',
    fontSize: 13,
    color: '#0f172a'
  };

  const cellStyle = {
    padding: '11px 12px',
    borderBottom: '1px solid #e2e8f0',
    textAlign: 'left',
    fontSize: 13,
    whiteSpace: 'nowrap'
  };

  return (
    <section
      style={{
        marginBottom: 22,
        padding: 20,
        background: '#fff',
        border: '1px solid #e2e8f0',
        borderRadius: 10,
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
      }}
    >
      <h3 style={{ marginTop: 0, color: '#0f172a', fontSize: '1.15rem', fontWeight: 700 }}>
        {t('alertsTable.title')}
      </h3>

      <p style={{ color: '#64748b', fontSize: 13, marginBottom: 16 }}>
        {t('alertsTable.subtitle')}
      </p>

      <div
        style={{
          display: 'flex',
          gap: 12,
          flexWrap: 'wrap',
          alignItems: 'center',
          marginBottom: 16
        }}
      >
        <select
          aria-label={t('alertsTable.timeRange')}
          style={selectStyle}
          value={minutes}
          onChange={(event) =>
            setMinutes(Number(event.target.value))
          }
        >
          <option value={60}>{t('alertsTable.oneHour')}</option>
          <option value={240}>{t('alertsTable.fourHours')}</option>
          <option value={1440}>{t('alertsTable.twentyFourHours')}</option>
          <option value={10080}>{t('alertsTable.sevenDays')}</option>
        </select>

        <select
          aria-label={t('alertsTable.filterType')}
          style={selectStyle}
          value={filter}
          onChange={(event) => setFilter(event.target.value)}
        >
          <option value="all">{t('alertsTable.allAlerts')}</option>
          <option value="test">{t('alertsTable.testOnly')}</option>
          <option value="unverified">{t('alertsTable.unverified')}</option>
        </select>

        <button
          type="button"
          style={{ ...selectStyle, cursor: 'pointer', background: '#0f172a', color: '#fff', border: '1px solid #334155', fontWeight: 600 }}
          onClick={() => setRefreshKey((value) => value + 1)}
        >
          {t('common.refresh')}
        </button>
      </div>

      <div style={{ marginBottom: 14, fontSize: 13, color: '#334155' }}>
        <strong>{t('common.showing')}: {visibleAlerts.length}</strong>
        {' | '}
        {t('common.all')}: {total} {t('common.records')}
      </div>

      {error && (
        <p role="alert" style={{ color: '#b91c1c', fontSize: 13 }}>
          {error}
        </p>
      )}

      {visibleAlerts.length === 0 ? (
        <p style={{ color: '#64748b', fontSize: 13 }}>
          {loading
            ? t('common.loadingData')
            : t('alertsTable.noMatchingAlerts')}
        </p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse'
            }}
          >
            <thead>
              <tr style={{ background: '#f8fafc', borderBottom: '1px solid #cbd5e1' }}>
                <th style={{ ...cellStyle, fontWeight: 700, color: '#475569' }}>{t('alertsTable.tableHeaders.time')}</th>
                <th style={{ ...cellStyle, fontWeight: 700, color: '#475569' }}>{t('alertsTable.tableHeaders.switch')}</th>
                <th style={{ ...cellStyle, fontWeight: 700, color: '#475569' }}>{t('alertsTable.tableHeaders.port')}</th>
                <th style={{ ...cellStyle, fontWeight: 700, color: '#475569' }}>{t('alertsTable.tableHeaders.peakPps')}</th>
                <th style={{ ...cellStyle, fontWeight: 700, color: '#475569' }}>{t('alertsTable.tableHeaders.thresholdPps')}</th>
                <th style={{ ...cellStyle, fontWeight: 700, color: '#475569' }}>{t('alertsTable.tableHeaders.status')}</th>
                <th style={{ ...cellStyle, fontWeight: 700, color: '#475569' }}>{t('alertsTable.tableHeaders.type')}</th>
              </tr>
            </thead>

            <tbody>
              {visibleAlerts.map((alert, index) => (
                <tr key={alert.alert_key || alert.event_id || index}>
                  <td style={cellStyle}>
                    {formatTime(
                      alert.detected_at_utc || alert.timestamp,
                      language
                    )}
                  </td>

                  <td style={cellStyle}>
                    <code>{alert.switch_id || '-'}</code>
                  </td>

                  <td style={cellStyle}>
                    {alert.port_number ?? '-'}
                  </td>

                  <td style={cellStyle}>
                    {formatNumber(alert.peak_pps)}
                  </td>

                  <td style={cellStyle}>
                    {formatNumber(alert.threshold_pps)}
                  </td>

                  <td style={cellStyle}>
                    {alert.status || 'unknown'}
                  </td>

                  <td style={cellStyle}>
                    <span
                      style={{
                        display: 'inline-block',
                        padding: '3px 8px',
                        borderRadius: 4,
                        background: alert.test_only === true
                          ? '#fef3c7'
                          : '#e2e8f0',
                        color: alert.test_only === true
                          ? '#92400e'
                          : '#334155',
                        fontWeight: 700,
                        fontSize: 11
                      }}
                    >
                      {alert.test_only === true
                        ? t('status.testAlert')
                        : t('status.unverified')}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p
        style={{
          fontSize: 12,
          color: '#94a3b8',
          marginBottom: 0,
          marginTop: 14
        }}
      >
        {lastLoaded
          ? `${t('common.lastUpdated')}: ${lastLoaded.toLocaleTimeString(language === 'vi' ? 'vi-VN' : 'en-US')}. `
          : ''}
        {t('common.autoRefresh', { seconds: 30 })}
      </p>
    </section>
  );
}

export default SecurityAlertsTable;
