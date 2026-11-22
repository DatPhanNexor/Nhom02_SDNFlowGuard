import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, waitFor } from '@testing-library/react';
import axios from 'axios';
import { LanguageProvider } from '../i18n/LanguageContext';
import { ThemeProvider } from '../theme/ThemeContext';
import TrafficOverview from '../pages/TrafficOverview';

jest.mock('vis-network', () => {
  class MockNetwork {
    constructor() {
      this.on = jest.fn();
      this.off = jest.fn();
      this.once = jest.fn((event, cb) => { if (cb) cb(); });
      this.destroy = jest.fn();
      this.fit = jest.fn();
      this.moveTo = jest.fn();
      this.getScale = jest.fn(() => 1);
      this.setData = jest.fn();
      this.setOptions = jest.fn();
    }
  }
  return {
    __esModule: true,
    Network: MockNetwork,
    default: { Network: MockNetwork },
  };
});

jest.mock('axios', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
  },
}));

const mockTopology = {
  data: {
    devices: [
      { id: 'of:0000000000000001', available: true, role: 'MASTER', type: 'SWITCH' },
      { id: 'of:0000000000000002', available: true, role: 'MASTER', type: 'SWITCH' },
    ],
    hosts: [
      { id: '00:00:00:00:00:01/-1', ipAddresses: ['10.0.0.1'], locations: [{ elementId: 'of:0000000000000001', port: '1' }] },
      { id: '00:00:00:00:00:02/-1', ipAddresses: ['10.0.0.2'], locations: [{ elementId: 'of:0000000000000001', port: '2' }] },
    ],
    links: [
      { src: { device: 'of:0000000000000001', port: '3' }, dst: { device: 'of:0000000000000002', port: '3' } },
    ],
  },
};

const mockLiveFlows = {
  data: {
    count: 2,
    source: 'ONOS',
    data: [
      {
        id: '123456789',
        device_id: 'of:0000000000000001',
        priority: 40000,
        app_id: 'org.onosproject.core',
        state: 'ADDED',
        packets: 150,
        bytes: 12000,
        output_ports: 'CONTROLLER',
      },
    ],
  },
};

const mockStoredFlows = {
  data: {
    data: [
      {
        flow_id: 'stored-1',
        source_ip: '10.0.0.1',
        destination_ip: '10.0.0.2',
        protocol: 'ICMP',
        action: 'ALLOW',
      },
    ],
  },
};

function renderTrafficOverview(locale = 'vi') {
  window.localStorage.setItem('sdnflowguard_locale', locale);
  return render(
    <ThemeProvider>
      <LanguageProvider>
        <TrafficOverview />
      </LanguageProvider>
    </ThemeProvider>
  );
}

describe('TrafficOverview Enterprise Topology & Flows Verification', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    axios.get.mockImplementation((url) => {
      if (url.includes('/api/topology')) return Promise.resolve(mockTopology);
      if (url.includes('/api/live-flows')) return Promise.resolve(mockLiveFlows);
      if (url.includes('/api/get-flows')) return Promise.resolve(mockStoredFlows);
      return Promise.reject(new Error(`Unhandled URL: ${url}`));
    });
  });

  test('renders page title, topology section, switches/hosts count, and flow tables', async () => {
    renderTrafficOverview('en');

    // Title & Sections
    expect(await screen.findByText('Traffic Overview')).toBeInTheDocument();
    expect(screen.getByText('SDN Network Topology')).toBeInTheDocument();
    expect(screen.getByText('Live ONOS Flow Rules')).toBeInTheDocument();
    expect(screen.getByText('Stored Flow Table (SQLite)')).toBeInTheDocument();

    // Badges
    expect(await screen.findByText(/2 Online/i)).toBeInTheDocument();
    expect(screen.getAllByText(/2 Host\(s\)/i).length).toBeGreaterThanOrEqual(1);

    // Live Flow data check
    expect(await screen.findByText('of:0000000000000001')).toBeInTheDocument();
    expect(screen.getByText('org.onosproject.core')).toBeInTheDocument();

    // Stored Flow data check
    expect(screen.getByText('10.0.0.1')).toBeInTheDocument();
    expect(screen.getByText('10.0.0.2')).toBeInTheDocument();
  });

  test('verifies Vietnamese localization and topology controls', async () => {
    renderTrafficOverview('vi');

    expect(await screen.findByText('Giám sát lưu lượng mạng')).toBeInTheDocument();
    expect(screen.getByText('Sơ đồ topo mạng SDN')).toBeInTheDocument();
    expect(screen.getByText('Quy tắc luồng thời gian thực (ONOS Live Flows)')).toBeInTheDocument();
    expect(screen.getByText('Lịch sử quy tắc luồng (SQLite)')).toBeInTheDocument();

    // Topology toolbar buttons
    expect(screen.getByTitle('Phóng to')).toBeInTheDocument();
    expect(screen.getByTitle('Thu nhỏ')).toBeInTheDocument();
    expect(screen.getByTitle('Vừa khung nhìn')).toBeInTheDocument();
  });

  test('handles topology API failure gracefully', async () => {
    axios.get.mockImplementation((url) => {
      if (url.includes('/api/topology')) return Promise.reject(new Error('502 ONOS Down'));
      if (url.includes('/api/live-flows')) return Promise.resolve({ data: { data: [] } });
      if (url.includes('/api/get-flows')) return Promise.resolve({ data: { data: [] } });
      return Promise.reject(new Error(`Unhandled URL: ${url}`));
    });

    renderTrafficOverview('vi');

    await waitFor(() => {
      expect(screen.getByText('ONOS: Mất kết nối')).toBeInTheDocument();
    });
  });
});
