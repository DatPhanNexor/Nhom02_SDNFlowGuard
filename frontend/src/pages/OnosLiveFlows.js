import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useLanguage } from '../i18n/LanguageContext';

const API_URL = (
  process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000/api'
).replace(/\/$/, '');

function OnosLiveFlows() {
  const { language, t } = useLanguage();
  const [flows, setFlows] = useState([]);
  const [status, setStatus] = useState('loading'); // 'loading' | 'online' | 'error'
  const [updatedAt, setUpdatedAt] = useState('');
  const [expandedFlowId, setExpandedFlowId] = useState(null);
  const [showRawJson, setShowRawJson] = useState({});

  useEffect(() => {
    let mounted = true;

    const loadFlows = async () => {
      try {
        const response = await axios.get(
          `${API_URL}/live-flows`,
          { timeout: 5000 }
        );

        if (!mounted) return;

        setFlows(
          Array.isArray(response.data?.data)
            ? response.data.data
            : []
        );

        setStatus('online');
        setUpdatedAt(new Date().toLocaleTimeString(language === 'vi' ? 'vi-VN' : 'en-US'));
      } catch (error) {
        if (!mounted) return;

        console.error('ONOS live flows fetch error:', error);
        setStatus('error');
        setFlows([]);
      }
    };

    loadFlows();

    const interval = setInterval(loadFlows, 5000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [language]);

  const toggleRowExpansion = (flowKey) => {
    setExpandedFlowId((prev) => (prev === flowKey ? null : flowKey));
  };

  const toggleRawJson = (flowKey, e) => {
    e.stopPropagation();
    setShowRawJson((prev) => ({
      ...prev,
      [flowKey]: !prev[flowKey],
    }));
  };

  return (
    <div className="traffic-card live-flows-card">
      {/* Professional Card Header */}
      <div className="card-header-bar">
        <div className="card-title-group">
          <h3 className="card-title">
            {t('trafficOverview.liveFlowsTitle')}
          </h3>
          <span className={`status-pill ${status === 'online' ? 'status-online' : status === 'loading' ? 'status-loading' : 'status-offline'}`}>
            <span className="pulsing-dot" />
            {status === 'online'
              ? t('dashboard.onosConnected')
              : status === 'loading'
                ? t('common.loadingData')
                : t('dashboard.onosUnavailable')}
          </span>
          <span className="card-badge-count">
            {flows.length} {t('common.records')}
          </span>
        </div>

        <div className="card-meta-group">
          {updatedAt && (
            <span className="meta-timestamp">
              ⏱️ {t('trafficOverview.lastUpdated')} {updatedAt}
            </span>
          )}
          <span className="auto-refresh-pill">
            🔄 {t('trafficOverview.autoRefresh')}
          </span>
        </div>
      </div>

      {/* Responsive Flow Table Container */}
      <div className="table-responsive-wrapper">
        <table className="noc-flow-table">
          <thead>
            <tr>
              <th style={{ minWidth: '130px' }}>{t('trafficOverview.tableHeaders.deviceId')}</th>
              <th style={{ minWidth: '130px' }}>{t('trafficOverview.tableHeaders.sourceIp')}</th>
              <th style={{ minWidth: '130px' }}>{t('trafficOverview.tableHeaders.destinationIp')}</th>
              <th style={{ minWidth: '180px' }}>{t('trafficOverview.tableHeaders.matchCriteria')}</th>
              <th className="col-num" style={{ minWidth: '75px' }}>{t('trafficOverview.tableHeaders.priority')}</th>
              <th style={{ minWidth: '75px' }}>{t('trafficOverview.tableHeaders.tableId')}</th>
              <th style={{ minWidth: '120px' }}>{t('trafficOverview.tableHeaders.appId')}</th>
              <th style={{ minWidth: '85px' }}>{t('trafficOverview.tableHeaders.state')}</th>
              <th className="col-num" style={{ minWidth: '90px' }}>{t('trafficOverview.tableHeaders.packets')}</th>
              <th className="col-num" style={{ minWidth: '100px' }}>{t('trafficOverview.tableHeaders.bytes')}</th>
              <th className="col-num" style={{ minWidth: '105px' }}>{t('trafficOverview.tableHeaders.lifetime') || (language === 'vi' ? 'Thời gian sống (s)' : 'Lifetime (s)')}</th>
              <th style={{ minWidth: '120px' }}>{t('trafficOverview.tableHeaders.output')}</th>
              <th style={{ minWidth: '70px', textAlign: 'center' }}>{t('trafficOverview.tableHeaders.details')}</th>
            </tr>
          </thead>

          <tbody>
            {flows.length === 0 ? (
              <tr>
                <td colSpan={13} className="table-empty-cell">
                  {status === 'error'
                    ? (language === 'vi' ? 'Không thể kết nối đến ONOS REST API.' : 'Cannot connect to the ONOS API.')
                    : status === 'loading'
                      ? (language === 'vi' ? 'Đang tải dữ liệu luồng ONOS...' : 'Loading ONOS flow rules...')
                      : t('trafficOverview.noLiveFlows')}
                </td>
              </tr>
            ) : (
              flows.map((flow) => {
                const isAcl = flow.app_id?.toLowerCase().includes('acl');
                const isAdded = flow.state === 'ADDED';
                const outputPorts = Array.isArray(flow.output_ports)
                  ? flow.output_ports
                  : (flow.output_ports ? [flow.output_ports] : []);
                const flowKey = `${flow.device_id}-${flow.id}`;
                const isExpanded = expandedFlowId === flowKey;
                const showRaw = !!showRawJson[flowKey];

                return (
                  <React.Fragment key={flowKey}>
                    <tr
                      className={`flow-data-row ${isExpanded ? 'flow-row-expanded' : ''}`}
                      onClick={() => toggleRowExpansion(flowKey)}
                      style={{ cursor: 'pointer' }}
                    >
                      {/* Device ID */}
                      <td>
                        <span className="device-id-chip" title={flow.device_id}>
                          {flow.device_id || '—'}
                        </span>
                      </td>

                      {/* Source IP (Strict L3 Matching - never converted from MAC) */}
                      <td>
                        {flow.source_ip ? (
                          <span className="flow-code-chip flow-ip-chip" title={`Source IP Match: ${flow.source_ip}`}>
                            {flow.source_ip}
                          </span>
                        ) : (
                          <span className="dimmed-na" title={t('trafficOverview.noIpTooltip')}>
                            N/A
                          </span>
                        )}
                      </td>

                      {/* Destination IP (Strict L3 Matching - never converted from MAC) */}
                      <td>
                        {flow.destination_ip ? (
                          <span className="flow-code-chip flow-ip-chip" title={`Destination IP Match: ${flow.destination_ip}`}>
                            {flow.destination_ip}
                          </span>
                        ) : (
                          <span className="dimmed-na" title={t('trafficOverview.noIpTooltip')}>
                            N/A
                          </span>
                        )}
                      </td>

                      {/* Match Criteria Summary */}
                      <td>
                        <span
                          className={`criteria-summary-chip ${flow.is_table_miss ? 'criteria-table-miss' : ''}`}
                          title={flow.match_criteria || 'WILDCARD'}
                        >
                          {flow.match_criteria || (language === 'vi' ? 'WILDCARD (Tất cả)' : 'WILDCARD (Match All)')}
                        </span>
                      </td>

                      {/* Priority */}
                      <td className="col-num font-mono">
                        <span className="priority-tag">{flow.priority}</span>
                      </td>

                      {/* Table ID */}
                      <td>
                        <span className="table-id-tag">
                          {`T${flow.table_id ?? 0}`}
                        </span>
                      </td>

                      {/* App ID */}
                      <td>
                        <span className={`app-id-tag ${isAcl ? 'app-id-acl' : 'app-id-normal'}`}>
                          {flow.app_id || '—'}
                        </span>
                      </td>

                      {/* State */}
                      <td>
                        <span className={`state-badge ${isAdded ? 'state-added' : 'state-pending'}`}>
                          {flow.state || '—'}
                        </span>
                      </td>

                      {/* Packets */}
                      <td className="col-num font-mono">
                        {Number(flow.packets ?? 0).toLocaleString()}
                      </td>

                      {/* Bytes */}
                      <td className="col-num font-mono">
                        {Number(flow.bytes ?? 0).toLocaleString()}
                      </td>

                      {/* Lifetime */}
                      <td className="col-num font-mono">
                        {flow.life_seconds ?? 0}s
                      </td>

                      {/* Output Port / Action */}
                      <td>
                        {outputPorts.length > 0 ? (
                          <div className="output-ports-group">
                            {outputPorts.map((port, pIdx) => (
                              <span
                                key={pIdx}
                                className={`port-chip ${port === 'CONTROLLER' ? 'port-controller' : 'port-normal'}`}
                              >
                                {port}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <span className="port-chip port-drop">DROP</span>
                        )}
                      </td>

                      {/* Details Toggle Button */}
                      <td style={{ textAlign: 'center' }}>
                        <button
                          type="button"
                          className="details-toggle-btn"
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleRowExpansion(flowKey);
                          }}
                          title={isExpanded ? t('trafficOverview.collapseDetails') : t('trafficOverview.expandDetails')}
                        >
                          {isExpanded ? '▲' : '▼'}
                        </button>
                      </td>
                    </tr>

                    {/* Expandable Flow Rule Details Sub-Card */}
                    {isExpanded && (
                      <tr className="flow-detail-expansion-row">
                        <td colSpan={13}>
                          <div className="flow-detail-card">
                            <div className="flow-detail-grid">
                              {/* Pane 1: Selector Criteria Breakdown */}
                              <div className="flow-detail-pane">
                                <div className="flow-detail-pane-title">
                                  <span>🎯</span>
                                  <span>{language === 'vi' ? 'Tiêu chí đối sánh (OpenFlow Match)' : 'Match Criteria Breakdown'}</span>
                                </div>
                                <div className="flow-detail-item">
                                  <span className="flow-detail-label">EtherType:</span>
                                  <span className="flow-detail-val">{flow.eth_type || (language === 'vi' ? 'Không chỉ định (Wildcard)' : 'Unspecified (Wildcard)')}</span>
                                </div>
                                <div className="flow-detail-item">
                                  <span className="flow-detail-label">{language === 'vi' ? 'Địa chỉ IP nguồn (L3):' : 'Source IP (L3):'}</span>
                                  <span className="flow-detail-val">{flow.source_ip || (language === 'vi' ? 'N/A (Không lọc theo IP)' : 'N/A (No L3 IP filter)')}</span>
                                </div>
                                <div className="flow-detail-item">
                                  <span className="flow-detail-label">{language === 'vi' ? 'Địa chỉ IP đích (L3):' : 'Destination IP (L3):'}</span>
                                  <span className="flow-detail-val">{flow.destination_ip || (language === 'vi' ? 'N/A (Không lọc theo IP)' : 'N/A (No L3 IP filter)')}</span>
                                </div>
                                <div className="flow-detail-item">
                                  <span className="flow-detail-label">{language === 'vi' ? 'Địa chỉ MAC nguồn (L2):' : 'Source MAC (L2):'}</span>
                                  <span className="flow-detail-val">{flow.source_mac || (language === 'vi' ? 'Bất kỳ (Wildcard)' : 'Any (Wildcard)')}</span>
                                </div>
                                <div className="flow-detail-item">
                                  <span className="flow-detail-label">{language === 'vi' ? 'Địa chỉ MAC đích (L2):' : 'Destination MAC (L2):'}</span>
                                  <span className="flow-detail-val">{flow.destination_mac || (language === 'vi' ? 'Bất kỳ (Wildcard)' : 'Any (Wildcard)')}</span>
                                </div>
                                <div className="flow-detail-item">
                                  <span className="flow-detail-label">{language === 'vi' ? 'Cổng đầu vào (In Port):' : 'Ingress Port:'}</span>
                                  <span className="flow-detail-val">{flow.in_port !== undefined && flow.in_port !== null ? `Port ${flow.in_port}` : (language === 'vi' ? 'Bất kỳ cổng nào' : 'Any Port')}</span>
                                </div>
                              </div>

                              {/* Pane 2: OpenFlow Treatment & Actions */}
                              <div className="flow-detail-pane">
                                <div className="flow-detail-pane-title">
                                  <span>⚡</span>
                                  <span>{language === 'vi' ? 'Hành động xử lý (OpenFlow Treatment)' : 'Treatment & Instructions'}</span>
                                </div>
                                <div className="flow-detail-item">
                                  <span className="flow-detail-label">{language === 'vi' ? 'Tóm tắt hành động:' : 'Action Summary:'}</span>
                                  <span className="flow-detail-val">{flow.treatment_summary || 'OUTPUT'}</span>
                                </div>
                                <div className="flow-detail-item">
                                  <span className="flow-detail-label">{language === 'vi' ? 'Cổng xuất đích:' : 'Target Ports:'}</span>
                                  <span className="flow-detail-val">{outputPorts.length > 0 ? outputPorts.join(', ') : 'DROP'}</span>
                                </div>
                                <div className="flow-detail-item">
                                  <span className="flow-detail-label">{language === 'vi' ? 'Loại chuyển tiếp:' : 'Forwarding Mode:'}</span>
                                  <span className="flow-detail-val">
                                    {outputPorts.includes('CONTROLLER')
                                      ? (language === 'vi' ? 'Punt về ONOS Controller' : 'Punt to ONOS Controller')
                                      : outputPorts.length > 0
                                        ? (language === 'vi' ? 'Chuyển tiếp cổng phần cứng' : 'Hardware Port Forwarding')
                                        : (language === 'vi' ? 'Hủy gói (Drop Packet)' : 'Drop Packet')}
                                  </span>
                                </div>
                              </div>

                              {/* Pane 3: Flow Identifiers & Lifecycle */}
                              <div className="flow-detail-pane">
                                <div className="flow-detail-pane-title">
                                  <span>📋</span>
                                  <span>{language === 'vi' ? 'Định danh & Vòng đời luồng' : 'Flow Identifiers & Lifecycle'}</span>
                                </div>
                                <div className="flow-detail-item">
                                  <span className="flow-detail-label">Flow ID:</span>
                                  <span className="flow-detail-val font-mono" style={{ fontSize: '11px' }}>{flow.id}</span>
                                </div>
                                <div className="flow-detail-item">
                                  <span className="flow-detail-label">Switch DPID:</span>
                                  <span className="flow-detail-val font-mono" style={{ fontSize: '11px' }}>{flow.device_id}</span>
                                </div>
                                <div className="flow-detail-item">
                                  <span className="flow-detail-label">Table ID:</span>
                                  <span className="flow-detail-val">{flow.table_id ?? 0}</span>
                                </div>
                                <div className="flow-detail-item">
                                  <span className="flow-detail-label">{language === 'vi' ? 'Độ ưu tiên (Priority):' : 'Priority:'}</span>
                                  <span className="flow-detail-val">{flow.priority}</span>
                                </div>
                                <div className="flow-detail-item">
                                  <span className="flow-detail-label">{language === 'vi' ? 'Thời gian sống:' : 'Lifetime:'}</span>
                                  <span className="flow-detail-val">{flow.life_seconds ?? 0} giây</span>
                                </div>
                              </div>
                            </div>

                            {/* Raw Criteria JSON Toggle */}
                            <div className="flow-raw-json-section">
                              <button
                                type="button"
                                className="raw-json-toggle-btn"
                                onClick={(e) => toggleRawJson(flowKey, e)}
                              >
                                {showRaw ? '▾ ' : '▸ '}
                                {t('trafficOverview.rawCriteria')}
                              </button>
                              {showRaw && (
                                <pre className="raw-criteria-json">
                                  {JSON.stringify(flow.criteria_raw || [], null, 2)}
                                </pre>
                              )}
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Explanatory Footnote Notice */}
      <div className="card-footer-note">
        <span className="info-icon">ℹ️</span>
        <span>{t('trafficOverview.liveFlowsNotice')}</span>
      </div>
    </div>
  );
}

export default OnosLiveFlows;
