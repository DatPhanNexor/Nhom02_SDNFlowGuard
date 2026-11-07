import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config/apiConfig';
import { useLanguage } from '../i18n/LanguageContext';
import './Reports.css';

function Reports() {
  const { t } = useLanguage();
  const [reportType, setReportType] = useState('anomalies');
  const [reportData, setReportData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchReportData = async () => {
      setIsLoading(true);
      setError('');
      try {
        const response = await axios.get(`${API_BASE_URL}/api/get-report`, {
          params: { time_range: 'monthly', report_type: reportType },
        });
        setReportData(
          Array.isArray(response.data?.data) ? response.data.data : []
        );
      } catch (err) {
        setError(t('reports.errorFetch'));
      } finally {
        setIsLoading(false);
      }
    };

    fetchReportData();
  }, [reportType, t]);

  const handleDownloadPDF = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/download-pdf`, {
        params: { time_range: 'monthly', report_type: reportType },
        responseType: 'blob',
      });

      const blob = new Blob([response.data], { type: 'application/pdf' });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = `${reportType}_report_monthly.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      setError(t('reports.errorDownload'));
    }
  };

  const reportTypeTitle =
    reportType === 'anomalies'
      ? t('reports.anomaliesOption')
      : t('reports.actionsOption');

  return (
    <div className="reports">
      <div style={{ marginBottom: 20 }}>
        <h2 style={{ margin: 0, color: '#0f172a', fontSize: '1.6rem', fontWeight: 700 }}>
          {t('reports.title')}
        </h2>
        <p style={{ margin: '4px 0 0 0', color: '#64748b', fontSize: 14 }}>
          {t('reports.localDbNotice')}
        </p>
      </div>

      {/* Filter & Export Bar */}
      <div className="report-filters" style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 20, flexWrap: 'wrap', background: '#fff', padding: '16px 20px', borderRadius: 10, border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
        <label htmlFor="report-type" style={{ fontWeight: 600, fontSize: 14, color: '#334155' }}>
          {t('reports.datasetLabel')}
        </label>
        <select
          id="report-type"
          value={reportType}
          onChange={(e) => setReportType(e.target.value)}
          style={{ padding: '8px 14px', border: '1px solid #cbd5e1', borderRadius: 6, fontSize: 14, background: '#fff' }}
        >
          <option value="anomalies">{t('reports.anomaliesOption')}</option>
          <option value="actions">{t('reports.actionsOption')}</option>
        </select>

        <button
          onClick={handleDownloadPDF}
          style={{
            padding: '8px 18px',
            background: '#0284c7',
            color: '#fff',
            borderRadius: 6,
            cursor: 'pointer',
            border: 'none',
            fontWeight: 700,
            fontSize: 14,
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            boxShadow: '0 1px 3px rgba(2, 132, 199, 0.3)'
          }}
        >
          <svg style={{ width: 16, height: 16 }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          {t('reports.btnExportPdf')}
        </button>
      </div>

      {/* Report Table Display */}
      <div className="report-display" style={{ background: '#fff', padding: 20, borderRadius: 10, border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14, flexWrap: 'wrap', gap: 8 }}>
          <h3 style={{ margin: 0, color: '#0f172a', fontSize: '1.15rem', fontWeight: 700 }}>
            {t('reports.auditReportTitle', { type: reportTypeTitle })}
          </h3>
          <span style={{ fontSize: 13, color: '#64748b' }}>
            {t('reports.recordsAvailable', { count: reportData.length })}
          </span>
        </div>

        {isLoading ? (
          <p style={{ color: '#64748b', padding: '24px 0', textAlign: 'center' }}>
            {t('reports.generating')}
          </p>
        ) : error ? (
          <p className="error" style={{ color: '#ef4444', padding: '12px 0' }}>
            {error}
          </p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr style={{ background: '#f8fafc' }}>
                  {reportData.length > 0 &&
                    Object.keys(reportData[0]).map((key) => (
                      <th key={key} style={{ textTransform: 'uppercase', fontSize: 12 }}>
                        {key.replace(/_/g, ' ')}
                      </th>
                    ))}
                </tr>
              </thead>
              <tbody>
                {reportData.length > 0 ? (
                  reportData.map((row, index) => (
                    <tr key={index}>
                      {Object.values(row).map((value, idx) => (
                        <td key={idx} style={{ fontSize: 13 }}>
                          {value !== null && typeof value === 'object'
                            ? JSON.stringify(value)
                            : String(value ?? 'N/A')}
                        </td>
                      ))}
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="100%" style={{ textAlign: 'center', padding: '36px', color: '#64748b' }}>
                      {t('reports.noReportRecords')}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default Reports;
