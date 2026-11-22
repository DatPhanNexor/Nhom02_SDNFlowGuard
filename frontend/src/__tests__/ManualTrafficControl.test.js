import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, fireEvent } from '@testing-library/react';
import axios from 'axios';
import { LanguageProvider } from '../i18n/LanguageContext';
import { ThemeProvider } from '../theme/ThemeContext';
import ManualTrafficControl from '../pages/ManualTrafficControl';

jest.mock('axios', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

function renderManualControl(locale = 'vi') {
  window.localStorage.setItem('sdnflowguard_locale', locale);
  return render(
    <ThemeProvider>
      <LanguageProvider>
        <ManualTrafficControl />
      </LanguageProvider>
    </ThemeProvider>
  );
}

describe('ManualTrafficControl 5-Step Execution Workflow', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders all 5 steps in strictly sequential order for block action', () => {
    renderManualControl('vi');

    // Title
    expect(screen.getByText('Điều khiển lưu lượng thủ công')).toBeInTheDocument();

    // Verify all 5 steps in order
    expect(screen.getByText('1. Chọn loại hành động can thiệp')).toBeInTheDocument();
    expect(screen.getByText('2. Điểm đầu và Điểm cuối (Layer 2 / Layer 3)')).toBeInTheDocument();
    expect(screen.getByText('3. Điều kiện khớp luồng (Flow Match Criteria)')).toBeInTheDocument();
    expect(screen.getByText('4. Kiểm soát an toàn & Phê duyệt Safety Gate')).toBeInTheDocument();
    expect(screen.getByText('5. Xem trước chính sách (Policy Preview)')).toBeInTheDocument();

    // Execute button
    expect(screen.getByText('Áp dụng chính sách mạng')).toBeInTheDocument();
  });

  test('verifies English localization and 5-step numbering for rate-limit action', () => {
    renderManualControl('en');

    // Change action to rate-limit
    const actionSelect = screen.getAllByRole('combobox')[0];
    fireEvent.change(actionSelect, { target: { value: 'rate-limit' } });

    // Step 1: Action Selection
    expect(screen.getByText('1. Select Enforcement Action')).toBeInTheDocument();
    // Step 2: Endpoints
    expect(screen.getByText('2. Layer 2 / Layer 3 Endpoints')).toBeInTheDocument();
    // Step 3: Rate Limit Configuration
    expect(screen.getByText('3. Rate Limit Configuration')).toBeInTheDocument();
    // Step 4: Safety Gate
    expect(screen.getByText('4. Safety Gate & Execution Mode')).toBeInTheDocument();
    // Step 5: Policy Preview
    expect(screen.getByText('5. Policy Preview')).toBeInTheDocument();

    // Check rate limit input field and unit note
    expect(screen.getByPlaceholderText(/1000000 bps/i)).toBeInTheDocument();
    expect(screen.getByText(/OpenFlow 1.3 Meter/i)).toBeInTheDocument();
  });

  test('toggles DRY_RUN simulation mode and updates policy preview', () => {
    renderManualControl('en');

    // Initial DRY_RUN is checked
    const dryRunCheckbox = screen.getByRole('checkbox');
    expect(dryRunCheckbox).toBeChecked();
    expect(screen.getByText(/DRY_RUN \(SIMULATED\)/i)).toBeInTheDocument();

    // Toggle DRY_RUN off
    fireEvent.click(dryRunCheckbox);
    expect(dryRunCheckbox).not.toBeChecked();
    expect(screen.getByText(/LIVE_ENFORCEMENT/i)).toBeInTheDocument();
    expect(screen.getByText(/WARNING: Disabling DRY_RUN/i)).toBeInTheDocument();
  });

  test('validates negative rate limit input', () => {
    renderManualControl('vi');

    const actionSelect = screen.getAllByRole('combobox')[0];
    fireEvent.change(actionSelect, { target: { value: 'rate-limit' } });

    const hostInput = screen.getByPlaceholderText('vd: 10.0.0.1');
    fireEvent.change(hostInput, { target: { value: '10.0.0.1' } });

    const rateInput = screen.getByPlaceholderText(/1000000 bps/i);
    fireEvent.change(rateInput, { target: { value: '-500' } });

    const submitBtn = screen.getByText('Áp dụng chính sách mạng');
    fireEvent.click(submitBtn);

    expect(screen.getByText(/Lỗi xác thực: Giới hạn tốc độ/i)).toBeInTheDocument();
    expect(axios.post).not.toHaveBeenCalled();
  });

  test('resets form when reset button is clicked', () => {
    renderManualControl('en');

    const srcInput = screen.getByPlaceholderText(/Enter Source IP/i);
    fireEvent.change(srcInput, { target: { value: '10.0.0.5' } });
    expect(srcInput.value).toBe('10.0.0.5');

    const resetBtn = screen.getByText('Reset Form');
    fireEvent.click(resetBtn);

    expect(srcInput.value).toBe('');
  });

  test('rejects policy execution and displays clear validation error when Target Subject is not specified', () => {
    renderManualControl('en');

    // Verify Target Subject shows Not specified (IP required)
    expect(screen.getByText('Not specified (IP required)')).toBeInTheDocument();

    // Click Apply Network Policy without specifying Target IP
    const submitBtn = screen.getByText('Apply Network Policy');
    fireEvent.click(submitBtn);

    // Explicit validation error displayed
    expect(screen.getByText(/Validation Error: Please enter a valid Source IP or Destination IP/i)).toBeInTheDocument();
    expect(axios.post).not.toHaveBeenCalled();
  });
});
