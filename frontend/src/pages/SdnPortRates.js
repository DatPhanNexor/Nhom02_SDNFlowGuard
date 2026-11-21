import React, { useEffect, useRef, useState, useCallback } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config/apiConfig';
import { useLanguage } from '../i18n/LanguageContext';

function SdnPortRates({ refreshTrigger }) {
  const { language, t } = useLanguage();
  const previous = useRef(null);
  const isMountedRef = useRef(true);
  const isFetchingRef = useRef(false);

  const [rate, setRate] = useState({
    rx: null,
    tx: null,
    status: 'loading', // 'no_devices' | 'sampling' | 'active' | 'error' | 'loading'
    updated: '',
    activeSwitches: null,
    activePorts: null,
    totalPackets: null,
  });
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadPortStats = useCallback(async (isManual = false) => {
    if (isFetchingRef.current) return;
    isFetchingRef.current = true;
    if (isManual) setIsRefreshing(true);

    try {
      const response = await axios.get(`${API_BASE_URL}/api/live-port-stats`, { timeout: 4500 });

      if (!isMountedRef.current) return;

      const data = response.data;
      if (
        data.source !== 'ONOS' ||
        !Array.isArray(data.devices) ||
        !Number.isFinite(Number(data.sample_time))
      ) {
        throw new Error('Invalid ONOS statistics payload');
      }

      const activeSwitches = data.devices.length;
      let totalPackets = 0;
      let activePorts = 0;

      if (activeSwitches === 0) {
        previous.current = null;
        setRate({
          rx: null,
          tx: null,
          status: 'no_devices',
          updated: new Date().toLocaleTimeString(language === 'vi' ? 'vi-VN' : 'en-US', { hour12: false }),
          activeSwitches: 0,
          activePorts: 0,
          totalPackets: 0,
        });
        return;
      }

      let totalRxBytes = 0;
      let totalTxBytes = 0;

      for (const dev of data.devices) {
        const ports = Array.isArray(dev.ports) ? dev.ports : [];
        for (const port of ports) {
          totalRxBytes += Number(port.rx_bytes ?? port.bytesReceived ?? 0);
          totalTxBytes += Number(port.tx_bytes ?? port.bytesSent ?? 0);
          totalPackets +=
            Number(port.rx_packets ?? port.packetsReceived ?? 0) +
            Number(port.tx_packets ?? port.packetsSent ?? 0);
          activePorts++;
        }
      }

      const current = {
        time: Number(data.sample_time),
        rx: totalRxBytes,
        tx: totalTxBytes,
      };

      if (previous.current && current.time > previous.current.time) {
        const deltaSeconds = current.time - previous.current.time;
        const deltaRxBytes = Math.max(0, current.rx - previous.current.rx);
        const deltaTxBytes = Math.max(0, current.tx - previous.current.tx);

        const calculatedRx = Number(((deltaRxBytes * 8) / (deltaSeconds * 1000000)).toFixed(4));
        const calculatedTx = Number(((deltaTxBytes * 8) / (deltaSeconds * 1000000)).toFixed(4));

        previous.current = current;

        setRate({
          rx: calculatedRx,
          tx: calculatedTx,
          status: 'active',
          updated: new Date().toLocaleTimeString(language === 'vi' ? 'vi-VN' : 'en-US', { hour12: false }),
          activeSwitches,
          activePorts,
          totalPackets,
        });
      } else {
        previous.current = current;
        setRate({
          rx: null,
          tx: null,
          status: 'sampling',
          updated: new Date().toLocaleTimeString(language === 'vi' ? 'vi-VN' : 'en-US', { hour12: false }),
          activeSwitches,
          activePorts,
          totalPackets,
        });
      }
    } catch (error) {
      if (isMountedRef.current) {
        console.error('ONOS port statistics error:', error);
        previous.current = null;
        setRate({
          rx: null,
          tx: null,
          status: 'error',
          updated: '',
          activeSwitches: null,
          activePorts: null,
          totalPackets: null,
        });
      }
    } finally {
      isFetchingRef.current = false;
      if (isMountedRef.current) {
        setIsRefreshing(false);
      }
    }
  }, [language]);

  useEffect(() => {
    isMountedRef.current = true;
    loadPortStats();

    const timer = setInterval(() => {
      if (document.visibilityState === 'visible') {
        loadPortStats();
      }
    }, 5000);

    return () => {
      isMountedRef.current = false;
      clearInterval(timer);
    };
  }, [loadPortStats, refreshTrigger]);

  const formatRateDisplay = (val) => {
    if (rate.status !== 'active' || val === null || !Number.isFinite(val)) {
      return '--';
    }
    return `${val.toFixed(4)} Mbps`;
  };

  const getRateSubtext = () => {
    switch (rate.status) {
      case 'active':
        return language === 'vi' ? 'Đo trực tiếp từ ONOS REST API' : 'Live sample from ONOS REST API';
      case 'sampling':
        return language === 'vi' ? 'Đang chờ mẫu kế tiếp (5s)' : 'Awaiting next sample (5s)';
      case 'no_devices':
        return language === 'vi' ? 'Chưa có switch kết nối' : 'No switches connected';
      case 'error':
        return language === 'vi' ? 'Không đo được (ONOS mất kết nối)' : 'Unavailable (ONOS offline)';
      case 'loading':
      default:
        return t('status.checking');
    }
  };

  const getStatusSubtitle = () => {
    switch (rate.status) {
      case 'active':
        return language === 'vi'
          ? 'Tốc độ tức thời tính từ biến thiên bộ đếm cổng ONOS (chu kỳ 5 giây).'
          : 'Instantaneous rate computed from consecutive ONOS port counters (5s interval).';
      case 'sampling':
        return language === 'vi'
          ? 'Đã thu mẫu đầu tiên; đang chờ mẫu thứ hai sau 5 giây để tính Mbps thực tế.'
          : 'Initial counter sample captured; awaiting second sample in 5s to compute Mbps.';
      case 'no_devices':
        return language === 'vi'
          ? 'Chưa có switch kết nối vào ONOS Controller. Khởi chạy Mininet để bắt đầu đo lưu lượng.'
          : 'No switches connected to ONOS Controller. Start Mininet to begin port telemetry.';
      case 'error':
        return language === 'vi'
          ? 'ONOS REST API (Port 8181) hiện mất kết nối — không thể đo thông lượng thời gian thực.'
          : 'ONOS REST API (Port 8181) is unreachable — real-time port throughput cannot be measured.';
      case 'loading':
      default:
        return language === 'vi'
          ? 'Đang kiểm tra kết nối bộ đếm cổng OpenFlow...'
          : 'Checking OpenFlow port counters...';
    }
  };

  const getStatusBadge = () => {
    switch (rate.status) {
      case 'active':
        return {
          text: language === 'vi' ? 'TRỰC TUYẾN (LIVE)' : 'ONLINE (LIVE)',
          cls: 'pill-online',
        };
      case 'sampling':
        return {
          text: language === 'vi' ? 'ĐANG LẤY MẪU' : 'SAMPLING',
          cls: 'pill-info',
        };
      case 'no_devices':
        return {
          text: language === 'vi' ? 'CHỜ SWITCH (0)' : 'STANDBY (0)',
          cls: 'pill-neutral',
        };
      case 'loading':
        return {
          text: language === 'vi' ? 'ĐANG KIỂM TRA' : 'CHECKING',
          cls: 'pill-warn',
        };
      case 'error':
      default:
        return {
          text: language === 'vi' ? 'ONOS: MẤT KẾT NỐI' : 'ONOS: OFFLINE',
          cls: 'pill-offline',
        };
    }
  };

  const badge = getStatusBadge();

  return (
    <section className="telemetry-gauge-card">
      <div className="panel-card-header">
        <div className="panel-card-title-group">
          <h3 className="card-heading">{t('dashboard.portThroughput')}</h3>
          <span className={`noc-pill ${badge.cls}`}>{badge.text}</span>
        </div>

        <button
          type="button"
          onClick={() => loadPortStats(true)}
          disabled={isRefreshing}
          className="noc-action-btn secondary"
          title={language === 'vi' ? 'Làm mới thống kê cổng ngay lập tức' : 'Refresh port statistics now'}
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
          {language === 'vi' ? 'Làm mới cổng' : 'Refresh Ports'}
        </button>
      </div>

      <p className="panel-card-subtitle">{getStatusSubtitle()}</p>

      {/* RX / TX Metric Cards */}
      <div className="port-rate-grid">
        <div className="port-rate-box rx">
          <div className="port-rate-label">
            <span>{t('dashboard.portRxTraffic')}</span>
            <span className="direction-tag rx">RX · Mbps</span>
          </div>
          <div className="port-rate-value">{formatRateDisplay(rate.rx)}</div>
          <div className="port-rate-meta">{getRateSubtext()}</div>
        </div>

        <div className="port-rate-box tx">
          <div className="port-rate-label">
            <span>{t('dashboard.portTxTraffic')}</span>
            <span className="direction-tag tx">TX · Mbps</span>
          </div>
          <div className="port-rate-value">{formatRateDisplay(rate.tx)}</div>
          <div className="port-rate-meta">{getRateSubtext()}</div>
        </div>
      </div>

      {/* Diagnostic Footer Pills */}
      <div className="panel-footer-meta">
        <div className="meta-pill-group">
          <span className="secondary-stat-pill">
            {language === 'vi' ? 'Switch' : 'Switches'}:{' '}
            <strong>{rate.activeSwitches ?? '--'}</strong>
          </span>
          <span className="secondary-stat-pill">
            {language === 'vi' ? 'Cổng' : 'Ports'}:{' '}
            <strong>{rate.activePorts ?? '--'}</strong>
          </span>
          <span className="secondary-stat-pill">
            {language === 'vi' ? 'Gói tin' : 'Packets'}:{' '}
            <strong>
              {rate.totalPackets !== null
                ? rate.totalPackets.toLocaleString(language === 'vi' ? 'vi-VN' : 'en-US')
                : '--'}
            </strong>
          </span>
        </div>
        {rate.updated && (
          <span className="panel-updated-time">
            {t('common.lastUpdated')}: <strong>{rate.updated}</strong>
          </span>
        )}
      </div>

      <p className="panel-footnote">{t('dashboard.rateSourceNotice')}</p>
    </section>
  );
}

export default SdnPortRates;
