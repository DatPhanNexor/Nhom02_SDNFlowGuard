import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useLanguage } from '../i18n/LanguageContext';

const API_URL = (
  process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000/api'
).replace(/\/$/, '');

function OnosLiveFlows() {
  const { language, t } = useLanguage();
  const [flows, setFlows] = useState([]);
  const [status, setStatus] = useState('loading');
  const [updatedAt, setUpdatedAt] = useState('');

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
              <th style={{ minWidth: '140px' }}>{t('trafficOverview.tableHeaders.sourceIp')}</th>
              <th style={{ minWidth: '140px' }}>{t('trafficOverview.tableHeaders.destinationIp')}</th>
              <th style={{ minWidth: '120px' }}>{t('trafficOverview.tableHeaders.appId')}</th>
              <th style={{ minWidth: '85px' }}>{t('trafficOverview.tableHeaders.state')}</th>
              <th className="col-num" style={{ minWidth: '95px' }}>{t('trafficOverview.tableHeaders.packets')}</th>
              <th className="col-num" style={{ minWidth: '105px' }}>{t('trafficOverview.tableHeaders.bytes')}</th>
              <th className="col-num" style={{ minWidth: '110px' }}>{language === 'vi' ? 'Thời gian sống (s)' : 'Lifetime (s)'}</th>
              <th style={{ minWidth: '120px' }}>{t('trafficOverview.tableHeaders.output')}</th>
            </tr>
          </thead>

          <tbody>
            {flows.length === 0 ? (
              <tr>
                <td colSpan={9} className="table-empty-cell">
                  {status === 'error'
                    ? (language === 'vi' ? 'Không thể kết nối đến ONOS REST API.' : 'Cannot connect to the ONOS API.')
                    : t('trafficOverview.noLiveFlows')}
                </td>
              </tr>
            ) : (
              flows.map((flow) => {
                const isAcl = flow.app_id?.toLowerCase().includes('acl');
                const isAdded = flow.state === 'ADDED';
                const srcIp = flow.source_ip || flow.source_mac;
                const dstIp = flow.destination_ip || flow.destination_mac;
                const outputPorts = Array.isArray(flow.output_ports) ? flow.output_ports : [];

                return (
                  <tr key={`${flow.device_id}-${flow.id}`}>
                    <td>
                      <span className="device-id-chip" title={flow.device_id}>
                        {flow.device_id || '—'}
                      </span>
                    </td>
                    <td>
                      {srcIp ? (
                        <span className="flow-code-chip">{srcIp}</span>
                      ) : (
                        <span className="dimmed-dash">—</span>
                      )}
                    </td>
                    <td>
                      {dstIp ? (
                        <span className="flow-code-chip">{dstIp}</span>
                      ) : (
                        <span className="dimmed-dash">—</span>
                      )}
                    </td>
                    <td>
                      <span className={`app-id-tag ${isAcl ? 'app-id-acl' : 'app-id-normal'}`}>
                        {flow.app_id || '—'}
                      </span>
                    </td>
                    <td>
                      <span className={`state-badge ${isAdded ? 'state-added' : 'state-pending'}`}>
                        {flow.state || '—'}
                      </span>
                    </td>
                    <td className="col-num font-mono">
                      {Number(flow.packets ?? 0).toLocaleString()}
                    </td>
                    <td className="col-num font-mono">
                      {Number(flow.bytes ?? 0).toLocaleString()}
                    </td>
                    <td className="col-num font-mono">
                      {flow.life_seconds ?? 0}s
                    </td>
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
                        <span className="dimmed-dash">—</span>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Footnote Notice */}
      <div className="card-footer-note">
        <span className="info-icon">ℹ️</span>
        <span>{t('trafficOverview.liveFlowsNotice')}</span>
      </div>
    </div>
  );
}

export default OnosLiveFlows;
