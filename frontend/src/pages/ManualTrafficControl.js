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
              ? 'Lỗi xác thực: Giới hạn tốc độ (Bps) phải là số dương lớn hơn 0.'
              : 'Validation Error: Rate Limit (Bps) must be a positive number.'
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
            <div style={{ background: '#f8fafc', padding: 16, borderRadius: 8, border: '1px solid #e2e8f0' }}>
              <h4 style={{ margin: '0 0 12px 0', color: '#0f172a', fontSize: 14, fontWeight: 700 }}>
                {t('manualControl.endpointSection')}
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14 }}>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block' }}>
                    {t('manualControl.sourceIp')}
                  </label>
                  <input
                    type="text"
                    value={formData.srcIp || ''}
                    placeholder={t('manualControl.sourceIpPlaceholder')}
                    onChange={(e) => handleInputChange('srcIp', e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid #cbd5e1' }}
                  />
                </div>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block' }}>
                    {t('manualControl.destinationIp')}
                  </label>
                  <input
                    type="text"
                    value={formData.dstIp || ''}
                    placeholder={t('manualControl.destinationIpPlaceholder')}
                    onChange={(e) => handleInputChange('dstIp', e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid #cbd5e1' }}
                  />
                </div>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block' }}>
                    {t('manualControl.sourceMac')}
                  </label>
                  <input
                    type="text"
                    value={formData.srcMac || ''}
                    placeholder="vd: 00:00:00:00:00:01"
                    onChange={(e) => handleInputChange('srcMac', e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid #cbd5e1' }}
                  />
                </div>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block' }}>
                    {t('manualControl.destinationMac')}
                  </label>
                  <input
                    type="text"
                    value={formData.dstMac || ''}
                    placeholder="vd: 00:00:00:00:00:02"
                    onChange={(e) => handleInputChange('dstMac', e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid #cbd5e1' }}
                  />
                </div>
              </div>
            </div>

            {/* Protocol & Match Criteria */}
            <div style={{ background: '#f8fafc', padding: 16, borderRadius: 8, border: '1px solid #e2e8f0' }}>
              <h4 style={{ margin: '0 0 12px 0', color: '#0f172a', fontSize: 14, fontWeight: 700 }}>
                {t('manualControl.flowMatchSection')}
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14 }}>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block' }}>
                    {t('manualControl.protocol')}
                  </label>
                  <select
                    value={formData.ipProto || ''}
                    onChange={(e) => handleInputChange('ipProto', e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid #cbd5e1', background: '#fff' }}
                  >
                    <option value="">{t('manualControl.protocolAll')}</option>
                    <option value="TCP">{t('manualControl.protocolTcp')}</option>
                    <option value="UDP">{t('manualControl.protocolUdp')}</option>
                    <option value="ICMP">{t('manualControl.protocolIcmp')}</option>
                  </select>
                </div>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block' }}>
                    {t('manualControl.sourcePort')}
                  </label>
                  <input
                    type="text"
                    value={formData.srcPort || ''}
                    placeholder="vd: 80, 443"
                    onChange={(e) => handleInputChange('srcPort', e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid #cbd5e1' }}
                  />
                </div>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block' }}>
                    {t('manualControl.destinationPort')}
                  </label>
                  <input
                    type="text"
                    value={formData.dstPort || ''}
                    placeholder="vd: 80, 443"
                    onChange={(e) => handleInputChange('dstPort', e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid #cbd5e1' }}
                  />
                </div>
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block' }}>
                    {t('manualControl.prefixLength')}
                  </label>
                  <input
                    type="number"
                    value={formData.prefixLength || ''}
                    placeholder="32"
                    min="0"
                    max="32"
                    onChange={(e) => handleInputChange('prefixLength', e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid #cbd5e1' }}
                  />
                </div>
              </div>
            </div>
          </div>
        );

      case 'rate-limit':
        return (
          <div style={{ background: '#f8fafc', padding: 16, borderRadius: 8, border: '1px solid #e2e8f0' }}>
            <h4 style={{ margin: '0 0 12px 0', color: '#0f172a', fontSize: 14, fontWeight: 700 }}>
              {t('manualControl.endpointSection')}
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14 }}>
              <div className="form-group">
                <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block' }}>
                  {t('manualControl.hostIp')}
                </label>
                <input
                  type="text"
                  placeholder="vd: 10.0.0.1"
                  value={hostIp}
                  onChange={(e) => setHostIp(e.target.value)}
                  style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid #cbd5e1' }}
                />
              </div>
              <div className="form-group">
                <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block' }}>
                  {t('manualControl.rateLimitValue')}
                </label>
                <input
                  type="number"
                  placeholder={t('manualControl.rateLimitPlaceholder')}
                  value={rateLimitBps}
                  onChange={(e) => setRateLimitBps(e.target.value)}
                  style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid #cbd5e1' }}
                />
              </div>
            </div>
            <p style={{ margin: '10px 0 0 0', fontSize: 12, color: '#64748b' }}>
              ℹ️ {t('manualControl.rateLimitNote')}
            </p>
          </div>
        );

      case 'redirect':
        return (
          <div style={{ background: '#f8fafc', padding: 16, borderRadius: 8, border: '1px solid #e2e8f0' }}>
            <h4 style={{ margin: '0 0 12px 0', color: '#0f172a', fontSize: 14, fontWeight: 700 }}>
              {t('manualControl.endpointSection')}
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14 }}>
              <div className="form-group">
                <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block' }}>
                  {t('manualControl.sourceIp')}
                </label>
                <input
                  type="text"
                  placeholder={t('manualControl.sourceIpPlaceholder')}
                  value={formData.srcIp || ''}
                  onChange={(e) => handleInputChange('srcIp', e.target.value)}
                  style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid #cbd5e1' }}
                />
              </div>
              <div className="form-group">
                <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block' }}>
                  {t('manualControl.redirectIp')}
                </label>
                <input
                  type="text"
                  placeholder="vd: 10.0.0.6 (Honeypot)"
                  value={redirectIp}
                  onChange={(e) => setRedirectIp(e.target.value)}
                  style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid #cbd5e1' }}
                />
              </div>
            </div>
          </div>
        );

      case 'unblock':
      case 'rollback':
        return (
          <div style={{ background: '#f8fafc', padding: 16, borderRadius: 8, border: '1px solid #e2e8f0' }}>
            <h4 style={{ margin: '0 0 12px 0', color: '#0f172a', fontSize: 14, fontWeight: 700 }}>
              {t('manualControl.endpointSection')}
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14 }}>
              <div className="form-group">
                <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block' }}>
                  {t('manualControl.sourceIp')}
                </label>
                <input
                  type="text"
                  placeholder={t('manualControl.sourceIpPlaceholder')}
                  value={formData.srcIp || ''}
                  onChange={(e) => handleInputChange('srcIp', e.target.value)}
                  style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid #cbd5e1' }}
                />
              </div>
              {action === 'unblock' && (
                <div className="form-group">
                  <label style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, display: 'block' }}>
                    {t('manualControl.destinationIp')} ({language === 'vi' ? 'Tùy chọn' : 'Optional'})
                  </label>
                  <input
                    type="text"
                    placeholder={t('manualControl.destinationIpPlaceholder')}
                    value={formData.dstIp || ''}
                    onChange={(e) => handleInputChange('dstIp', e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid #cbd5e1' }}
                  />
                </div>
              )}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="manual-traffic-control">
      <div style={{ marginBottom: 20 }}>
        <h2 style={{ margin: 0, color: '#0f172a', fontSize: '1.6rem', fontWeight: 700 }}>
          {t('manualControl.title')}
        </h2>
        <p style={{ margin: '4px 0 0 0', color: '#64748b', fontSize: 14 }}>
          {t('manualControl.subtitle')}
        </p>
      </div>

      {/* Safety Gate Warning & DRY_RUN Toggle */}
      <div
        style={{
          background: dryRun ? '#ecfdf5' : '#fffbeb',
          borderLeft: `5px solid ${dryRun ? '#10b981' : '#f59e0b'}`,
          padding: '14px 18px',
          borderRadius: 8,
          marginBottom: 20,
          border: '1px solid #e2e8f0',
        }}
      >
        <label
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            fontWeight: 700,
            cursor: 'pointer',
            color: dryRun ? '#065f46' : '#92400e',
            fontSize: 14,
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
      <form onSubmit={handleSubmit} style={{ background: '#fff', padding: 22, borderRadius: 10, border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
        {/* 1. Action Selection */}
        <div className="form-group" style={{ marginBottom: 20 }}>
          <label style={{ fontWeight: 700, fontSize: 14, color: '#0f172a', marginBottom: 6, display: 'block' }}>
            {t('manualControl.actionSelection')}
          </label>
          <select
            value={action}
            onChange={(e) => setAction(e.target.value)}
            style={{ width: '100%', maxWidth: '400px', padding: '9px 12px', borderRadius: 6, border: '1px solid #cbd5e1', fontSize: 14, background: '#fff' }}
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

        {/* 5. Policy Preview Card */}
        <div style={{ background: '#f8fafc', padding: 14, borderRadius: 8, border: '1px solid #cbd5e1', marginBottom: 20 }}>
          <h4 style={{ margin: '0 0 8px 0', fontSize: 13, fontWeight: 700, color: '#334155' }}>
            {t('manualControl.policyPreviewTitle')}
          </h4>
          <div style={{ fontSize: 12, color: '#475569', display: 'flex', flexDirection: 'column', gap: 4 }}>
            <div><strong>{t('manualControl.selectedAction')}:</strong> <code style={{ color: '#0284c7' }}>{action.toUpperCase()}</code></div>
            <div><strong>{t('manualControl.targetSubject')}:</strong> <code>{formData.srcIp || hostIp || (language === 'vi' ? 'Chưa chỉ định' : 'Not specified')}</code></div>
            <div><strong>{t('manualControl.safetyStatus')}:</strong> <span style={{ fontWeight: 600, color: dryRun ? '#0d9488' : '#e11d48' }}>{dryRun ? 'DRY_RUN (SIMULATED)' : 'LIVE_ENFORCEMENT'}</span></div>
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

      {/* Telemetry Response Box */}
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
          <h4 style={{ marginTop: 0, color: '#38bdf8', fontSize: 14, fontWeight: 700 }}>
            {t('manualControl.executionResponseTitle')}
          </h4>
          <pre style={{ margin: 0, overflowX: 'auto', fontSize: 12, color: '#e2e8f0', lineHeight: 1.4 }}>
            {JSON.stringify(telemetry, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default ManualTrafficControl;
