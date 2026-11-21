import fs from 'fs';
import path from 'path';
import { vi } from '../i18n/vi';
import { en } from '../i18n/en';

function flattenDict(obj, prefix = '') {
  const out = {};
  Object.entries(obj).forEach(([key, val]) => {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    if (val && typeof val === 'object' && !Array.isArray(val)) {
      Object.assign(out, flattenDict(val, fullKey));
    } else {
      out[fullKey] = val;
    }
  });
  return out;
}

function walkJsFiles(dir) {
  const results = [];
  fs.readdirSync(dir, { withFileTypes: true }).forEach((entry) => {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name !== '__tests__') {
        results.push(...walkJsFiles(full));
      }
    } else if (entry.isFile() && entry.name.endsWith('.js')) {
      results.push(full);
    }
  });
  return results;
}

describe('SDNFlowGuard i18n Integrity & UI Label Hygiene', () => {
  const flatVi = flattenDict(vi);
  const flatEn = flattenDict(en);

  test('vi.js and en.js have 100% key parity', () => {
    const viKeys = Object.keys(flatVi).sort();
    const enKeys = Object.keys(flatEn).sort();
    expect(viKeys).toEqual(enKeys);
  });

  test('every t("...") key used in frontend/src exists in both vi.js and en.js', () => {
    const srcRoot = path.resolve(__dirname, '..');
    const jsFiles = walkJsFiles(srcRoot);
    const keyRegex = /\bt\(\s*['"]([a-zA-Z0-9_.-]+)['"]/g;
    const missingVi = [];
    const missingEn = [];

    jsFiles.forEach((filePath) => {
      const content = fs.readFileSync(filePath, 'utf8');
      let match;
      while ((match = keyRegex.exec(content)) !== null) {
        const key = match[1];
        if (!(key in flatVi)) missingVi.push(`${path.basename(filePath)} -> ${key}`);
        if (!(key in flatEn)) missingEn.push(`${path.basename(filePath)} -> ${key}`);
      }
    });

    expect(missingVi).toEqual([]);
    expect(missingEn).toEqual([]);
  });

  test('no internal milestone labels (Step 63/64/72) appear in user-facing translations', () => {
    const forbidden = /step\s*6[34]|step\s*72/i;
    const leaks = [];

    Object.entries(flatVi).forEach(([k, v]) => {
      if (typeof v === 'string' && forbidden.test(v)) {
        leaks.push(`vi.${k}: ${v}`);
      }
    });
    Object.entries(flatEn).forEach(([k, v]) => {
      if (typeof v === 'string' && forbidden.test(v)) {
        leaks.push(`en.${k}: ${v}`);
      }
    });

    expect(leaks).toEqual([]);
  });
});
