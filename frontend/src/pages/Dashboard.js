import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import LiveSdnSummary from './LiveSdnSummary';
import SdnPortRates from './SdnPortRates';
import SecurityAlertsTable from '../components/SecurityAlertsTable';
import ElkPortHistoryChart from '../components/ElkPortHistoryChart';
import CollapsibleSection from '../components/CollapsibleSection';
import { API_BASE_URL } from '../config/apiConfig';
import { useLanguage } from '../i18n/LanguageContext';
import { useTheme } from '../theme/ThemeContext';
import './Dashboard.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function normalizeServiceState(rawValue, backendReachable, isInitialLoading) {
  if (isInitialLoading) return 'CHECKING';
  if (!backendReachable) return 'UNKNOWN';
  const normalized = String(rawValue || '').trim().toUpperCase();
  if (normalized === 'UP' || normalized === 'ONLINE' || normalized === 'READY') return 'ONLINE';
  if (normalized === 'DEGRADED') return 'DEGRADED';
  if (normalized === 'DOWN' || normalized === 'OFFLINE') return 'OFFLINE';
  return 'UNKNOWN';
}

function classifyActionEntry(action, language) {
  const rawType = String(action?.action_type || 'Unknown');
  const lower = rawType.toLowerCase();

  if (lower.includes('dry_run') || lower.includes('dry run') || lower.includes('simulat')) {
    return {
      bucket: language === 'vi' ? 'Dry-Run (Mô phỏng)' : 'Dry-Run (Simulated)',
      color: '#0ea5e9',
      category: 'dry_run',
    };
  }
  if (lower.includes('approval') || lower.includes('staged') || lower.includes('pending')) {
    return {
      bucket: language === 'vi' ? 'Chờ phê duyệt / Dự thảo' : 'Staged / Approval Req.',
      color: '#f59e0b',
      category: 'staged',
    };
  }
  if (lower.includes('fail') || lower.includes('error') || lower.includes('reject')) {
    return {
      bucket: language === 'vi' ? 'Thất bại / Từ chối' : 'Failed / Rejected',
      color: '#dc2626',
      category: 'failed',
    };
  }
  if (lower.includes('unblock') || lower.includes('rollback') || lower.includes('allow')) {
    return {
      bucket: language === 'vi' ? 'Hoàn tác / Gỡ chặn' : 'Rollback / Unblock',
      color: '#10b981',
      category: 'rollback',
    };
  }
  if (lower.includes('rate')) {
    return {
      bucket: language === 'vi' ? 'Giới hạn tốc độ' : 'Rate Limit',
      color: '#8b5cf6',
      category: 'rate_limit',
    };
  }
  if (lower.includes('redirect')) {
    return {
      bucket: language === 'vi' ? 'Chuyển hướng' : 'Redirect',
      color: '#f97316',
      category: 'redirect',
    };
  }
  if (lower.includes('block') || lower.includes('deny')) {
    return {
      bucket: language === 'vi' ? 'Chặn lưu lượng (Block)' : 'Block Traffic',
      color: '#e11d48',
      category: 'block',
    };
  }
  return {
    bucket: rawType,
    color: '#64748b',
    category: 'other',
  };
}

function Dashboard() {
  const { language, t } = useLanguage();
  const { isDark } = useTheme();
  const [trafficData, setTrafficData] = useState([]);
  const [recentActions, setRecentActions] = useState([]);
  const [serviceStatus, setServiceStatus] = useState({});
  const [backendReachable, setBackendReachable] = useState(null); // null | true | false
  const [defenseMode, setDefenseMode] = useState('');
  const [evidenceSummary, setEvidenceSummary] = useState(null);
  const [siemScope, setSiemScope] = useState(null);
  const [logstashPipelineStats, setLogstashPipelineStats] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [syncError, setSyncError] = useState(false);
  const [lastRefreshedAt, setLastRefreshedAt] = useState('--:--:--');
  const navigate = useNavigate();

  const fetchDashboardData = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const [
        healthRes,
        flowsRes,
        actionsRes,
        statusRes,
        logstashRes,
        evidenceRes,
        siemRes,
      ] = await Promise.allSettled([
        axios.get(`${API_BASE_URL}/api/health`, { timeout: 5000 }),
        axios.get(`${API_BASE_URL}/api/get-flows`, { timeout: 5000 }),
        axios.get(`${API_BASE_URL}/api/get-actions`, { timeout: 5000 }),
        axios.get(`${API_BASE_URL}/api/service-status`, { timeout: 5000 }),
        axios.get(`${API_BASE_URL}/api/logstash/pipeline-status`, { timeout: 5000 }),
        axios.get(`${API_BASE_URL}/api/defense/evidence-correlation`, { timeout: 5000 }),
        axios.get(`${API_BASE_URL}/api/siem/evaluate-fixtures`, { timeout: 5000 }),
      ]);

      const apiUp =
        healthRes.status === 'fulfilled' ||
        statusRes.status === 'fulfilled' ||
        flowsRes.status === 'fulfilled';

      setBackendReachable(apiUp);
      setSyncError(!apiUp);

      if (healthRes.status === 'fulfilled' && healthRes.value.data) {
        setDefenseMode(healthRes.value.data.defense_mode || 'DRY_RUN');
      } else if (!apiUp) {
        setDefenseMode('');
      }

      if (flowsRes.status === 'fulfilled') {
        setTrafficData(Array.isArray(flowsRes.value.data?.data) ? flowsRes.value.data.data : []);
      } else {
        setTrafficData([]);
      }

      if (actionsRes.status === 'fulfilled') {
        setRecentActions(Array.isArray(actionsRes.value.data?.data) ? actionsRes.value.data.data : []);
      } else {
        setRecentActions([]);
      }

      if (statusRes.status === 'fulfilled') {
        setServiceStatus(statusRes.value.data?.data || {});
      } else {
        setServiceStatus({});
      }

      if (logstashRes.status === 'fulfilled') {
        setLogstashPipelineStats(logstashRes.value.data?.data || null);
      } else {
        setLogstashPipelineStats(null);
      }

      if (evidenceRes.status === 'fulfilled') {
        setEvidenceSummary(evidenceRes.value.data?.data || null);
      } else {
        setEvidenceSummary(null);
      }

      if (siemRes.status === 'fulfilled') {
        setSiemScope(siemRes.value.data?.data || null);
      } else {
        setSiemScope(null);
      }

      setLastRefreshedAt(
        new Date().toLocaleTimeString(language === 'vi' ? 'vi-VN' : 'en-US', { hour12: false })
      );
    } catch (err) {
      console.error('Error fetching dashboard telemetry:', err);
      setBackendReachable(false);
      setSyncError(true);
    } finally {
      setIsInitialLoading(false);
      setIsRefreshing(false);
    }
  }, [language]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData, refreshTrigger]);

  const handleRefreshAll = () => {
    if (isRefreshing) return;
    setRefreshTrigger((prev) => prev + 1);
  };

  // Compute real independent statuses for all 6 platform services
  const serviceStates = useMemo(() => {
    const backendState = isInitialLoading
      ? 'CHECKING'
      : backendReachable
        ? 'ONLINE'
        : 'OFFLINE';

    const onosState = normalizeServiceState(serviceStatus.ONOS, backendReachable, isInitialLoading);
    const openflowState = normalizeServiceState(serviceStatus.OPENFLOW, backendReachable, isInitialLoading);
    const esState = normalizeServiceState(serviceStatus.ELK, backendReachable, isInitialLoading);
    const logstashState = normalizeServiceState(serviceStatus.LOGSTASH, backendReachable, isInitialLoading);
    const kibanaState = normalizeServiceState(serviceStatus.KIBANA, backendReachable, isInitialLoading);

    return {
      backend: backendState,
      onos: onosState,
      openflow: openflowState,
      elasticsearch: esState,
      logstash: logstashState,
      kibana: kibanaState,
    };
  }, [serviceStatus, backendReachable, isInitialLoading]);

  const healthBarItems = useMemo(
    () => [
      { id: 'backend', label: 'Backend API', port: '5000', state: serviceStates.backend },
      { id: 'onos', label: 'ONOS Controller', port: '8181', state: serviceStates.onos },
      { id: 'openflow', label: 'OpenFlow 1.3', port: '6653', state: serviceStates.openflow },
      { id: 'elasticsearch', label: 'Elasticsearch', port: '9200', state: serviceStates.elasticsearch },
      { id: 'logstash', label: 'Logstash', port: '18080', state: serviceStates.logstash },
      { id: 'kibana', label: 'Kibana', port: '5601', state: serviceStates.kibana },
    ],
    [serviceStates]
  );

  const onlineServicesCount = healthBarItems.filter((item) => item.state === 'ONLINE').length;
  const totalServicesCount = healthBarItems.length;

  const overallSystemState = useMemo(() => {
    if (isInitialLoading) return 'CHECKING';
    if (!backendReachable) return 'OFFLINE';
    if (onlineServicesCount === totalServicesCount) return 'ONLINE';
    if (onlineServicesCount > 0) return 'DEGRADED';
    return 'OFFLINE';
  }, [isInitialLoading, backendReachable, onlineServicesCount, totalServicesCount]);

  const formatServiceStateLabel = (state, serviceId = '') => {
    if (serviceId === 'onos' && state === 'OFFLINE') {
      return language === 'vi' ? 'Mất kết nối' : 'OFFLINE';
    }
    switch (state) {
      case 'ONLINE':
        return 'ONLINE';
      case 'OFFLINE':
        return 'OFFLINE';
      case 'DEGRADED':
        return 'DEGRADED';
      case 'CHECKING':
        return 'CHECKING';
      default:
        return 'UNKNOWN';
    }
  };

  const getMonitoringModeLabel = () => {
    if (!backendReachable && !isInitialLoading) {
      return language === 'vi' ? 'Không xác định (API Offline)' : 'Unknown (API Offline)';
    }
    const mode = (defenseMode || 'DRY_RUN').toUpperCase();
    if (mode === 'DRY_RUN' || mode === 'AUTO_STAGE_ONLY') {
      return t('dashboard.observationSafeMode');
    }
    if (mode === 'MANUAL_APPROVAL') {
      return t('dashboard.approvalRequiredMode');
    }
    if (mode === 'ACTIVE_ENFORCEMENT') {
      return t('dashboard.activeDefenseModeLabel');
    }
    return t('dashboard.safeMonitoringMode');
  };

  const trafficChartData = useMemo(
    () => ({
      labels: trafficData.map((_, index) => `${language === 'vi' ? 'Luồng' : 'Flow'} ${index + 1}`),
      datasets: [
        {
          label: t('dashboard.transferredBytes'),
          data: trafficData.map((flow) => Number(flow.bandwidth || 0)),
          borderColor: '#0284c7',
          backgroundColor: 'rgba(2, 132, 199, 0.12)',
          borderWidth: 2,
          pointRadius: 2.5,
          tension: 0.25,
          fill: true,
        },
      ],
    }),
    [trafficData, language, t]
  );

  const actionBreakdown = useMemo(() => {
    const map = new Map();
    recentActions.forEach((action) => {
      const classified = classifyActionEntry(action, language);
      const existing = map.get(classified.bucket) || {
        label: classified.bucket,
        count: 0,
        color: classified.color,
        category: classified.category,
      };
      existing.count += 1;
      map.set(classified.bucket, existing);
    });
    return Array.from(map.values());
  }, [recentActions, language]);

  const actionsChartData = useMemo(
    () => ({
      labels: actionBreakdown.map((item) => item.label),
      datasets: [
        {
          label: t('dashboard.actionsCount'),
          data: actionBreakdown.map((item) => item.count),
          backgroundColor: actionBreakdown.map((item) => item.color),
          borderRadius: 4,
        },
      ],
    }),
    [actionBreakdown, t]
  );

  const siemSourceCount = Array.isArray(siemScope?.sources) ? siemScope.sources.length : null;
  const siemVerifiedCount = Array.isArray(siemScope?.sources)
    ? siemScope.sources.filter((s) => s.integration_status === 'VERIFIED_INTEGRATION').length
    : null;

  const isOnosOffline = serviceStates.onos === 'OFFLINE';

  return (
    <div className="dashboard">
      {/* =========================================================
         SECTION 1: DASHBOARD HEADER
         ========================================================= */}
      <header className="dashboard-header">
        <div className="dashboard-title-area">
          <h2>{t('dashboard.title')}</h2>
          <p>
            {language === 'vi'
              ? 'Giám sát trạng thái mạng SDN, lưu lượng, cảnh báo an ninh và hoạt động phòng thủ.'
              : 'Monitor SDN network health, traffic telemetry, security alerts, and defense operations.'}
          </p>
        </div>

        <div className="dashboard-header-actions">
          <span
            className={`sync-state-pill state-${
              isRefreshing ? 'checking' : syncError ? 'offline' : overallSystemState.toLowerCase()
            }`}
          >
            <span className="status-dot" />
            {isRefreshing
              ? language === 'vi'
                ? 'Đang đồng bộ...'
                : 'Syncing...'
              : syncError
                ? language === 'vi'
                  ? 'Lỗi đồng bộ API'
                  : 'Sync Error'
                : overallSystemState === 'ONLINE'
                  ? language === 'vi'
                    ? 'Đồng bộ đầy đủ'
                    : 'All Systems Synced'
                  : language === 'vi'
                    ? 'Suy giảm một phần'
                    : 'Partial Connectivity'}
          </span>

          <span className="header-meta-timestamp">
            {t('common.lastUpdated')}: <strong>{lastRefreshedAt}</strong>
          </span>

          <button
            type="button"
            className="noc-action-btn primary"
            onClick={handleRefreshAll}
            disabled={isRefreshing}
            title={
              language === 'vi'
                ? 'Làm mới toàn bộ chỉ số, thông lượng cổng và bảng cảnh báo'
                : 'Refresh all telemetry, port throughput, and alerts'
            }
          >
            <svg
              className={isRefreshing ? 'spin-icon' : ''}
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
            {t('common.refresh')}
          </button>
        </div>
      </header>

      {/* =========================================================
         SECTION 2: NETWORK OVERVIEW KPIS (4-CARD ROW)
         ========================================================= */}
      <LiveSdnSummary refreshTrigger={refreshTrigger} />

      {/* =========================================================
         SECTION 3: HEALTH STATUS BAR (ALL 6 SERVICES)
         ========================================================= */}
      <section
        className="health-status-bar"
        aria-label={t('dashboard.systemHealth')}
      >
        <div className="health-bar-header">
          <div className="health-bar-summary">
            <span className={`status-dot state-${overallSystemState.toLowerCase()}`} />
            <span className="health-bar-title">
              {t('dashboard.systemHealth')}:{' '}
              <strong>{overallSystemState}</strong>
            </span>
            <span className="health-bar-count">
              ({onlineServicesCount}/{totalServicesCount}{' '}
              {language === 'vi' ? 'dịch vụ trực tuyến' : 'services online'})
            </span>
          </div>

          <div className="defense-mode-box">
            <span className="status-label">
              {language === 'vi' ? 'Chế độ phòng vệ:' : 'Defense Mode:'}
            </span>
            <span className="defense-mode-pill">
              {defenseMode
                ? `${defenseMode} · ${getMonitoringModeLabel()}`
                : t('status.unknown')}
            </span>
          </div>
        </div>

        <div className="health-chips-grid">
          {healthBarItems.map((svc) => (
            <div key={svc.id} className={`health-chip state-${svc.state.toLowerCase()}`}>
              <span className={`status-dot state-${svc.state.toLowerCase()}`} />
              <span className="health-chip-name">{svc.label}</span>
              <span className="health-chip-port">:{svc.port}</span>
              <span className={`health-chip-state state-${svc.state.toLowerCase()}`}>
                {formatServiceStateLabel(svc.state, svc.id)}
              </span>
            </div>
          ))}
        </div>

        {isOnosOffline && (
          <div className="health-diagnostic-banner" role="status">
            <strong>{language === 'vi' ? 'ONOS: Mất kết nối' : 'ONOS: Disconnected'}</strong> —{' '}
            {language === 'vi'
              ? 'Dữ liệu topo/luồng trực tiếp không khả dụng và các thao tác thay đổi luật trên ONOS sẽ không thể thực thi cho đến khi controller hoạt động trở lại. Mở mục Dịch vụ bên dưới để xem chẩn đoán.'
              : 'Live topology/flow telemetry is unavailable and ONOS rule enforcement cannot execute until the controller recovers. Expand the Service Directory below for diagnostics.'}
          </div>
        )}
      </section>

      {/* =========================================================
         SECTION 4: LIVE PORT TELEMETRY & SECURITY ALERTS
         ========================================================= */}
      <div className="telemetry-alerts-grid">
        <SdnPortRates refreshTrigger={refreshTrigger} />
        <SecurityAlertsTable refreshTrigger={refreshTrigger} />
      </div>

      {/* =========================================================
         SECTION 5: ELK PORT TRAFFIC HISTORY (HISTORICAL TIME-SERIES)
         ========================================================= */}
      <ElkPortHistoryChart refreshTrigger={refreshTrigger} />

      {/* =========================================================
         SECTION 6: STORED FLOW TRAFFIC & RECENT DEFENSE ACTIONS (SQLITE)
         ========================================================= */}
      <div className="dashboard-widgets">
        {/* Stored Flow Traffic Chart (Historical SQLite) */}
        <section className="widget">
          <div className="widget-header">
            <div>
              <div className="widget-title-row">
                <h3 className="card-heading">{t('dashboard.storedFlowTraffic')}</h3>
                <span className="noc-pill pill-info">
                  {language === 'vi' ? 'Dữ liệu lịch sử' : 'Historical Data'}
                </span>
              </div>
              <div className="widget-subtitle">
                {language === 'vi'
                  ? 'Bản ghi lưu vết quy tắc luồng trong SQLite (không phải tốc độ live trên ONOS).'
                  : 'Persisted flow table snapshots in SQLite (not live ONOS throughput).'}
              </div>
            </div>
            <div className="widget-header-right">
              <span className="widget-badge">
                {trafficData.length} {t('common.records')}
              </span>
              <button
                type="button"
                className="widget-nav-btn"
                onClick={() => navigate('/traffic-overview')}
              >
                {language === 'vi' ? 'Xem lưu lượng' : 'Open Traffic'} &rarr;
              </button>
            </div>
          </div>

          {trafficData.length === 0 ? (
            <div className="widget-empty-box">
              <p className="empty-box-title">{t('dashboard.noTrafficRecorded')}</p>
              <p className="empty-box-desc">{t('dashboard.connectMininetPrompt')}</p>
            </div>
          ) : (
            <div className="widget-chart-container">
              <Line
                data={trafficChartData}
                options={{
                  maintainAspectRatio: false,
                  responsive: true,
                  plugins: {
                    legend: {
                      display: true,
                      position: 'top',
                      labels: { font: { size: 12 }, usePointStyle: true },
                    },
                    tooltip: {
                      callbacks: {
                        label: (ctx) =>
                          `${ctx.dataset.label}: ${Number(ctx.parsed.y).toLocaleString(
                            language === 'vi' ? 'vi-VN' : 'en-US'
                          )} Bytes`,
                      },
                    },
                  },
                  scales: {
                    x: {
                      grid: { color: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)' },
                      ticks: { color: isDark ? '#94a3b8' : '#475569', maxTicksLimit: 8, font: { size: 11 } },
                    },
                    y: {
                      beginAtZero: true,
                      grid: { color: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)' },
                      ticks: { color: isDark ? '#94a3b8' : '#475569', font: { size: 11 } },
                      title: { display: true, text: 'Bytes', color: isDark ? '#f8fafc' : '#0f172a', font: { size: 11, weight: 'bold' } },
                    },
                  },
                }}
              />
            </div>
          )}
        </section>

        {/* Recent Defense Actions Chart (SQLite Audit Log) */}
        <section className="widget">
          <div className="widget-header">
            <div>
              <div className="widget-title-row">
                <h3 className="card-heading">{t('dashboard.recentActions')}</h3>
                <span className="noc-pill pill-neutral">
                  {language === 'vi' ? 'Nhật ký kiểm toán' : 'Audit Log'}
                </span>
              </div>
              <div className="widget-subtitle">
                {language === 'vi'
                  ? 'Phân tách rõ hành động mô phỏng (Dry-Run), chặn, giới hạn tốc độ, hoàn tác và lỗi.'
                  : 'Separates Dry-Run simulations, blocks, rate limits, rollbacks, and failed actions.'}
              </div>
            </div>
            <div className="widget-header-right">
              <span className="widget-badge">
                {recentActions.length} {language === 'vi' ? 'hành động' : 'actions'}
              </span>
              <button
                type="button"
                className="widget-nav-btn"
                onClick={() => navigate('/decision-logs')}
              >
                {language === 'vi' ? 'Nhật ký quyết định' : 'Decision Logs'} &rarr;
              </button>
            </div>
          </div>

          {actionBreakdown.length > 0 && (
            <div className="action-legend-row">
              {actionBreakdown.map((item) => (
                <span key={item.label} className="action-legend-pill">
                  <span className="legend-dot" style={{ backgroundColor: item.color }} />
                  <span>{item.label}:</span>
                  <strong>{item.count}</strong>
                </span>
              ))}
            </div>
          )}

          {recentActions.length === 0 ? (
            <div className="widget-empty-box">
              <p className="empty-box-title">{t('dashboard.noActionsRecorded')}</p>
              <p className="empty-box-desc">{t('dashboard.actionsPrompt')}</p>
            </div>
          ) : (
            <div className="widget-chart-container">
              <Bar
                data={actionsChartData}
                options={{
                  maintainAspectRatio: false,
                  responsive: true,
                  plugins: {
                    legend: { display: false },
                    tooltip: {
                      callbacks: {
                        label: (ctx) =>
                          `${ctx.label}: ${ctx.parsed.y} ${
                            language === 'vi' ? 'hành động' : 'actions'
                          }`,
                      },
                    },
                  },
                  scales: {
                    x: {
                      grid: { color: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)' },
                      ticks: { color: isDark ? '#94a3b8' : '#475569', font: { size: 11 } },
                    },
                    y: {
                      beginAtZero: true,
                      grid: { color: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)' },
                      ticks: { color: isDark ? '#94a3b8' : '#475569', precision: 0, font: { size: 11 } },
                    },
                  },
                }}
              />
            </div>
          )}
        </section>
      </div>

      {/* =========================================================
         SECTION 7: SECURITY EVIDENCE & SIEM CORRELATION (COLLAPSIBLE)
         Default: Collapsed | Zero internal "Step 64" labels
         ========================================================= */}
      <CollapsibleSection
        id="security-evidence"
        title={t('dashboard.evidenceSectionTitle')}
        subtitle={t('dashboard.evidenceSectionSubtitle')}
        expandLabel={t('dashboard.viewEvidenceDetails')}
        collapseLabel={t('dashboard.collapseEvidenceDetails')}
        expandAriaLabel={t('dashboard.showEvidenceAria')}
        collapseAriaLabel={t('dashboard.collapseEvidenceAria')}
        defaultExpanded={false}
        summaryPills={
          <>
            <span className="summary-pill mode-pill">
              <strong>{getMonitoringModeLabel()}</strong>
              {evidenceSummary?.security_assessment?.decision
                ? ` · ${evidenceSummary.security_assessment.decision}`
                : ''}
            </span>
            <span className="summary-pill">
              SIEM:{' '}
              <strong>
                {siemSourceCount !== null
                  ? language === 'vi'
                    ? `${siemSourceCount} nguồn (${siemVerifiedCount} xác minh)`
                    : `${siemSourceCount} sources (${siemVerifiedCount} verified)`
                  : language === 'vi'
                    ? 'Chưa có dữ liệu'
                    : 'Unavailable'}
              </strong>
            </span>
          </>
        }
      >
        <div className="evidence-panel-stack">
          {/* Host Identity & Evidence Correlation */}
          {evidenceSummary ? (
            <div className="evidence-detail-card teal-accent">
              <div className="evidence-card-top">
                <h4 className="evidence-card-heading">
                  {t('dashboard.hostVerificationTitle')}
                </h4>
                <button
                  type="button"
                  className="widget-nav-btn"
                  onClick={() => navigate('/anomaly-detection')}
                >
                  {language === 'vi' ? 'Mở phân tích bất thường' : 'Open Anomaly Analysis'} &rarr;
                </button>
              </div>
              <p className="evidence-detail-line">
                <strong>{t('dashboard.evidenceArtifact')}:</strong>{' '}
                <code>{evidenceSummary.evidence_source_file}</code> ({evidenceSummary.total_packets}{' '}
                {language === 'vi' ? 'gói tin ICMP bắt tại cổng ingress' : 'switch ingress ICMP packets'}) |{' '}
                <strong>{t('dashboard.sha256Hash')}:</strong>{' '}
                <code>{(evidenceSummary.evidence_source_sha256 || '').slice(0, 24)}...</code>
              </p>
              <p className="evidence-detail-line">
                <strong>{t('dashboard.topologyCorroboration')}:</strong>{' '}
                {evidenceSummary.security_assessment?.topology_corroborated
                  ? t('dashboard.corroboratedObservation')
                  : t('status.unverified')}{' '}
                | <strong>{t('dashboard.historicalUtcCorrelation')}:</strong>{' '}
                {evidenceSummary.security_assessment?.historical_alert_correlation_verified
                  ? t('status.verified')
                  : language === 'vi'
                    ? 'CHƯA XÁC MINH (Dữ liệu bắt gói thiếu nhãn múi giờ/ngày)'
                    : 'NOT VERIFIED (Capture clock lacks date/timezone)'}
              </p>
              <p className="evidence-detail-line strong-line">
                <strong>{t('dashboard.defenseDecision')}:</strong>{' '}
                <span className="decision-highlight">
                  {evidenceSummary.security_assessment?.decision || t('status.observed')}
                </span>{' '}
                | <strong>{t('dashboard.automaticBlocking')}:</strong>{' '}
                {evidenceSummary.security_assessment?.automatic_block_allowed
                  ? t('status.online')
                  : t('dashboard.safeDryRunMode')}
              </p>
            </div>
          ) : (
            <div className="noc-empty-box">
              {language === 'vi'
                ? 'Không tải được dữ liệu đối chiếu bằng chứng từ Backend API.'
                : 'Evidence correlation data could not be loaded from Backend API.'}
            </div>
          )}

          {/* SIEM Multi-Source Integration Matrix */}
          {siemScope && Array.isArray(siemScope.sources) ? (
            <div className="evidence-detail-card blue-accent">
              <h4 className="evidence-card-heading">{t('dashboard.siemMatrixTitle')}</h4>
              <div className="siem-matrix-grid">
                {siemScope.sources.map((item) => {
                  const isVerified = item.integration_status === 'VERIFIED_INTEGRATION';
                  return (
                    <div key={item.source_system} className="siem-source-card">
                      <div className="siem-source-title">{item.source_system}</div>
                      <span
                        className={`siem-source-badge ${
                          isVerified ? 'verified' : 'simulated'
                        }`}
                      >
                        {isVerified
                          ? language === 'vi'
                            ? 'TÍCH HỢP ĐÃ XÁC MINH'
                            : 'VERIFIED INTEGRATION'
                          : language === 'vi'
                            ? 'DỮ LIỆU MÔ PHỎNG LAB'
                            : 'FIXTURE SIMULATION'}
                      </span>
                      <div className="siem-source-desc">{item.description}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <div className="noc-empty-box">
              {language === 'vi'
                ? 'Không tải được ma trận nguồn SIEM từ Backend API.'
                : 'SIEM source integration matrix could not be loaded from Backend API.'}
            </div>
          )}
        </div>
      </CollapsibleSection>

      {/* =========================================================
         SECTION 8: SERVICE ACCESS DIRECTORY & NETWORK GATEWAYS (COLLAPSIBLE)
         Default: Collapsed | Unified toggle button & real X/Y counter
         ========================================================= */}
      <CollapsibleSection
        id="service-directory"
        title={t('dashboard.serviceAccessTitle')}
        subtitle={t('dashboard.serviceAccessSubtitle')}
        expandLabel={t('dashboard.viewServiceDetails')}
        collapseLabel={t('dashboard.collapseServiceDetails')}
        expandAriaLabel={t('dashboard.showServiceAria')}
        collapseAriaLabel={t('dashboard.collapseServiceAria')}
        defaultExpanded={false}
        summaryPills={
          <>
            <span className="summary-pill">
              {t('dashboard.activeServicesSummary')}:{' '}
              <strong>
                {onlineServicesCount}/{totalServicesCount}
              </strong>
            </span>
            {isOnosOffline && (
              <span className="summary-pill alert-pill">
                {language === 'vi' ? 'ONOS: Mất kết nối' : 'ONOS: OFFLINE'}
              </span>
            )}
          </>
        }
      >
        {/* Detailed System Health Grid (All 6 Services) */}
        <div className="bottom-system-health">
          <div className="bottom-health-title">{t('dashboard.systemHealth')}</div>
          <div className="service-status-grid">
            {/* 1. Backend API */}
            <div className="service-status-card">
              <span className={`status-indicator state-${serviceStates.backend.toLowerCase()}`} />
              <div>
                <div className="service-name">Backend API</div>
                <div className="status-text">
                  {formatServiceStateLabel(serviceStates.backend)} (Port 5000)
                </div>
              </div>
            </div>

            {/* 2. ONOS Controller */}
            <div className="service-status-card">
              <span className={`status-indicator state-${serviceStates.onos.toLowerCase()}`} />
              <div>
                <div className="service-name">ONOS SDN</div>
                <div className="status-text">
                  {serviceStates.onos === 'ONLINE'
                    ? `${t('status.online')} (Port 8181)`
                    : formatServiceStateLabel(serviceStates.onos, 'onos')}
                </div>
              </div>
            </div>

            {/* 3. Elasticsearch */}
            <div className="service-status-card">
              <span className={`status-indicator state-${serviceStates.elasticsearch.toLowerCase()}`} />
              <div>
                <div className="service-name">Elasticsearch</div>
                <div className="status-text">
                  {serviceStates.elasticsearch === 'ONLINE'
                    ? `${t('status.online')} (Port 9200)`
                    : formatServiceStateLabel(serviceStates.elasticsearch)}
                </div>
              </div>
            </div>

            {/* 4. Logstash Pipeline */}
            <div className="service-status-card">
              <span className={`status-indicator state-${serviceStates.logstash.toLowerCase()}`} />
              <div>
                <div className="service-name">Logstash Pipeline</div>
                <div className="status-text">
                  {serviceStates.logstash === 'ONLINE'
                    ? logstashPipelineStats
                      ? `${logstashPipelineStats.documents_indexed} indexed (18080)`
                      : `${t('dashboard.ingestionActive')} (18080)`
                    : formatServiceStateLabel(serviceStates.logstash)}
                </div>
              </div>
            </div>

            {/* 5. Kibana Console */}
            <div className="service-status-card">
              <span className={`status-indicator state-${serviceStates.kibana.toLowerCase()}`} />
              <div>
                <div className="service-name">Kibana Console</div>
                <div className="status-text">
                  {serviceStates.kibana === 'ONLINE'
                    ? `${t('status.ready')} (Port 5601)`
                    : formatServiceStateLabel(serviceStates.kibana)}
                </div>
              </div>
            </div>

            {/* 6. OpenFlow 1.3 Channel */}
            <div className="service-status-card">
              <span className={`status-indicator state-${serviceStates.openflow.toLowerCase()}`} />
              <div>
                <div className="service-name">OpenFlow 1.3</div>
                <div className="status-text">
                  {serviceStates.openflow === 'ONLINE'
                    ? `${t('dashboard.openflowActive')} (6653)`
                    : formatServiceStateLabel(serviceStates.openflow)}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 6 Service Access Gateway Cards */}
        <div className="service-access-grid">
          {/* 1. ONOS Controller */}
          <div className="service-access-card">
            <div className="service-card-body">
              <div className="service-card-top">
                <span className="service-card-title">{t('dashboard.onosTitle')}</span>
                <span className="service-protocol-badge">OpenFlow 1.3 / REST</span>
              </div>
              <p className="service-card-desc">{t('dashboard.onosDesc')}</p>
              <div
                className={`service-card-notice ${
                  serviceStates.onos === 'OFFLINE' ? 'notice-danger' : ''
                }`}
              >
                {serviceStates.onos === 'OFFLINE'
                  ? language === 'vi'
                    ? 'Chẩn đoán: ONOS Controller đang mất kết nối (Port 8181/6653). Kiểm tra container sdnflowguard-onos hoặc trạng thái Atomix/Raft.'
                    : 'Diagnostic: ONOS Controller is unreachable (Port 8181/6653). Inspect container sdnflowguard-onos or Atomix/Raft status.'
                  : t('dashboard.onosNotice')}
              </div>
            </div>
            <div className="service-card-action">
              <span className={`service-status-pill state-${serviceStates.onos.toLowerCase()}`}>
                {serviceStates.onos === 'ONLINE'
                  ? t('status.online')
                  : formatServiceStateLabel(serviceStates.onos, 'onos')}
              </span>
              <a
                href="http://127.0.0.1:8181/onos/ui"
                target="_blank"
                rel="noopener noreferrer"
                className={`service-link-btn ${serviceStates.onos === 'OFFLINE' ? 'muted' : ''}`}
                title={language === 'vi' ? 'Mở giao diện điều khiển ONOS SDN' : 'Open ONOS SDN Controller Web UI'}
              >
                {t('dashboard.onosDashboard')} &rarr;
              </a>
            </div>
          </div>

          {/* 2. Elasticsearch */}
          <div className="service-access-card">
            <div className="service-card-body">
              <div className="service-card-top">
                <span className="service-card-title">{t('dashboard.esTitle')}</span>
                <span className="service-protocol-badge">HTTP JSON 9200</span>
              </div>
              <p className="service-card-desc">{t('dashboard.esDesc')}</p>
              <div
                className={`service-card-notice ${
                  serviceStates.elasticsearch === 'OFFLINE' ? 'notice-danger' : ''
                }`}
              >
                {serviceStates.elasticsearch === 'OFFLINE'
                  ? language === 'vi'
                    ? 'Chẩn đoán: Elasticsearch không phản hồi trên cổng 9200. Cảnh báo ELK và lịch sử lưu lượng sẽ không khả dụng.'
                    : 'Diagnostic: Elasticsearch is unreachable on port 9200. Security alerts and traffic history are unavailable.'
                  : t('dashboard.esNotice')}
              </div>
            </div>
            <div className="service-card-action">
              <span
                className={`service-status-pill state-${serviceStates.elasticsearch.toLowerCase()}`}
              >
                {serviceStates.elasticsearch === 'ONLINE'
                  ? t('status.online')
                  : formatServiceStateLabel(serviceStates.elasticsearch)}
              </span>
              <a
                href="http://127.0.0.1:9200"
                target="_blank"
                rel="noopener noreferrer"
                className={`service-link-btn ${
                  serviceStates.elasticsearch === 'OFFLINE' ? 'muted' : ''
                }`}
                title={language === 'vi' ? 'Xem trạng thái cụm Elasticsearch REST JSON' : 'View Elasticsearch Cluster REST JSON'}
              >
                {t('dashboard.clusterStatus')} &rarr;
              </a>
            </div>
          </div>

          {/* 3. Kibana */}
          <div className="service-access-card">
            <div className="service-card-body">
              <div className="service-card-top">
                <span className="service-card-title">{t('dashboard.kibanaTitle')}</span>
                <span className="service-protocol-badge">HTTP Web 5601</span>
              </div>
              <p className="service-card-desc">{t('dashboard.kibanaDesc')}</p>
              <div
                className={`service-card-notice ${
                  serviceStates.kibana === 'OFFLINE' ? 'notice-danger' : ''
                }`}
              >
                {serviceStates.kibana === 'OFFLINE'
                  ? language === 'vi'
                    ? 'Chẩn đoán: Kibana không phản hồi trên cổng 5601 (hoặc đang tắt theo chế độ -SkipKibana).'
                    : 'Diagnostic: Kibana is unreachable on port 5601 (or disabled via -SkipKibana).'
                  : t('dashboard.kibanaNotice')}
              </div>
            </div>
            <div className="service-card-action">
              <span className={`service-status-pill state-${serviceStates.kibana.toLowerCase()}`}>
                {serviceStates.kibana === 'ONLINE'
                  ? t('status.ready')
                  : formatServiceStateLabel(serviceStates.kibana)}
              </span>
              <a
                href="http://127.0.0.1:5601"
                target="_blank"
                rel="noopener noreferrer"
                className={`service-link-btn ${serviceStates.kibana === 'OFFLINE' ? 'muted' : ''}`}
                title={language === 'vi' ? 'Mở bàn điều khiển phân tích Kibana' : 'Open Kibana Analytics Console'}
              >
                {t('dashboard.kibanaConsole')} &rarr;
              </a>
            </div>
          </div>

          {/* 4. Logstash */}
          <div className="service-access-card">
            <div className="service-card-body">
              <div className="service-card-top">
                <span className="service-card-title">{t('dashboard.logstashTitle')}</span>
                <span className="service-protocol-badge">TCP 18080 (In: 8080)</span>
              </div>
              <p className="service-card-desc">{t('dashboard.logstashDesc')}</p>
              {serviceStates.logstash === 'ONLINE' && logstashPipelineStats ? (
                <div className="service-card-notice notice-ok">
                  <div className="notice-ok-title">
                    {logstashPipelineStats.documents_indexed > 0
                      ? language === 'vi'
                        ? 'Pipeline đang hoạt động'
                        : 'Pipeline Active'
                      : language === 'vi'
                        ? 'Pipeline sẵn sàng (0 sự kiện mới trong phiên)'
                        : 'Pipeline Ready (0 new events in session)'}
                  </div>
                  <div className="notice-ok-sub">
                    {language === 'vi'
                      ? `Nhận: ${logstashPipelineStats.events_received} | Lập chỉ mục ES: ${logstashPipelineStats.documents_indexed} | Nghẽn: ${logstashPipelineStats.queue_backpressure}%`
                      : `In: ${logstashPipelineStats.events_received} | ES Indexed: ${logstashPipelineStats.documents_indexed} | Backpressure: ${logstashPipelineStats.queue_backpressure}%`}
                  </div>
                </div>
              ) : (
                <div
                  className={`service-card-notice ${
                    serviceStates.logstash === 'OFFLINE' ? 'notice-danger' : ''
                  }`}
                >
                  {serviceStates.logstash === 'OFFLINE'
                    ? language === 'vi'
                      ? 'Chẩn đoán: Logstash hiện mất kết nối trên cổng 18080.'
                      : 'Diagnostic: Logstash receiver is unreachable on port 18080.'
                    : t('dashboard.logstashNotice')}
                </div>
              )}
            </div>
            <div className="service-card-action">
              <span className={`service-status-pill state-${serviceStates.logstash.toLowerCase()}`}>
                {serviceStates.logstash === 'ONLINE'
                  ? t('dashboard.ingestionActive')
                  : formatServiceStateLabel(serviceStates.logstash)}
              </span>
              <a
                href={`${API_BASE_URL}/api/logstash/pipeline-status`}
                target="_blank"
                rel="noopener noreferrer"
                className="service-link-btn secondary"
                title={language === 'vi' ? 'Xem số liệu JSON từ Logstash Monitoring API' : 'View JSON metrics from Logstash Monitoring API'}
              >
                {language === 'vi' ? 'Trạng thái Pipeline' : 'Pipeline Status'} &rarr;
              </a>
            </div>
          </div>

          {/* 5. SDNFlowGuard Backend API */}
          <div className="service-access-card">
            <div className="service-card-body">
              <div className="service-card-top">
                <span className="service-card-title">SDNFlowGuard Backend API</span>
                <span className="service-protocol-badge">HTTP REST 5000</span>
              </div>
              <p className="service-card-desc">{t('dashboard.backendDesc')}</p>
              <div
                className={`service-card-notice ${
                  serviceStates.backend === 'OFFLINE' ? 'notice-danger' : ''
                }`}
              >
                {serviceStates.backend === 'OFFLINE'
                  ? language === 'vi'
                    ? 'Chẩn đoán: Không thể kết nối Backend Flask API tại cổng 5000.'
                    : 'Diagnostic: Unable to reach Backend Flask API on port 5000.'
                  : language === 'vi'
                    ? 'Tài liệu REST API tại /docs; kiểm tra sức khỏe JSON tại /api/health.'
                    : 'REST API reference at /docs; JSON health endpoint at /api/health.'}
              </div>
            </div>
            <div className="service-card-action">
              <span className={`service-status-pill state-${serviceStates.backend.toLowerCase()}`}>
                {formatServiceStateLabel(serviceStates.backend)}
              </span>
              <a
                href="http://127.0.0.1:5000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="service-link-btn"
                title={language === 'vi' ? 'Mở tài liệu đặc tả REST API' : 'Open REST API Specification Docs'}
              >
                {t('dashboard.openApiDocs')} &rarr;
              </a>
            </div>
          </div>

          {/* 6. SDNFlowGuard Web Console */}
          <div className="service-access-card">
            <div className="service-card-body">
              <div className="service-card-top">
                <span className="service-card-title">SDNFlowGuard Web Console</span>
                <span className="service-protocol-badge">HTTP React 3000</span>
              </div>
              <p className="service-card-desc">{t('dashboard.frontendDesc')}</p>
              <div className="service-card-notice">
                {language === 'vi'
                  ? 'Giao diện điều hành chính tích hợp giám sát mạng, cảnh báo SIEM và phòng thủ SDN.'
                  : 'Primary operations console unifying SDN telemetry, SIEM alerts, and controlled defense.'}
              </div>
            </div>
            <div className="service-card-action">
              <span className="service-status-pill state-info">
                {t('dashboard.activeConsole')}
              </span>
              <span className="console-endpoint-tag">localhost:3000</span>
            </div>
          </div>
        </div>
      </CollapsibleSection>
    </div>
  );
}

export default Dashboard;
