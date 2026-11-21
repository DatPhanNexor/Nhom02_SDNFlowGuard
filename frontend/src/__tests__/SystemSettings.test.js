import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, fireEvent } from '@testing-library/react';
import axios from 'axios';
import { LanguageProvider } from '../i18n/LanguageContext';
import { ThemeProvider } from '../theme/ThemeContext';
import SystemSettings from '../pages/SystemSettings';

jest.mock('axios', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

const mockSettings = {
  data: {
    status: 'success',
    data: {
      Mode: 'balanced',
      'SDN Controller IP': '127.0.0.1',
      'ELK IP Address': '10.0.0.100',
      'Honeypot IP Address': '10.0.0.6',
    },
  },
};

const mockHealth = {
  data: {
    status: 'OK',
    defense_mode: 'DRY_RUN',
    config: {
      allowlist_ips: ['127.0.0.1', '::1'],
      db_path: '/app/database/sdnflowguard.db',
      defense_mode: 'DRY_RUN',
      elk_url: 'http://elasticsearch:9200',
      onos_url: 'http://onos:8181/onos/v1',
    },
  },
};

function renderSettings(locale = 'vi') {
  window.localStorage.setItem('sdnflowguard_locale', locale);
  return render(
    <ThemeProvider>
      <LanguageProvider>
        <SystemSettings />
      </LanguageProvider>
    </ThemeProvider>
  );
}

describe('SystemSettings Enterprise Layout & Functional Verification', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    axios.get.mockImplementation((url) => {
      if (url.includes('/api/get-settings')) return Promise.resolve(mockSettings);
      if (url.includes('/api/health')) return Promise.resolve(mockHealth);
      return Promise.reject(new Error(`Unhandled GET: ${url}`));
    });
  });

  test('renders centered settings-container and all primary sections', async () => {
    renderSettings('en');
    await screen.findByDisplayValue('127.0.0.1');

    const settingsContainer = screen.getByTestId('settings-container');
    expect(settingsContainer).toBeInTheDocument();

    // Check title & subtitle
    expect(screen.getByText('System Settings')).toBeInTheDocument();
    expect(screen.getByText(/Manage network service endpoints/i)).toBeInTheDocument();

    // Check Notice Card
    const noticeCard = screen.getByRole('note', { name: /Runtime Precedence Notice/i });
    expect(noticeCard).toBeInTheDocument();

    // Verify NO DUPLICATE Runtime Precedence Notice prefix
    const noticeText = noticeCard.textContent;
    const occurrences = (noticeText.match(/Runtime Precedence Notice:/g) || []).length;
    expect(occurrences).toBe(1);

    // Check all 3 section headings
    const sectionHeadings = screen.getAllByRole('heading', { level: 3 });
    expect(sectionHeadings).toHaveLength(3);
  });

  test('verifies Vietnamese localization without duplicate notice prefix', async () => {
    renderSettings('vi');
    await screen.findByDisplayValue('127.0.0.1');

    expect(screen.getByText('Cấu hình hệ thống')).toBeInTheDocument();
    const noticeCard = screen.getByRole('note', { name: /Runtime Precedence Notice/i });
    expect(noticeCard).toBeInTheDocument();

    const noticeText = noticeCard.textContent;
    const occurrences = (noticeText.match(/Lưu ý về thứ tự ưu tiên cấu hình:/g) || []).length;
    expect(occurrences).toBe(1);
    expect(noticeText).not.toContain('Thông báo quyền ưu tiên:');
  });

  test('handles detection mode switching', async () => {
    renderSettings('en');
    await screen.findByDisplayValue('127.0.0.1');

    const strictRadio = screen.getByLabelText(/Strict/i);
    const balancedRadio = screen.getByLabelText(/Balanced/i);

    expect(balancedRadio).toBeChecked();

    fireEvent.click(strictRadio);
    expect(strictRadio).toBeChecked();
    expect(screen.getByText(/High sensitivity, low thresholds/i)).toBeInTheDocument();
  });

  test('validates IP address inputs before saving', async () => {
    renderSettings('en');
    const ctrlInput = await screen.findByDisplayValue('127.0.0.1');
    fireEvent.change(ctrlInput, { target: { value: 'invalid-ip-string' } });

    const saveBtn = screen.getByRole('button', { name: /Save System Settings/i });
    fireEvent.click(saveBtn);

    expect(await screen.findByRole('alert')).toHaveTextContent(/Validation Error/i);
    expect(axios.post).not.toHaveBeenCalled();
  });

  test('renders effective runtime configuration code viewer with copy button', async () => {
    renderSettings('en');
    await screen.findByDisplayValue('127.0.0.1');

    const codeViewer = screen.getByTestId('runtime-config-viewer');
    expect(codeViewer).toBeInTheDocument();
    expect(codeViewer.textContent).toContain('DRY_RUN');
    expect(codeViewer.textContent).toContain('http://onos:8181/onos/v1');

    const copyBtn = screen.getByTitle(/Copy active configuration JSON/i);
    expect(copyBtn).toBeInTheDocument();
  });
});
