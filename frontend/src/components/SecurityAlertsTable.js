import React, { useEffect, useState, useCallback, useRef } from 'react';
import { API_BASE_URL } from '../config/apiConfig';
import { useLanguage } from '../i18n/LanguageContext';

const API_URL = `${API_BASE_URL}/api/elk/security-alerts`;

function formatTime(value, language) {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);

  return date.toLocaleString(language === 'vi' ? 'vi-VN' : 'en-US', {
    timeZone: 'Asia/Ho_Chi_Minh',
    hour12: false,
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

function formatNumber(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number.toFixed(0) : '-';
}

function SecurityAlertsTable({ refreshTrigger }) {
  const { language, t } = useLanguage();
  const [minutes, setMinutes] = useState(1440);
  const [filter, setFilter] = useState('all');
  const [alerts, setAlerts] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);
  const [lastLoaded, setLastLoaded] = useState(null);
  const isMountedRef = useRef(true);

  const loadAlerts = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}?minutes=${minutes}&limit=100`, {
        cache: 'no-store',
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();
      if (!isMountedRef.current) return;

      setAlerts(Array.isArray(result.alerts) ? result.alerts : []);
      setTotal(Number(result.total) || 0);
      setLastLoaded(new Date());
      setError('');
    } catch (err) {
      if (!isMountedRef.current) return;
      console.error('Security Alerts API:', err);
      setAlerts([]);
      setTotal(0);
      setError(
        language === 'vi'
          ? 'Không thể tải cảnh báo từ Elasticsearch. Kiểm tra kết nối Backend và container Elasticsearch.'
          : 'Unable to load security alerts from Elasticsearch. Verify Backend and Elasticsearch connectivity.'
      );
    } finally {
      if (isMountedRef.current) setLoading(false);
    }
  }, [minutes, language]);

  useEffect(() => {
    isMountedRef.current = true;
    loadAlerts();

    const timer = setInterval(() => {
      if (document.visibilityState === 'visible') {
        loadAlerts();
      }
    }, 30000);

    return () => {
      isMountedRef.current = false;
      clearInterval(timer);
    };
  }, [loadAlerts, refreshKey, refreshTrigger]);

  const visibleAlerts = alerts.filter((alert) => {
    if (filter === 'test') return alert.test_only === true;
    if (filter === 'unverified') return alert.test_only !== true;
    return true;
  });

  const getHeaderBadge = () => {
    if (loading) {
      return {
        text: language === 'vi' ? 'ĐANG TẢI...' : 'CHECKING...',
        cls: 'pill-warn',
      };
    }
    if (error) {
      return {
        text: language === 'vi' ? 'ELK MẤT KẾT NỐI' : 'ELK OFFLINE',
        cls: 'pill-offline',
      };
    }
    if (visibleAlerts.length > 0) {
      return {
        text: `${visibleAlerts.length} ${language === 'vi' ? 'CẢNH BÁO' : 'ALERTS'}`,
        cls: 'pill-offline',
      };
    }
    return {
      text: language === 'vi' ? '0 CẢNH BÁO TRONG KHUNG LỌC' : '0 ALERTS IN RANGE',
      cls: 'pill-neutral',
    };
  };

  const headerBadge = getHeaderBadge();

  return (
    <section className="security-alerts-card">
      <div className="panel-card-header">
        <div className="panel-card-title-group">
          <h3 className="card-heading">{t('alertsTable.title')}</h3>
          <span className={`noc-pill ${headerBadge.cls}`}>{headerBadge.text}</span>
        </div>

        <div className="panel-toolbar-controls">
          <select
            aria-label={t('alertsTable.timeRange')}
            className="noc-select"
            value={minutes}
            onChange={(e) => setMinutes(Number(e.target.value))}
          >
            <option value={60}>{t('alertsTable.oneHour')}</option>
            <option value={240}>{t('alertsTable.fourHours')}</option>
            <option value={1440}>{t('alertsTable.twentyFourHours')}</option>
            <option value={10080}>{t('alertsTable.sevenDays')}</option>
          </select>

          <select
            aria-label={t('alertsTable.filterType')}
            className="noc-select"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">{t('alertsTable.allAlerts')}</option>
            <option value="test">{t('alertsTable.testOnly')}</option>
            <option value="unverified">{t('alertsTable.unverified')}</option>
          </select>

          <button
            type="button"
            className="noc-icon-btn"
            disabled={loading}
            onClick={() => setRefreshKey((val) => val + 1)}
            title={language === 'vi' ? 'Làm mới bảng cảnh báo' : 'Refresh alerts'}
            aria-label={language === 'vi' ? 'Làm mới bảng cảnh báo' : 'Refresh alerts'}
          >
            <svg
              className={loading ? 'spin-icon' : ''}
              viewBox="0 0 24 24"
              width="14"
              height="14"
              stroke="currentColor"
              fill="none"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="23 4 23 10 17 10"></polyline>
              <polyline points="1 20 1 14 7 14"></polyline>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
          </button>
        </div>
      </div>

      <p className="panel-card-subtitle">{t('alertsTable.subtitle')}</p>

      {error && (
        <div className="noc-error-banner" role="alert">
          {error}
        </div>
      )}

      {/* Table / Empty Container */}
      <div className="alerts-table-body">
        {visibleAlerts.length === 0 ? (
          <div className="noc-empty-box">
            {loading ? (
              <span>{t('common.loadingData')}</span>
            ) : error ? (
              <span>
                {language === 'vi'
                  ? 'Không có dữ liệu cảnh báo do lỗi kết nối Elasticsearch.'
                  : 'Alert data unavailable because Elasticsearch could not be reached.'}
              </span>
            ) : (
              <span>
                {alerts.length > 0
                  ? t('alertsTable.noMatchingAlerts')
                  : language === 'vi'
                    ? 'Chưa có cảnh báo an ninh nào trong khoảng thời gian đang lọc.'
                    : 'No security alerts recorded in the selected time range.'}
              </span>
            )}
          </div>
        ) : (
          <div className="noc-table-scroll">
            <table className="noc-table">
              <thead>
                <tr>
                  <th>{t('alertsTable.tableHeaders.time')}</th>
                  <th>{t('alertsTable.tableHeaders.switch')}</th>
                  <th>{t('alertsTable.tableHeaders.port')}</th>
                  <th>{language === 'vi' ? 'PPS / Ngưỡng' : 'PPS / Threshold'}</th>
                  <th>{t('alertsTable.tableHeaders.status')}</th>
                  <th>{t('alertsTable.tableHeaders.type')}</th>
                </tr>
              </thead>
              <tbody>
                {visibleAlerts.map((alert, index) => (
                  <tr key={alert.alert_key || alert.event_id || index}>
                    <td>{formatTime(alert.detected_at_utc || alert.timestamp, language)}</td>
                    <td>
                      <code>{alert.switch_id ? alert.switch_id.slice(-6) : '-'}</code>
                    </td>
                    <td>{alert.port_number ? `Port ${alert.port_number}` : '-'}</td>
                    <td>
                      <span className="metric-danger">{formatNumber(alert.peak_pps)}</span>
                      <span className="metric-divider">/</span>
                      <span className="metric-muted">{formatNumber(alert.threshold_pps)}</span>
                    </td>
                    <td>
                      <span
                        className={`noc-tag ${
                          alert.status === 'DETECTED' ? 'tag-danger' : 'tag-neutral'
                        }`}
                      >
                        {alert.status || 'DETECTED'}
                      </span>
                    </td>
                    <td>
                      <span
                        className={`noc-tag ${
                          alert.test_only === true ? 'tag-warn' : 'tag-info'
                        }`}
                      >
                        {alert.test_only === true ? t('status.testAlert') : t('status.unverified')}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="panel-footer-meta">
        <span>
          {t('common.showing')}: <strong>{visibleAlerts.length}</strong> / {total}{' '}
          {t('common.records')}
        </span>
        {lastLoaded && !error && (
          <span className="panel-updated-time">
            {t('common.lastUpdated')}:{' '}
            <strong>
              {lastLoaded.toLocaleTimeString(language === 'vi' ? 'vi-VN' : 'en-US', { hour12: false })}
            </strong>
          </span>
        )}
      </div>
    </section>
  );
}

export default SecurityAlertsTable;
