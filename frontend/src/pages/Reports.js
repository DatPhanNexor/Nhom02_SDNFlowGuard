import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config/apiConfig';
import { useLanguage } from '../i18n/LanguageContext';
import './Reports.css';

function Reports() {
  const { t } = useLanguage();
  const [reportType, setReportType] = useState('anomalies');
  const [timeRange, setTimeRange] = useState('last_30d');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [severity, setSeverity] = useState('all');
  const [actionType, setActionType] = useState('all');
  const [sourceIp, setSourceIp] = useState('');
  const [initiationSource, setInitiationSource] = useState('all');

  const [reportData, setReportData] = useState([]);
  const [kpi, setKpi] = useState({
    total_records: 0,
    security_events: 0,
    defense_decisions: 0,
    simulated_actions: 0,
    enforced_actions: 0,
  });
  const [displayPeriod, setDisplayPeriod] = useState('Last 30 Days');
  const [lastRefreshed, setLastRefreshed] = useState('');
  const [isApiOnline, setIsApiOnline] = useState(true);

  const [isLoading, setIsLoading] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Pagination & Sorting
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [sortField, setSortField] = useState('timestamp');
  const [sortAsc, setSortAsc] = useState(false);

  const fetchReportData = useCallback(async () => {
    // Validate custom date range if selected
    if (timeRange === 'custom') {
      if (startDate && endDate && startDate > endDate) {
        setError(t('reports.errorInvalidRange'));
        return;
      }
    }

    setIsLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      const params = {
        report_type: reportType,
        time_range: timeRange,
      };

      if (timeRange === 'custom') {
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;
      }

      if (reportType === 'anomalies') {
        if (severity !== 'all') params.severity = severity;
      } else if (reportType === 'actions') {
        if (actionType !== 'all') params.action_type = actionType;
        if (initiationSource !== 'all') params.initiation_source = initiationSource;
      }

      if (sourceIp.trim()) {
        params.source_ip = sourceIp.trim();
      }

      const response = await axios.get(`${API_BASE_URL}/api/get-report`, { params });
      const rawRows = Array.isArray(response.data?.data) ? response.data.data : [];
      setReportData(rawRows);

      if (response.data?.kpi) {
        setKpi(response.data.kpi);
      }
      if (response.data?.display_period) {
        setDisplayPeriod(response.data.display_period);
      }
      setIsApiOnline(true);
      setLastRefreshed(new Date().toLocaleTimeString('vi-VN', { hour12: false }));
      setCurrentPage(1);
    } catch (err) {
      setIsApiOnline(false);
      setError(t('reports.errorFetch'));
    } finally {
      setIsLoading(false);
    }
  }, [reportType, timeRange, startDate, endDate, severity, actionType, initiationSource, sourceIp, t]);

  useEffect(() => {
    fetchReportData();
  }, [fetchReportData]);

  const handleResetFilters = () => {
    setTimeRange('last_30d');
    setStartDate('');
    setEndDate('');
    setSeverity('all');
    setActionType('all');
    setSourceIp('');
    setInitiationSource('all');
    setError('');
  };

  const handleDownloadPDF = async () => {
    if (timeRange === 'custom' && startDate && endDate && startDate > endDate) {
      setError(t('reports.errorInvalidRange'));
      return;
    }

    setIsExporting(true);
    setError('');
    setSuccessMessage('');
    try {
      const params = {
        report_type: reportType,
        time_range: timeRange,
      };
      if (timeRange === 'custom') {
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;
      }
      if (reportType === 'anomalies') {
        if (severity !== 'all') params.severity = severity;
      } else if (reportType === 'actions') {
        if (actionType !== 'all') params.action_type = actionType;
        if (initiationSource !== 'all') params.initiation_source = initiationSource;
      }
      if (sourceIp.trim()) {
        params.source_ip = sourceIp.trim();
      }

      const response = await axios.get(`${API_BASE_URL}/api/download-pdf`, {
        params,
        responseType: 'blob',
      });

      const blob = new Blob([response.data], { type: 'application/pdf' });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      const tag = timeRange === 'custom' && startDate && endDate ? `${startDate}_to_${endDate}` : timeRange;
      link.download = `SDNFlowGuard_${reportType}_report_${tag}.pdf`;
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

  const handleSort = (field) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(true);
    }
  };

  // Sorted and Paginated Data
  const sortedData = useMemo(() => {
    const list = [...reportData];
    list.sort((a, b) => {
      let va = a[sortField];
      let vb = b[sortField];
      if (sortField === 'score') {
        va = Number(va || 0);
        vb = Number(vb || 0);
      } else {
        va = String(va || '').toLowerCase();
        vb = String(vb || '').toLowerCase();
      }
      if (va < vb) return sortAsc ? -1 : 1;
      if (va > vb) return sortAsc ? 1 : -1;
      return 0;
    });
    return list;
  }, [reportData, sortField, sortAsc]);

  const totalPages = Math.max(1, Math.ceil(sortedData.length / pageSize));
  const paginatedData = useMemo(() => {
    const startIdx = (currentPage - 1) * pageSize;
    return sortedData.slice(startIdx, startIdx + pageSize);
  }, [sortedData, currentPage, pageSize]);

  const reportTypeTitle =
    reportType === 'anomalies'
      ? t('reports.anomaliesOption')
      : t('reports.actionsOption');

  return (
    <div className="reports soc-reports">
      <div className="reports-container">
        {/* Section 1: SOC Page Header */}
        <div className="reports-header soc-header">
          <div className="reports-header-left">
            <h2 className="reports-title">{t('reports.title')}</h2>
            <p className="reports-subtitle">{t('reports.subtitle')}</p>
          </div>
          <div className="reports-header-badges">
            <span className={`telemetry-badge ${isApiOnline ? 'badge-online' : 'badge-offline'}`}>
              <span className="status-dot" />
              {isApiOnline ? t('reports.backendOnline') : t('reports.backendOffline')}
            </span>
            <span className="telemetry-badge">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <ellipse cx="12" cy="5" rx="9" ry="3" />
                <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
                <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
              </svg>
              {t('reports.storageBadge')}
            </span>
            <span className="telemetry-badge">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
              {t('reports.timezoneBadge')}
            </span>
            {lastRefreshed && (
              <span className="telemetry-badge telemetry-timestamp">
                {t('reports.lastRefreshedLabel')} {lastRefreshed}
              </span>
            )}
          </div>
        </div>

        {/* Section 2: Summary KPI Cards Grid (4 Cards) */}
        <div className="soc-kpi-grid">
          <div className="soc-kpi-card">
            <div className="kpi-icon-wrap kpi-blue">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
              </svg>
            </div>
            <div className="kpi-content">
              <div className="kpi-label">{t('reports.kpi.totalRecords')}</div>
              <div className="kpi-value">{reportData.length}</div>
              <div className="kpi-subtext">{displayPeriod}</div>
            </div>
          </div>

          <div className="soc-kpi-card">
            <div className="kpi-icon-wrap kpi-red">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                <line x1="12" y1="9" x2="12" y2="13" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
            </div>
            <div className="kpi-content">
              <div className="kpi-label">{t('reports.kpi.securityEvents')}</div>
              <div className="kpi-value">{kpi.security_events}</div>
              <div className="kpi-subtext">Telemetry & SIEM Sensor Alerts</div>
            </div>
          </div>

          <div className="soc-kpi-card">
            <div className="kpi-icon-wrap kpi-purple">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
            </div>
            <div className="kpi-content">
              <div className="kpi-label">{t('reports.kpi.defenseDecisions')}</div>
              <div className="kpi-value">{kpi.defense_decisions}</div>
              <div className="kpi-subtext">Safety Gate Policy Evaluations</div>
            </div>
          </div>

          <div className="soc-kpi-card">
            <div className="kpi-icon-wrap kpi-amber">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <polygon points="10 8 16 12 10 16 10 8" />
              </svg>
            </div>
            <div className="kpi-content">
              <div className="kpi-label">{t('reports.kpi.simulatedActions')}</div>
              <div className="kpi-value">
                <span className="sim-count">{kpi.simulated_actions} Sim</span>
                <span className="kpi-separator">/</span>
                <span className="enf-count">{kpi.enforced_actions} Enf</span>
              </div>
              <div className="kpi-subtext">{t('reports.kpi.enforcementModeTag')}</div>
            </div>
          </div>
        </div>

        {/* Section 3: Report Configuration & Multi-Tier Filter Toolbar */}
        <div className="report-control-card soc-toolbar-card">
          <div className="control-card-header">
            <h3 className="control-card-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="4" y1="21" x2="4" y2="14" />
                <line x1="4" y1="10" x2="4" y2="3" />
                <line x1="12" y1="21" x2="12" y2="12" />
                <line x1="12" y1="8" x2="12" y2="3" />
                <line x1="20" y1="21" x2="20" y2="16" />
                <line x1="20" y1="12" x2="20" y2="3" />
                <line x1="1" y1="14" x2="7" y2="14" />
                <line x1="9" y1="8" x2="15" y2="8" />
                <line x1="17" y1="16" x2="23" y2="16" />
              </svg>
              {t('reports.controlCardTitle')}
            </h3>
            <span className="telemetry-badge telemetry-count">
              {t('reports.recordsAvailable', { count: reportData.length })}
            </span>
          </div>

          {/* Row 1: Primary Controls */}
          <div className="control-card-row-primary">
            {/* Report Type */}
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

            {/* Time Range Preset */}
            <div className="control-item select-item">
              <label htmlFor="time-range">{t('reports.timeRangeLabel')}</label>
              <select
                id="time-range"
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
              >
                <option value="last_30d">{t('reports.preset30d')}</option>
                <option value="last_24h">{t('reports.preset24h')}</option>
                <option value="last_7d">{t('reports.preset7d')}</option>
                <option value="this_month">{t('reports.presetThisMonth')}</option>
                <option value="prev_month">{t('reports.presetPrevMonth')}</option>
                <option value="all">{t('reports.presetAll')}</option>
                <option value="custom">{t('reports.presetCustom')}</option>
              </select>
            </div>

            {/* Custom Range Inputs (Only when Custom is selected) */}
            {timeRange === 'custom' && (
              <>
                <div className="control-item date-item">
                  <label htmlFor="start-date">{t('reports.startDateLabel')}</label>
                  <input
                    type="date"
                    id="start-date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                  />
                </div>
                <div className="control-item date-item">
                  <label htmlFor="end-date">{t('reports.endDateLabel')}</label>
                  <input
                    type="date"
                    id="end-date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                  />
                </div>
              </>
            )}

            {/* Action Buttons */}
            <div className="control-actions-row">
              <button
                type="button"
                className="btn-apply-filters"
                onClick={fetchReportData}
                disabled={isLoading}
                title={t('reports.filters.applyFilters')}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                {t('reports.filters.applyFilters')}
              </button>

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
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
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

          {/* Row 2: Advanced Contextual Filters */}
          <div className="control-card-row-advanced">
            {reportType === 'anomalies' ? (
              <>
                <div className="control-item filter-sm">
                  <label htmlFor="severity-filter">{t('reports.filters.severity')}</label>
                  <select
                    id="severity-filter"
                    value={severity}
                    onChange={(e) => setSeverity(e.target.value)}
                  >
                    <option value="all">{t('reports.filters.allSeverities')}</option>
                    <option value="high">{t('reports.filters.highCritical')}</option>
                    <option value="medium">{t('reports.filters.medium')}</option>
                    <option value="low">{t('reports.filters.low')}</option>
                  </select>
                </div>

                <div className="control-item filter-ip">
                  <label htmlFor="source-ip-search">{t('reports.tableHeaders.sourceIp')}</label>
                  <input
                    type="text"
                    id="source-ip-search"
                    placeholder={t('reports.filters.searchIp')}
                    value={sourceIp}
                    onChange={(e) => setSourceIp(e.target.value)}
                  />
                </div>
              </>
            ) : (
              <>
                <div className="control-item filter-sm">
                  <label htmlFor="action-type-filter">{t('reports.filters.actionType')}</label>
                  <select
                    id="action-type-filter"
                    value={actionType}
                    onChange={(e) => setActionType(e.target.value)}
                  >
                    <option value="all">{t('reports.filters.allActions')}</option>
                    <option value="block">Block</option>
                    <option value="rate limit">Rate Limit</option>
                    <option value="redirect">Redirect</option>
                    <option value="unblock">Unblock</option>
                  </select>
                </div>

                <div className="control-item filter-sm">
                  <label htmlFor="initiation-source-filter">{t('reports.filters.initiationSource')}</label>
                  <select
                    id="initiation-source-filter"
                    value={initiationSource}
                    onChange={(e) => setInitiationSource(e.target.value)}
                  >
                    <option value="all">{t('reports.filters.allSources')}</option>
                    <option value="automated">{t('reports.filters.automatedSource')}</option>
                    <option value="admin">{t('reports.filters.adminSource')}</option>
                  </select>
                </div>

                <div className="control-item filter-ip">
                  <label htmlFor="target-ip-search">{t('reports.tableHeaders.targetIp')}</label>
                  <input
                    type="text"
                    id="target-ip-search"
                    placeholder={t('reports.filters.searchIp')}
                    value={sourceIp}
                    onChange={(e) => setSourceIp(e.target.value)}
                  />
                </div>
              </>
            )}

            <button
              type="button"
              className="btn-reset-filters"
              onClick={handleResetFilters}
              title={t('reports.filters.resetFilters')}
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
              {t('reports.filters.resetFilters')}
            </button>
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

        {/* Section 4: SOC Report Preview Table Card */}
        <div className="report-preview-card soc-table-card">
          <div className="preview-card-header">
            <div className="preview-title-group">
              <h3 className="preview-card-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
                {t('reports.auditReportTitle', { type: reportTypeTitle })}
              </h3>
              <p className="preview-card-subtitle">
                {displayPeriod} &bull; {reportData.length} {t('reports.recordsAvailable', { count: reportData.length })}
              </p>
            </div>
            <div className="preview-badges">
              <span className="telemetry-badge telemetry-primary">
                {t('reports.formatBadge')}
              </span>
              <span className="telemetry-badge telemetry-count">
                {t('reports.recordsAvailable', { count: reportData.length })}
              </span>
            </div>
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
                      <th style={{ width: 45 }}>#</th>
                      <th onClick={() => handleSort('timestamp')} style={{ cursor: 'pointer' }}>
                        {t('reports.tableHeaders.time')} {sortField === 'timestamp' && (sortAsc ? '▲' : '▼')}
                      </th>
                      <th>{t('reports.tableHeaders.sourceIp')}</th>
                      <th>{t('reports.tableHeaders.destinationIp')}</th>
                      <th>{t('reports.tableHeaders.event')}</th>
                      <th onClick={() => handleSort('score')} style={{ cursor: 'pointer' }}>
                        {t('reports.tableHeaders.score')} {sortField === 'score' && (sortAsc ? '▲' : '▼')}
                      </th>
                      <th>{t('reports.tableHeaders.severity')}</th>
                      <th>{t('reports.tableHeaders.source')}</th>
                    </tr>
                  ) : (
                    <tr>
                      <th style={{ width: 45 }}>#</th>
                      <th onClick={() => handleSort('timestamp')} style={{ cursor: 'pointer' }}>
                        {t('reports.tableHeaders.time')} {sortField === 'timestamp' && (sortAsc ? '▲' : '▼')}
                      </th>
                      <th>{t('reports.tableHeaders.actionType')}</th>
                      <th>{t('reports.tableHeaders.targetIp')}</th>
                      <th>{t('reports.tableHeaders.initiation')}</th>
                      <th>{t('reports.tableHeaders.mode')}</th>
                      <th>{t('reports.tableHeaders.status')}</th>
                      <th>{t('reports.tableHeaders.reason')}</th>
                    </tr>
                  )}
                </thead>
                <tbody>
                  {paginatedData.length === 0 ? (
                    <tr>
                      <td colSpan="10" className="reports-empty-cell">
                        <div className="reports-empty-container">
                          <svg className="empty-state-icon" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                            <line x1="16" y1="2" x2="16" y2="6" />
                            <line x1="8" y1="2" x2="8" y2="6" />
                            <line x1="3" y1="10" x2="21" y2="10" />
                          </svg>
                          <div className="empty-title">{t('reports.empty.title')}</div>
                          <div className="empty-period-note">{t('reports.empty.desc')}</div>
                          <div className="empty-actions-row">
                            <button
                              type="button"
                              className="btn-empty-action"
                              onClick={() => setTimeRange('last_30d')}
                            >
                              {t('reports.empty.expand30d')}
                            </button>
                            <button
                              type="button"
                              className="btn-empty-action"
                              onClick={() => setTimeRange('all')}
                            >
                              {t('reports.empty.viewAll')}
                            </button>
                            <button
                              type="button"
                              className="btn-empty-action btn-empty-reset"
                              onClick={handleResetFilters}
                            >
                              {t('reports.empty.reset')}
                            </button>
                          </div>
                        </div>
                      </td>
                    </tr>
                  ) : reportType === 'anomalies' ? (
                    paginatedData.map((row, index) => {
                      const score = Number(row.score || 0);
                      let scoreClass = 'score-low';
                      let sevClass = 'sev-low';
                      if (score >= 85) {
                        scoreClass = 'score-critical';
                        sevClass = 'sev-critical';
                      } else if (score >= 70) {
                        scoreClass = 'score-high';
                        sevClass = 'sev-high';
                      } else if (score >= 40) {
                        scoreClass = 'score-medium';
                        sevClass = 'sev-medium';
                      }

                      const globalIdx = (currentPage - 1) * pageSize + index + 1;

                      return (
                        <tr key={index}>
                          <td style={{ color: 'var(--text-muted, #94a3b8)', fontSize: 12 }}>{globalIdx}</td>
                          <td style={{ whiteSpace: 'nowrap', fontFamily: 'monospace', fontSize: 12.5, color: 'var(--text-secondary)' }}>
                            {row.timestamp}
                          </td>
                          <td>
                            <span className="ip-chip">{row.source_ip || 'N/A'}</span>
                          </td>
                          <td>
                            <span className="ip-chip ip-dst-chip">{row.destination_ip || '0.0.0.0'}</span>
                          </td>
                          <td>
                            <span className="event-chip">{row.event || 'Unknown'}</span>
                          </td>
                          <td>
                            <span className={`score-badge ${scoreClass}`}>
                              {row.score}
                            </span>
                          </td>
                          <td>
                            <span className={`severity-badge ${sevClass}`}>
                              {row.severity || (score >= 70 ? 'High' : score >= 40 ? 'Medium' : 'Low')}
                            </span>
                          </td>
                          <td>
                            <span className="sensor-chip">{row.source || 'Netflow'}</span>
                          </td>
                        </tr>
                      );
                    })
                  ) : (
                    paginatedData.map((row, index) => {
                      const actionLower = String(row.action_type || '').toLowerCase();
                      let actionClass = 'action-chip-default';
                      if (actionLower.includes('block')) actionClass = 'action-chip-block';
                      else if (actionLower.includes('rate')) actionClass = 'action-chip-rate';
                      else if (actionLower.includes('redirect')) actionClass = 'action-chip-redirect';
                      else if (actionLower.includes('unblock')) actionClass = 'action-chip-unblock';

                      const isAutomated = String(row.admin_or_automated || '').toLowerCase().includes('auto');
                      const globalIdx = (currentPage - 1) * pageSize + index + 1;

                      return (
                        <tr key={index}>
                          <td style={{ color: 'var(--text-muted, #94a3b8)', fontSize: 12 }}>{globalIdx}</td>
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
                          <td>
                            <span className={`source-badge ${isAutomated ? 'source-badge-automated' : 'source-badge-manual'}`}>
                              {isAutomated ? t('decisionLogs.automatedSource') : t('decisionLogs.manualSource')}
                            </span>
                          </td>
                          <td>
                            <span className="mode-chip mode-dry-run">
                              DRY_RUN (SIMULATED)
                            </span>
                          </td>
                          <td>
                            <span className="status-chip status-staged">
                              STAGED_POLICY
                            </span>
                          </td>
                          <td style={{ fontSize: 13, maxWidth: 300 }}>{row.reason}</td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>

              {/* Pagination Controls */}
              {sortedData.length > 0 && (
                <div className="soc-table-pagination">
                  <div className="pagination-info">
                    Showing {(currentPage - 1) * pageSize + 1} -{' '}
                    {Math.min(currentPage * pageSize, sortedData.length)} of {sortedData.length} records
                  </div>
                  <div className="pagination-controls">
                    <select
                      className="page-size-select"
                      value={pageSize}
                      onChange={(e) => {
                        setPageSize(Number(e.target.value));
                        setCurrentPage(1);
                      }}
                    >
                      <option value={10}>10 / page</option>
                      <option value={25}>25 / page</option>
                      <option value={50}>50 / page</option>
                      <option value={100}>100 / page</option>
                    </select>

                    <button
                      type="button"
                      className="btn-page-nav"
                      onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                      disabled={currentPage <= 1}
                    >
                      &lsaquo; Prev
                    </button>
                    <span className="page-indicator">
                      {currentPage} / {totalPages}
                    </span>
                    <button
                      type="button"
                      className="btn-page-nav"
                      onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                      disabled={currentPage >= totalPages}
                    >
                      Next &rsaquo;
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Reports;
