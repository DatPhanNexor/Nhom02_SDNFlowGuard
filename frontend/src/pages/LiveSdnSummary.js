import React, { useEffect, useState } from 'react';
import axios from 'axios';
import SdnPortRates from './SdnPortRates';
import { useLanguage } from '../i18n/LanguageContext';

const API = (
  process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000/api'
).replace(/\/$/, '');

function LiveSdnSummary() {
  const { language, t } = useLanguage();
  const [status, setStatus] = useState('loading');
  const [updated, setUpdated] = useState('');
  const [stats, setStats] = useState({
    switches: 0,
    hosts: 0,
    flows: 0,
    packets: 0,
    bytes: 0
  });

  useEffect(() => {
    let mounted = true;

    async function load() {
      try {
        const [topologyRes, flowsRes] = await Promise.all([
          axios.get(`${API}/topology`, { timeout: 4500 }),
          axios.get(`${API}/live-flows`, { timeout: 4500 })
        ]);

        if (!mounted) return;

        const topology = topologyRes.data || {};
        const devices = Array.isArray(topology.devices)
          ? topology.devices : [];
        const hosts = Array.isArray(topology.hosts)
          ? topology.hosts : [];
        const flows = Array.isArray(flowsRes.data.data)
          ? flowsRes.data.data : [];

        setStats({
          switches: devices.filter(
            d => d.type === 'SWITCH' && d.available === true
          ).length,
          hosts: hosts.length,
          flows: flows.length,
          packets: flows.reduce(
            (sum, f) => sum + Number(f.packets || 0), 0
          ),
          bytes: flows.reduce(
            (sum, f) => sum + Number(f.bytes || 0), 0
          )
        });

        setStatus('online');
        setUpdated(new Date().toLocaleTimeString(language === 'vi' ? 'vi-VN' : 'en-US'));

      } catch (error) {
        if (!mounted) return;

        console.error('Live SDN Dashboard:', error);
        setStatus('error');
      }
    }

    load();
    const timer = setInterval(load, 5000);

    return () => {
      mounted = false;
      clearInterval(timer);
    };
  }, [language]);

  const metrics = [
    { label: t('dashboard.switchesOnline'), value: stats.switches },
    { label: t('dashboard.detectedHosts'), value: stats.hosts },
    { label: t('dashboard.activeFlowRules'), value: stats.flows },
    { label: t('dashboard.flowPackets'), value: stats.packets },
    { label: t('dashboard.flowBytes'), value: stats.bytes }
  ];

  return (
    <section style={{
      background: '#ffffff',
      border: '1px solid #dce3ed',
      borderRadius: 10,
      padding: 20,
      marginBottom: 22,
      boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
    }}>
      <h3 style={{ marginTop: 0, color: '#0f172a', fontSize: '1.15rem', fontWeight: 700 }}>
        {t('dashboard.liveSdnNetwork')}
      </h3>

      <p style={{ fontSize: 13, color: '#64748b', marginBottom: 16 }}>
        {status === 'online'
          ? `${t('dashboard.onosConnected')} | ${t('common.lastUpdated')}: ${updated} | ${t('common.autoRefresh', { seconds: 5 })}`
          : status === 'loading'
            ? t('common.loadingData')
            : t('dashboard.onosUnavailable')}
      </p>

      {status === 'online' && (
        <>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
            gap: 12
          }}>
            {metrics.map(item => (
              <div key={item.label} style={{
                background: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: 8,
                padding: 16,
                boxShadow: '0 1px 2px rgba(0,0,0,0.02)'
              }}>
                <div style={{
                  color: '#64748b',
                  fontSize: 12,
                  fontWeight: 600,
                  marginBottom: 8,
                  textTransform: 'uppercase',
                  letterSpacing: '0.03em'
                }}>
                  {item.label}
                </div>

                <strong style={{
                  color: '#0f172a',
                  fontSize: 26,
                  fontWeight: 700
                }}>
                  {item.value.toLocaleString(language === 'vi' ? 'vi-VN' : 'en-US')}
                </strong>
              </div>
            ))}
          </div>

          {stats.switches === 1 && stats.hosts === 0 && stats.packets === 0 && (
            <div style={{
              marginTop: 12,
              padding: '10px 14px',
              backgroundColor: '#f0fdf4',
              border: '1px solid #bbf7d0',
              borderRadius: 6,
              fontSize: 12,
              color: '#166534'
            }}>
              ℹ️ {language === 'vi'
                ? 'Ghi nhận 1 switch OpenFlow kết nối. Chưa phát hiện host hoặc chưa có lưu lượng truyền tải. Khởi chạy pingall trong Mininet để cập nhật MAC học được.'
                : '1 OpenFlow switch connected. No host activity or flow counters detected yet. Run pingall in Mininet to discover hosts and generate forwarding telemetry.'}
            </div>
          )}
        </>
      )}

      <p style={{
        color: '#94a3b8',
        fontSize: 12,
        marginTop: 14,
        marginBottom: 0
      }}>
        {t('dashboard.telemetrySourceNotice')}
      </p>
      <SdnPortRates />
    </section>
  );
}

export default LiveSdnSummary;
