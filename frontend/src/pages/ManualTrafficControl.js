import React, { useState } from 'react';
import axios from 'axios';
import {
  API_BASE_URL,
  getApiHeaders,
  isValidIpAddress,
} from '../config/apiConfig';
import { useLanguage } from '../i18n/LanguageContext';

function ManualTrafficControl() {
  const { language, t } = useLanguage();
  const [action, setAction] = useState('block');
  const [formData, setFormData] = useState({});
  const [rateLimitBps, setRateLimitBps] = useState('');
  const [hostIp, setHostIp] = useState('');
  const [redirectIp, setRedirectIp] = useState('');
  const [dryRun, setDryRun] = useState(true);
  const [statusMessage, setStatusMessage] = useState('');
  const [telemetry, setTelemetry] = useState(null);

  const resetForm = () => {
    setFormData({});
    setRateLimitBps('');
    setHostIp('');
    setRedirectIp('');
    setStatusMessage('');
    setTelemetry(null);
  };

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatusMessage('');

    let endpoint = '';
    let requestBody = { dry_run: dryRun };

    switch (action) {
      case 'block':
      case 'allow':
        if (
          !isValidIpAddress(formData.srcIp) &&
          !isValidIpAddress(formData.dstIp)
        ) {
          setStatusMessage(
            language === 'vi'
              ? 'Lỗi xác thực: Vui lòng nhập địa chỉ IP nguồn hoặc IP đích hợp lệ.'
              : 'Validation Error: Please enter a valid Source IP or Destination IP.'
          );
          return;
        }
        endpoint = `/api/${action}`;
        requestBody = { ...formData, dry_run: dryRun };
        break;
      case 'rate-limit':
        if (!isValidIpAddress(hostIp)) {
          setStatusMessage(
            language === 'vi'
              ? 'Lỗi xác thực: Vui lòng nhập địa chỉ IP Host hợp lệ.'
              : 'Validation Error: Please enter a valid Host IP.'
          );
          return;
        }
        if (!rateLimitBps || Number(rateLimitBps) <= 0) {
          setStatusMessage(
            language === 'vi'
              ? 'Lỗi xác thực: Giới hạn tốc độ (bps) phải là số dương lớn hơn 0.'
              : 'Validation Error: Rate Limit (bps) must be a positive number.'
          );
          return;
        }
        endpoint = '/api/rate-limit';
        requestBody = { hostIp, rateLimitBps, dry_run: dryRun };
        break;
      case 'redirect':
        if (!isValidIpAddress(formData.srcIp) || !isValidIpAddress(redirectIp)) {
          setStatusMessage(
            language === 'vi'
              ? 'Lỗi xác thực: Cả IP nguồn và IP đích chuyển hướng đều phải là địa chỉ IP hợp lệ.'
              : 'Validation Error: Both Source IP and Redirect IP must be valid IP addresses.'
          );
          return;
        }
        endpoint = '/api/redirect';
        requestBody = { ...formData, redirectIp, dry_run: dryRun };
        break;
      case 'unblock':
        if (
          !isValidIpAddress(formData.srcIp) &&
          !isValidIpAddress(formData.dstIp)
        ) {
          setStatusMessage(
            language === 'vi'
              ? 'Lỗi xác thực: Vui lòng nhập IP nguồn hoặc IP đích cần gỡ chặn.'
              : 'Validation Error: Please enter a valid Source IP or Destination IP to unblock.'
          );
          return;
        }
        endpoint = '/api/unblock';
        requestBody = { ...formData, dry_run: dryRun };
        break;
      case 'rollback':
        if (!isValidIpAddress(formData.srcIp)) {
          setStatusMessage(
            language === 'vi'
              ? 'Lỗi xác thực: Vui lòng nhập địa chỉ IP nguồn để hoàn tác quy tắc.'
              : 'Validation Error: Please enter a valid Source IP to roll back.'
          );
          return;
        }
        endpoint = '/api/defense/rollback';
        requestBody = { srcIp: formData.srcIp, dry_run: dryRun };
        break;
      default:
        setStatusMessage(language === 'vi' ? 'Hành động không hợp lệ' : 'Invalid action selected');
        return;
    }

    try {
      const response = await axios.post(
        `${API_BASE_URL}${endpoint}`,
        requestBody,
        { headers: getApiHeaders() }
      );
      setStatusMessage(response.data.message || (language === 'vi' ? 'Yêu cầu đã được xử lý' : 'Action processed'));
      setTelemetry(response.data);
    } catch (error) {
      const errData = error.response?.data;
      setStatusMessage(
        errData?.error || errData?.message || (language === 'vi' ? 'Thao tác không thành công' : 'Failed to apply action')
      );
      setTelemetry(errData || null);
    }
  };

  const renderFields = () => {
    switch (action) {
      case 'block':
      case 'allow':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {/* L2/L3 Endpoints */}
            <div style={{ background: 'var(--bg-surface-subtle)', padding: 16, borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <h4 style={{ margin: '0 0 12px 0', color: 'var(--text-primary)', fontSize: 14, fontWeight: 700 }}>
                {t('manualControl.endpointSection')}
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14 }}>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block', color: 'var(--text-secondary)' }}>
                    {t('manualControl.sourceIp')}
                  </label>
                  <input
                    type="text"
                    value={formData.srcIp || ''}
                    placeholder={t('manualControl.sourceIpPlaceholder')}
                    onChange={(e) => handleInputChange('srcIp', e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid var(--input-border)', background: 'var(--input-bg)', color: 'var(--input-text)' }}
                  />
                </div>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block', color: 'var(--text-secondary)' }}>
                    {t('manualControl.destinationIp')}
                  </label>
                  <input
                    type="text"
                    value={formData.dstIp || ''}
                    placeholder={t('manualControl.destinationIpPlaceholder')}
                    onChange={(e) => handleInputChange('dstIp', e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid var(--input-border)', background: 'var(--input-bg)', color: 'var(--input-text)' }}
                  />
                </div>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block', color: 'var(--text-secondary)' }}>
                    {t('manualControl.sourceMac')}
                  </label>
                  <input
                    type="text"
                    value={formData.srcMac || ''}
                    placeholder="vd: 00:00:00:00:00:01"
                    onChange={(e) => handleInputChange('srcMac', e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid var(--input-border)', background: 'var(--input-bg)', color: 'var(--input-text)' }}
                  />
                </div>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block', color: 'var(--text-secondary)' }}>
                    {t('manualControl.destinationMac')}
                  </label>
                  <input
                    type="text"
                    value={formData.dstMac || ''}
                    placeholder="vd: 00:00:00:00:00:02"
                    onChange={(e) => handleInputChange('dstMac', e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid var(--input-border)', background: 'var(--input-bg)', color: 'var(--input-text)' }}
                  />
                </div>
              </div>
            </div>

            {/* Protocol & Match Criteria */}
            <div style={{ background: 'var(--bg-surface-subtle)', padding: 16, borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <h4 style={{ margin: '0 0 12px 0', color: 'var(--text-primary)', fontSize: 14, fontWeight: 700 }}>
                {t('manualControl.flowMatchSection')}
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14 }}>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block', color: 'var(--text-secondary)' }}>
                    {t('manualControl.protocol')}
                  </label>
                  <select
                    value={formData.ipProto || ''}
                    onChange={(e) => handleInputChange('ipProto', e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid var(--input-border)', background: 'var(--input-bg)', color: 'var(--input-text)' }}
                  >
                    <option value="">{t('manualControl.protocolAll')}</option>
                    <option value="TCP">{t('manualControl.protocolTcp')}</option>
                    <option value="UDP">{t('manualControl.protocolUdp')}</option>
                    <option value="ICMP">{t('manualControl.protocolIcmp')}</option>
                  </select>
                </div>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block', color: 'var(--text-secondary)' }}>
                    {t('manualControl.sourcePort')}
                  </label>
                  <input
                    type="text"
                    value={formData.srcPort || ''}
                    placeholder="vd: 80, 443"
                    onChange={(e) => handleInputChange('srcPort', e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid var(--input-border)', background: 'var(--input-bg)', color: 'var(--input-text)' }}
                  />
                </div>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block', color: 'var(--text-secondary)' }}>
                    {t('manualControl.destinationPort')}
                  </label>
                  <input
                    type="text"
                    value={formData.dstPort || ''}
                    placeholder="vd: 80, 443"
                    onChange={(e) => handleInputChange('dstPort', e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid var(--input-border)', background: 'var(--input-bg)', color: 'var(--input-text)' }}
                  />
                </div>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block', color: 'var(--text-secondary)' }}>
                    {t('manualControl.prefixLength')}
                  </label>
                  <input
                    type="number"
                    value={formData.prefixLength || ''}
                    placeholder="32"
                    min="0"
                    max="32"
                    onChange={(e) => handleInputChange('prefixLength', e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid var(--input-border)', background: 'var(--input-bg)', color: 'var(--input-text)' }}
                  />
                </div>
              </div>
            </div>
          </div>
        );

      case 'rate-limit':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <div style={{ background: 'var(--bg-surface-subtle)', padding: 16, borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <h4 style={{ margin: '0 0 12px 0', color: 'var(--text-primary)', fontSize: 14, fontWeight: 700 }}>
                {t('manualControl.endpointSection')}
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14 }}>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block', color: 'var(--text-secondary)' }}>
                    {t('manualControl.hostIp')}
                  </label>
                  <input
                    type="text"
                    placeholder="vd: 10.0.0.1"
                    value={hostIp}
                    onChange={(e) => setHostIp(e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid var(--input-border)', background: 'var(--input-bg)', color: 'var(--input-text)' }}
                  />
                </div>
              </div>
            </div>

            <div style={{ background: 'var(--bg-surface-subtle)', padding: 16, borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <h4 style={{ margin: '0 0 12px 0', color: 'var(--text-primary)', fontSize: 14, fontWeight: 700 }}>
                {t('manualControl.rateLimitSection')}
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14 }}>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block', color: 'var(--text-secondary)' }}>
                    {t('manualControl.rateLimitValue')}
                  </label>
                  <input
                    type="number"
                    placeholder={t('manualControl.rateLimitPlaceholder')}
                    value={rateLimitBps}
                    onChange={(e) => setRateLimitBps(e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid var(--input-border)', background: 'var(--input-bg)', color: 'var(--input-text)' }}
                  />
                </div>
              </div>
              <p style={{ margin: '10px 0 0 0', fontSize: 12, color: 'var(--text-muted)' }}>
                ℹ️ {t('manualControl.rateLimitNote')}
              </p>
            </div>
          </div>
        );

      case 'redirect':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <div style={{ background: 'var(--bg-surface-subtle)', padding: 16, borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <h4 style={{ margin: '0 0 12px 0', color: 'var(--text-primary)', fontSize: 14, fontWeight: 700 }}>
                {t('manualControl.endpointSection')}
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14 }}>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block', color: 'var(--text-secondary)' }}>
                    {t('manualControl.sourceIp')}
                  </label>
                  <input
                    type="text"
                    placeholder={t('manualControl.sourceIpPlaceholder')}
                    value={formData.srcIp || ''}
                    onChange={(e) => handleInputChange('srcIp', e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid var(--input-border)', background: 'var(--input-bg)', color: 'var(--input-text)' }}
                  />
                </div>
              </div>
            </div>

            <div style={{ background: 'var(--bg-surface-subtle)', padding: 16, borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <h4 style={{ margin: '0 0 12px 0', color: 'var(--text-primary)', fontSize: 14, fontWeight: 700 }}>
                {t('manualControl.redirectSection')}
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14 }}>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block', color: 'var(--text-secondary)' }}>
                    {t('manualControl.redirectIp')}
                  </label>
                  <input
                    type="text"
                    placeholder="vd: 10.0.0.6 (Honeypot)"
                    value={redirectIp}
                    onChange={(e) => setRedirectIp(e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid var(--input-border)', background: 'var(--input-bg)', color: 'var(--input-text)' }}
                  />
                </div>
              </div>
            </div>
          </div>
        );

      case 'unblock':
      case 'rollback':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <div style={{ background: 'var(--bg-surface-subtle)', padding: 16, borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <h4 style={{ margin: '0 0 12px 0', color: 'var(--text-primary)', fontSize: 14, fontWeight: 700 }}>
                {t('manualControl.endpointSection')}
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14 }}>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block', color: 'var(--text-secondary)' }}>
                    {t('manualControl.sourceIp')}
                  </label>
                  <input
                    type="text"
                    placeholder={t('manualControl.sourceIpPlaceholder')}
                    value={formData.srcIp || ''}
                    onChange={(e) => handleInputChange('srcIp', e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid var(--input-border)', background: 'var(--input-bg)', color: 'var(--input-text)' }}
                  />
                </div>
              </div>
            </div>

            <div style={{ background: 'var(--bg-surface-subtle)', padding: 16, borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <h4 style={{ margin: '0 0 12px 0', color: 'var(--text-primary)', fontSize: 14, fontWeight: 700 }}>
                {t('manualControl.rollbackScopeSection')}
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14 }}>
                {action === 'unblock' ? (
                  <div className="form-group">
                    <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block', color: 'var(--text-secondary)' }}>
                      {t('manualControl.destinationIp')} ({language === 'vi' ? 'Tùy chọn' : 'Optional'})
                    </label>
                    <input
                      type="text"
                      placeholder={t('manualControl.destinationIpPlaceholder')}
                      value={formData.dstIp || ''}
                      onChange={(e) => handleInputChange('dstIp', e.target.value)}
                      style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid var(--input-border)', background: 'var(--input-bg)', color: 'var(--input-text)' }}
                    />
                  </div>
                ) : (
                  <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                    {language === 'vi'
                      ? 'Hoàn tác toàn bộ quy tắc ACL và khôi phục chuyển tiếp mặc định qua OpenFlow 1.3 Controller.'
                      : 'Reverts candidate ACL rule and restores default forwarding through OpenFlow 1.3 Controller.'}
                  </div>
                )}
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const resolveStageBadge = (res) => {
    if (!res) return null;
    const status = String(res.status || res.enforcement_status || '').toUpperCase();
    const isDryRun = res.dry_run || status.includes('DRY_RUN') || status.includes('STAGED');
    const isRejected = status.includes('REJECT') || status.includes('FAIL') || status.includes('DENIED');
    const isRollback = status.includes('ROLLBACK');
    const isDataplane = status.includes('DATAPLANE_VERIFIED');
    const isInstalled = res.rule_installed === true || status.includes('RULE_INSTALLED');
    const isAccepted = status.includes('CONTROLLER_ACCEPTED') || status.includes('ACCEPTED');
    const isApprovalReq = status.includes('APPROVAL_REQUIRED') || status.includes('OPERATOR');

    if (isDryRun) {
      return {
        badge: t('manualControl.stageDryRun'),
        bg: '#0284c7',
        color: '#ffffff',
      };
    }
    if (isRejected) {
      return {
        badge: t('manualControl.stageSafetyGateRejected'),
        bg: '#dc2626',
        color: '#ffffff',
      };
    }
    if (isRollback) {
      return {
        badge: t('manualControl.stageRollbackVerified'),
        bg: '#059669',
        color: '#ffffff',
      };
    }
    if (isDataplane) {
      return {
        badge: t('manualControl.stageDataplaneVerified'),
        bg: '#0d9488',
        color: '#ffffff',
      };
    }
    if (isInstalled) {
      return {
        badge: t('manualControl.stageRuleInstalled'),
        bg: '#16a34a',
        color: '#ffffff',
      };
    }
    if (isAccepted) {
      return {
        badge: t('manualControl.stageControllerAccepted'),
        bg: '#d97706',
        color: '#ffffff',
      };
    }
    if (isApprovalReq) {
      return {
        badge: t('manualControl.stageApprovalRequired'),
        bg: '#ea580c',
        color: '#ffffff',
      };
    }
    if (status.includes('ERROR') || status.includes('DOWN')) {
      return {
        badge: t('manualControl.stageFailed'),
        bg: '#b91c1c',
        color: '#ffffff',
      };
    }
    return {
      badge: status || (language === 'vi' ? 'Đã hoàn tất' : 'Completed'),
      bg: '#475569',
      color: '#ffffff',
    };
  };

  return (
    <div className="manual-traffic-control">
      <div style={{ marginBottom: 20 }}>
        <h2>
          {t('manualControl.title')}
        </h2>
        <p style={{ margin: '4px 0 0 0', color: 'var(--text-secondary)', fontSize: 14 }}>
          {t('manualControl.subtitle')}
        </p>
      </div>

      {statusMessage && (
        <div
          style={{
            background: '#e0f2fe',
            color: '#0369a1',
            padding: '10px 14px',
            borderRadius: 6,
            marginBottom: 18,
            fontWeight: 600,
            border: '1px solid #bae6fd',
            fontSize: 13,
          }}
        >
          {statusMessage}
        </div>
      )}

      {/* Main Control Form */}
      <form onSubmit={handleSubmit} style={{ background: 'var(--card-bg)', padding: 22, borderRadius: 10, border: '1px solid var(--card-border)', boxShadow: 'var(--card-shadow)' }}>
        {/* 1. Action Selection */}
        <div className="form-group" style={{ marginBottom: 20 }}>
          <label style={{ fontWeight: 700, fontSize: 14, color: 'var(--text-primary)', marginBottom: 6, display: 'block' }}>
            {t('manualControl.actionSelection')}
          </label>
          <select
            value={action}
            onChange={(e) => setAction(e.target.value)}
            style={{ width: '100%', maxWidth: '400px', padding: '9px 12px', borderRadius: 6, border: '1px solid var(--input-border)', fontSize: 14, background: 'var(--input-bg)', color: 'var(--input-text)' }}
          >
            <option value="block">{t('manualControl.actionBlock')}</option>
            <option value="allow">{t('manualControl.actionAllow')}</option>
            <option value="rate-limit">{t('manualControl.actionRateLimit')}</option>
            <option value="redirect">{t('manualControl.actionRedirect')}</option>
            <option value="unblock">{t('manualControl.actionUnblock')}</option>
            <option value="rollback">{t('manualControl.actionRollback')}</option>
          </select>
        </div>

        {/* 2 & 3. Fields */}
        <div style={{ marginBottom: 22 }}>
          {renderFields()}
        </div>

        {/* 4. Safety Gate & Execution Mode */}
        <div
          style={{
            background: dryRun ? 'var(--bg-surface-subtle)' : '#fffbeb',
            borderLeft: `5px solid ${dryRun ? '#0d9488' : '#f59e0b'}`,
            padding: '14px 18px',
            borderRadius: 8,
            marginBottom: 20,
            border: `1px solid ${dryRun ? 'var(--border-color)' : '#fde68a'}`,
          }}
        >
          <h4 style={{ margin: '0 0 10px 0', fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>
            {t('manualControl.safetySection')}
          </h4>
          <label
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              fontWeight: 600,
              cursor: 'pointer',
              color: dryRun ? 'var(--text-primary)' : '#92400e',
              fontSize: 13.5,
            }}
          >
            <input
              type="checkbox"
              checked={dryRun}
              onChange={(e) => setDryRun(e.target.checked)}
              style={{ width: 18, height: 18, cursor: 'pointer' }}
            />
            <span>
              {dryRun
                ? t('manualControl.dryRunActiveNotice')
                : t('manualControl.liveEnforcementNotice')}
            </span>
          </label>
        </div>

        {/* 5. Policy Preview Card */}
        <div style={{ background: 'var(--bg-surface-subtle)', padding: 14, borderRadius: 8, border: '1px solid var(--border-color)', marginBottom: 20 }}>
          <h4 style={{ margin: '0 0 8px 0', fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>
            {t('manualControl.policyPreviewTitle')}
          </h4>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: 4 }}>
            <div><strong>{t('manualControl.selectedAction')}</strong> <code style={{ color: '#0284c7' }}>{action.toUpperCase()}</code></div>
            <div>
              <strong>{t('manualControl.targetSubject')}</strong>{' '}
              {formData.srcIp || hostIp ? (
                <code style={{ color: '#0284c7', fontWeight: 600 }}>{formData.srcIp || hostIp}</code>
              ) : (
                <code style={{ color: '#e11d48', fontWeight: 600 }}>
                  {language === 'vi' ? 'Chưa chỉ định (Cần nhập IP)' : 'Not specified (IP required)'}
                </code>
              )}
            </div>
            <div><strong>{t('manualControl.safetyStatus')}</strong> <span style={{ fontWeight: 600, color: dryRun ? '#0d9488' : '#e11d48' }}>{dryRun ? 'DRY_RUN (SIMULATED)' : 'LIVE_ENFORCEMENT'}</span></div>
          </div>
        </div>

        {/* Form Actions */}
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <button
            type="submit"
            style={{
              padding: '10px 22px',
              background: '#0284c7',
              color: '#ffffff',
              border: 'none',
              borderRadius: 6,
              fontWeight: 700,
              fontSize: 14,
              cursor: 'pointer',
              boxShadow: '0 1px 3px rgba(2, 132, 199, 0.3)'
            }}
          >
            {t('manualControl.btnExecute')}
          </button>
          <button
            type="button"
            onClick={resetForm}
            style={{
              padding: '10px 18px',
              background: '#e2e8f0',
              color: '#334155',
              border: 'none',
              borderRadius: 6,
              fontWeight: 600,
              fontSize: 14,
              cursor: 'pointer',
            }}
          >
            {t('manualControl.btnReset')}
          </button>
        </div>
      </form>

      {/* Telemetry Response Box with Structured Stage Badge */}
      {telemetry && (
        <div
          style={{
            marginTop: 24,
            padding: 18,
            background: '#0f172a',
            color: '#f8fafc',
            borderRadius: 8,
            boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10, marginBottom: 12 }}>
            <h4 style={{ margin: 0, color: '#38bdf8', fontSize: 14, fontWeight: 700 }}>
              {t('manualControl.executionResponseTitle')}
            </h4>
            {(() => {
              const stage = resolveStageBadge(telemetry);
              return stage ? (
                <span
                  style={{
                    fontSize: 12,
                    fontWeight: 700,
                    padding: '4px 10px',
                    borderRadius: '9999px',
                    backgroundColor: stage.bg,
                    color: stage.color,
                  }}
                >
                  {stage.badge}
                </span>
              ) : null;
            })()}
          </div>
          {telemetry.message && (
            <p style={{ margin: '0 0 12px 0', fontSize: 13, color: '#cbd5e1' }}>
              {telemetry.message}
            </p>
          )}
          <pre style={{ margin: 0, overflowX: 'auto', fontSize: 12, color: '#e2e8f0', lineHeight: 1.4, background: '#1e293b', padding: 12, borderRadius: 6 }}>
            {JSON.stringify(telemetry, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default ManualTrafficControl;
