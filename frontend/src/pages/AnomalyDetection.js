import React, { useState, useEffect, useMemo, useCallback } from 'react';
import axios from 'axios';
import {
  API_BASE_URL,
  getApiHeaders,
  isValidIpAddress,
} from '../config/apiConfig';
import { useLanguage } from '../i18n/LanguageContext';
import './AnomalyDetection.css';

function AnomalyDetection() {
  const { language, t } = useLanguage();
  const [anomalies, setAnomalies] = useState([]);
  const [evidenceData, setEvidenceData] = useState(null);
  const [policyReport, setPolicyReport] = useState(null);
  const [showBlockModal, setShowBlockModal] = useState(false);
  const [blockIp, setBlockIp] = useState('');
  const [showHoneypotModal, setShowHoneypotModal] = useState(false);
  const [redirectIp, setRedirectIp] = useState('');
  const [showIgnoreModal, setShowIgnoreModal] = useState(false);
  const [ignoreIp, setIgnoreIp] = useState('');
  const [flowDetails, setFlowDetails] = useState([]);
  const [selectedIp, setSelectedIp] = useState('');
  const [showFlowModal, setShowFlowModal] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [selectedAnomaly, setSelectedAnomaly] = useState(null);
  const [customActionIp, setCustomActionIp] = useState('');
  const [lastRefreshed, setLastRefreshed] = useState('');

  const loadData = useCallback(() => {
    axios
      .get(`${API_BASE_URL}/api/get-anomalies`, { timeout: 4500 })
      .then((response) => {
        const data = response.data?.data || [];
        setAnomalies(data);
        setSelectedAnomaly((prev) => {
          if (!prev && data.length > 0) {
            setCustomActionIp(data[0].source_ip);
            return data[0];
          }
          return prev;
        });
      })
      .catch(() => setAnomalies([]));

    axios
      .get(`${API_BASE_URL}/api/defense/evidence-correlation`, { timeout: 4500 })
      .then((response) => setEvidenceData(response.data?.data || null))
      .catch(() => setEvidenceData(null));

    axios
      .get(`${API_BASE_URL}/api/defense/evaluate`, { timeout: 4500 })
      .then((response) => setPolicyReport(response.data?.data || null))
      .catch(() => setPolicyReport(null));

    setLastRefreshed(new Date().toLocaleTimeString(language === 'vi' ? 'vi-VN' : 'en-US'));
  }, [language]);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, [loadData]);

  const effectiveActionIp = useMemo(() => {
    return (customActionIp || selectedAnomaly?.source_ip || '').trim();
  }, [customActionIp, selectedAnomaly]);

  const handleSelectAnomaly = (anomaly) => {
    setSelectedAnomaly(anomaly);
    setCustomActionIp(anomaly.source_ip || '');
    setStatusMessage('');
  };

  const handleIgnoreSubmit = () => {
    const ipToIgnore = (ignoreIp || effectiveActionIp).trim();
    if (!isValidIpAddress(ipToIgnore)) {
      setStatusMessage(
        language === 'vi'
          ? 'Lỗi xác thực: Vui lòng nhập địa chỉ IP hợp lệ.'
          : 'Validation Error: Please enter a valid IP address.'
      );
      return;
    }
    axios
      .post(
        `${API_BASE_URL}/api/ignore`,
        { srcIp: ipToIgnore },
        { headers: getApiHeaders() }
      )
      .then((response) => {
        setStatusMessage(response.data?.message || (language === 'vi' ? 'Đã bỏ qua sự kiện an ninh thành công.' : 'Event ignored successfully.'));
        setShowIgnoreModal(false);
        setIgnoreIp('');
        return axios.get(`${API_BASE_URL}/api/get-anomalies`);
      })
      .then((response) => setAnomalies(response.data?.data || []))
      .catch((error) => {
        setStatusMessage(
          error.response?.data?.error || (language === 'vi' ? 'Không thể bỏ qua sự kiện' : 'Failed to ignore event')
        );
      });
  };

  const handleBlockIpSubmit = () => {
    const ipToBlock = (blockIp || effectiveActionIp).trim();
    if (!isValidIpAddress(ipToBlock)) {
      setStatusMessage(
        language === 'vi'
          ? 'Lỗi xác thực: Vui lòng nhập địa chỉ IP hợp lệ.'
          : 'Validation Error: Please enter a valid IP address.'
      );
      return;
    }
    axios
      .post(
        `${API_BASE_URL}/api/block`,
        { srcIp: ipToBlock },
        { headers: getApiHeaders() }
      )
      .then((response) => {
        setStatusMessage(response.data?.message || (language === 'vi' ? 'Chính sách đã được thẩm định qua Safety Gate (DRY_RUN).' : 'Policy evaluated via Safety Gate (DRY_RUN).'));
        setShowBlockModal(false);
        setBlockIp('');
      })
      .catch((error) => {
        setStatusMessage(
          error.response?.data?.error || (language === 'vi' ? 'Yêu cầu bị từ chối bởi Safety Gate' : 'Action rejected by Safety Gate')
        );
      });
  };

  const handleRedirectToHoneypot = () => {
    const ipToRedirect = (redirectIp || effectiveActionIp).trim();
    if (!isValidIpAddress(ipToRedirect)) {
      setStatusMessage(
        language === 'vi'
          ? 'Lỗi xác thực: Vui lòng nhập địa chỉ IP hợp lệ.'
          : 'Validation Error: Please enter a valid IP address.'
      );
      return;
    }
    axios
      .post(
        `${API_BASE_URL}/api/redirectHoney`,
        { srcIp: ipToRedirect },
        { headers: getApiHeaders() }
      )
      .then((response) => {
        setStatusMessage(response.data?.message || (language === 'vi' ? 'Đã lập lịch chuyển hướng Honeypot qua Safety Gate.' : 'Honeypot redirection scheduled via Safety Gate.'));
        setShowHoneypotModal(false);
        setRedirectIp('');
      })
      .catch((error) => {
        setStatusMessage(
          error.response?.data?.error || (language === 'vi' ? 'Không thể chuyển hướng đến Honeypot' : 'Failed to redirect to honeypot')
        );
      });
  };

  const fetchFlowDetails = (ip) => {
    axios
      .post(
        `${API_BASE_URL}/api/get-documents-by-ip`,
        { ip_address: ip },
        { headers: getApiHeaders() }
      )
      .then((response) => {
        const rawData = response.data?.data || {};
        const consolidatedDetails = [];

        for (const [indexName, logs] of Object.entries(rawData)) {
          if (!Array.isArray(logs)) continue;
          logs.forEach((log) => {
            if (
              log.client?.ip === ip ||
              log.server?.ip === ip ||
              log.host?.ip?.includes(ip) ||
              log.client_ip === ip
            ) {
              let detail = {
                timestamp: log['@timestamp'] || '-',
                source_ip: ip,
                log_type: indexName,
                description:
                  log.event?.action ||
                  log.question_name ||
                  log.message ||
                  (language === 'vi' ? 'Không có mô tả' : 'No description'),
                destination_ip: log.destination?.ip || 'N/A',
                protocol: log.network?.transport || log.protocol || 'N/A',
                bytes: log.network?.bytes || 'N/A',
                packets: log.network?.packets || 'N/A',
              };
              consolidatedDetails.push(detail);
            }
          });
        }

        setFlowDetails(consolidatedDetails);
        setSelectedIp(ip);
        setShowFlowModal(true);
      })
      .catch(() => {
        setStatusMessage(
          language === 'vi'
            ? `Truy vấn Elasticsearch không khả dụng cho IP ${ip} (kiểm tra trạng thái cụm ELK).`
            : `Elasticsearch query unavailable for IP ${ip} (check ELK service status).`
        );
      });
  };

  return (
    <div className="anomaly-detection">
      <div className="anomaly-page-container">
        {/* SECTION 1: Page Header */}
        <div className="anomaly-header">
          <div className="anomaly-header-left">
            <h2 className="anomaly-title">
              {t('anomalyDetection.title')}
            </h2>
            <p className="anomaly-subtitle">
              {language === 'vi'
                ? 'Quy trình đối soát an ninh: Quan sát lưu lượng → Bằng chứng gói tin → Đối chiếu định danh Host → Quyết định chính sách'
                : 'Forensic workflow: Traffic Observation → Packet Evidence → Host Identity Correlation → Policy Decision'}
            </p>
          </div>
          <div className="anomaly-header-badges">
            <span className="telemetry-badge telemetry-online">
              <span className="pulsing-dot" />
              {language === 'vi' ? 'Giám sát: TRỰC TUYẾN' : 'Detection: ONLINE'}
            </span>
            <span className="telemetry-badge">
              📡 {language === 'vi' ? 'Nguồn: ONOS + SIEM + SQLite' : 'Source: ONOS + SIEM + SQLite'}
            </span>
            <span className="telemetry-badge telemetry-defense">
              🛡️ {t('header.defenseMode')}: {policyReport?.defense_mode || 'DRY_RUN'}
            </span>
            {lastRefreshed && (
              <span className="telemetry-badge telemetry-muted">
                ⏱️ {lastRefreshed}
              </span>
            )}
          </div>
        </div>

        {/* Global Notification Banner */}
        {statusMessage && (
          <div className="status-notification-banner" role="alert">
            <span className="notification-icon">ℹ️</span>
            <span className="notification-text">{statusMessage}</span>
          </div>
        )}

        {/* SECTION 2: Packet Evidence & ONOS Host Topology Correlation */}
        {evidenceData && (
          <div className="anomaly-card packet-evidence-card">
            <div className="card-header-bar">
              <div className="card-title-group">
                <h3 className="card-title">
                  {t('anomalyDetection.packetEvidenceTitle')}
                </h3>
                <span className="card-badge-count">
                  {evidenceData.total_packets || 0} {t('anomalyDetection.tableHeaders.packets')}
                </span>
              </div>
              <span
                className="evidence-step-tag"
                title={evidenceData.evidence_type || 'host_correlated_packet_observation'}
              >
                {language === 'vi'
                  ? 'Đối soát gói tin & Định danh ONOS Host'
                  : 'ONOS Host Correlated Packet Observation'}
              </span>
            </div>

            {/* Structured Evidence Metadata Grid */}
            <div className="evidence-metadata-grid">
              <div className="metadata-item">
                <span className="metadata-label">{t('dashboard.evidenceArtifact')}:</span>
                <span className="metadata-value font-mono">
                  {evidenceData.evidence_source_file || 'ingress_icmp_20261101_014645.json'}
                </span>
              </div>
              <div className="metadata-item">
                <span className="metadata-label">{t('anomalyDetection.captureClockQuality')}:</span>
                <span className="metadata-value">
                  {t('anomalyDetection.localClockNote')}
                </span>
              </div>
              <div className="metadata-item">
                <span className="metadata-label">{t('dashboard.historicalUtcCorrelation')}:</span>
                <span className="metadata-badge badge-warning">
                  {evidenceData.time_verification?.historical_alert_correlation_verified
                    ? 'VERIFIED'
                    : t('anomalyDetection.utcCorrelationUnverified')}
                </span>
              </div>
              <div className="metadata-item">
                <span className="metadata-label">{language === 'vi' ? 'Khoảng thời gian thu nhận' : 'Capture Window'}:</span>
                <span className="metadata-value font-mono">
                  {evidenceData.first_packet_clock || '18:46:47'} → {evidenceData.last_packet_clock || '18:46:50'}
                </span>
              </div>
            </div>

            {/* Evidence Correlation Table */}
            <div className="table-responsive-wrapper">
              <table className="noc-table">
                <thead>
                  <tr>
                    <th style={{ minWidth: '150px' }}>{t('anomalyDetection.tableHeaders.switchPort')}</th>
                    <th style={{ minWidth: '110px' }}>{t('anomalyDetection.tableHeaders.interface')}</th>
                    <th style={{ minWidth: '140px' }}>{t('anomalyDetection.tableHeaders.observedMac')}</th>
                    <th style={{ minWidth: '130px' }}>{t('anomalyDetection.tableHeaders.observedIp')}</th>
                    <th style={{ minWidth: '160px' }}>{t('anomalyDetection.tableHeaders.forensicAttribution')}</th>
                    <th className="col-num" style={{ minWidth: '120px' }}>{t('anomalyDetection.tableHeaders.packets')}</th>
                    <th style={{ minWidth: '170px' }}>{t('anomalyDetection.tableHeaders.correlationStatus')}</th>
                    <th style={{ minWidth: '120px' }}>{t('anomalyDetection.tableHeaders.policyDecision')}</th>
                  </tr>
                </thead>
                <tbody>
                  {(evidenceData.correlated_observations || []).map((item, idx) => (
                    <tr key={idx}>
                      <td>
                        <span className="device-id-chip">
                          {item.switch_id} : p{item.ingress_port}
                        </span>
                      </td>
                      <td className="font-mono">{item.interface}</td>
                      <td className="font-mono">{item.observed_source_mac}</td>
                      <td className="font-mono">
                        <span className="flow-code-chip">{item.observed_source_ip}</span>
                      </td>
                      <td>
                        <span
                          className={`attribution-badge ${
                            item.observed_source_ip === '10.0.0.1'
                              ? 'attr-suspected'
                              : 'attr-target'
                          }`}
                        >
                          {item.observed_source_ip === '10.0.0.1'
                            ? t('anomalyDetection.suspectedHost')
                            : t('anomalyDetection.echoTargetHost')}
                        </span>
                      </td>
                      <td className="col-num font-mono">
                        {item.packet_count} ({item.protocol} {item.icmp_type})
                      </td>
                      <td>
                        <span className="correlation-status-pill">
                          {item.correlation_status}
                        </span>
                      </td>
                      <td>
                        <span className={`decision-badge decision-${(item.recommended_decision || '').toLowerCase()}`}>
                          {item.recommended_decision}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* SECTION 3: Defense Policy Engine Per-Port Evaluation */}
        {policyReport && (
          <div className="anomaly-card policy-engine-card">
            <div className="card-header-bar">
              <div className="card-title-group">
                <h3 className="card-title">
                  {t('anomalyDetection.policyEvaluationTitle')}
                </h3>
                <span className="defense-mode-pill">
                  {t('header.defenseMode')}: {policyReport.defense_mode}
                </span>
              </div>
              <span className="meta-text">
                Switch: <code>{policyReport.device_id || 'of:0000000000000001'}</code>
              </span>
            </div>

            <div className="table-responsive-wrapper">
              <table className="noc-table">
                <thead>
                  <tr>
                    <th style={{ minWidth: '110px' }}>{t('anomalyDetection.tableHeaders.switchPort')}</th>
                    <th style={{ minWidth: '150px' }}>{t('anomalyDetection.tableHeaders.attachedHosts')}</th>
                    <th className="col-num" style={{ minWidth: '90px' }}>{t('anomalyDetection.tableHeaders.alerts')}</th>
                    <th className="col-num" style={{ minWidth: '100px' }}>{t('anomalyDetection.tableHeaders.testAlerts')}</th>
                    <th style={{ minWidth: '140px' }}>{t('anomalyDetection.tableHeaders.sourceAttributed')}</th>
                    <th style={{ minWidth: '110px' }}>{t('anomalyDetection.tableHeaders.policyDecision')}</th>
                    <th style={{ minWidth: '220px' }}>{t('anomalyDetection.tableHeaders.reason')}</th>
                  </tr>
                </thead>
                <tbody>
                  {(policyReport.port_decisions || []).map((p, idx) => {
                    const ips = (p.attached_hosts || [])
                      .flatMap((h) => h.ips || [])
                      .join(', ');
                    return (
                      <tr key={idx}>
                        <td>
                          <span className="port-badge">Port {p.port_number}</span>
                        </td>
                        <td>
                          {ips ? (
                            <span className="flow-code-chip">{ips}</span>
                          ) : (
                            <span className="dimmed-dash">{language === 'vi' ? 'Cổng Khám phá / Chưa gán Host' : 'Unassigned / Discovery Port'}</span>
                          )}
                        </td>
                        <td className="col-num font-mono">{p.alert_count}</td>
                        <td className="col-num font-mono">{p.test_alert_count}</td>
                        <td>
                          <span className={`source-attr-badge ${p.source_ip_attributed ? 'attr-yes' : 'attr-unverified'}`}>
                            {p.source_ip_attributed
                              ? (language === 'vi' ? 'CÓ (XÁC ĐỊNH)' : 'YES (ATTRIBUTED)')
                              : (language === 'vi' ? 'CHƯA XÁC MINH' : 'UNVERIFIED')}
                          </span>
                        </td>
                        <td>
                          <span className={`decision-badge decision-${(p.decision || '').toLowerCase()}`}>
                            {p.decision}
                          </span>
                        </td>
                        <td className="reason-cell">{p.reason}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* SECTION 4: Recent Webhook / SIEM Anomalies (SQLite Events) */}
        <div className="anomaly-card recent-anomalies-card">
          <div className="card-header-bar">
            <div className="card-title-group">
              <h3 className="card-title">
                {t('anomalyDetection.recentAnomaliesTitle')}
              </h3>
              <span className="card-badge-count">
                {anomalies.length} {t('common.records')}
              </span>
            </div>
            <span className="meta-text">
              📁 {language === 'vi' ? 'Cơ sở dữ liệu an ninh: SQLite Repository' : 'Security DB: SQLite Repository'}
            </span>
          </div>

          <div className="table-responsive-wrapper">
            <table className="noc-table">
              <thead>
                <tr>
                  <th style={{ width: '40px', textAlign: 'center' }}>✓</th>
                  <th style={{ minWidth: '150px' }}>{t('common.timestamp')}</th>
                  <th style={{ minWidth: '130px' }}>{t('trafficOverview.tableHeaders.sourceIp')}</th>
                  <th style={{ minWidth: '150px' }}>{t('anomalyDetection.tableHeaders.anomalyType')}</th>
                  <th className="col-num" style={{ minWidth: '100px' }}>{t('anomalyDetection.tableHeaders.score')}</th>
                  <th style={{ minWidth: '180px' }}>{t('common.actions')}</th>
                </tr>
              </thead>
              <tbody>
                {anomalies.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="table-empty-cell">
                      {t('common.noData')}
                    </td>
                  </tr>
                ) : (
                  anomalies.map((anomaly, index) => {
                    const isSelected = selectedAnomaly && selectedAnomaly.source_ip === anomaly.source_ip && selectedAnomaly.timestamp === anomaly.timestamp;
                    return (
                      <tr
                        key={index}
                        className={`anomaly-row ${isSelected ? 'row-selected' : ''}`}
                        onClick={() => handleSelectAnomaly(anomaly)}
                        style={{ cursor: 'pointer' }}
                      >
                        <td style={{ textAlign: 'center' }}>
                          <input
                            type="radio"
                            name="selected-anomaly"
                            checked={Boolean(isSelected)}
                            onChange={() => handleSelectAnomaly(anomaly)}
                            aria-label={`Select anomaly ${anomaly.source_ip}`}
                          />
                        </td>
                        <td className="font-mono text-muted">{anomaly.timestamp}</td>
                        <td>
                          <span className="flow-code-chip">{anomaly.source_ip}</span>
                        </td>
                        <td>
                          <span className="anomaly-type-tag">
                            {anomaly.event}
                          </span>
                        </td>
                        <td className="col-num font-mono">
                          <strong className={anomaly.score >= 70 ? 'score-high' : 'score-med'}>
                            {anomaly.score}
                          </strong>
                        </td>
                        <td>
                          <div className="action-buttons-group">
                            <button
                              type="button"
                              className="btn-action-sm btn-investigate"
                              onClick={(e) => {
                                e.stopPropagation();
                                fetchFlowDetails(anomaly.source_ip);
                              }}
                              title={t('anomalyDetection.btnInvestigate')}
                            >
                              🔍 {t('anomalyDetection.btnInvestigate')}
                            </button>
                            <button
                              type="button"
                              className={`btn-action-sm ${isSelected ? 'btn-selected' : 'btn-select'}`}
                              onClick={(e) => {
                                e.stopPropagation();
                                handleSelectAnomaly(anomaly);
                              }}
                            >
                              {isSelected ? `✓ ${t('anomalyDetection.selectedBadge')}` : t('anomalyDetection.selectRowPrompt')}
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* SECTION 5: Alert Actions & Safety Gate (Integrated Card) */}
        <div className="anomaly-card alert-actions-card">
          <div className="card-header-bar">
            <div className="card-title-group">
              <h3 className="card-title">
                {t('anomalyDetection.alertActionsTitle')}
              </h3>
              <span className="safety-gate-badge">
                🛡️ {t('anomalyDetection.safetyGateActive')}
              </span>
              <span className="defense-mode-pill">
                {t('anomalyDetection.defenseModeSimulated')}
              </span>
            </div>
            <span className="meta-text">
              {language === 'vi'
                ? 'Can thiệp OpenFlow 1.3 có kiểm soát qua Safety Gate'
                : 'Controlled OpenFlow 1.3 intervention via Safety Gate'}
            </span>
          </div>

          <p className="card-subtitle-inline" style={{ marginBottom: 16 }}>
            {language === 'vi'
              ? 'Mọi thao tác phòng thủ đều được kiểm duyệt bởi Safety Gate. Trong chế độ DRY_RUN, các quyết định sẽ được lưu vết kiểm toán và mô phỏng trên controller mà không làm gián đoạn dataplane.'
              : 'All enforcement operations are protected by Safety Gate. Under DRY_RUN mode, decisions are audited and staged on the controller without impacting dataplane stability.'}
          </p>

          {/* Action Context Preview Panel */}
          <div className="action-context-panel">
            <div className="context-item">
              <span className="context-label">{t('anomalyDetection.targetIpLabel')}:</span>
              <div className="context-input-wrapper">
                <input
                  type="text"
                  className="target-ip-input font-mono"
                  value={effectiveActionIp}
                  onChange={(e) => setCustomActionIp(e.target.value)}
                  placeholder="vd: 10.0.0.2"
                />
                {selectedAnomaly && (
                  <span className="selected-event-hint">
                    ({selectedAnomaly.event} · {t('anomalyDetection.riskScoreLabel')}: {selectedAnomaly.score})
                  </span>
                )}
              </div>
            </div>

            <div className="context-item">
              <span className="context-label">{t('anomalyDetection.actionPreview')}:</span>
              <div className="action-preview-box font-mono">
                <code>
                  {effectiveActionIp
                    ? `[SAFETY GATE STAGING] flow_rule: match={dl_type:0x800, nw_src:${effectiveActionIp}} priority=50000 mode=DRY_RUN`
                    : t('anomalyDetection.noEventSelected')}
                </code>
              </div>
            </div>
          </div>

          {/* Action Trigger Buttons */}
          <div className="action-buttons-bar">
            <button
              type="button"
              className="btn-defense btn-defense-block"
              onClick={() => {
                if (effectiveActionIp) {
                  setBlockIp(effectiveActionIp);
                }
                setShowBlockModal(true);
              }}
            >
              🛑 {t('anomalyDetection.btnBlock')}
            </button>
            <button
              type="button"
              className="btn-defense btn-defense-honeypot"
              onClick={() => {
                if (effectiveActionIp) {
                  setRedirectIp(effectiveActionIp);
                }
                setShowHoneypotModal(true);
              }}
            >
              🍯 {t('anomalyDetection.btnHoneypot')}
            </button>
            <button
              type="button"
              className="btn-defense btn-defense-ignore"
              onClick={() => {
                if (effectiveActionIp) {
                  setIgnoreIp(effectiveActionIp);
                }
                setShowIgnoreModal(true);
              }}
            >
              👁️ {t('anomalyDetection.btnIgnore')}
            </button>
          </div>
        </div>

        {/* Modal: Block IP */}
        {showBlockModal && (
          <div className="modal-backdrop" onClick={() => setShowBlockModal(false)}>
            <div className="modal-card" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>🛑 {t('anomalyDetection.modalBlockTitle')}</h3>
                <button type="button" className="modal-close-btn" onClick={() => setShowBlockModal(false)}>✕</button>
              </div>
              <div className="modal-body">
                <p className="modal-desc">
                  {language === 'vi'
                    ? 'Chính sách Block sẽ được thẩm định bởi Safety Gate. Nếu IP thuộc dải bảo vệ (Gateway/DNS), yêu cầu sẽ bị chặn ngay lập tức.'
                    : 'Block policy will be evaluated by Safety Gate. Requests targeting protected subnets (Gateway/DNS) are immediately rejected.'}
                </p>
                <label htmlFor="block-ip" className="modal-label">
                  {t('anomalyDetection.modalBlockPrompt')}
                </label>
                <input
                  type="text"
                  id="block-ip"
                  className="modal-input font-mono"
                  value={blockIp}
                  onChange={(e) => setBlockIp(e.target.value)}
                  placeholder="vd: 10.0.0.2"
                  autoFocus
                />
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn-defense btn-defense-block"
                  onClick={handleBlockIpSubmit}
                >
                  {t('common.submit')}
                </button>
                <button
                  type="button"
                  className="btn-modal-cancel"
                  onClick={() => setShowBlockModal(false)}
                >
                  {t('common.cancel')}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Modal: Ignore Event */}
        {showIgnoreModal && (
          <div className="modal-backdrop" onClick={() => setShowIgnoreModal(false)}>
            <div className="modal-card" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>👁️ {t('anomalyDetection.modalIgnoreTitle')}</h3>
                <button type="button" className="modal-close-btn" onClick={() => setShowIgnoreModal(false)}>✕</button>
              </div>
              <div className="modal-body">
                <p className="modal-desc">
                  {language === 'vi'
                    ? 'Đánh dấu bỏ qua sự kiện trong cơ sở dữ liệu SQLite, giúp ngăn tích lũy điểm rủi ro cho địa chỉ IP này.'
                    : 'Marks event as ignored in SQLite database, preventing excessive risk score accumulation for this host.'}
                </p>
                <label htmlFor="ignore-ip" className="modal-label">
                  {t('anomalyDetection.modalIgnorePrompt')}
                </label>
                <input
                  type="text"
                  id="ignore-ip"
                  className="modal-input font-mono"
                  value={ignoreIp}
                  onChange={(e) => setIgnoreIp(e.target.value)}
                  placeholder="vd: 10.0.0.2"
                  autoFocus
                />
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn-defense btn-defense-ignore"
                  onClick={handleIgnoreSubmit}
                >
                  {t('common.submit')}
                </button>
                <button
                  type="button"
                  className="btn-modal-cancel"
                  onClick={() => setShowIgnoreModal(false)}
                >
                  {t('common.cancel')}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Modal: Honeypot Redirect */}
        {showHoneypotModal && (
          <div className="modal-backdrop" onClick={() => setShowHoneypotModal(false)}>
            <div className="modal-card" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>🍯 {t('anomalyDetection.modalHoneypotTitle')}</h3>
                <button type="button" className="modal-close-btn" onClick={() => setShowHoneypotModal(false)}>✕</button>
              </div>
              <div className="modal-body">
                <p className="modal-desc">
                  {language === 'vi'
                    ? 'Lập lịch chuyển hướng lưu lượng nghi vấn sang máy chủ bẫy (Honeypot h6: 10.0.0.6) để phân tích hành vi độc hại.'
                    : 'Schedules redirection of suspicious traffic to Honeypot decoy host (h6: 10.0.0.6) for deep telemetry capture.'}
                </p>
                <label htmlFor="redirect-ip" className="modal-label">
                  {t('anomalyDetection.modalHoneypotPrompt')}
                </label>
                <input
                  type="text"
                  id="redirect-ip"
                  className="modal-input font-mono"
                  value={redirectIp}
                  onChange={(e) => setRedirectIp(e.target.value)}
                  placeholder="vd: 10.0.0.2"
                  autoFocus
                />
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn-defense btn-defense-honeypot"
                  onClick={handleRedirectToHoneypot}
                >
                  {t('common.submit')}
                </button>
                <button
                  type="button"
                  className="btn-modal-cancel"
                  onClick={() => setShowHoneypotModal(false)}
                >
                  {t('common.cancel')}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Modal: ELK Flow Details */}
        {showFlowModal && (
          <div className="modal-backdrop" onClick={() => setShowFlowModal(false)}>
            <div className="modal-card modal-lg" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>🔍 {t('anomalyDetection.flowDetailsTitle', { ip: selectedIp })}</h3>
                <button type="button" className="modal-close-btn" onClick={() => setShowFlowModal(false)}>✕</button>
              </div>
              <div className="modal-body">
                <div className="table-responsive-wrapper" style={{ maxHeight: '420px', overflowY: 'auto' }}>
                  <table className="noc-table">
                    <thead>
                      <tr>
                        <th style={{ minWidth: '150px' }}>{t('common.timestamp')}</th>
                        <th style={{ minWidth: '120px' }}>{t('trafficOverview.tableHeaders.sourceIp')}</th>
                        <th style={{ minWidth: '120px' }}>Index / Type</th>
                        <th style={{ minWidth: '180px' }}>{t('common.details')}</th>
                        <th style={{ minWidth: '120px' }}>{t('trafficOverview.tableHeaders.destinationIp')}</th>
                        <th style={{ minWidth: '90px' }}>{t('trafficOverview.tableHeaders.protocol')}</th>
                        <th className="col-num" style={{ minWidth: '90px' }}>Bytes</th>
                        <th className="col-num" style={{ minWidth: '90px' }}>Packets</th>
                      </tr>
                    </thead>
                    <tbody>
                      {flowDetails.length > 0 ? (
                        flowDetails.map((detail, index) => (
                          <tr key={index}>
                            <td className="font-mono text-muted">{detail.timestamp}</td>
                            <td><span className="flow-code-chip">{detail.source_ip}</span></td>
                            <td><span className="device-id-chip">{detail.log_type}</span></td>
                            <td style={{ fontSize: 12.5 }}>{detail.description}</td>
                            <td><code>{detail.destination_ip}</code></td>
                            <td><span className="proto-tag">{detail.protocol}</span></td>
                            <td className="col-num font-mono">{detail.bytes}</td>
                            <td className="col-num font-mono">{detail.packets}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan="8" className="table-empty-cell">
                            {t('anomalyDetection.noFlowDetails')}
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn-modal-cancel"
                  onClick={() => setShowFlowModal(false)}
                >
                  {t('common.close')}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AnomalyDetection;
