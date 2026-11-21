// Centralized API configuration for SDNFlowGuard Frontend
export const API_BASE_URL = (
  process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:5000'
).replace(/\/+$/, '');

export const OPERATOR_KEY_STORAGE_KEY = 'sdnflow_operator_api_key';

export const getOperatorApiKey = () => {
  try {
    if (typeof window !== 'undefined' && window.sessionStorage) {
      const sessionKey = window.sessionStorage.getItem(OPERATOR_KEY_STORAGE_KEY);
      if (sessionKey && sessionKey.trim()) {
        return sessionKey.trim();
      }
    }
  } catch (err) {
    // Ignore storage access errors in restricted browser contexts
  }
  return '';
};

export const setOperatorApiKey = (apiKey) => {
  try {
    if (typeof window !== 'undefined' && window.sessionStorage) {
      if (apiKey && String(apiKey).trim()) {
        window.sessionStorage.setItem(OPERATOR_KEY_STORAGE_KEY, String(apiKey).trim());
      } else {
        window.sessionStorage.removeItem(OPERATOR_KEY_STORAGE_KEY);
      }
    }
  } catch (err) {
    // Ignore storage access errors
  }
};

export const getApiHeaders = () => {
  const headers = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  };
  // Prefer runtime session-scoped operator key; never bake production secrets into REACT_APP_* bundles.
  const apiKey = getOperatorApiKey();
  if (apiKey) {
    headers['X-SDNFlow-API-Key'] = apiKey;
  }
  return headers;
};

export const isValidIpAddress = (value) => {
  if (!value || typeof value !== 'string') return false;
  const trimmed = value.trim();
  const ipv4Regex =
    /^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$/;
  const ipv6Regex = /^([0-9a-fA-F]{1,4}:){1,7}[0-9a-fA-F]{1,4}$|^::1$/;
  return ipv4Regex.test(trimmed) || ipv6Regex.test(trimmed);
};

