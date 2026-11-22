import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import { LanguageProvider } from '../i18n/LanguageContext';
import { ThemeProvider } from '../theme/ThemeContext';
import Reports from '../pages/Reports';

jest.mock('axios', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
  },
}));

const mockAnomaliesData = {
  data: {
    data: [
      {
        timestamp: '2025-01-13 01:24:13',
        source_ip: '10.0.0.2',
        event: 'Port Scanning',
        score: 31,
      },
      {
        timestamp: '2025-01-03 10:00:00',
        source_ip: '10.0.0.11',
        event: 'Port Scanning',
        score: 75,
      },
    ],
  },
};

const mockActionsData = {
  data: {
    data: [
      {
        timestamp: '2025-01-17 16:49:32',
        action_type: 'Redirect',
        source_ip: '10.0.0.1',
        reason: 'Redirected traffic from 10.0.0.1 to 10.0.0.6.',
        admin_or_automated: 'Automated',
      },
      {
        timestamp: '2025-01-13 02:46:59',
        action_type: 'Block',
        source_ip: '10.0.0.1/32',
        reason: 'Blocked traffic for 10.0.0.1/32 to 10.0.0.2/32.',
        admin_or_automated: 'Admin',
      },
    ],
  },
};

function renderReports(locale = 'vi') {
  window.localStorage.setItem('sdnflowguard_locale', locale);
  return render(
    <ThemeProvider>
      <LanguageProvider>
        <Reports />
      </LanguageProvider>
    </ThemeProvider>
  );
}

describe('Reports Module Enterprise Layout & Export Verification', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});
    axios.get.mockImplementation((url, config) => {
      if (url.includes('/api/get-report')) {
        const reportType = config?.params?.report_type;
        if (reportType === 'actions') return Promise.resolve(mockActionsData);
        return Promise.resolve(mockAnomaliesData);
      }
      if (url.includes('/api/download-pdf')) {
        return Promise.resolve({ data: new Uint8Array([37, 80, 68, 70]) }); // %PDF
      }
      return Promise.reject(new Error(`Unhandled URL: ${url}`));
    });

    // Mock window.URL methods
    window.URL.createObjectURL = jest.fn(() => 'blob:http://localhost/test-uuid');
    window.URL.revokeObjectURL = jest.fn();
  });

  test('renders header, control card, retention notice, and preview card', async () => {
    renderReports('en');

    // Title & Subtitle
    expect(await screen.findByText('Security & Traffic Reports')).toBeInTheDocument();
    expect(screen.getByText(/Aggregate audit telemetry and generate forensic PDF/i)).toBeInTheDocument();

    // Data rows loaded
    expect(await screen.findByText('10.0.0.2')).toBeInTheDocument();
    expect(screen.getByText('10.0.0.11')).toBeInTheDocument();

    // Badges
    expect(screen.getByText(/Storage: SQLite/i)).toBeInTheDocument();
    expect(screen.getByText(/Format: Forensic PDF/i)).toBeInTheDocument();

    // Cards
    expect(screen.getByText('Extraction Controls & PDF Export')).toBeInTheDocument();
    expect(screen.getByText(/Monthly Retention Window:/i)).toBeInTheDocument();
    expect(screen.getByText(/Audit Report: Security Anomalies & Traffic Thresholds/i)).toBeInTheDocument();
  });

  test('switches dataset between anomalies and actions', async () => {
    renderReports('vi');

    await screen.findByText('10.0.0.2');

    // Switch to actions dataset
    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: 'actions' } });

    expect(await screen.findByText(/Báo cáo kiểm toán Hành động can thiệp phòng vệ/i)).toBeInTheDocument();
    expect(await screen.findByText('Redirected traffic from 10.0.0.1 to 10.0.0.6.')).toBeInTheDocument();
    expect(screen.getByText('10.0.0.1/32')).toBeInTheDocument();
  });

  test('triggers PDF export download cleanly with blob URL', async () => {
    renderReports('en');

    await screen.findByText('10.0.0.2');

    const exportBtn = screen.getByText('Download PDF Report');
    fireEvent.click(exportBtn);

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/download-pdf'),
        expect.objectContaining({
          params: expect.objectContaining({ report_type: 'anomalies' }),
          responseType: 'blob',
        })
      );
    });
    expect(await screen.findByText(/PDF report exported successfully/i)).toBeInTheDocument();
  });

  test('handles API fetch failure gracefully with alert banner', async () => {
    axios.get.mockRejectedValueOnce(new Error('Network error'));

    renderReports('vi');

    await waitFor(() => {
      expect(screen.getByText('Không thể tải dữ liệu báo cáo. Vui lòng thử lại.')).toBeInTheDocument();
    });
  });
});
