import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config/apiConfig';
import { useLanguage } from '../i18n/LanguageContext';

function DecisionLogs() {
  const { language, t } = useLanguage();
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

  return (
    <div className="decision-logs">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', marginBottom: 20 }}>
        <div>
          <h2>
            {t('decisionLogs.title')}
          </h2>
          <p style={{ margin: '4px 0 0 0', color: 'var(--text-secondary)', fontSize: 14 }}>
            {language === 'vi'
              ? 'Lịch sử kiểm toán các quyết định phòng vệ, nguồn phát sinh và mức độ thực thi'
              : 'Audit trail of defense policy decisions, initiation sources, and enforcement status'}
          </p>
        </div>
        <span style={{ fontSize: 13, color: 'var(--text-secondary)', fontWeight: 600, background: 'var(--bg-surface-subtle)', padding: '6px 12px', borderRadius: 6, border: '1px solid var(--border-color)' }}>
          {t('decisionLogs.showingRecords', { filtered: filteredLogs.length, total: logs.length })}
        </span>
      </div>

      {/* Filter Bar */}
      <div className="filter-section">
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ flex: '1 1 240px' }}>
            <label htmlFor="search-kw" style={{ fontWeight: 600, fontSize: 13, marginRight: 6, display: 'block', marginBottom: 4 }}>
              {t('decisionLogs.searchLabel')}
            </label>
            <input
              id="search-kw"
              type="text"
              placeholder={t('decisionLogs.searchPlaceholder')}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ width: '100%', maxWidth: '320px', padding: '7px 10px', border: '1px solid var(--input-border)', borderRadius: 6, fontSize: 13, background: 'var(--input-bg)', color: 'var(--input-text)' }}
            />
          </div>

          <div>
            <label htmlFor="log-type" style={{ fontWeight: 600, fontSize: 13, marginRight: 6, display: 'block', marginBottom: 4 }}>
              {t('decisionLogs.filterAction')}
            </label>
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

          <div>
            <label htmlFor="admin-type" style={{ fontWeight: 600, fontSize: 13, marginRight: 6, display: 'block', marginBottom: 4 }}>
              {t('decisionLogs.filterSource')}
            </label>
            <select
              id="admin-type"
              value={adminTypeFilter}
              onChange={(e) => setAdminTypeFilter(e.target.value)}
            >
              <option value="all">{t('decisionLogs.allSources')}</option>
              <option value="admin">{t('decisionLogs.manualSource')}</option>
              <option value="automated">{t('decisionLogs.automatedSource')}</option>
            </select>
          </div>
        </div>
      </div>

      {/* Decision Table */}
      <div style={{ overflowX: 'auto' }}>
        <table>
          <thead>
            <tr>
              <th>
                {t('decisionLogs.tableHeaders.time')}
              </th>
              <th>
                {t('decisionLogs.tableHeaders.actionType')}
              </th>
              <th>
                {t('decisionLogs.tableHeaders.reason')}
              </th>
              <th>
                {t('decisionLogs.tableHeaders.sourceIp')}
              </th>
              <th>
                {t('decisionLogs.tableHeaders.enforcement')}
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredLogs.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center', padding: '36px', color: 'var(--text-muted)' }}>
                  {t('decisionLogs.noMatchingLogs')}
                </td>
              </tr>
            ) : (
              filteredLogs.map((log, index) => {
                const isBlock = String(log.action_type || '').toLowerCase().includes('block');
                const isAutomated = String(log.admin_or_automated || '').toLowerCase() === 'automated';
                return (
                  <tr key={index}>
                    <td style={{ whiteSpace: 'nowrap', fontSize: 13 }}>
                      {log.timestamp}
                    </td>
                    <td>
                      <span
                        style={{
                          display: 'inline-block',
                          padding: '3px 8px',
                          borderRadius: 4,
                          fontSize: 11,
                          fontWeight: 700,
                          background: isBlock ? '#fee2e2' : '#e0f2fe',
                          color: isBlock ? '#991b1b' : '#0369a1',
                        }}
                      >
                        {log.action_type}
                      </span>
                    </td>
                    <td style={{ fontSize: 13 }}>
                      {log.reason}
                    </td>
                    <td>
                      <code>{log.source_ip || 'N/A'}</code>
                    </td>
                    <td>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        <span
                          style={{
                            display: 'inline-block',
                            padding: '2px 6px',
                            borderRadius: 4,
                            fontSize: 11,
                            fontWeight: 700,
                            background: isAutomated ? '#ecfdf5' : '#f3e8ff',
                            color: isAutomated ? '#065f46' : '#6b21a8',
                            width: 'fit-content'
                          }}
                        >
                          {isAutomated ? t('decisionLogs.automatedSource') : t('decisionLogs.manualSource')}
                        </span>
                        <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                          {t('decisionLogs.unverifiedNotice')}
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
  );
}

export default DecisionLogs;
