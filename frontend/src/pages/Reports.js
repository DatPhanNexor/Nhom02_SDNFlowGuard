import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config/apiConfig';
import { useLanguage } from '../i18n/LanguageContext';
import './Reports.css';

function Reports() {
  const { t } = useLanguage();
  const [reportType, setReportType] = useState('anomalies');
  const [reportData, setReportData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const fetchReportData = useCallback(async () => {
    setIsLoading(true);
    setError('');
    setSuccessMessage('');
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
  }, [reportType, t]);

  useEffect(() => {
    fetchReportData();
  }, [fetchReportData]);

  const handleDownloadPDF = async () => {
    setIsExporting(true);
    setError('');
    setSuccessMessage('');
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
      setSuccessMessage(t('reports.exportSuccess'));
    } catch (err) {
      setError(t('reports.errorDownload'));
    } finally {
      setIsExporting(false);
    }
  };

  const reportTypeTitle =
    reportType === 'anomalies'
      ? t('reports.anomaliesOption')
      : t('reports.actionsOption');

  return (
    <div className="reports">
      <div className="reports-container">
        {/* Section A: Header */}
        <div className="reports-header">
          <div className="reports-header-left">
            <h2 className="reports-title">{t('reports.title')}</h2>
            <p className="reports-subtitle">{t('reports.subtitle')}</p>
          </div>
          <div className="reports-header-badges">
            <span className="telemetry-badge">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <ellipse cx="12" cy="5" rx="9" ry="3" />
                <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
                <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
              </svg>
              {t('reports.storageBadge')}
            </span>
            <span className="telemetry-badge telemetry-primary">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
              </svg>
              {t('reports.formatBadge')}
            </span>
            <span className="telemetry-badge telemetry-count">
              {t('reports.recordsAvailable', { count: reportData.length })}
            </span>
          </div>
        </div>

        {/* Section B: Extraction Controls & PDF Export Card */}
        <div className="report-control-card">
          <div className="control-card-header">
            <h3 className="control-card-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <line x1="3" y1="9" x2="21" y2="9" />
                <line x1="9" y1="21" x2="9" y2="9" />
              </svg>
              {t('reports.controlCardTitle')}
            </h3>
          </div>

          <div className="control-card-grid">
            <div className="control-item select-item">
              <label htmlFor="report-type">{t('reports.datasetLabel')}</label>
              <select
                id="report-type"
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
              >
                <option value="anomalies">{t('reports.anomaliesOption')}</option>
                <option value="actions">{t('reports.actionsOption')}</option>
              </select>
            </div>

            <div className="retention-notice-box">
              <svg className="retention-notice-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="16" x2="12" y2="12" />
                <line x1="12" y1="8" x2="12.01" y2="8" />
              </svg>
              <div>{t('reports.monthlyWindowNotice')}</div>
            </div>

            <div className="control-actions-row">
              <button
                type="button"
                className="btn-export-pdf"
                onClick={handleDownloadPDF}
                disabled={isExporting || isLoading}
                title={t('reports.btnExportPdf')}
              >
                {isExporting ? (
                  <>
                    <span className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} />
                    {t('reports.exportingBtn')}
                  </>
                ) : (
                  <>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                      <polyline points="7 10 12 15 17 10" />
                      <line x1="12" y1="15" x2="12" y2="3" />
                    </svg>
                    {t('reports.btnExportPdf')}
                  </>
                )}
              </button>

              <button
                type="button"
                className="btn-refresh-report"
                onClick={fetchReportData}
                disabled={isLoading}
                title={t('reports.refreshBtn')}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
                </svg>
                {t('reports.refreshBtn')}
              </button>
            </div>
          </div>
        </div>

        {/* Feedback Banners */}
        {error && (
          <div className="reports-alert-banner alert-error">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        {successMessage && (
          <div className="reports-alert-banner alert-success">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
            <span>{successMessage}</span>
          </div>
        )}

        {/* Section C: Dedicated Report Preview Card */}
        <div className="report-preview-card">
          <div className="preview-card-header">
            <div className="preview-title-group">
              <h3 className="preview-card-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
                {t('reports.auditReportTitle', { type: reportTypeTitle })}
              </h3>
              <p className="preview-card-subtitle">
                {t('reports.exportSummary', { count: reportData.length })}
              </p>
            </div>
            <span className="telemetry-badge telemetry-count">
              {t('reports.recordsAvailable', { count: reportData.length })}
            </span>
          </div>

          {isLoading ? (
            <div className="reports-loading-box">
              <div className="spinner" />
              <span>{t('reports.generating')}</span>
            </div>
          ) : (
            <div className="reports-table-wrapper">
              <table className="reports-audit-table">
                <thead>
                  {reportType === 'anomalies' ? (
                    <tr>
                      <th>{t('reports.tableHeaders.time')}</th>
                      <th>{t('reports.tableHeaders.sourceIp')}</th>
                      <th>{t('reports.tableHeaders.event')}</th>
                      <th>{t('reports.tableHeaders.score')}</th>
                    </tr>
                  ) : reportType === 'actions' ? (
                    <tr>
                      <th>{t('reports.tableHeaders.time')}</th>
                      <th>{t('reports.tableHeaders.actionType')}</th>
                      <th>{t('reports.tableHeaders.sourceIp')}</th>
                      <th>{t('reports.tableHeaders.reason')}</th>
                      <th>{t('reports.tableHeaders.source')}</th>
                    </tr>
                  ) : (
                    <tr>
                      {reportData.length > 0 &&
                        Object.keys(reportData[0]).map((key) => (
                          <th key={key}>{key.replace(/_/g, ' ').toUpperCase()}</th>
                        ))}
                    </tr>
                  )}
                </thead>
                <tbody>
                  {reportData.length === 0 ? (
                    <tr>
                      <td colSpan="10" style={{ textAlign: 'center', padding: '40px 16px', color: 'var(--text-muted)' }}>
                        {t('reports.noReportRecords')}
                      </td>
                    </tr>
                  ) : reportType === 'anomalies' ? (
                    reportData.map((row, index) => {
                      const score = Number(row.score || 0);
                      let scoreClass = 'score-low';
                      if (score >= 70) scoreClass = 'score-high';
                      else if (score >= 40) scoreClass = 'score-medium';

                      return (
                        <tr key={index}>
                          <td style={{ whiteSpace: 'nowrap', fontFamily: 'monospace', fontSize: 12.5, color: 'var(--text-secondary)' }}>
                            {row.timestamp}
                          </td>
                          <td>
                            <span className="ip-chip">{row.source_ip || 'N/A'}</span>
                          </td>
                          <td>
                            <span className="event-chip">{row.event || 'Unknown'}</span>
                          </td>
                          <td>
                            <span className={`score-badge ${scoreClass}`}>
                              {row.score}
                            </span>
                          </td>
                        </tr>
                      );
                    })
                  ) : reportType === 'actions' ? (
                    reportData.map((row, index) => {
                      const actionLower = String(row.action_type || '').toLowerCase();
                      let actionClass = 'action-chip-default';
                      if (actionLower.includes('block')) actionClass = 'action-chip-block';
                      else if (actionLower.includes('rate')) actionClass = 'action-chip-rate';
                      else if (actionLower.includes('redirect')) actionClass = 'action-chip-redirect';
                      else if (actionLower.includes('unblock')) actionClass = 'action-chip-unblock';

                      const isAutomated =
                        String(row.admin_or_automated || '').toLowerCase() === 'automated';

                      return (
                        <tr key={index}>
                          <td style={{ whiteSpace: 'nowrap', fontFamily: 'monospace', fontSize: 12.5, color: 'var(--text-secondary)' }}>
                            {row.timestamp}
                          </td>
                          <td>
                            <span className={`action-chip ${actionClass}`}>
                              {row.action_type}
                            </span>
                          </td>
                          <td>
                            <span className="ip-chip">{row.source_ip || 'N/A'}</span>
                          </td>
                          <td style={{ fontSize: 13 }}>{row.reason}</td>
                          <td>
                            <span
                              className={`source-badge ${
                                isAutomated ? 'source-badge-automated' : 'source-badge-manual'
                              }`}
                            >
                              {isAutomated ? t('decisionLogs.automatedSource') : t('decisionLogs.manualSource')}
                            </span>
                          </td>
                        </tr>
                      );
                    })
                  ) : (
                    reportData.map((row, index) => (
                      <tr key={index}>
                        {Object.values(row).map((val, idx) => (
                          <td key={idx} style={{ fontSize: 13 }}>
                            {val !== null && typeof val === 'object'
                              ? JSON.stringify(val)
                              : String(val ?? 'N/A')}
                          </td>
                        ))}
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Reports;
