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
    display_period: 'Last 30 Days',
    kpi: {
      total_records: 2,
      security_events: 2,
      defense_decisions: 2,
      simulated_actions: 2,
      enforced_actions: 0,
    },
    data: [
      {
        timestamp: '2026-11-05 14:30:00',
        source_ip: '10.0.0.2',
        destination_ip: '10.0.0.3',
        event: 'Port Scanning',
        score: 31,
        severity: 'Low',
        source: 'AD-logs',
      },
      {
        timestamp: '2026-11-01 10:00:00',
        source_ip: '10.0.0.11',
        destination_ip: '10.0.0.12',
        event: 'Port Scanning',
        score: 75,
        severity: 'High',
        source: 'Netflow',
      },
    ],
  },
};

const mockActionsData = {
  data: {
    display_period: 'Last 30 Days',
    kpi: {
      total_records: 2,
      security_events: 2,
      defense_decisions: 2,
      simulated_actions: 2,
      enforced_actions: 0,
    },
    data: [
      {
        timestamp: '2026-11-17 16:49:32',
        action_type: 'Redirect',
        source_ip: '10.0.0.1',
        reason: 'Redirected traffic from 10.0.0.1 to 10.0.0.6.',
        admin_or_automated: 'Automated',
      },
      {
        timestamp: '2026-11-13 02:46:59',
        action_type: 'Block',
        source_ip: '10.0.0.1/32',
        reason: 'Blocked traffic for 10.0.0.1/32 to 10.0.0.2/32.',
        admin_or_automated: 'Admin',
      },
    ],
  },
};

const mockEmptyData = {
  data: {
    display_period: 'Last 30 Days',
    kpi: {
      total_records: 0,
      security_events: 0,
      defense_decisions: 0,
      simulated_actions: 0,
      enforced_actions: 0,
    },
    data: [],
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

describe('SOC Reporting & Audit Center Master Verification (V20)', () => {
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

    window.URL.createObjectURL = jest.fn(() => 'blob:http://localhost/test-uuid');
    window.URL.revokeObjectURL = jest.fn();
  });

  test('renders header, 4 KPI cards, dynamic controls, and preview table', async () => {
    renderReports('en');

    // Title & Subtitle
    expect(await screen.findByText('Security Reports & Audit Center')).toBeInTheDocument();
    expect(screen.getByText(/Analyze network security events, review defense decisions/i)).toBeInTheDocument();

    // 4 KPI Cards
    expect(screen.getByText('Total Records')).toBeInTheDocument();
    expect(screen.getByText('Security Events')).toBeInTheDocument();
    expect(screen.getByText('Defense Decisions')).toBeInTheDocument();
    expect(screen.getByText('Simulated / Enforced Actions')).toBeInTheDocument();

    // Header Badges
    expect(screen.getByText(/API: ONLINE/i)).toBeInTheDocument();
    expect(screen.getByText(/Data Source: SQLite/i)).toBeInTheDocument();
    expect(screen.getByText(/Timezone: Asia\/Ho_Chi_Minh/i)).toBeInTheDocument();

    // Data rows loaded
    expect(await screen.findByText('10.0.0.2')).toBeInTheDocument();
    expect(screen.getByText('10.0.0.11')).toBeInTheDocument();
    expect(screen.getByText('10.0.0.3')).toBeInTheDocument(); // Destination IP
  });

  test('switches dataset between anomalies and actions', async () => {
    renderReports('vi');

    await screen.findByText('10.0.0.2');

    // Switch to actions dataset
    const select = screen.getByLabelText('Loại báo cáo:');
    fireEvent.change(select, { target: { value: 'actions' } });

    expect(await screen.findByText(/Báo cáo kiểm toán: Nhật ký can thiệp phòng vệ & Kiểm toán/i)).toBeInTheDocument();
    expect(await screen.findByText('Redirected traffic from 10.0.0.1 to 10.0.0.6.')).toBeInTheDocument();
    expect(screen.getByText('10.0.0.1/32')).toBeInTheDocument();
  });

  test('switches time range to All Time and queries without hardcoded dates', async () => {
    renderReports('en');

    await screen.findByText('10.0.0.2');

    const rangeSelect = screen.getByLabelText('Time Range:');
    fireEvent.change(rangeSelect, { target: { value: 'all' } });

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/get-report'),
        expect.objectContaining({
          params: expect.objectContaining({
            time_range: 'all',
          }),
        })
      );
    });
  });

  test('renders informative SOC empty state when zero records returned', async () => {
    axios.get.mockImplementation((url) => {
      if (url.includes('/api/get-report')) {
        return Promise.resolve(mockEmptyData);
      }
      return Promise.reject(new Error(`Unhandled URL: ${url}`));
    });

    renderReports('vi');

    expect(await screen.findByText('Không tìm thấy bản ghi nào trong khoảng thời gian đã chọn.')).toBeInTheDocument();
    expect(screen.getByText(/Không có dữ liệu cảm biến hoặc quyết định phòng thủ nào khớp/i)).toBeInTheDocument();
    expect(screen.getByText('30 ngày qua')).toBeInTheDocument();
    expect(screen.getByText('Toàn bộ thời gian')).toBeInTheDocument();
  });

  test('validates custom date range when start date is greater than end date', async () => {
    renderReports('en');

    await screen.findByText('10.0.0.2');

    const rangeSelect = screen.getByLabelText('Time Range:');
    fireEvent.change(rangeSelect, { target: { value: 'custom' } });

    const startDateInput = screen.getByLabelText('Start Date & Time:');
    const endDateInput = screen.getByLabelText('End Date & Time:');

    fireEvent.change(startDateInput, { target: { value: '2026-11-25' } });
    fireEvent.change(endDateInput, { target: { value: '2026-11-20' } });

    const applyBtn = screen.getByText('Apply Filters');
    fireEvent.click(applyBtn);

    expect(await screen.findByText(/Invalid Date Range: Start date\/time cannot be greater than End date\/time/i)).toBeInTheDocument();
  });

  test('triggers PDF export download cleanly', async () => {
    renderReports('en');

    await screen.findByText('10.0.0.2');

    const exportBtn = screen.getByText('Download PDF Report');
    fireEvent.click(exportBtn);

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/download-pdf'),
        expect.objectContaining({
          params: expect.objectContaining({
            report_type: 'anomalies',
            time_range: 'last_30d',
          }),
          responseType: 'blob',
        })
      );
    });
    expect(await screen.findByText(/PDF report exported successfully/i)).toBeInTheDocument();
  });

  test('handles API fetch failure gracefully with offline badge', async () => {
    axios.get.mockRejectedValueOnce(new Error('Network error'));

    renderReports('vi');

    await waitFor(() => {
      expect(screen.getByText('Không thể tải dữ liệu báo cáo. Vui lòng thử lại.')).toBeInTheDocument();
    });
    expect(screen.getByText(/API: MẤT KẾT NỐI/i)).toBeInTheDocument();
  });
});
