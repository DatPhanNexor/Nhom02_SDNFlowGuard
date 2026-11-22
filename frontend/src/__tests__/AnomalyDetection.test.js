import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import { LanguageProvider } from '../i18n/LanguageContext';
import { ThemeProvider } from '../theme/ThemeContext';
import AnomalyDetection from '../pages/AnomalyDetection';

jest.mock('axios', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

const mockAnomalies = {
  data: {
    data: [
      {
        id: 1,
        source_ip: '10.0.0.1',
        event: 'ICMP Flooding',
        score: 85,
        timestamp: '2026-11-20 14:30:00',
      },
    ],
  },
};

const mockCorrelation = {
  data: {
    status: 'SUCCESS',
    data: {
      capture_artifact: 'ingress_icmp_20261101_014645.json',
      capture_clock_quality: 'local_capture_clock_time_only',
      utc_correlation_status: 'HISTORICAL_ALERT_CORRELATION_NOT_VERIFIED',
      single_switch_three_hosts: {
        device_id: 'of:0000000000000001',
        ingress_port: '1',
        source_ip: '10.0.0.1',
        source_mac: '00:00:00:00:00:01',
        attribution: 'SUSPECTED_ATTACKER_INGRESS',
        status: 'CORROBORATED_SINGLE_HOST',
      },
    },
  },
};

const mockEvaluate = {
  data: {
    status: 'SUCCESS',
    data: {
      defense_mode: 'DRY_RUN',
      device_id: 'of:0000000000000001',
      port_decisions: [
        {
          switch_id: 'of:0000000000000001',
          port: '1',
          decision: 'OBSERVE',
          reason: 'Ingress traffic within normal observed bounds',
          attached_hosts: [{ ips: ['10.0.0.1'] }],
          active_alerts: 0,
        },
      ],
    },
  },
};

function renderAnomalyDetection(locale = 'vi') {
  window.localStorage.setItem('sdnflowguard_locale', locale);
  return render(
    <ThemeProvider>
      <LanguageProvider>
        <AnomalyDetection />
      </LanguageProvider>
    </ThemeProvider>
  );
}

describe('AnomalyDetection Enterprise NOC/SOC Security Telemetry Verification', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    axios.get.mockImplementation((url) => {
      if (url.includes('/api/get-anomalies')) return Promise.resolve(mockAnomalies);
      if (url.includes('/api/defense/evidence-correlation')) return Promise.resolve(mockCorrelation);
      if (url.includes('/api/defense/evaluate')) return Promise.resolve(mockEvaluate);
      return Promise.reject(new Error(`Unhandled URL: ${url}`));
    });
  });

  test('renders all 5 primary sections and telemetry badges', async () => {
    renderAnomalyDetection('en');

    // Section 1: Page Header
    expect(await screen.findByText('Anomaly Detection & Host Evidence Correlation')).toBeInTheDocument();
    expect(screen.getByText(/Detection: ONLINE/i)).toBeInTheDocument();
    expect(screen.getAllByText(/DRY_RUN/i).length).toBeGreaterThanOrEqual(1);

    // Section 2: Packet Evidence (wait for async data)
    expect(await screen.findByText(/ingress_icmp_20261101_014645\.json/i)).toBeInTheDocument();
    expect(screen.getByText(/HISTORICAL_ALERT_CORRELATION_NOT_VERIFIED/i)).toBeInTheDocument();

    // Section 3: Policy Evaluation
    expect(screen.getByText('Defense Policy Engine Per-Port Evaluation')).toBeInTheDocument();
    expect(await screen.findByText('OBSERVE')).toBeInTheDocument();

    // Section 4: Recent Anomalies
    expect(screen.getByText('Recent Webhook / SIEM Anomalies (SQLite Events)')).toBeInTheDocument();
    expect(screen.getByText('ICMP Flooding')).toBeInTheDocument();

    // Section 5: Alert Actions & Safety Gate
    expect(screen.getByText('Alert Actions (Protected by Safety Gate)')).toBeInTheDocument();
    expect(screen.getByText(/Safety Gate: Protected \(Active\)/i)).toBeInTheDocument();
  });

  test('selects anomaly table row and prefills action target IP', async () => {
    renderAnomalyDetection('vi');

    const cell = await screen.findByText('ICMP Flooding');
    fireEvent.click(cell);

    // Verify Action Target IP input receives the selected IP
    const targetIpInput = screen.getByPlaceholderText(/10\.0\.0\.2/i);
    expect(targetIpInput.value).toBe('10.0.0.1');

    // Action Preview updates
    expect(screen.getByText(/\[SAFETY GATE STAGING\]/i)).toBeInTheDocument();
  });

  test('opens and closes Block modal cleanly', async () => {
    renderAnomalyDetection('en');

    await screen.findByText('ICMP Flooding');

    const blockBtn = screen.getByText(/Block Traffic/i);
    fireEvent.click(blockBtn);

    // Modal opens
    expect(screen.getByRole('heading', { name: /Block Source IP Traffic/i })).toBeInTheDocument();

    // Close modal
    const cancelBtn = screen.getByText('Cancel');
    fireEvent.click(cancelBtn);

    await waitFor(() => {
      expect(screen.queryByRole('heading', { name: /Block Source IP Traffic/i })).not.toBeInTheDocument();
    });
  });
});
