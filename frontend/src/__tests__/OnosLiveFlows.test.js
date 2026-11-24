import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import OnosLiveFlows from '../pages/OnosLiveFlows';
import { LanguageProvider } from '../i18n/LanguageContext';
import { ThemeProvider } from '../theme/ThemeContext';

jest.mock('axios', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
  },
}));

const mockDiverseFlows = {
  data: {
    count: 3,
    source: 'ONOS',
    data: [
      {
        id: 'flow-l3-ipv4',
        device_id: 'of:0000000000000001',
        app_id: 'org.onosproject.acl',
        state: 'ADDED',
        priority: 50000,
        table_id: 0,
        source_ip: '10.0.0.1/32',
        destination_ip: '10.0.0.2/32',
        source_mac: null,
        destination_mac: null,
        in_port: '1',
        eth_type: '0x800',
        ip_proto: 6,
        match_criteria: 'IN_PORT: 1, ETH_TYPE: 0x800 (IPv4), SRC_IP: 10.0.0.1/32, DST_IP: 10.0.0.2/32, IP_PROTO: 6 (TCP)',
        has_ip_match: true,
        is_table_miss: false,
        treatment_summary: 'OUTPUT: 2',
        packets: 120,
        bytes: 9600,
        life_seconds: 45,
        output_ports: ['2'],
        criteria_raw: [
          { type: 'ETH_TYPE', ethType: '0x800' },
          { type: 'IPV4_SRC', ip: '10.0.0.1/32' },
          { type: 'IPV4_DST', ip: '10.0.0.2/32' },
        ],
      },
      {
        id: 'flow-l2-lldp',
        device_id: 'of:0000000000000001',
        app_id: 'org.onosproject.core',
        state: 'ADDED',
        priority: 40000,
        table_id: 0,
        source_ip: null,
        destination_ip: null,
        source_mac: null,
        destination_mac: null,
        in_port: null,
        eth_type: '0x88cc',
        ip_proto: null,
        match_criteria: 'ETH_TYPE: 0x88cc (LLDP)',
        has_ip_match: false,
        is_table_miss: false,
        treatment_summary: 'OUTPUT: CONTROLLER',
        packets: 500,
        bytes: 35000,
        life_seconds: 120,
        output_ports: ['CONTROLLER'],
        criteria_raw: [{ type: 'ETH_TYPE', ethType: '0x88cc' }],
      },
      {
        id: 'flow-l2-mac-only',
        device_id: 'of:0000000000000002',
        app_id: 'org.onosproject.fwd',
        state: 'ADDED',
        priority: 10,
        table_id: 0,
        source_ip: null,
        destination_ip: null,
        source_mac: '00:00:00:00:00:01',
        destination_mac: '00:00:00:00:00:02',
        in_port: null,
        eth_type: null,
        ip_proto: null,
        match_criteria: 'ETH_SRC: 00:00:00:00:00:01, ETH_DST: 00:00:00:00:00:02',
        has_ip_match: false,
        is_table_miss: false,
        treatment_summary: 'OUTPUT: 3',
        packets: 80,
        bytes: 6400,
        life_seconds: 10,
        output_ports: ['3'],
        criteria_raw: [
          { type: 'ETH_SRC', mac: '00:00:00:00:00:01' },
          { type: 'ETH_DST', mac: '00:00:00:00:00:02' },
        ],
      },
    ],
  },
};

function renderOnosLiveFlows(locale = 'vi') {
  window.localStorage.setItem('sdnflowguard_locale', locale);
  return render(
    <ThemeProvider>
      <LanguageProvider>
        <OnosLiveFlows />
      </LanguageProvider>
    </ThemeProvider>
  );
}

describe('OnosLiveFlows Phase C OpenFlow Match & IP Visibility', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('displays real IP when rule has IPv4 match and displays N/A when rule does not match IP', async () => {
    axios.get.mockResolvedValueOnce(mockDiverseFlows);
    renderOnosLiveFlows('vi');

    // Flow 1 (L3 IPv4 match): Source & Destination IP chips rendered
    expect(await screen.findByText('10.0.0.1/32')).toBeInTheDocument();
    expect(screen.getByText('10.0.0.2/32')).toBeInTheDocument();

    // Flow 2 (LLDP) & Flow 3 (MAC only): No IP match -> displays N/A
    const naChips = screen.getAllByText('N/A');
    expect(naChips.length).toBeGreaterThanOrEqual(4); // 2 rows * 2 columns

    // Priority and Table ID rendered
    expect(screen.getByText('50000')).toBeInTheDocument();
    expect(screen.getAllByText('T0').length).toBe(3);

    // Explanatory footnote notice is present
    expect(
      screen.getByText(/Địa chỉ IP nguồn và IP đích chỉ hiển thị khi được đối sánh tường minh trong OpenFlow selector/i)
    ).toBeInTheDocument();
  });

  test('never converts MAC to IP and renders MAC in Match Criteria', async () => {
    axios.get.mockResolvedValueOnce(mockDiverseFlows);
    renderOnosLiveFlows('en');

    // MAC should be visible in Match Criteria, NOT in IP chips
    expect(await screen.findByText(/ETH_SRC: 00:00:00:00:00:01/i)).toBeInTheDocument();

    // English explanatory footnote
    expect(
      screen.getByText(/Source IP and Destination IP are displayed only when explicitly matched by the OpenFlow selector/i)
    ).toBeInTheDocument();
  });

  test('toggles detail card expansion when row is clicked', async () => {
    axios.get.mockResolvedValueOnce(mockDiverseFlows);
    renderOnosLiveFlows('vi');

    const ipChips = await screen.findAllByText('10.0.0.1/32');
    expect(ipChips[0]).toBeInTheDocument();

    // Click row 1 to expand
    fireEvent.click(ipChips[0]);

    // Expansion card appears
    expect(screen.getByText('Tiêu chí đối sánh (OpenFlow Match)')).toBeInTheDocument();
    expect(screen.getByText('Hành động xử lý (OpenFlow Treatment)')).toBeInTheDocument();
    expect(screen.getByText('Định danh & Vòng đời luồng')).toBeInTheDocument();

    // Click again to collapse
    const updatedChips = screen.getAllByText('10.0.0.1/32');
    fireEvent.click(updatedChips[0]);
    await waitFor(() => {
      expect(screen.queryByText('Tiêu chí đối sánh (OpenFlow Match)')).not.toBeInTheDocument();
    });
  });

  test('handles API error state cleanly without confusing with N/A', async () => {
    axios.get.mockRejectedValueOnce(new Error('503 Service Unavailable'));
    renderOnosLiveFlows('vi');

    expect(await screen.findByText('Không thể kết nối đến ONOS REST API.')).toBeInTheDocument();
    expect(screen.getAllByText(/Không thể kết nối đến ONOS/i).length).toBeGreaterThanOrEqual(1);
  });
});
