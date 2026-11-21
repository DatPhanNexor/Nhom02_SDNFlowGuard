import React, { useEffect, useState, useRef, useCallback } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config/apiConfig';
import { useLanguage } from '../i18n/LanguageContext';

function LiveSdnSummary({ refreshTrigger }) {
  const { language, t } = useLanguage();
  const [onosState, setOnosState] = useState('checking'); // 'checking' | 'online' | 'offline'
  const [elkState, setElkState] = useState('checking'); // 'checking' | 'online' | 'offline'
  const [updated, setUpdated] = useState('');
  const [stats, setStats] = useState({
    switches: null,
    hosts: null,
    flows: null,
    alerts: null,
    packets: null,
    bytes: null,
  });
  const isMountedRef = useRef(true);
  const isFetchingRef = useRef(false);

  const loadNetworkOverview = useCallback(async () => {
    if (isFetchingRef.current) return;
    isFetchingRef.current = true;

    try {
      const [topologyRes, flowsRes, alertsRes] = await Promise.allSettled([
        axios.get(`${API_BASE_URL}/api/topology`, { timeout: 4500 }),
        axios.get(`${API_BASE_URL}/api/live-flows`, { timeout: 4500 }),
        axios.get(`${API_BASE_URL}/api/elk/security-alerts?minutes=1440&limit=1`, { timeout: 4500 }),
      ]);

      if (!isMountedRef.current) return;

      const topoOk =
        topologyRes.status === 'fulfilled' &&
        topologyRes.value?.data?.controller_status !== 'UNAVAILABLE';
      const flowsOk = flowsRes.status === 'fulfilled';
      const alertsOk = alertsRes.status === 'fulfilled';

      let activeSwitches = null;
      let hostsCount = null;
      let flowsCount = null;
      let packetsSum = null;
      let bytesSum = null;
      let alertsCount = null;

      if (topoOk) {
        const devices = Array.isArray(topologyRes.value.data?.devices)
          ? topologyRes.value.data.devices
          : [];
        const hosts = Array.isArray(topologyRes.value.data?.hosts)
          ? topologyRes.value.data.hosts
          : [];
        activeSwitches = devices.filter(
          (d) => d.available !== false && (d.type === 'SWITCH' || !d.type)
        ).length;
        hostsCount = hosts.length;
      }

      if (flowsOk) {
        const flows = Array.isArray(flowsRes.value.data?.data)
          ? flowsRes.value.data.data
          : [];
        flowsCount = flows.length;
        packetsSum = flows.reduce((sum, f) => sum + Number(f.packets || 0), 0);
        bytesSum = flows.reduce((sum, f) => sum + Number(f.bytes || 0), 0);
      }

      if (alertsOk) {
        alertsCount = Number(alertsRes.value.data?.total ?? alertsRes.value.data?.count ?? 0);
      }

      setOnosState(topoOk || flowsOk ? 'online' : 'offline');
      setElkState(alertsOk ? 'online' : 'offline');
      setStats({
        switches: activeSwitches,
        hosts: hostsCount,
        flows: flowsCount,
        alerts: alertsCount,
        packets: packetsSum,
        bytes: bytesSum,
      });

      setUpdated(
        new Date().toLocaleTimeString(language === 'vi' ? 'vi-VN' : 'en-US', {
          hour12: false,
        })
      );
    } catch (error) {
      if (!isMountedRef.current) return;
      console.error('Live SDN Overview error:', error);
      setOnosState('offline');
      setElkState('offline');
    } finally {
      isFetchingRef.current = false;
    }
  }, [language]);

  useEffect(() => {
    isMountedRef.current = true;
    loadNetworkOverview();

    const timer = setInterval(() => {
      if (document.visibilityState === 'visible') {
        loadNetworkOverview();
      }
    }, 5000);

    return () => {
      isMountedRef.current = false;
      clearInterval(timer);
    };
  }, [loadNetworkOverview, refreshTrigger]);

  const formatMetric = (val, isChecking) => {
    if (isChecking) return '...';
    if (val === null || val === undefined) return '--';
    return Number(val).toLocaleString(language === 'vi' ? 'vi-VN' : 'en-US');
  };

  const primaryKpis = [
    {
      id: 'switches',
      title: language === 'vi' ? 'Switch kết nối' : 'Connected Switches',
      value: formatMetric(stats.switches, onosState === 'checking'),
      unit: language === 'vi' ? 'thiết bị' : 'devices',
      state:
        onosState === 'checking'
          ? t('status.checking')
          : onosState === 'offline'
            ? (language === 'vi' ? 'ONOS mất kết nối (không có dữ liệu live)' : 'ONOS disconnected (no live data)')
            : stats.switches === 0
              ? (language === 'vi' ? 'Trực tuyến · Chờ kết nối Mininet' : 'Online · Awaiting Mininet')
              : (language === 'vi' ? 'Trực tuyến · OpenFlow 1.3 (ONOS)' : 'Online · OpenFlow 1.3 (ONOS)'),
      statusColor: onosState === 'offline' ? '#b91c1c' : stats.switches > 0 ? '#047857' : '#475569',
      stateVariant:
        onosState === 'checking'
          ? 'checking'
          : onosState === 'offline'
            ? 'offline'
            : stats.switches > 0
              ? 'online'
              : 'neutral',
      accentColor: onosState === 'offline' ? '#ef4444' : '#0284c7',
      iconSvg: (
        <svg viewBox="0 0 24 24" width="18" height="18" stroke={onosState === 'offline' ? '#dc2626' : '#0284c7'} fill="none" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="2" y="6" width="20" height="12" rx="2"></rect>
          <line x1="6" y1="12" x2="6.01" y2="12"></line>
          <line x1="10" y1="12" x2="10.01" y2="12"></line>
          <line x1="14" y1="12" x2="14.01" y2="12"></line>
          <line x1="18" y1="12" x2="18.01" y2="12"></line>
        </svg>
      ),
    },
    {
      id: 'hosts',
      title: language === 'vi' ? 'Host kết nối' : 'Connected Hosts',
      value: formatMetric(stats.hosts, onosState === 'checking'),
      unit: language === 'vi' ? 'host' : 'hosts',
      state:
        onosState === 'checking'
          ? t('status.checking')
          : onosState === 'offline'
            ? (language === 'vi' ? 'ONOS mất kết nối (chưa xác định)' : 'ONOS disconnected (unavailable)')
            : stats.hosts === 0
              ? (stats.switches > 0
                  ? (language === 'vi' ? 'Chưa phát hiện · Chạy pingall trong Mininet' : 'None detected · Run pingall in Mininet')
                  : (language === 'vi' ? 'Chưa có host hoạt động' : 'No active hosts'))
              : (language === 'vi' ? 'Đã định danh qua ONOS Host Service' : 'Discovered via ONOS Host Service'),
      statusColor: onosState === 'offline' ? '#b91c1c' : stats.hosts > 0 ? '#047857' : '#475569',
      stateVariant:
        onosState === 'checking'
          ? 'checking'
          : onosState === 'offline'
            ? 'offline'
            : stats.hosts > 0
              ? 'online'
              : 'neutral',
      accentColor: onosState === 'offline' ? '#ef4444' : '#0284c7',
      iconSvg: (
        <svg viewBox="0 0 24 24" width="18" height="18" stroke={onosState === 'offline' ? '#dc2626' : '#0284c7'} fill="none" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="2" y="3" width="20" height="14" rx="2"></rect>
          <line x1="8" y1="21" x2="16" y2="21"></line>
          <line x1="12" y1="17" x2="12" y2="21"></line>
        </svg>
      ),
    },
    {
      id: 'flows',
      title: language === 'vi' ? 'Quy tắc luồng' : 'Flow Rules',
      value: formatMetric(stats.flows, onosState === 'checking'),
      unit: language === 'vi' ? 'quy tắc' : 'rules',
      state:
        onosState === 'checking'
          ? t('status.checking')
          : onosState === 'offline'
            ? (language === 'vi' ? 'Không đọc được bảng luồng từ ONOS' : 'Unable to query ONOS flow table')
            : stats.flows === 0
              ? (language === 'vi' ? '0 quy tắc đang hoạt động trên switch' : '0 active flow rules on switches')
              : (language === 'vi' ? 'Đang nạp trên switch (ONOS Live)' : 'Installed on switches (ONOS Live)'),
      statusColor: onosState === 'offline' ? '#b91c1c' : stats.flows > 0 ? '#0369a1' : '#475569',
      stateVariant:
        onosState === 'checking'
          ? 'checking'
          : onosState === 'offline'
            ? 'offline'
            : stats.flows > 0
              ? 'info'
              : 'neutral',
      accentColor: onosState === 'offline' ? '#ef4444' : '#0ea5e9',
      iconSvg: (
        <svg viewBox="0 0 24 24" width="18" height="18" stroke={onosState === 'offline' ? '#dc2626' : '#0284c7'} fill="none" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
        </svg>
      ),
    },
    {
      id: 'alerts',
      title: language === 'vi' ? 'Cảnh báo an ninh' : 'Security Alerts',
      value: formatMetric(stats.alerts, elkState === 'checking'),
      unit: language === 'vi' ? 'cảnh báo (24h)' : 'alerts (24h)',
      state:
        elkState === 'checking'
          ? t('status.checking')
          : elkState === 'offline'
            ? (language === 'vi' ? 'Elasticsearch mất kết nối' : 'Elasticsearch unavailable')
            : stats.alerts === 0
              ? (language === 'vi' ? '0 cảnh báo trong 24 giờ qua (ELK)' : '0 alerts in past 24h (ELK)')
              : (language === 'vi' ? 'Ghi nhận trong Elasticsearch (24h)' : 'Recorded in Elasticsearch (24h)'),
      statusColor:
        elkState === 'offline'
          ? '#b91c1c'
          : stats.alerts > 0
            ? '#b91c1c'
            : '#475569',
      stateVariant:
        elkState === 'checking'
          ? 'checking'
          : elkState === 'offline'
            ? 'offline'
            : stats.alerts > 0
              ? 'alert'
              : 'neutral',
      accentColor:
        elkState === 'offline' || stats.alerts > 0 ? '#ef4444' : '#0d9488',
      iconSvg: (
        <svg
          viewBox="0 0 24 24"
          width="18"
          height="18"
          stroke={elkState === 'offline' || stats.alerts > 0 ? '#dc2626' : '#0d9488'}
          fill="none"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
      ),
    },
  ];

  const formatBytes = (bytes) => {
    if (bytes === null || bytes === undefined) return '--';
    const num = Number(bytes);
    if (!Number.isFinite(num)) return '--';
    if (num < 1024) return `${num} B`;
    if (num < 1024 * 1024) return `${(num / 1024).toFixed(1)} KB`;
    return `${(num / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <section className="network-overview-section" aria-label={t('dashboard.liveSdnNetwork')}>
      <div className="network-overview-header">
        <div className="network-overview-title-group">
          <h3 className="section-heading">{t('dashboard.liveSdnNetwork')}</h3>
          <span
            className={`network-status-badge ${
              onosState === 'online' ? 'online' : onosState === 'checking' ? 'loading' : 'offline'
            }`}
          >
            <span className="pulsing-circle" />
            {onosState === 'online'
              ? (language === 'vi' ? 'ONOS: Trực tuyến' : 'ONOS: ONLINE')
              : onosState === 'checking'
                ? (language === 'vi' ? 'ĐANG KIỂM TRA' : 'CHECKING')
                : (language === 'vi' ? 'ONOS: Mất kết nối' : 'ONOS: OFFLINE')}
          </span>
        </div>

        <div className="overview-refresh-meta">
          {updated && (
            <span className="meta-text">
              {t('common.lastUpdated')}: <strong>{updated}</strong>
            </span>
          )}
          <span className="meta-badge">
            {t('common.autoRefresh', { seconds: 5 })}
          </span>
        </div>
      </div>

      {/* Primary 4-KPI Row */}
      <div className="kpi-grid">
        {primaryKpis.map((kpi) => (
          <div
            key={kpi.id}
            className="kpi-card"
            style={{ borderTop: `3px solid ${kpi.accentColor}` }}
          >
            <div className="kpi-card-top">
              <span className="kpi-title">{kpi.title}</span>
              <span className="kpi-icon-container">{kpi.iconSvg}</span>
            </div>
            <div className="kpi-value-row">
              <span
                className={`kpi-value ${kpi.id === 'alerts' && stats.alerts > 0 ? 'kpi-value-alert' : ''}`}
              >
                {kpi.value}
              </span>
              <span className="kpi-unit">{kpi.unit}</span>
            </div>
            <div className={`kpi-state-label state-${kpi.stateVariant}`}>
              {kpi.state}
            </div>
          </div>
        ))}
      </div>

      {/* Secondary Flow Counter Row */}
      <div className="secondary-stats-row">
        <div className="secondary-stat-pill">
          <span className="stat-label">{t('dashboard.flowPackets')}:</span>
          <strong className="stat-number">
            {formatMetric(stats.packets, onosState === 'checking')}
          </strong>
        </div>

        <div className="secondary-stat-pill">
          <span className="stat-label">{t('dashboard.flowBytes')}:</span>
          <strong className="stat-number">{formatBytes(stats.bytes)}</strong>
        </div>

        <div className="secondary-stat-note">
          {t('dashboard.telemetrySourceNotice')}
        </div>
      </div>

      {onosState === 'offline' && (
        <div className="context-notice-banner error" role="status">
          {language === 'vi'
            ? 'ONOS Controller hiện không phản hồi (Port 8181). Chỉ số Switch, Host và Quy tắc luồng không thể đọc trực tiếp; dữ liệu phía dưới chỉ hiển thị bản ghi lịch sử nếu có.'
            : 'ONOS Controller is currently unreachable (Port 8181). Live switch, host, and flow counters cannot be retrieved; lower panels reflect historical records only.'}
        </div>
      )}

      {onosState === 'online' && stats.switches === 0 && (
        <div className="context-notice-banner warning" role="status">
          {language === 'vi'
            ? 'ONOS đang trực tuyến nhưng chưa phát hiện Switch OpenFlow kết nối. Khởi chạy Mininet với OpenFlow 1.3 để kết nối Switch vào ONOS.'
            : 'ONOS is online with 0 connected OpenFlow switches. Launch Mininet with OpenFlow 1.3 to attach switches to ONOS.'}
        </div>
      )}
    </section>
  );
}

export default LiveSdnSummary;
