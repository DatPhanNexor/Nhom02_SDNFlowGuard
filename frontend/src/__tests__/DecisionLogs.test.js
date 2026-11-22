import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import { LanguageProvider } from '../i18n/LanguageContext';
import { ThemeProvider } from '../theme/ThemeContext';
import DecisionLogs from '../pages/DecisionLogs';

jest.mock('axios', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
  },
}));

const mockDecisionData = {
  data: {
    data: [
      {
        timestamp: '2025-01-17 16:49:32',
        action_type: 'Redirect',
        admin_or_automated: 'Automated',
        reason: 'Redirected traffic from 10.0.0.1 to intermediate switch of:0000000000000003.',
        source_ip: '10.0.0.1',
      },
      {
        timestamp: '2025-01-13 02:50:45',
        action_type: 'Rate Limit',
        admin_or_automated: 'Automated',
        reason: 'Rate limited 10.0.0.1 (0A:47:01:10:4D:6D) to 50 bps.',
        source_ip: '10.0.0.1',
      },
      {
        timestamp: '2025-01-13 02:46:59',
        action_type: 'Block',
        admin_or_automated: 'Admin',
        reason: 'Blocked traffic for 10.0.0.1/32 to 10.0.0.2/32.',
        source_ip: '10.0.0.1/32',
      },
      {
        timestamp: '2026-11-20 10:15:00',
        action_type: 'Unblock',
        admin_or_automated: 'Admin',
        reason: 'Operator approved rollback of ACL rule for 10.0.0.5.',
        source_ip: '10.0.0.5',
      },
    ],
  },
};

function renderDecisionLogs(locale = 'vi') {
  window.localStorage.setItem('sdnflowguard_locale', locale);
  return render(
    <ThemeProvider>
      <LanguageProvider>
        <DecisionLogs />
      </LanguageProvider>
    </ThemeProvider>
  );
}

describe('DecisionLogs Enterprise Layout & Audit Integrity', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    axios.get.mockResolvedValue(mockDecisionData);
  });

  test('renders page header, telemetry badges, and two separated cards', async () => {
    renderDecisionLogs('en');

    // Title & subtitle
    expect(await screen.findByText('Policy Decision & Enforcement Logs')).toBeInTheDocument();
    expect(screen.getByText(/Audit trail of defense policy decisions/i)).toBeInTheDocument();

    // Telemetry Badges
    expect(screen.getByText(/Storage: SQLite/i)).toBeInTheDocument();
    expect(screen.getByText(/Mode: DRY_RUN/i)).toBeInTheDocument();
    const recordBadges = await screen.findAllByText(/Showing 4 of 4 records/i);
    expect(recordBadges.length).toBeGreaterThanOrEqual(1);

    // Two cards
    expect(screen.getByText('Audit Filters')).toBeInTheDocument();
    expect(screen.getByText('Network Policy Audit Records')).toBeInTheDocument();
  });

  test('accurately identifies historical legacy log without mutating database', async () => {
    renderDecisionLogs('vi');

    await screen.findByText(/50 bps/i);

    // Look for Historical Log tag
    const historicalTag = screen.getByText('Bản ghi lịch sử (Legacy Log)');
    expect(historicalTag).toBeInTheDocument();
  });

  test('filters audit records by action type', async () => {
    renderDecisionLogs('en');

    await screen.findByText(/Redirected traffic from 10.0.0.1/i);

    // Filter by Block action
    const actionSelect = screen.getByLabelText('Action Type:');
    fireEvent.change(actionSelect, { target: { value: 'block' } });

    await waitFor(() => {
      expect(screen.getByText(/Blocked traffic for 10.0.0.1\/32/i)).toBeInTheDocument();
    });
    expect(screen.queryByText(/Redirected traffic from 10.0.0.1/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/50 bps/i)).not.toBeInTheDocument();
  });

  test('filters audit records by initiation source (Automated vs Admin)', async () => {
    renderDecisionLogs('en');

    await screen.findByText(/Redirected traffic from 10.0.0.1/i);

    // Filter by Admin
    const sourceSelect = screen.getByLabelText('Initiation Source:');
    fireEvent.change(sourceSelect, { target: { value: 'admin' } });

    await waitFor(() => {
      expect(screen.getByText(/Blocked traffic for 10.0.0.1\/32/i)).toBeInTheDocument();
    });
    expect(screen.getByText(/Operator approved rollback/i)).toBeInTheDocument();
    expect(screen.queryByText(/Redirected traffic from 10.0.0.1/i)).not.toBeInTheDocument();
  });

  test('searches by IP keyword and resets filters properly', async () => {
    renderDecisionLogs('vi');

    await screen.findByText(/Redirected traffic from 10.0.0.1/i);

    const searchInput = screen.getByPlaceholderText(/Lọc theo IP/i);
    fireEvent.change(searchInput, { target: { value: '10.0.0.5' } });

    expect(await screen.findByText('Operator approved rollback of ACL rule for 10.0.0.5.')).toBeInTheDocument();
    expect(screen.queryByText(/10.0.0.1\/32/i)).not.toBeInTheDocument();

    // Reset button appears
    const resetButtons = screen.getAllByTitle(/Đặt lại bộ lọc/i);
    fireEvent.click(resetButtons[0]);

    await waitFor(() => {
      expect(searchInput.value).toBe('');
    });
    expect(screen.getByText(/Blocked traffic for 10.0.0.1\/32/i)).toBeInTheDocument();
  });

  test('distinguishes automated initiation from unverified dataplane status', async () => {
    renderDecisionLogs('vi');

    await screen.findByText(/Redirected traffic from 10.0.0.1/i);

    // Check that automated source badge is rendered
    const automatedBadges = screen.getAllByText('Hệ thống tự động (Safety Gate)');
    expect(automatedBadges.length).toBeGreaterThanOrEqual(1);

    // Check that unverified dataplane subtext is rendered
    const dryRunStatuses = screen.getAllByText('DRY_RUN (Chưa xác minh Dataplane)');
    expect(dryRunStatuses.length).toBeGreaterThanOrEqual(1);
  });
});
