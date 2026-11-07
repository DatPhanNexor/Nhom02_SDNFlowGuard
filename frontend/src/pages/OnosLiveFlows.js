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
          Array.isArray(response.data.data)
            ? response.data.data
            : []
        );

        setStatus('online');
        setUpdatedAt(new Date().toLocaleTimeString(language === 'vi' ? 'vi-VN' : 'en-US'));
      } catch (error) {
        if (!mounted) return;

        console.error('ONOS live flows:', error);
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
    <section className="traffic-details" style={{ marginBottom: 24 }}>
      <h3 style={{ margin: '0 0 8px 0', color: '#0f172a', fontSize: '1.15rem', fontWeight: 700 }}>
        {t('trafficOverview.liveFlowsTitle')}
      </h3>

      <p style={{ fontSize: 13, color: '#64748b', marginBottom: 14 }}>
        {status === 'online'
          ? `${t('dashboard.onosConnected')} | ${flows.length} ${t('common.records')} | ${t('common.lastUpdated')}: ${updatedAt} | ${t('common.autoRefresh', { seconds: 5 })}`
          : status === 'loading'
            ? t('common.loadingData')
            : t('dashboard.onosUnavailable')}
      </p>

      <div style={{ overflowX: 'auto' }}>
        <table>
          <thead>
            <tr>
              <th>{t('trafficOverview.tableHeaders.deviceId')}</th>
              <th>{t('trafficOverview.tableHeaders.sourceIp')}</th>
              <th>{t('trafficOverview.tableHeaders.destinationIp')}</th>
              <th>{t('trafficOverview.tableHeaders.appId')}</th>
              <th>{t('trafficOverview.tableHeaders.state')}</th>
              <th>{t('trafficOverview.tableHeaders.packets')}</th>
              <th>{t('trafficOverview.tableHeaders.bytes')}</th>
              <th>{language === 'vi' ? 'Thời gian sống (s)' : 'Lifetime (s)'}</th>
              <th>{t('trafficOverview.tableHeaders.output')}</th>
            </tr>
          </thead>

          <tbody>
            {flows.length === 0 ? (
              <tr>
                <td colSpan={9} style={{ textAlign: 'center', padding: '24px', color: '#64748b' }}>
                  {status === 'error'
                    ? (language === 'vi' ? 'Không thể kết nối đến ONOS REST API.' : 'Cannot connect to the ONOS API.')
                    : t('trafficOverview.noLiveFlows')}
                </td>
              </tr>
            ) : (
              flows.map((flow) => (
                <tr key={`${flow.device_id}-${flow.id}`}>
                  <td><code>{flow.device_id || '-'}</code></td>
                  <td><code>{flow.source_ip || flow.source_mac || '-'}</code></td>
                  <td><code>{flow.destination_ip || flow.destination_mac || '-'}</code></td>
                  <td>
                    <span style={{
                      padding: '2px 6px',
                      borderRadius: 4,
                      background: flow.app_id?.includes('acl') ? '#fee2e2' : '#f1f5f9',
                      color: flow.app_id?.includes('acl') ? '#991b1b' : '#334155',
                      fontWeight: 600,
                      fontSize: 11
                    }}>
                      {flow.app_id || '-'}
                    </span>
                  </td>
                  <td>
                    <span style={{
                      padding: '2px 6px',
                      borderRadius: 4,
                      background: flow.state === 'ADDED' ? '#dcfce7' : '#fef3c7',
                      color: flow.state === 'ADDED' ? '#166534' : '#92400e',
                      fontWeight: 600,
                      fontSize: 11
                    }}>
                      {flow.state || '-'}
                    </span>
                  </td>
                  <td>{Number(flow.packets ?? 0).toLocaleString()}</td>
                  <td>{Number(flow.bytes ?? 0).toLocaleString()}</td>
                  <td>{flow.life_seconds ?? 0}s</td>
                  <td><code>{(flow.output_ports || []).join(', ') || '-'}</code></td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <p style={{ fontSize: 12, color: '#94a3b8', marginTop: 12, marginBottom: 0 }}>
        {t('trafficOverview.liveFlowsNotice')}
      </p>
    </section>
  );
}

export default OnosLiveFlows;
