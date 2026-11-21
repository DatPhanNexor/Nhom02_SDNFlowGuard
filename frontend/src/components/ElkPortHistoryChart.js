import React, { useEffect, useState, useCallback, useRef } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { API_BASE_URL } from '../config/apiConfig';
import { useLanguage } from '../i18n/LanguageContext';
import { useTheme } from '../theme/ThemeContext';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
);

const API_URL = `${API_BASE_URL}/api/elk/port-traffic-history`;

function ElkPortHistoryChart({ refreshTrigger }) {
  const { language, t } = useLanguage();
  const { isDark } = useTheme();
  const [minutes, setMinutes] = useState(240);
  const [rows, setRows] = useState([]);
  const [topologyDevices, setTopologyDevices] = useState([]);
  const [switchId, setSwitchId] = useState('');
  const [port, setPort] = useState('1');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);
  const [lastLoaded, setLastLoaded] = useState(null);
  const isMountedRef = useRef(true);

  const loadHistoryAndTopology = useCallback(async () => {
    setLoading(true);
    setError('');

    try {
      const [historyRes, topoRes] = await Promise.allSettled([
        axios.get(API_URL, {
          params: { minutes, limit: 500 },
          timeout: 10000,
        }),
        axios.get(`${API_BASE_URL}/api/topology`, { timeout: 4500 }),
      ]);

      if (!isMountedRef.current) return;

      if (historyRes.status === 'fulfilled') {
        const historyData = historyRes.value.data;
        const validRows = Array.isArray(historyData?.data)
          ? historyData.data
          : Array.isArray(historyData?.rows)
            ? historyData.rows
            : Array.isArray(historyData)
              ? historyData
              : [];
        setRows(validRows);
        setLastLoaded(new Date());
      } else {
        setRows([]);
        setError(
          language === 'vi'
            ? 'Không thể truy vấn lịch sử lưu lượng từ Elasticsearch. Kiểm tra dịch vụ Elasticsearch/Backend.'
            : 'Unable to query port traffic history from Elasticsearch. Verify Elasticsearch/Backend availability.'
        );
      }

      if (topoRes.status === 'fulfilled' && topoRes.value?.data?.controller_status !== 'UNAVAILABLE') {
        const devices = Array.isArray(topoRes.value.data?.devices)
          ? topoRes.value.data.devices
          : [];
        setTopologyDevices(devices);
      } else {
        setTopologyDevices([]);
      }
    } catch (err) {
      if (!isMountedRef.current) return;
      console.error('ELK traffic history error:', err);
      setRows([]);
      setError(
        language === 'vi'
          ? 'Lỗi kết nối dịch vụ đo lường lưu lượng lịch sử.'
          : 'Failed to connect to port traffic history service.'
      );
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  }, [minutes, language]);

  useEffect(() => {
    isMountedRef.current = true;
    loadHistoryAndTopology();

    const timer = setInterval(() => {
      if (document.visibilityState === 'visible') {
        loadHistoryAndTopology();
      }
    }, 30000);

    return () => {
      isMountedRef.current = false;
      clearInterval(timer);
    };
  }, [loadHistoryAndTopology, refreshKey, refreshTrigger]);

  const switchesFromRows = rows.map((row) => row.switch_id).filter(Boolean);
  const switchesFromTopo = topologyDevices.map((d) => d.id).filter(Boolean);
  const switches = Array.from(new Set([...switchesFromRows, ...switchesFromTopo]));

  const currentSwitch = switches.includes(switchId)
    ? switchId
    : switches[0] || topologyDevices[0]?.id || '';

  const selectedTopoDevice = topologyDevices.find((d) => d.id === currentSwitch);
  const livePortsSet = new Set(
    Array.isArray(selectedTopoDevice?.ports)
      ? selectedTopoDevice.ports
          .map((p) => String(p.port || p.portNumber || p))
          .filter(Boolean)
      : []
  );

  const portsFromRows = rows
    .filter((row) => row.switch_id === currentSwitch)
    .map((row) => String(row.port_number))
    .filter((val) => val && val !== 'undefined' && val !== 'null');

  const fallbackPorts = ['1', '2', '3', '4'];
  const allCandidatePorts = Array.from(
    new Set([
      ...Array.from(livePortsSet),
      ...portsFromRows,
      ...(livePortsSet.size === 0 && portsFromRows.length === 0 ? fallbackPorts : []),
    ])
  ).sort((a, b) => Number(a) - Number(b));

  const currentPort = allCandidatePorts.includes(port)
    ? port
    : allCandidatePorts[0] || '1';

  const selectedRows = rows.filter(
    (row) =>
      row.switch_id === currentSwitch &&
      String(row.port_number) === currentPort
  );

  const values = (field) =>
    selectedRows.map((row) => {
      const num = Number(row[field]);
      return Number.isFinite(num) ? num : 0;
    });

  const rxValues = values('rx_mbps');
  const txValues = values('tx_mbps');

  const peakRx = rxValues.length > 0 ? Math.max(...rxValues) : 0;
  const peakTx = txValues.length > 0 ? Math.max(...txValues) : 0;
  const avgRx =
    rxValues.length > 0 ? rxValues.reduce((a, b) => a + b, 0) / rxValues.length : 0;
  const avgTx =
    txValues.length > 0 ? txValues.reduce((a, b) => a + b, 0) / txValues.length : 0;

  const chartData = {
    labels: selectedRows.map((row) =>
      new Date(row.timestamp).toLocaleTimeString(
        language === 'vi' ? 'vi-VN' : 'en-US',
        {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false,
        }
      )
    ),
    datasets: [
      {
        label: t('elkChart.rxMbps'),
        data: rxValues,
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        borderWidth: 2,
        pointRadius: 2.5,
        tension: 0.2,
        fill: true,
      },
      {
        label: t('elkChart.txMbps'),
        data: txValues,
        borderColor: '#0284c7',
        backgroundColor: 'rgba(2, 132, 199, 0.1)',
        borderWidth: 2,
        pointRadius: 2.5,
        tension: 0.2,
        fill: true,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: isDark ? '#f8fafc' : '#0f172a',
          font: { family: 'sans-serif', size: 13 },
          usePointStyle: true,
        },
      },
      tooltip: {
        callbacks: {
          label: (context) =>
            `${context.dataset.label}: ${Number(context.parsed.y).toFixed(6)} Mbps`,
        },
      },
    },
    scales: {
      x: {
        grid: { color: isDark ? 'rgba(255, 255, 255, 0.08)' : '#f1f5f9' },
        ticks: { color: isDark ? '#94a3b8' : '#475569', maxTicksLimit: 8, font: { size: 12 } },
        title: {
          display: true,
          text: t('elkChart.timeAxis'),
          color: isDark ? '#f8fafc' : '#0f172a',
          font: { weight: 'bold', size: 12 },
        },
      },
      y: {
        beginAtZero: true,
        grid: { color: isDark ? 'rgba(255, 255, 255, 0.08)' : '#f1f5f9' },
        ticks: { color: isDark ? '#94a3b8' : '#475569', font: { size: 12 } },
        title: {
          display: true,
          text: t('elkChart.speedAxis'),
          color: isDark ? '#f8fafc' : '#0f172a',
          font: { weight: 'bold', size: 12 },
        },
      },
    },
  };

  const getTimeRangeText = () => {
    switch (minutes) {
      case 60:
        return language === 'vi' ? '1 giờ qua' : 'past 1 hour';
      case 240:
        return language === 'vi' ? '4 giờ qua' : 'past 4 hours';
      case 1440:
        return language === 'vi' ? '24 giờ qua' : 'past 24 hours';
      case 10080:
        return language === 'vi' ? '7 ngày qua' : 'past 7 days';
      default:
        return `${minutes} min`;
    }
  };

  return (
    <section className="elk-history-card">
      <div className="panel-card-header">
        <div className="panel-card-title-group">
          <h3 className="card-heading">{t('elkChart.title')}</h3>
          <span className={`noc-pill ${error ? 'pill-offline' : 'pill-info'}`}>
            {error
              ? language === 'vi'
                ? 'ELK MẤT KẾT NỐI'
                : 'ELK OFFLINE'
              : language === 'vi'
                ? 'Dữ liệu lịch sử (ELK)'
                : 'Historical Data (ELK)'}
          </span>
          {!error && (
            <span className="noc-pill pill-neutral">
              {selectedRows.length} {language === 'vi' ? 'mẫu đo' : 'samples'}
            </span>
          )}
        </div>

        {/* Filter Toolbar */}
        <div className="panel-toolbar-controls">
          <label className="toolbar-field">
            <span>{t('elkChart.switchLabel')}:</span>
            <select
              className="noc-select"
              value={currentSwitch}
              onChange={(e) => setSwitchId(e.target.value)}
            >
              {switches.length > 0 ? (
                switches.map((id) => (
                  <option key={id} value={id}>
                    {id}
                  </option>
                ))
              ) : (
                <option value="" disabled>
                  {language === 'vi' ? '-- Chưa có Switch --' : '-- No switch --'}
                </option>
              )}
            </select>
          </label>

          <label className="toolbar-field">
            <span>{t('elkChart.portLabel')}:</span>
            <select
              className="noc-select"
              value={currentPort}
              onChange={(e) => setPort(e.target.value)}
            >
              {allCandidatePorts.map((number) => {
                const isLive = livePortsSet.has(number);
                return (
                  <option key={number} value={number}>
                    Port {number}{' '}
                    {isLive
                      ? `(${language === 'vi' ? 'Live ONOS' : 'Live'})`
                      : `(${language === 'vi' ? 'Lịch sử' : 'History'})`}
                  </option>
                );
              })}
            </select>
          </label>

          <label className="toolbar-field">
            <span>{t('elkChart.timeRangeLabel')}:</span>
            <select
              className="noc-select"
              value={minutes}
              onChange={(e) => setMinutes(Number(e.target.value))}
            >
              <option value={60}>{t('alertsTable.oneHour')}</option>
              <option value={240}>{t('alertsTable.fourHours')}</option>
              <option value={1440}>{t('alertsTable.twentyFourHours')}</option>
              <option value={10080}>{t('alertsTable.sevenDays')}</option>
            </select>
          </label>

          <button
            type="button"
            className="noc-action-btn primary"
            disabled={loading}
            onClick={() => setRefreshKey((val) => val + 1)}
          >
            <svg
              className={loading ? 'spin-icon' : ''}
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
      </div>

      <p className="panel-card-subtitle">{t('elkChart.subtitle')}</p>

      {error && (
        <div className="noc-error-banner" role="alert">
          {error}
        </div>
      )}

      {/* Stats Summary Bar when data exists */}
      {selectedRows.length > 0 && (
        <div className="elk-stats-strip">
          <span>
            <strong>{t('elkChart.samples')}:</strong> {selectedRows.length}
          </span>
          <span>
            <strong>{t('elkChart.rxMax')}:</strong>{' '}
            <span className="metric-rx">{peakRx.toFixed(6)} Mbps</span>
          </span>
          <span>
            <strong>{t('elkChart.txMax')}:</strong>{' '}
            <span className="metric-tx">{peakTx.toFixed(6)} Mbps</span>
          </span>
          <span>
            <strong>{language === 'vi' ? 'Trung bình RX/TX' : 'Avg RX/TX'}:</strong>{' '}
            {avgRx.toFixed(4)} / {avgTx.toFixed(4)} Mbps
          </span>
        </div>
      )}

      {/* Chart Canvas or Compact Empty State */}
      {selectedRows.length > 0 ? (
        <div className="elk-chart-canvas">
          <Line data={chartData} options={chartOptions} />
        </div>
      ) : (
        <div className="elk-empty-strip">
          <div>
            <div className="elk-empty-title">
              {loading
                ? t('common.loadingData')
                : error
                  ? language === 'vi'
                    ? 'Không thể tải dữ liệu lưu lượng lịch sử từ Elasticsearch.'
                    : 'Historical port traffic cannot be loaded from Elasticsearch.'
                  : language === 'vi'
                    ? `Chưa có dữ liệu lưu lượng để hiển thị cho ${currentSwitch || 'Switch'} (Cổng ${currentPort}) trong ${getTimeRangeText()}.`
                    : `No traffic data available to display for ${currentSwitch || 'Switch'} (Port ${currentPort}) in ${getTimeRangeText()}.`}
            </div>
            <div className="elk-empty-desc">
              {language === 'vi'
                ? 'Chỉ mục: sdnflowguard-events-*. Dữ liệu được Logstash lập chỉ mục từ ONOS Port Collector khi có lưu lượng đi qua switch.'
                : 'Index: sdnflowguard-events-*. Telemetry is indexed via Logstash from ONOS Port Collector when traffic traverses switch ports.'}
            </div>
          </div>
        </div>
      )}

      <div className="panel-footer-meta">
        <span>{t('elkChart.footerNotice')}</span>
        {lastLoaded && !error && (
          <span className="panel-updated-time">
            {t('common.lastUpdated')}:{' '}
            <strong>
              {lastLoaded.toLocaleTimeString(language === 'vi' ? 'vi-VN' : 'en-US', {
                hour12: false,
              })}
            </strong>
          </span>
        )}
      </div>
    </section>
  );
}

export default ElkPortHistoryChart;
