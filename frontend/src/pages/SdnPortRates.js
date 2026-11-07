import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { useLanguage } from '../i18n/LanguageContext';

const API = (
  process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000/api'
).replace(/\/$/, '');

function SdnPortRates() {
  const { language, t } = useLanguage();
  const previous = useRef(null);

  const [rate, setRate] = useState({
    rx: null,
    tx: null,
    status: 'loading',
    updated: ''
  });

  useEffect(() => {
    let mounted = true;
    let busy = false;

    const load = async () => {
      if (busy) return;
      busy = true;

      try {
        const response = await axios.get(
          `${API}/live-port-stats`,
          { timeout: 4500 }
        );

        if (!mounted) return;

        const data = response.data;

        if (
          data.source !== 'ONOS' ||
          !Array.isArray(data.devices) ||
          !Number.isFinite(Number(data.sample_time))
        ) {
          throw new Error('Invalid ONOS statistics');
        }

        const current = {
          time: Number(data.sample_time),
          ports: {}
        };

        data.devices.forEach(device => {
          (device.ports || []).forEach(port => {
            const key = `${device.device_id}:${port.port}`;
            const rx = Number(port.rx_bytes);
            const tx = Number(port.tx_bytes);

            if (Number.isFinite(rx) && Number.isFinite(tx)) {
              current.ports[key] = { rx, tx };
            }
          });
        });

        const old = previous.current;
        const seconds = old ? current.time - old.time : 0;

        let rxBytes = 0;
        let txBytes = 0;
        let validPorts = 0;

        if (old && seconds > 0 && seconds < 60) {
          Object.keys(current.ports).forEach(key => {
            const before = old.ports[key];
            const after = current.ports[key];

            if (!before) return;

            // Skip ports whose counters were reset.
            if (after.rx < before.rx || after.tx < before.tx) {
              return;
            }

            rxBytes += after.rx - before.rx;
            txBytes += after.tx - before.tx;
            validPorts++;
          });
        }

        previous.current = current;

        setRate({
          rx: validPorts > 0
            ? (rxBytes * 8) / (seconds * 1000000)
            : null,
          tx: validPorts > 0
            ? (txBytes * 8) / (seconds * 1000000)
            : null,
          status: 'online',
          updated: new Date().toLocaleTimeString(language === 'vi' ? 'vi-VN' : 'en-US')
        });

      } catch (error) {
        if (mounted) {
          console.error('ONOS port statistics:', error);
          previous.current = null;

          setRate({
            rx: null,
            tx: null,
            status: 'error',
            updated: ''
          });
        }
      } finally {
        busy = false;
      }
    };

    load();
    const timer = setInterval(load, 5000);

    return () => {
      mounted = false;
      clearInterval(timer);
    };
  }, [language]);

  const formatMbps = value => {
    if (value === null) return '--';
    return `${value.toFixed(4)} Mbps`;
  };

  const metrics = [
    { label: t('dashboard.portRxTraffic'), value: rate.rx },
    { label: t('dashboard.portTxTraffic'), value: rate.tx }
  ];

  return (
    <div style={{
      marginTop: 20,
      paddingTop: 18,
      borderTop: '1px solid #e2e8f0'
    }}>
      <h4 style={{ color: '#0f172a', fontSize: '1rem', fontWeight: 700, marginBottom: 8 }}>
        {t('dashboard.portThroughput')}
      </h4>

      <p style={{ color: '#64748b', fontSize: 13, marginBottom: 14 }}>
        {rate.status === 'error'
          ? (language === 'vi' ? 'Không thể đọc thống kê cổng từ ONOS' : 'ONOS port statistics unavailable')
          : rate.rx === null
            ? t('dashboard.collectingMbps')
            : `${t('dashboard.onosConnected')} | ${t('common.lastUpdated')}: ${rate.updated} | ${t('common.autoRefresh', { seconds: 5 })}`}
      </p>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: 12
      }}>
        {metrics.map(metric => (
          <div key={metric.label} style={{
            background: '#f8fafc',
            border: '1px solid #e2e8f0',
            borderRadius: 8,
            padding: 16
          }}>
            <div style={{
              fontSize: 12,
              fontWeight: 600,
              color: '#64748b',
              marginBottom: 8,
              textTransform: 'uppercase',
              letterSpacing: '0.03em'
            }}>
              {metric.label}
            </div>

            <strong style={{ color: '#0f172a', fontSize: 24, fontWeight: 700 }}>
              {formatMbps(metric.value)}
            </strong>
          </div>
        ))}
      </div>

      <p style={{
        color: '#94a3b8',
        fontSize: 12,
        marginTop: 12,
        marginBottom: 0
      }}>
        {t('dashboard.rateSourceNotice')}
      </p>
    </div>
  );
}

export default SdnPortRates;
