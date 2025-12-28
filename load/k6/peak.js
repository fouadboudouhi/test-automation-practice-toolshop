import http from 'k6/http';
import { check, group, sleep } from 'k6';

/**
 * Peak test (short, intense spike)
 *
 * Goal
 * ----
 * Validate system behavior under near-max load for a short time window.
 *
 * Scenario
 * --------
 * - ramping-vus: 0 -> PEAK_VUS -> hold -> 0
 *
 * Environment variables
 * ---------------------
 * - API_URL         Base URL (default: http://localhost:8091)
 * - DEMO_EMAIL      Login user (default: customer@practicesoftwaretesting.com)
 * - DEMO_PASSWORD   Login password (default: welcome01)
 *
 * - PEAK_RAMP_UP    Stage duration (default: 15s)
 * - PEAK_VUS        Target VUs (default: 50)
 * - PEAK_HOLD       Hold duration (default: 60s)
 * - PEAK_RAMP_DOWN  Ramp down duration (default: 30s)
 *
 * Notes
 * -----
 * - Uses per-VU token caching and refresh close to expiry to reduce login overhead.
 * - Adds jitter (random sleeps) to avoid synchronized request bursts.
 */
export const options = {
  scenarios: {
    peak: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        {
          duration: String(__ENV.PEAK_RAMP_UP || '15s'),
          target: Number(__ENV.PEAK_VUS || 50),
        },
        {
          duration: String(__ENV.PEAK_HOLD || '60s'),
          target: Number(__ENV.PEAK_VUS || 50),
        },
        {
          duration: String(__ENV.PEAK_RAMP_DOWN || '30s'),
          target: 0,
        },
      ],
      gracefulRampDown: '30s',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.02'],
    http_req_duration: ['p(95)<1500', 'p(99)<3000'],
  },
};

const API_BASE_URL = (__ENV.API_URL || 'http://localhost:8091').replace(/\/+$/, '');
const DEMO_EMAIL = __ENV.DEMO_EMAIL || 'customer@practicesoftwaretesting.com';
const DEMO_PASSWORD = __ENV.DEMO_PASSWORD || 'welcome01';

function buildUrl(path) {
  return `${API_BASE_URL}${path}`;
}

/**
 * Per-VU auth cache:
 * - token: Bearer token
 * - tokenExpMs: absolute expiration timestamp (ms)
 */
let token = null;
let tokenExpMs = 0;

function login() {
  const payload = JSON.stringify({ email: DEMO_EMAIL, password: DEMO_PASSWORD });

  const res = http.post(buildUrl('/users/login'), payload, {
    headers: { 'Content-Type': 'application/json' },
    tags: { name: 'POST /users/login' },
  });

  const ok = check(res, { 'login 200': (r) => r.status === 200 });
  if (!ok) return;

  const body = res.json() || {};
  token = body.access_token || null;

  const expires = Number(body.expires_in || 120);
  tokenExpMs = Date.now() + expires * 1000;
}

function ensureToken() {
  if (!token || Date.now() > tokenExpMs - 5000) login();
}

function jitter(min = 0.1, max = 0.8) {
  sleep(min + Math.random() * (max - min));
}

function pickRandomProductId(items) {
  if (!Array.isArray(items) || items.length === 0) return null;

  const idx = Math.floor(Math.random() * items.length);
  const item = items[idx];
  return item && item.id ? String(item.id) : null;
}

export default function () {
  let productId = null;

  group('catalog', () => {
    const res = http.get(buildUrl('/products?page=1'), { tags: { name: 'GET /products' } });
    check(res, { 'products 200': (r) => r.status === 200 });

    if (res.status === 200) {
      const body = res.json() || {};
      productId = pickRandomProductId(body.data || []);
    }
  });

  jitter();

  group('lists', () => {
    const brands = http.get(buildUrl('/brands'), { tags: { name: 'GET /brands' } });
    check(brands, { 'brands 200': (r) => r.status === 200 });

    const categories = http.get(buildUrl('/categories'), { tags: { name: 'GET /categories' } });
    check(categories, { 'categories 200': (r) => r.status === 200 });
  });

  if (productId) {
    jitter(0.05, 0.4);

    group('product-detail', () => {
      const res = http.get(buildUrl(`/products/${productId}`), { tags: { name: 'GET /products/:id' } });
      check(res, { 'product 200': (r) => r.status === 200 });
    });

    jitter(0.05, 0.4);

    group('product-related', () => {
      const res = http.get(buildUrl(`/products/${productId}/related`), { tags: { name: 'GET /products/:id/related' } });
      check(res, { 'related 200': (r) => r.status === 200 });
    });
  }

  jitter(0.05, 0.5);

  group('auth', () => {
    ensureToken();
    if (!token) return;

    const res = http.get(buildUrl('/users/me'), {
      headers: { Authorization: `Bearer ${token}` },
      tags: { name: 'GET /users/me' },
    });
    check(res, { 'me 200': (r) => r.status === 200 });
  });

  jitter(0.1, 0.9);
}