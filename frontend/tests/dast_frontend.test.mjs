import test from 'node:test';
import assert from 'node:assert/strict';

const FRONTEND_URL = 'http://localhost:3000';
const BACKEND_URL = 'http://127.0.0.1:8000';

test('FE-DAST-01: Live SPA entry renders cleanly without debug/stack exposure', async () => {
  const res = await fetch(FRONTEND_URL);
  assert.equal(res.status, 200);
  const html = await res.text();
  assert.ok(html.includes('<div id="root"></div>'), 'Root mount point missing');
  assert.ok(!html.includes('Traceback (most recent call last)'), 'Backend stack trace leaked');
});

test('FE-DAST-02: Sensitive files (.env, .git/config) are not publicly exposed', async () => {
  const sensitivePaths = ['/.env', '/.env.local', '/.git/config'];
  for (const path of sensitivePaths) {
    const res = await fetch(`${FRONTEND_URL}${path}`);
    const body = await res.text();
    assert.ok(
      !body.includes('DB_PASSWORD') && !body.includes('[core]'),
      `Sensitive file leaked at ${path}`
    );
  }
});

test('FE-DAST-03: Reflected XSS payload in URL query is not echoed unescaped', async () => {
  const xssPayload = '<script>alert("xss")</script>';
  const res = await fetch(`${FRONTEND_URL}/?q=${encodeURIComponent(xssPayload)}`);
  assert.equal(res.status, 200);
  const html = await res.text();
  assert.ok(!html.includes(xssPayload), 'Unescaped XSS payload reflected in HTML response');
});

test('FE-DAST-04: CORS policy permits localhost:3000 and blocks untrusted origins', async () => {
  // 1. Valid frontend origin preflight
  const validPreflight = await fetch(`${BACKEND_URL}/api/v1/auth/login`, {
    method: 'OPTIONS',
    headers: {
      Origin: 'http://localhost:3000',
      'Access-Control-Request-Method': 'POST',
    },
  });
  assert.equal(
    validPreflight.headers.get('access-control-allow-origin'),
    'http://localhost:3000'
  );

  // 2. Malicious external origin preflight
  const evilPreflight = await fetch(`${BACKEND_URL}/api/v1/auth/login`, {
    method: 'OPTIONS',
    headers: {
      Origin: 'http://evil-phishing-site.com',
      'Access-Control-Request-Method': 'POST',
    },
  });
  assert.notEqual(
    evilPreflight.headers.get('access-control-allow-origin'),
    'http://evil-phishing-site.com'
  );
});