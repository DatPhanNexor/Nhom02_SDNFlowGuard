import React, { useState, useEffect } from 'react';
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
import SecurityAlertsTable from '../components/SecurityAlertsTable';
import ElkPortHistoryChart from '../components/ElkPortHistoryChart';
import LiveSdnSummary from './LiveSdnSummary';
import { API_BASE_URL } from '../config/apiConfig';
import { useLanguage } from '../i18n/LanguageContext';
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

function Dashboard() {
  const { language, t } = useLanguage();
  const [trafficData, setTrafficData] = useState([]);
  const [recentActions, setRecentActions] = useState([]);
  const [serviceStatus, setServiceStatus] = useState({});
  const [step64Summary, setStep64Summary] = useState(null);
  const [siemScope, setSiemScope] = useState(null);
  const [logstashPipelineStats, setLogstashPipelineStats] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    axios
      .get(`${API_BASE_URL}/api/get-flows`)
      .then((response) => setTrafficData(response.data?.data || []))
      .catch(() => setTrafficData([]));

    axios
      .get(`${API_BASE_URL}/api/get-actions`)
      .then((response) => setRecentActions(response.data?.data || []))
      .catch(() => setRecentActions([]));

    axios
      .get(`${API_BASE_URL}/api/service-status`)
      .then((response) => setServiceStatus(response.data?.data || {}))
      .catch(() => setServiceStatus({ ELK: 'DOWN', ONOS: 'DOWN' }));

    axios
      .get(`${API_BASE_URL}/api/logstash/pipeline-status`)
      .then((response) => setLogstashPipelineStats(response.data?.data || null))
      .catch(() => setLogstashPipelineStats(null));

    axios
      .get(`${API_BASE_URL}/api/defense/evidence-correlation`)
      .then((response) => setStep64Summary(response.data?.data || null))
      .catch(() => setStep64Summary(null));

    axios
      .get(`${API_BASE_URL}/api/siem/evaluate-fixtures`)
      .then((response) => setSiemScope(response.data?.data || null))
      .catch(() => setSiemScope(null));
  }, []);

  const trafficChartData = {
    labels: trafficData.map((flow, index) => `${language === 'vi' ? 'Luồng' : 'Flow'} ${index + 1}`),
    datasets: [
      {
        label: t('dashboard.transferredBytes'),
        data: trafficData.map((flow) => flow.bandwidth || 0),
        borderColor: '#0284c7',
        backgroundColor: 'rgba(2, 132, 199, 0.15)',
        tension: 0.3,
        fill: true,
      },
    ],
  };

  const actionCounts = recentActions.reduce((acc, action) => {
    const key = action.action_type || 'Unknown';
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});

  const actionsChartData = {
    labels: Object.keys(actionCounts),
    datasets: [
      {
        label: t('dashboard.actionsCount'),
        data: Object.values(actionCounts),
        backgroundColor: [
          '#0284c7',
          '#e11d48',
          '#f59e0b',
          '#10b981',
          '#8b5cf6',
        ],
      },
    ],
  };

  const renderServiceStatus = () => {
    return Object.entries(serviceStatus).map(([service, status]) => (
      <div key={service} className="service-status-card">
        <span
          className={`status-indicator ${status === 'UP' ? 'up' : 'down'}`}
        ></span>
        <p>{service}</p>
        <p className="status-text">{status === 'UP' ? t('status.up') : t('status.down')}</p>
      </div>
    ));
  };

  return (
    <div className="dashboard">
      <div style={{ marginBottom: 20 }}>
        <h2 style={{ margin: 0, color: '#0f172a', fontSize: '1.6rem', fontWeight: 700 }}>
          {t('dashboard.title')}
        </h2>
        <p style={{ margin: '4px 0 0 0', color: '#64748b', fontSize: 14 }}>
          {language === 'vi'
            ? 'Mặt phẳng điều hành an ninh và giám sát mạng SDN (ONOS, OpenFlow 1.3, ELK Stack, SQLite)'
            : 'Unified SDN network security operations and telemetry plane (ONOS, OpenFlow 1.3, ELK Stack, SQLite)'}
        </p>
      </div>

      {/* 1. Live Network Telemetry */}
      <LiveSdnSummary />
      <ElkPortHistoryChart />
      <SecurityAlertsTable />

      {/* 2. Step 64 Host Identity Corroboration */}
      {step64Summary && (
        <section
          style={{
            background: '#ffffff',
            border: '1px solid #dce3ed',
            borderLeft: '5px solid #0d9488',
            borderRadius: 10,
            padding: 20,
            marginBottom: 22,
            boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
          }}
        >
          <h3 style={{ marginTop: 0, color: '#0f172a', fontSize: '1.15rem', fontWeight: 700 }}>
            {t('dashboard.hostVerificationTitle')}
          </h3>
          <p style={{ fontSize: 13, color: '#475569', margin: '6px 0' }}>
            <strong>{t('dashboard.evidenceArtifact')}:</strong>{' '}
            <code>{step64Summary.evidence_source_file}</code> ({step64Summary.total_packets}{' '}
            {language === 'vi' ? 'gói tin ICMP bắt tại cổng ingress' : 'switch ingress ICMP packets'}) |{' '}
            <strong>{t('dashboard.sha256Hash')}:</strong>{' '}
            <code>
              {(step64Summary.evidence_source_sha256 || '').slice(0, 24)}...
            </code>
          </p>
          <p style={{ fontSize: 13, color: '#475569', margin: '6px 0' }}>
            <strong>{t('dashboard.topologyCorroboration')}:</strong>{' '}
            {step64Summary.security_assessment?.topology_corroborated
              ? t('dashboard.corroboratedObservation')
              : t('status.unverified')}{' '}
            | <strong>{t('dashboard.historicalUtcCorrelation')}:</strong>{' '}
            {step64Summary.security_assessment?.historical_alert_correlation_verified
              ? t('status.verified')
              : (language === 'vi' ? 'CHƯA XÁC MINH (Dữ liệu bắt gói thiếu nhãn múi giờ/ngày)' : 'NOT VERIFIED (Capture clock lacks date/timezone)')}
          </p>
          <p style={{ fontSize: 13, color: '#0f172a', margin: '6px 0 0 0' }}>
            <strong>{t('dashboard.defenseDecision')}:</strong>{' '}
            <span style={{ fontWeight: 700, color: '#0284c7' }}>
              {step64Summary.security_assessment?.decision}
            </span>{' '}
            | <strong>{t('dashboard.automaticBlocking')}:</strong>{' '}
            {step64Summary.security_assessment?.automatic_block_allowed
              ? t('status.online')
              : t('dashboard.safeDryRunMode')}
          </p>
        </section>
      )}

      {/* 3. SIEM Matrix */}
      {siemScope && (
        <section
          style={{
            background: '#ffffff',
            border: '1px solid #dce3ed',
            borderLeft: '5px solid #0284c7',
            borderRadius: 10,
            padding: 20,
            marginBottom: 22,
            boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
          }}
        >
          <h3 style={{ marginTop: 0, color: '#0f172a', fontSize: '1.15rem', fontWeight: 700 }}>
            {t('dashboard.siemMatrixTitle')}
          </h3>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: 12,
              marginTop: 14
            }}
          >
            {(siemScope.sources || []).map((item) => (
              <div
                key={item.source_system}
                style={{
                  background: '#f8fafc',
                  border: '1px solid #e2e8f0',
                  borderRadius: 8,
                  padding: 12,
                }}
              >
                <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 4, color: '#0f172a' }}>
                  {item.source_system}
                </div>
                <span
                  style={{
                    display: 'inline-block',
                    padding: '2px 8px',
                    borderRadius: 4,
                    fontSize: 11,
                    fontWeight: 700,
                    background:
                      item.integration_status === 'VERIFIED_INTEGRATION'
                        ? '#dcfce7'
                        : '#fef3c7',
                    color:
                      item.integration_status === 'VERIFIED_INTEGRATION'
                        ? '#166534'
                        : '#92400e',
                    marginBottom: 6,
                  }}
                >
                  {item.integration_status === 'VERIFIED_INTEGRATION'
                    ? (language === 'vi' ? 'TÍCH HỢP ĐÃ XÁC MINH' : 'VERIFIED INTEGRATION')
                    : (language === 'vi' ? 'DỮ LIỆU MÔ PHỎNG LAB' : 'FIXTURE SIMULATION')}
                </span>
                <div style={{ fontSize: 12, color: '#64748b' }}>
                  {item.description}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 4. Widgets Row */}
      <div className="dashboard-widgets">
        <div
          className="widget"
          onClick={() => navigate('/traffic-overview')}
          title={t('nav.trafficOverview')}
        >
          <h3>{t('dashboard.storedFlowTraffic')}</h3>
          {trafficData.length === 0 ? (
            <div style={{ padding: '48px 16px', textAlign: 'center', color: '#64748b' }}>
              <p style={{ margin: 0, fontWeight: 600 }}>{t('dashboard.noTrafficRecorded')}</p>
              <p style={{ fontSize: 12, margin: '6px 0 0 0' }}>{t('dashboard.connectMininetPrompt')}</p>
            </div>
          ) : (
            <Line
              data={trafficChartData}
              options={{ maintainAspectRatio: false }}
            />
          )}
        </div>
        <div
          className="widget"
          onClick={() => navigate('/decision-logs')}
          title={t('nav.decisionLogs')}
        >
          <h3>{t('dashboard.recentActions')}</h3>
          {recentActions.length === 0 ? (
            <div style={{ padding: '48px 16px', textAlign: 'center', color: '#64748b' }}>
              <p style={{ margin: 0, fontWeight: 600 }}>{t('dashboard.noActionsRecorded')}</p>
              <p style={{ fontSize: 12, margin: '6px 0 0 0' }}>{t('dashboard.actionsPrompt')}</p>
            </div>
          ) : (
            <Bar
              data={actionsChartData}
              options={{ maintainAspectRatio: false }}
            />
          )}
        </div>
      </div>

      {/* 5. Service Access & Protocol Gateways */}
      <section className="service-access-section">
        <div className="service-access-header">
          <h3>{t('dashboard.serviceAccessTitle')}</h3>
          <p>{t('dashboard.serviceAccessSubtitle')}</p>
        </div>

        <div className="service-access-grid">
          {/* ONOS Controller */}
          <div className="service-access-card">
            <div>
              <div className="service-card-top">
                <span className="service-card-title">ONOS SDN Controller</span>
                <span className="service-protocol-badge">HTTP 8181 / TCP 6653</span>
              </div>
              <p className="service-card-desc">{t('dashboard.onosGuiDesc')}</p>
              <div className="service-card-notice">{t('dashboard.onosOpenFlowNotice')}</div>
            </div>
            <div className="service-card-action">
              <span className={`service-status-pill ${serviceStatus.ONOS === 'UP' ? 'up' : 'down'}`}>
                {serviceStatus.ONOS === 'UP' ? t('status.online') : t('status.down')}
              </span>
              <a
                href="http://127.0.0.1:8181/onos/ui"
                target="_blank"
                rel="noopener noreferrer"
                className="service-link-btn"
              >
                {t('dashboard.openOnosGui')} &rarr;
              </a>
            </div>
          </div>

          {/* Kibana Dashboard */}
          <div className="service-access-card">
            <div>
              <div className="service-card-top">
                <span className="service-card-title">Kibana Telemetry & SIEM</span>
                <span className="service-protocol-badge">HTTP 5601</span>
              </div>
              <p className="service-card-desc">{t('dashboard.kibanaDesc')}</p>
              <div className="service-card-notice">
                {language === 'vi'
                  ? 'Giao diện trực quan hóa dữ liệu chỉ mục thời gian thực từ Elasticsearch.'
                  : 'Real-time telemetry and forensic index visualizer powered by Elasticsearch.'}
              </div>
            </div>
            <div className="service-card-action">
              <span className={`service-status-pill ${serviceStatus.KIBANA === 'UP' || serviceStatus.ELK === 'UP' ? 'up' : 'down'}`}>
                {serviceStatus.KIBANA === 'UP' || serviceStatus.ELK === 'UP' ? t('status.online') : t('status.down')}
              </span>
              <a
                href="http://127.0.0.1:5601"
                target="_blank"
                rel="noopener noreferrer"
                className="service-link-btn"
              >
                {t('dashboard.openKibanaDashboard')} &rarr;
              </a>
            </div>
          </div>

          {/* Elasticsearch REST */}
          <div className="service-access-card">
            <div>
              <div className="service-card-top">
                <span className="service-card-title">Elasticsearch REST Engine</span>
                <span className="service-protocol-badge">HTTP REST 9200</span>
              </div>
              <p className="service-card-desc">{t('dashboard.elasticsearchDesc')}</p>
              <div className="service-card-notice">
                {language === 'vi'
                  ? 'Chuẩn API REST trả về JSON cluster; để xem biểu đồ hãy dùng Kibana (5601).'
                  : 'REST API returning raw cluster JSON metadata; use Kibana (5601) for UI.'}
              </div>
            </div>
            <div className="service-card-action">
              <span className={`service-status-pill ${serviceStatus.ELK === 'UP' ? 'up' : 'down'}`}>
                {serviceStatus.ELK === 'UP' ? t('status.online') : t('status.down')}
              </span>
              <a
                href="http://127.0.0.1:9200"
                target="_blank"
                rel="noopener noreferrer"
                className="service-link-btn secondary"
              >
                {t('dashboard.viewElasticsearchRest')} &rarr;
              </a>
            </div>
          </div>

          {/* Logstash Pipeline */}
          <div className="service-access-card">
            <div>
              <div className="service-card-top">
                <span className="service-card-title">Logstash Telemetry Pipeline</span>
                <span className="service-protocol-badge">HTTP 18080 (In: 8080)</span>
              </div>
              <p className="service-card-desc">{t('dashboard.logstashDesc')}</p>
              {logstashPipelineStats ? (
                <div className="service-card-notice" style={{ borderLeftColor: '#10b981', background: '#f0fdf4' }}>
                  <div style={{ fontWeight: 600, color: '#166534', marginBottom: 2 }}>
                    {language === 'vi' ? 'Trạng thái Pipeline: Đang hoạt động (Xanh)' : 'Pipeline Status: Active (Green)'}
                  </div>
                  <div style={{ fontSize: 11, color: '#374151' }}>
                    {language === 'vi'
                      ? `Sự kiện nhận: ${logstashPipelineStats.events_received} | Lập chỉ mục ES: ${logstashPipelineStats.documents_indexed} | Nghẽn: ${logstashPipelineStats.queue_backpressure}%`
                      : `Events in: ${logstashPipelineStats.events_received} | Indexed to ES: ${logstashPipelineStats.documents_indexed} | Backpressure: ${logstashPipelineStats.queue_backpressure}%`}
                  </div>
                </div>
              ) : (
                <div className="service-card-notice">{t('dashboard.logstashNotice')}</div>
              )}
            </div>
            <div className="service-card-action">
              <span className={`service-status-pill ${serviceStatus.LOGSTASH === 'UP' || serviceStatus.ELK === 'UP' ? 'up' : 'down'}`}>
                {serviceStatus.LOGSTASH === 'UP' || serviceStatus.ELK === 'UP' ? t('dashboard.ingestionActive') : t('status.down')}
              </span>
              <a
                href={`${API_BASE_URL}/api/logstash/pipeline-status`}
                target="_blank"
                rel="noopener noreferrer"
                className="service-link-btn secondary"
                title={language === 'vi' ? 'Xem số liệu JSON từ Logstash Monitoring API' : 'View JSON metrics from Logstash Monitoring API'}
              >
                {language === 'vi' ? 'Xem Trạng thái Pipeline' : 'View Pipeline Status'} &rarr;
              </a>
            </div>
          </div>

          {/* Backend API */}
          <div className="service-access-card">
            <div>
              <div className="service-card-top">
                <span className="service-card-title">SDNFlowGuard Backend API</span>
                <span className="service-protocol-badge">HTTP REST 5000</span>
              </div>
              <p className="service-card-desc">{t('dashboard.backendDesc')}</p>
              <div className="service-card-notice">
                {language === 'vi'
                  ? 'Tài liệu OpenAPI độc lập tại /docs; kiểm tra nhịp tim JSON tại /api/health.'
                  : 'Standalone OpenAPI spec at /docs; JSON heartbeat at /api/health.'}
              </div>
            </div>
            <div className="service-card-action">
              <span className="service-status-pill up">
                {t('status.online')}
              </span>
              <a
                href="http://127.0.0.1:5000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="service-link-btn"
              >
                {t('dashboard.openApiDocs')} &rarr;
              </a>
            </div>
          </div>

          {/* Frontend Console */}
          <div className="service-access-card">
            <div>
              <div className="service-card-top">
                <span className="service-card-title">SDNFlowGuard Web Console</span>
                <span className="service-protocol-badge">HTTP React 3000</span>
              </div>
              <p className="service-card-desc">{t('dashboard.frontendDesc')}</p>
              <div className="service-card-notice">
                {language === 'vi'
                  ? 'Giao diện chính điều phối toàn bộ các phân hệ an ninh và thiết bị mạng.'
                  : 'Central console unifying security analytics and network devices.'}
              </div>
            </div>
            <div className="service-card-action">
              <span className="service-status-pill info">
                {t('dashboard.activeConsole')}
              </span>
              <span style={{ fontSize: 12, fontWeight: 700, color: '#0284c7' }}>
                localhost:3000
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* 6. System Health Status Bar */}
      <div className="system-health" style={{ marginTop: 20 }}>
        <h3 style={{ margin: '0 0 14px 0', fontSize: '1rem', fontWeight: 600, color: '#334155' }}>
          {t('dashboard.systemHealth')}
        </h3>
        <div className="service-status">{renderServiceStatus()}</div>
      </div>
    </div>
  );
}

export default Dashboard;
