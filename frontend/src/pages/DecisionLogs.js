import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config/apiConfig';
import { useLanguage } from '../i18n/LanguageContext';
import './DecisionLogs.css';

function DecisionLogs() {
  const { t } = useLanguage();
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [actionTypeFilter, setActionTypeFilter] = useState('all');
  const [adminTypeFilter, setAdminTypeFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    axios
      .get(`${API_BASE_URL}/api/get-actions`)
      .then((response) => {
        const items = Array.isArray(response.data?.data)
          ? response.data.data
          : [];
        setLogs(items);
        setFilteredLogs(items);
      })
      .catch(() => {
        setLogs([]);
        setFilteredLogs([]);
      });
  }, []);

  useEffect(() => {
    let filtered = logs;

    if (actionTypeFilter !== 'all') {
      filtered = filtered.filter((log) =>
        String(log.action_type || '')
          .toLowerCase()
          .includes(actionTypeFilter)
      );
    }

    if (adminTypeFilter !== 'all') {
      filtered = filtered.filter(
        (log) =>
          String(log.admin_or_automated || '').toLowerCase() === adminTypeFilter
      );
    }

    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      filtered = filtered.filter(
        (log) =>
          String(log.source_ip || '').toLowerCase().includes(q) ||
          String(log.reason || '').toLowerCase().includes(q) ||
          String(log.action_type || '').toLowerCase().includes(q)
      );
    }

    setFilteredLogs(filtered);
  }, [actionTypeFilter, adminTypeFilter, searchTerm, logs]);

  const handleResetFilters = () => {
    setActionTypeFilter('all');
    setAdminTypeFilter('all');
    setSearchTerm('');
  };

  const activeFiltersCount =
    (actionTypeFilter !== 'all' ? 1 : 0) +
    (adminTypeFilter !== 'all' ? 1 : 0) +
    (searchTerm.trim() ? 1 : 0);

  return (
    <div className="decision-logs">
      <div className="decision-logs-container">
        {/* Section A: Header */}
        <div className="decision-header">
          <div className="decision-header-left">
            <h2 className="decision-title">{t('decisionLogs.title')}</h2>
            <p className="decision-subtitle">{t('decisionLogs.subtitle')}</p>
          </div>
          <div className="decision-header-badges">
            <span className="telemetry-badge">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <ellipse cx="12" cy="5" rx="9" ry="3" />
                <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
                <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
              </svg>
              {t('decisionLogs.storageBadge')}
            </span>
            <span className="telemetry-badge telemetry-defense">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
              {t('decisionLogs.defenseModeBadge')}
            </span>
            <span className="telemetry-badge telemetry-count">
              {t('decisionLogs.showingRecords', {
                filtered: filteredLogs.length,
                total: logs.length,
              })}
            </span>
          </div>
        </div>

        {/* Section B: Dedicated Filter Toolbar Card */}
        <div className="decision-filter-card">
          <div className="filter-card-header">
            <h3 className="filter-card-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
              </svg>
              {t('decisionLogs.filterCardTitle')}
            </h3>
            {activeFiltersCount > 0 && (
              <span className="telemetry-badge telemetry-defense">
                {t('decisionLogs.activeFiltersCount', { count: activeFiltersCount })}
              </span>
            )}
          </div>
          <div className="filter-controls-row">
            <div className="filter-control-group search-group">
              <label htmlFor="search-kw">{t('decisionLogs.searchLabel')}</label>
              <input
                id="search-kw"
                type="text"
                placeholder={t('decisionLogs.searchPlaceholder')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            <div className="filter-control-group">
              <label htmlFor="log-type">{t('decisionLogs.filterAction')}</label>
              <select
                id="log-type"
                value={actionTypeFilter}
                onChange={(e) => setActionTypeFilter(e.target.value)}
              >
                <option value="all">{t('decisionLogs.allActions')}</option>
                <option value="block">{t('decisionLogs.blockAction')}</option>
                <option value="rate">{t('decisionLogs.rateAction')}</option>
                <option value="redirect">{t('decisionLogs.redirectAction')}</option>
                <option value="unblock">{t('decisionLogs.unblockAction')}</option>
              </select>
            </div>

            <div className="filter-control-group">
              <label htmlFor="admin-type">{t('decisionLogs.filterSource')}</label>
              <select
                id="admin-type"
                value={adminTypeFilter}
                onChange={(e) => setAdminTypeFilter(e.target.value)}
              >
                <option value="all">{t('decisionLogs.allSources')}</option>
                <option value="automated">{t('decisionLogs.automatedSource')}</option>
                <option value="admin">{t('decisionLogs.manualSource')}</option>
              </select>
            </div>

            {activeFiltersCount > 0 && (
              <button
                type="button"
                className="btn-reset-filters"
                onClick={handleResetFilters}
                title={t('decisionLogs.resetFilters')}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                  <path d="M3 3v5h5" />
                </svg>
                {t('decisionLogs.resetFilters')}
              </button>
            )}
          </div>
        </div>

        {/* Section C: Dedicated Audit Records Card */}
        <div className="decision-table-card">
          <div className="table-card-header">
            <h3 className="table-card-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
                <polyline points="10 9 9 9 8 9" />
              </svg>
              {t('decisionLogs.tableCardTitle')}
            </h3>
            <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              {t('decisionLogs.showingRecords', {
                filtered: filteredLogs.length,
                total: logs.length,
              })}
            </span>
          </div>

          <div className="decision-table-wrapper">
            <table className="decision-audit-table">
              <thead>
                <tr>
                  <th>{t('decisionLogs.tableHeaders.time')}</th>
                  <th>{t('decisionLogs.tableHeaders.actionType')}</th>
                  <th>{t('decisionLogs.tableHeaders.reason')}</th>
                  <th>{t('decisionLogs.tableHeaders.sourceIp')}</th>
                  <th>{t('decisionLogs.tableHeaders.enforcement')}</th>
                </tr>
              </thead>
              <tbody>
                {filteredLogs.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="table-empty-cell">
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 }}>
                        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="1.5">
                          <circle cx="11" cy="11" r="8" />
                          <line x1="21" y1="21" x2="16.65" y2="16.65" />
                        </svg>
                        <span>{t('decisionLogs.noMatchingLogs')}</span>
                        {activeFiltersCount > 0 && (
                          <button
                            type="button"
                            className="btn-reset-filters"
                            onClick={handleResetFilters}
                            style={{ marginTop: 6 }}
                          >
                            {t('decisionLogs.resetFilters')}
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ) : (
                  filteredLogs.map((log, index) => {
                    const actionLower = String(log.action_type || '').toLowerCase();
                    let actionChipClass = 'action-chip-default';
                    if (actionLower.includes('block')) {
                      actionChipClass = 'action-chip-block';
                    } else if (actionLower.includes('rate')) {
                      actionChipClass = 'action-chip-rate';
                    } else if (actionLower.includes('redirect')) {
                      actionChipClass = 'action-chip-redirect';
                    } else if (actionLower.includes('unblock')) {
                      actionChipClass = 'action-chip-unblock';
                    }

                    const isAutomated =
                      String(log.admin_or_automated || '').toLowerCase() === 'automated';

                    const isHistoricalRate =
                      actionLower.includes('rate') &&
                      (String(log.reason || '').includes('50 bps') ||
                        String(log.reason || '').includes('50000 bps') ||
                        String(log.timestamp || '').startsWith('2024') ||
                        String(log.timestamp || '').startsWith('2025-01-12') ||
                        String(log.timestamp || '').startsWith('2025-01-13'));

                    return (
                      <tr key={index}>
                        <td className="timestamp-cell">{log.timestamp}</td>
                        <td>
                          <span className={`action-chip ${actionChipClass}`}>
                            {log.action_type}
                          </span>
                        </td>
                        <td className="reason-cell">
                          {log.reason}
                          {isHistoricalRate && (
                            <span className="historical-tag" title="Historical audit log entry from earlier experiments">
                              {t('decisionLogs.historicalBadge')}
                            </span>
                          )}
                        </td>
                        <td>
                          <span className="ip-chip">{log.source_ip || 'N/A'}</span>
                        </td>
                        <td>
                          <div className="enforcement-cell">
                            <span
                              className={`source-badge ${
                                isAutomated ? 'source-badge-automated' : 'source-badge-manual'
                              }`}
                            >
                              {isAutomated
                                ? t('decisionLogs.automatedSource')
                                : t('decisionLogs.manualSource')}
                            </span>
                            <span
                              className="enforcement-subtext"
                              title={t('decisionLogs.enforcementTooltip')}
                            >
                              {t('decisionLogs.enforcementDryRun')}
                            </span>
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DecisionLogs;
