import React, { useState, useEffect } from 'react';
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

  useEffect(() => {
    axios
      .get(`${API_BASE_URL}/api/get-anomalies`)
      .then((response) => setAnomalies(response.data?.data || []))
      .catch(() => setAnomalies([]));

    axios
      .get(`${API_BASE_URL}/api/defense/evidence-correlation`)
      .then((response) => setEvidenceData(response.data?.data || null))
      .catch(() => setEvidenceData(null));

    axios
      .get(`${API_BASE_URL}/api/defense/evaluate`)
      .then((response) => setPolicyReport(response.data?.data || null))
      .catch(() => setPolicyReport(null));
  }, []);

  const handleIgnoreSubmit = () => {
    if (!isValidIpAddress(ignoreIp)) {
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
        { srcIp: ignoreIp.trim() },
        { headers: getApiHeaders() }
      )
      .then((response) => {
        setStatusMessage(response.data.message);
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
    if (!isValidIpAddress(blockIp)) {
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
        { srcIp: blockIp.trim() },
        { headers: getApiHeaders() }
      )
      .then((response) => {
        setStatusMessage(response.data.message);
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
    if (!isValidIpAddress(redirectIp)) {
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
        { srcIp: redirectIp.trim() },
        { headers: getApiHeaders() }
      )
      .then((response) => {
        setStatusMessage(response.data.message);
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
      <div className="anomaly-header" style={{ marginBottom: 20 }}>
        <h2>
          {t('anomalyDetection.title')}
        </h2>
        <p className="anomaly-subtitle">
          {language === 'vi'
            ? 'Quy trình đối soát an ninh: Quan sát lưu lượng → Bằng chứng gói tin → Đối chiếu định danh Host → Quyết định chính sách'
            : 'Forensic workflow: Traffic Observation → Packet Evidence → Host Identity Correlation → Policy Decision'}
        </p>
      </div>

      {statusMessage && (
        <div
          style={{
            background: '#e0f2fe',
            color: '#0369a1',
            padding: '10px 14px',
            borderRadius: 6,
            marginBottom: 16,
            fontWeight: 600,
            border: '1px solid #bae6fd',
            fontSize: 13,
          }}
        >
          {statusMessage}
        </div>
      )}

      {/* 1. Packet Evidence & ONOS Host Topology Correlation */}
      {evidenceData && (
        <div className="anomaly-list">
          <h3>
            {t('anomalyDetection.packetEvidenceTitle')}
          </h3>
          <p>
            <strong>{t('dashboard.evidenceArtifact')}:</strong> <code>{evidenceData.evidence_source_file}</code> |{' '}
            <strong>{t('anomalyDetection.tableHeaders.packets')}:</strong> {evidenceData.total_packets} |{' '}
            <strong>{t('dashboard.historicalUtcCorrelation')}:</strong>{' '}
            {evidenceData.time_verification?.reason}
          </p>
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>{t('anomalyDetection.tableHeaders.switchPort')}</th>
                  <th>{t('anomalyDetection.tableHeaders.interface')}</th>
                  <th>{t('anomalyDetection.tableHeaders.observedMac')}</th>
                  <th>{t('anomalyDetection.tableHeaders.observedIp')}</th>
                  <th>{t('anomalyDetection.tableHeaders.forensicAttribution')}</th>
                  <th>{t('anomalyDetection.tableHeaders.packets')}</th>
                  <th>{t('anomalyDetection.tableHeaders.correlationStatus')}</th>
                  <th>{t('anomalyDetection.tableHeaders.policyDecision')}</th>
                </tr>
              </thead>
              <tbody>
                {(evidenceData.correlated_observations || []).map((item, idx) => (
                  <tr key={idx}>
                    <td>
                      <code>{item.switch_id} : port {item.ingress_port}</code>
                    </td>
                    <td><code>{item.interface}</code></td>
                    <td><code>{item.observed_source_mac}</code></td>
                    <td><code>{item.observed_source_ip}</code></td>
                    <td>
                      <span
                        style={{
                          padding: '3px 8px',
                          borderRadius: 4,
                          fontSize: 11,
                          fontWeight: 700,
                          background: item.observed_source_ip === '10.0.0.1' ? '#fef3c7' : '#f0fdf4',
                          color: item.observed_source_ip === '10.0.0.1' ? '#92400e' : '#166534',
                        }}
                      >
                        {item.observed_source_ip === '10.0.0.1'
                          ? t('anomalyDetection.suspectedHost')
                          : t('anomalyDetection.echoTargetHost')}
                      </span>
                    </td>
                    <td>
                      {item.packet_count} ({item.protocol} {item.icmp_type})
                    </td>
                    <td>
                      <strong style={{ color: '#0284c7' }}>{item.correlation_status}</strong>
                    </td>
                    <td>
                      <span style={{ fontWeight: 700, color: item.recommended_decision === 'OBSERVE' ? '#0d9488' : '#e11d48' }}>
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

      {/* 2. Defense Policy Engine Per-Port Evaluation */}
      {policyReport && (
        <div className="anomaly-list">
          <h3>
            {t('anomalyDetection.policyEvaluationTitle')} ({t('header.defenseMode')}: {policyReport.defense_mode})
          </h3>
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>{t('anomalyDetection.tableHeaders.switchPort')}</th>
                  <th>{t('anomalyDetection.tableHeaders.attachedHosts')}</th>
                  <th>{t('anomalyDetection.tableHeaders.alerts')}</th>
                  <th>{t('anomalyDetection.tableHeaders.testAlerts')}</th>
                  <th>{t('anomalyDetection.tableHeaders.sourceAttributed')}</th>
                  <th>{t('anomalyDetection.tableHeaders.policyDecision')}</th>
                  <th>{t('anomalyDetection.tableHeaders.reason')}</th>
                </tr>
              </thead>
              <tbody>
                {(policyReport.port_decisions || []).map((p, idx) => {
                  const ips = (p.attached_hosts || [])
                    .flatMap((h) => h.ips || [])
                    .join(', ');
                  return (
                    <tr key={idx}>
                      <td>Port {p.port_number}</td>
                      <td><code>{ips || (language === 'vi' ? 'Cổng Khám phá / Chưa gán Host' : 'Unassigned / Discovery Port')}</code></td>
                      <td>{p.alert_count}</td>
                      <td>{p.test_alert_count}</td>
                      <td>
                        <span style={{
                          padding: '2px 6px',
                          borderRadius: 4,
                          fontSize: 11,
                          fontWeight: 600,
                          background: p.source_ip_attributed ? '#dcfce7' : '#f1f5f9',
                          color: p.source_ip_attributed ? '#166534' : '#64748b',
                        }}>
                          {p.source_ip_attributed ? (language === 'vi' ? 'CÓ (XÁC ĐỊNH)' : 'YES (ATTRIBUTED)') : (language === 'vi' ? 'CHƯA XÁC MINH' : 'UNVERIFIED')}
                        </span>
                      </td>
                      <td>
                        <strong style={{ color: p.decision === 'OBSERVE' ? '#0d9488' : '#0284c7' }}>
                          {p.decision}
                        </strong>
                      </td>
                      <td>{p.reason}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 3. Recent Webhook / SIEM Anomalies (SQLite Events) */}
      <div className="anomaly-list">
        <h3>
          {t('anomalyDetection.recentAnomaliesTitle')}
        </h3>
        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>{t('common.timestamp')}</th>
                <th>{t('trafficOverview.tableHeaders.sourceIp')}</th>
                <th>{t('anomalyDetection.tableHeaders.anomalyType')}</th>
                <th>{t('anomalyDetection.tableHeaders.score')}</th>
                <th>{t('common.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {anomalies.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', padding: '24px', color: '#64748b' }}>
                    {t('common.noData')}
                  </td>
                </tr>
              ) : (
                anomalies.map((anomaly, index) => (
                  <tr key={index}>
                    <td style={{ fontSize: 13, whiteSpace: 'nowrap' }}>{anomaly.timestamp}</td>
                    <td><code>{anomaly.source_ip}</code></td>
                    <td>
                      <span style={{ padding: '2px 6px', borderRadius: 4, background: '#fef3c7', color: '#92400e', fontWeight: 600, fontSize: 11 }}>
                        {anomaly.event}
                      </span>
                    </td>
                    <td><strong>{anomaly.score}</strong></td>
                    <td>
                      <button
                        className="investigate-btn"
                        onClick={() => fetchFlowDetails(anomaly.source_ip)}
                      >
                        {t('anomalyDetection.btnInvestigate')}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. Alert Actions Panel */}
      <div className="alerts-panel">
        <h3>
          {t('anomalyDetection.alertActionsTitle')}
        </h3>
        <p>
          {language === 'vi'
            ? 'Mọi hành động can thiệp đều bắt buộc tuân thủ chính sách Safety Gate và cơ chế kiểm soát DRY_RUN.'
            : 'All enforcement actions strictly adhere to Safety Gate authorization and DRY_RUN staging.'}
        </p>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <button
            onClick={() => setShowBlockModal(true)}
            style={{ padding: '8px 16px', background: '#e11d48', color: '#fff', border: 'none', borderRadius: 6, fontWeight: 600, cursor: 'pointer' }}
          >
            {t('anomalyDetection.btnBlock')}
          </button>
          <button
            onClick={() => setShowHoneypotModal(true)}
            style={{ padding: '8px 16px', background: '#f59e0b', color: '#fff', border: 'none', borderRadius: 6, fontWeight: 600, cursor: 'pointer' }}
          >
            {t('anomalyDetection.btnHoneypot')}
          </button>
          <button
            onClick={() => setShowIgnoreModal(true)}
            style={{ padding: '8px 16px', background: '#64748b', color: '#fff', border: 'none', borderRadius: 6, fontWeight: 600, cursor: 'pointer' }}
          >
            {t('anomalyDetection.btnIgnore')}
          </button>
        </div>
      </div>

      {/* Block Modal */}
      {showBlockModal && (
        <div className="modal">
          <div className="modal-content">
            <h3>{t('anomalyDetection.modalBlockTitle')}</h3>
            <label htmlFor="block-ip">
              {t('anomalyDetection.modalBlockPrompt')}
            </label>
            <input
              type="text"
              id="block-ip"
              value={blockIp}
              onChange={(e) => setBlockIp(e.target.value)}
              placeholder="vd: 10.0.0.1"
            />
            <div className="modal-actions">
              <button
                onClick={handleBlockIpSubmit}
                style={{ background: '#e11d48', color: '#fff' }}
              >
                {t('common.submit')}
              </button>
              <button
                type="button"
                onClick={() => setShowBlockModal(false)}
              >
                {t('common.cancel')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Ignore Modal */}
      {showIgnoreModal && (
        <div className="modal">
          <div className="modal-content">
            <h3>{t('anomalyDetection.modalIgnoreTitle')}</h3>
            <label htmlFor="ignore-ip">
              {t('anomalyDetection.modalIgnorePrompt')}
            </label>
            <input
              type="text"
              id="ignore-ip"
              value={ignoreIp}
              onChange={(e) => setIgnoreIp(e.target.value)}
              placeholder="vd: 10.0.0.1"
            />
            <div className="modal-actions">
              <button
                onClick={handleIgnoreSubmit}
                style={{ background: '#0284c7', color: '#fff' }}
              >
                {t('common.submit')}
              </button>
              <button
                type="button"
                onClick={() => setShowIgnoreModal(false)}
              >
                {t('common.cancel')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Honeypot Modal */}
      {showHoneypotModal && (
        <div className="modal">
          <div className="modal-content">
            <h3>{t('anomalyDetection.modalHoneypotTitle')}</h3>
            <label htmlFor="redirect-ip">
              {t('anomalyDetection.modalHoneypotPrompt')}
            </label>
            <input
              type="text"
              id="redirect-ip"
              value={redirectIp}
              onChange={(e) => setRedirectIp(e.target.value)}
              placeholder="vd: 10.0.0.1"
            />
            <div className="modal-actions">
              <button
                onClick={handleRedirectToHoneypot}
                style={{ background: '#f59e0b', color: '#fff' }}
              >
                {t('common.submit')}
              </button>
              <button
                type="button"
                onClick={() => setShowHoneypotModal(false)}
              >
                {t('common.cancel')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ELK Flow Details Modal */}
      {showFlowModal && (
        <div className="modal">
          <div className="modal-content" style={{ maxWidth: '850px', width: '92vw' }}>
            <h3>
              {t('anomalyDetection.flowDetailsTitle', { ip: selectedIp })}
            </h3>
            <div className="table-container" style={{ maxHeight: '380px', overflowY: 'auto' }}>
              <table>
                <thead>
                  <tr>
                    <th>{t('common.timestamp')}</th>
                    <th>{t('trafficOverview.tableHeaders.sourceIp')}</th>
                    <th>Index / Type</th>
                    <th>{t('common.details')}</th>
                    <th>{t('trafficOverview.tableHeaders.destinationIp')}</th>
                    <th>{t('trafficOverview.tableHeaders.protocol')}</th>
                    <th>Bytes</th>
                    <th>Packets</th>
                  </tr>
                </thead>
                <tbody>
                  {flowDetails.length > 0 ? (
                    flowDetails.map((detail, index) => (
                      <tr key={index}>
                        <td style={{ fontSize: 12, whiteSpace: 'nowrap' }}>{detail.timestamp}</td>
                        <td><code>{detail.source_ip}</code></td>
                        <td><code>{detail.log_type}</code></td>
                        <td style={{ fontSize: 12 }}>{detail.description}</td>
                        <td><code>{detail.destination_ip}</code></td>
                        <td>{detail.protocol}</td>
                        <td>{detail.bytes}</td>
                        <td>{detail.packets}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="8" style={{ textAlign: 'center', padding: '24px', color: '#64748b' }}>
                        {t('anomalyDetection.noFlowDetails')}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            <div style={{ marginTop: 16, display: 'flex', justifyContent: 'flex-end' }}>
              <button
                className="investigate-btn"
                onClick={() => setShowFlowModal(false)}
              >
                {t('common.close')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AnomalyDetection;
