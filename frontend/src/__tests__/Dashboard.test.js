import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import axios from 'axios';
import { LanguageProvider } from '../i18n/LanguageContext';
import { ThemeProvider } from '../theme/ThemeContext';
import Dashboard from '../pages/Dashboard';

jest.mock('axios', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));
jest.mock('react-chartjs-2', () => ({
  Line: ({ data }) => (
    <div data-testid="mock-line-chart">
      LineChart ({data?.datasets?.[0]?.data?.length ?? 0} points)
    </div>
  ),
  Bar: ({ data }) => (
    <div data-testid="mock-bar-chart">
      BarChart ({data?.labels?.length ?? 0} bars)
    </div>
  ),
}));

const MOCK_EVIDENCE = {
  evidence_source_file: 'ingress_icmp_20261101_014645.json',
  evidence_source_sha256: 'de91995d973fbaa36fe414541af234804d6bbf48838f2a9978164d4b860a6ecd',
  total_packets: 24,
  security_assessment: {
    topology_corroborated: true,
    historical_alert_correlation_verified: false,
    decision: 'OBSERVE',
    automatic_block_allowed: false,
  },
};

const MOCK_SIEM = {
  sources: [
    {
      source_system: 'ONOS_OPENFLOW_COLLECTOR',
      integration_status: 'VERIFIED_INTEGRATION',
      description: 'ONOS telemetry collector',
    },
    {
      source_system: 'SURICATA_WEBHOOK_RECEPTION',
      integration_status: 'VERIFIED_INTEGRATION',
      description: 'Suricata webhook',
    },
    {
      source_system: 'FIREWALL_SYSLOG',
      integration_status: 'FIXTURE_SIMULATION',
      description: 'Firewall syslog fixture',
    },
    {
      source_system: 'WINDOWS_SERVER_EVENTLOG',
      integration_status: 'FIXTURE_SIMULATION',
      description: 'Windows event fixture',
    },
  ],
};

function setupAxiosScenario({
  onosUp = false,
  esUp = true,
  backendUp = true,
  logstashIndexed = 0,
} = {}) {
  axios.get.mockImplementation((url) => {
    if (!backendUp) {
      return Promise.reject(new Error('Network Error: Backend unavailable'));
    }
    if (url.includes('/api/health')) {
      return Promise.resolve({
        data: { status: 'OK', defense_mode: 'DRY_RUN' },
      });
    }
    if (url.includes('/api/service-status')) {
      return Promise.resolve({
        data: {
          data: {
            ONOS: onosUp ? 'UP' : 'DOWN',
            OPENFLOW: onosUp ? 'UP' : 'DOWN',
            ELK: esUp ? 'UP' : 'DOWN',
            LOGSTASH: esUp ? 'UP' : 'DOWN',
            KIBANA: esUp ? 'UP' : 'DOWN',
          },
        },
      });
    }
    if (url.includes('/api/logstash/pipeline-status')) {
      return Promise.resolve({
        data: {
          data: {
            status: 'UP',
            events_received: logstashIndexed,
            documents_indexed: logstashIndexed,
            queue_backpressure: 0,
            operational: true,
          },
        },
      });
    }
    if (url.includes('/api/defense/evidence-correlation')) {
      return Promise.resolve({ data: { status: 'SUCCESS', data: MOCK_EVIDENCE } });
    }
    if (url.includes('/api/siem/evaluate-fixtures')) {
      return Promise.resolve({ data: { status: 'SUCCESS', data: MOCK_SIEM } });
    }
    if (url.includes('/api/get-flows')) {
      return Promise.resolve({
        data: { data: [{ id: '1', bandwidth: 1024 }, { id: '2', bandwidth: 2048 }] },
      });
    }
    if (url.includes('/api/get-actions')) {
      return Promise.resolve({
        data: {
          data: [
            { action_type: 'Block [DRY_RUN]', source_ip: '10.0.0.1' },
            { action_type: 'Unblock [DRY_RUN]', source_ip: '10.0.0.1' },
          ],
        },
      });
    }
    if (url.includes('/api/topology')) {
      if (!onosUp) return Promise.reject(new Error('502 ONOS Down'));
      return Promise.resolve({
        data: {
          devices: [{ id: 'of:0000000000000001', type: 'SWITCH', available: true }],
          hosts: [{ id: 'h1', ipAddresses: ['10.0.0.1'] }],
          links: [],
        },
      });
    }
    if (url.includes('/api/live-flows')) {
      if (!onosUp) return Promise.reject(new Error('502 ONOS Down'));
      return Promise.resolve({
        data: { source: 'ONOS', count: 4, data: [{ packets: 10, bytes: 1000 }] },
      });
    }
    if (url.includes('/api/live-port-stats')) {
      if (!onosUp) return Promise.reject(new Error('502 ONOS Down'));
      return Promise.resolve({
        data: {
          source: 'ONOS',
          sample_time: 1700000000,
          devices: [
            {
              device_id: 'of:0000000000000001',
              ports: [{ port: '1', rx_bytes: 1000, tx_bytes: 2000, rx_packets: 10, tx_packets: 20 }],
            },
          ],
        },
      });
    }
    if (url.includes('/api/elk/security-alerts')) {
      if (!esUp) return Promise.reject(new Error('503 ES Down'));
      return Promise.resolve({ data: { source: 'Elasticsearch', total: 0, count: 0, alerts: [] } });
    }
    if (url.includes('/api/elk/port-traffic-history')) {
      if (!esUp) return Promise.reject(new Error('503 ES Down'));
      return Promise.resolve({ data: { source: 'Elasticsearch', count: 0, data: [] } });
    }
    return Promise.resolve({ data: {} });
  });

  global.fetch = jest.fn().mockImplementation(() => {
    if (!backendUp || !esUp) {
      return Promise.resolve({ ok: false, status: 503 });
    }
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ source: 'Elasticsearch', total: 0, count: 0, alerts: [] }),
    });
  });
}

function renderDashboard(locale = 'vi') {
  window.localStorage.setItem('sdnflowguard_locale', locale);
  return render(
    <MemoryRouter>
      <ThemeProvider>
        <LanguageProvider>
          <Dashboard />
        </LanguageProvider>
      </ThemeProvider>
    </MemoryRouter>
  );
}

describe('Dashboard UI/UX — Collapsible Panels, i18n & Degraded States', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('both Evidence and Service Directory panels default to collapsed, toggle cleanly with mouse & keyboard without duplicate API calls, and contain zero Step 64 or raw i18n keys', async () => {
    setupAxiosScenario({ onosUp: false, esUp: true, backendUp: true, logstashIndexed: 0 });
    const { container } = renderDashboard('vi');

    await waitFor(() => {
      expect(screen.getByText('4/6')).toBeInTheDocument();
    });

    // Zero "Step 64" and zero raw translation keys in rendered DOM
    expect(container.textContent).not.toMatch(/step\s*64/i);
    expect(container.textContent).not.toMatch(/dashboard\.[a-zA-Z]+/);
    expect(container.textContent).not.toMatch(/status\.ready/);

    // 1. Both collapsible toggle buttons default to collapsed with unique IDs
    const evidenceBtn = screen.getByRole('button', { name: /Mở chi tiết bằng chứng an ninh/i });
    const serviceBtn = screen.getByRole('button', { name: /Mở chi tiết cổng truy cập dịch vụ/i });

    expect(evidenceBtn.id).toBe('security-evidence-toggle');
    expect(serviceBtn.id).toBe('service-directory-toggle');
    expect(evidenceBtn.id).not.toBe(serviceBtn.id);
    expect(evidenceBtn).toHaveAttribute('aria-expanded', 'false');
    expect(serviceBtn).toHaveAttribute('aria-expanded', 'false');

    expect(evidenceBtn).toHaveAttribute('aria-controls', 'security-evidence-panel');
    expect(serviceBtn).toHaveAttribute('aria-controls', 'service-directory-panel');

    const evidencePanel = screen.getByTestId('security-evidence-panel');
    const servicePanel = screen.getByTestId('service-directory-panel');
    expect(evidencePanel).toHaveAttribute('hidden');
    expect(servicePanel).toHaveAttribute('hidden');

    const callsBeforeToggle = axios.get.mock.calls.length;

    // 2. Click open Evidence panel
    await userEvent.click(evidenceBtn);
    expect(evidenceBtn).toHaveAttribute('aria-expanded', 'true');
    expect(evidenceBtn.textContent).toContain('Thu gọn');
    expect(evidenceBtn.textContent).toContain('▲');
    expect(evidencePanel).not.toHaveAttribute('hidden');
    expect(
      within(evidencePanel).getByText('Xác minh danh tính thiết bị & Chính sách phòng thủ')
    ).toBeVisible();
    expect(within(evidencePanel).getByText(/ingress_icmp_20261101_014645\.json/i)).toBeVisible();

    // 3. Keyboard toggle close Evidence panel
    evidenceBtn.focus();
    await userEvent.keyboard('{Enter}');
    expect(evidenceBtn).toHaveAttribute('aria-expanded', 'false');
    expect(evidencePanel).toHaveAttribute('hidden');

    // 4. Click open Service Directory panel & verify all 6 service cards + honest Logstash 0-event copy
    await userEvent.click(serviceBtn);
    expect(serviceBtn).toHaveAttribute('aria-expanded', 'true');
    expect(serviceBtn.textContent).toContain('Thu gọn');
    expect(servicePanel).not.toHaveAttribute('hidden');
    expect(within(servicePanel).getByText('ONOS SDN Controller')).toBeVisible();
    expect(within(servicePanel).getAllByText('Elasticsearch').length).toBeGreaterThanOrEqual(2);
    expect(within(servicePanel).getByText('Kibana')).toBeVisible();
    expect(within(servicePanel).getByText('Logstash')).toBeVisible();
    expect(within(servicePanel).getByText('SDNFlowGuard Backend API')).toBeVisible();
    expect(within(servicePanel).getByText('SDNFlowGuard Web Console')).toBeVisible();
    expect(
      within(servicePanel).getByText(/Pipeline sẵn sàng \(0 sự kiện mới trong phiên\)/i)
    ).toBeVisible();

    // 5. Space key collapses Service Directory panel
    serviceBtn.focus();
    await userEvent.keyboard(' ');
    expect(serviceBtn).toHaveAttribute('aria-expanded', 'false');
    expect(servicePanel).toHaveAttribute('hidden');

    // 6. Toggling never fired extra API requests
    expect(axios.get.mock.calls.length).toBe(callsBeforeToggle);
  });

  test('English mode uses unified "View Evidence Details" / "Collapse" buttons with distinct accessible names and zero Step 64 or raw keys', async () => {
    setupAxiosScenario({ onosUp: true, esUp: true, backendUp: true, logstashIndexed: 0 });
    const { container } = renderDashboard('en');

    await waitFor(() => {
      expect(screen.getByText('6/6')).toBeInTheDocument();
    });

    expect(container.textContent).not.toMatch(/step\s*64/i);
    expect(container.textContent).not.toMatch(/dashboard\.[a-zA-Z]+/);
    expect(container.textContent).not.toMatch(/status\.ready/);

    const evidenceBtn = screen.getByRole('button', { name: 'Show security evidence details' });
    const serviceBtn = screen.getByRole('button', { name: 'Show service access details' });

    expect(evidenceBtn.textContent).toContain('View Evidence Details');
    expect(evidenceBtn.textContent).toContain('▼');
    expect(serviceBtn.textContent).toContain('View Evidence Details');
    expect(serviceBtn.textContent).toContain('▼');
    expect(evidenceBtn.id).not.toBe(serviceBtn.id);

    await userEvent.click(evidenceBtn);
    expect(evidenceBtn.textContent).toContain('Collapse');
    expect(evidenceBtn.textContent).toContain('▲');
    expect(screen.getByText('Host Identity Verification & Defense Policy')).toBeVisible();

    await userEvent.click(serviceBtn);
    expect(serviceBtn.textContent).toContain('Collapse');
    expect(serviceBtn.textContent).toContain('▲');
  });

  test('ONOS offline state shows accurate degraded telemetry without fake 0.0000 Mbps', async () => {
    setupAxiosScenario({ onosUp: false, esUp: true, backendUp: true });
    renderDashboard();

    await waitFor(() => {
      expect(screen.getAllByText(/ONOS: Mất kết nối/i).length).toBeGreaterThan(0);
    });

    // Port throughput must NOT display misleading 0.0000 Mbps when ONOS is offline
    expect(screen.queryByText('0.0000 Mbps')).not.toBeInTheDocument();
    // Active service summary shows real 4/6 (Backend, ES, Logstash, Kibana UP; ONOS, OpenFlow DOWN)
    expect(screen.getByText('4/6')).toBeInTheDocument();
  });

  test('Elasticsearch offline state never displays AN TOAN badge on Security Alerts', async () => {
    setupAxiosScenario({ onosUp: false, esUp: false, backendUp: true });
    renderDashboard();

    await waitFor(() => {
      expect(screen.getAllByText(/ELK MẤT KẾT NỐI/i).length).toBeGreaterThan(0);
    });

    expect(screen.queryByText(/AN TOÀN \(0\)/i)).not.toBeInTheDocument();
    expect(screen.getByText(/Không có dữ liệu cảnh báo do lỗi kết nối Elasticsearch/i)).toBeInTheDocument();
  });

  test('Backend API completely unavailable shows 0/6 active services and sync error', async () => {
    setupAxiosScenario({ onosUp: false, esUp: false, backendUp: false });
    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText(/Lỗi đồng bộ API/i)).toBeInTheDocument();
    });

    expect(screen.getByText('0/6')).toBeInTheDocument();
  });

  test('KPI values do not carry hardcoded dark text color in inline style', async () => {
    setupAxiosScenario({ onosUp: true, esUp: true, backendUp: true });
    const { container } = renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('Switch kết nối')).toBeInTheDocument();
    });

    // eslint-disable-next-line testing-library/no-node-access, testing-library/no-container
    const kpiValues = container.querySelectorAll('.kpi-value');
    expect(kpiValues.length).toBe(4);
    kpiValues.forEach((el) => {
      // Inline style color must NOT be '#0f172a' or 'rgb(15, 23, 42)'
      expect(el.style.color).not.toBe('#0f172a');
      expect(el.style.color).not.toBe('rgb(15, 23, 42)');
    });
  });
});
