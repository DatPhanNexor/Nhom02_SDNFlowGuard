import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
} from 'chart.js';
import { API_BASE_URL } from '../config/apiConfig';
import { useLanguage } from '../i18n/LanguageContext';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
);

const API_URL = `${API_BASE_URL}/api/elk/port-traffic-history`;

function ElkPortHistoryChart() {
  const { language, t } = useLanguage();
  const [minutes, setMinutes] = useState(240);
  const [rows, setRows] = useState([]);
  const [switchId, setSwitchId] = useState('');
  const [port, setPort] = useState('1');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);
  const [lastLoaded, setLastLoaded] = useState(null);

  useEffect(() => {
    let active = true;

    const loadHistory = async () => {
      try {
        const response = await axios.get(API_URL, {
          params: {
            minutes,
            limit: 500
          },
          timeout: 12000
        });

        if (!active) return;

        const data = Array.isArray(response.data.data)
          ? response.data.data
          : [];

        const sorted = [...data].sort(
          (a, b) => new Date(a.timestamp) - new Date(b.timestamp)
        );

        setRows(sorted);
        setError('');
        setLastLoaded(new Date());
      } catch (err) {
        if (!active) return;

        setError(
          language === 'vi'
            ? 'Không thể tải lịch sử từ Elasticsearch. Kiểm tra Flask và Elasticsearch.'
            : 'Unable to load traffic history from Elasticsearch. Verify Flask and Elasticsearch.'
        );

        console.error('ELK traffic history error:', err);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    setLoading(true);
    loadHistory();

    const timer = setInterval(loadHistory, 30000);

    return () => {
      active = false;
      clearInterval(timer);
    };
  }, [minutes, refreshKey, language]);

  const switches = Array.from(
    new Set(rows.map((row) => row.switch_id).filter(Boolean))
  );

  const currentSwitch = switches.includes(switchId)
    ? switchId
    : (switches[0] || '');

  const ports = Array.from(
    new Set(
      rows
        .filter((row) => row.switch_id === currentSwitch)
        .map((row) => String(row.port_number))
        .filter((value) => value !== 'undefined' && value !== 'null')
    )
  ).sort((a, b) => Number(a) - Number(b));

  const currentPort = ports.includes(port)
    ? port
    : (ports[0] || '');

  const selectedRows = rows.filter(
    (row) =>
      row.switch_id === currentSwitch &&
      String(row.port_number) === currentPort
  );

  const values = (field) =>
    selectedRows.map((row) => {
      const number = Number(row[field]);
      return Number.isFinite(number) ? number : 0;
    });

  const rxValues = values('rx_mbps');
  const txValues = values('tx_mbps');

  const peakRx = Math.max(0, ...rxValues);
  const peakTx = Math.max(0, ...txValues);

  const chartData = {
    labels: selectedRows.map((row) =>
      new Date(row.timestamp).toLocaleTimeString(language === 'vi' ? 'vi-VN' : 'en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    ),
    datasets: [
      {
        label: t('elkChart.rxMbps'),
        data: rxValues,
        borderColor: '#15803d',
        backgroundColor: '#15803d',
        borderWidth: 2,
        pointRadius: 3,
        tension: 0.2
      },
      {
        label: t('elkChart.txMbps'),
        data: txValues,
        borderColor: '#0284c7',
        backgroundColor: '#0284c7',
        borderWidth: 2,
        pointRadius: 3,
        tension: 0.2
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false
    },
    plugins: {
      legend: {
        position: 'top'
      },
      tooltip: {
        callbacks: {
          label: (context) =>
            `${context.dataset.label}: ${Number(context.parsed.y).toFixed(6)} Mbps`
        }
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: t('elkChart.timeAxis')
        }
      },
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: t('elkChart.speedAxis')
        }
      }
    }
  };

  const selectStyle = {
    padding: '7px 12px',
    border: '1px solid #cbd5e1',
    borderRadius: 6,
    background: '#fff',
    fontSize: 13,
    color: '#0f172a'
  };

  return (
    <section
      style={{
        background: '#fff',
        border: '1px solid #e2e8f0',
        borderRadius: 10,
        padding: 20,
        marginBottom: 22,
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
      }}
    >
      <h3 style={{ marginTop: 0, color: '#0f172a', fontSize: '1.15rem', fontWeight: 700 }}>
        {t('elkChart.title')}
      </h3>

      <p style={{ color: '#64748b', fontSize: 13, marginBottom: 16 }}>
        {t('elkChart.subtitle')}
      </p>

      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'end',
          gap: 14,
          marginBottom: 18
        }}
      >
        <label style={{ fontSize: 13, color: '#475569', fontWeight: 600 }}>
          <div style={{ marginBottom: 4 }}>{t('elkChart.switchLabel')}</div>
          <select
            style={selectStyle}
            value={currentSwitch}
            onChange={(e) => setSwitchId(e.target.value)}
          >
            {switches.map((id) => (
              <option key={id} value={id}>{id}</option>
            ))}
          </select>
        </label>

        <label style={{ fontSize: 13, color: '#475569', fontWeight: 600 }}>
          <div style={{ marginBottom: 4 }}>{t('elkChart.portLabel')}</div>
          <select
            style={selectStyle}
            value={currentPort}
            onChange={(e) => setPort(e.target.value)}
          >
            {ports.map((number) => (
              <option key={number} value={number}>
                Port {number}
              </option>
            ))}
          </select>
        </label>

        <label style={{ fontSize: 13, color: '#475569', fontWeight: 600 }}>
          <div style={{ marginBottom: 4 }}>{t('elkChart.timeRangeLabel')}</div>
          <select
            style={selectStyle}
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
          style={{
            ...selectStyle,
            cursor: 'pointer',
            background: '#0f172a',
            color: '#fff',
            border: '1px solid #334155',
            fontWeight: 600
          }}
          onClick={() => setRefreshKey((value) => value + 1)}
        >
          {t('common.refresh')}
        </button>
      </div>

      {error && (
        <p role="alert" style={{ color: '#b91c1c', fontSize: 13 }}>
          {error}
        </p>
      )}

      <div style={{ marginBottom: 12, fontSize: 13, color: '#334155' }}>
        <strong>{t('elkChart.samples')}: {selectedRows.length}</strong>
        {' | '}
        {t('elkChart.rxMax')}: {peakRx.toFixed(6)} Mbps
        {' | '}
        {t('elkChart.txMax')}: {peakTx.toFixed(6)} Mbps
      </div>

      {selectedRows.length > 0 ? (
        <div style={{ position: 'relative', height: 320, width: '100%' }}>
          <Line data={chartData} options={chartOptions} />
        </div>
      ) : (
        <div
          style={{
            padding: 30,
            textAlign: 'center',
            background: '#f8fafc',
            color: '#64748b',
            borderRadius: 8,
            fontSize: 13
          }}
        >
          {loading
            ? t('common.loadingData')
            : t('elkChart.noHistoryData')}
        </div>
      )}

      <p style={{ marginBottom: 0, marginTop: 14, fontSize: 12, color: '#94a3b8' }}>
        {lastLoaded
          ? `${t('common.lastUpdated')}: ${lastLoaded.toLocaleTimeString(language === 'vi' ? 'vi-VN' : 'en-US')}. `
          : ''}
        {t('elkChart.footerNotice')}
      </p>
    </section>
  );
}

export default ElkPortHistoryChart;
