import http from 'k6/http';
import { check, group, sleep } from 'k6';

/**
 * Smoke load test (cheap and fast)
 *
 * Goal
 * ----
 * Quick validation that core endpoints are responsive under light load.
 *
 * Execution model
 * ---------------
 * - constant VUs for a short duration (vus + duration)
 *
 * Environment variables
 * ---------------------
 * - API_URL         Base URL (default: http://localhost:8091)
 * - DEMO_EMAIL      Login user (default: customer@practicesoftwaretesting.com)
 * - DEMO_PASSWORD   Login password (default: welcome01)
 *
 * - VUS             Number of VUs (default: 10)
 * - DURATION        Test duration (default: 1m)
 * - AUTH            If "true", run authenticated /users/me checks (default: true)
 *
 * Notes
 * -----
 * - Uses setup() to perform login once and share the token with all VUs.
 * - Product selection is deterministic per VU via __VU (kept identical).
 */
export const options = {
  vus: Number(__ENV.VUS || 10),
  duration: String(__ENV.DURATION || '1m'),
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<800', 'p(99)<1500'],
  },
};

const API_BASE_URL = (__ENV.API_URL || 'http://localhost:8091').replace(/\/+$/, '');
const DEMO_EMAIL = __ENV.DEMO_EMAIL || 'customer@practicesoftwaretesting.com';
const DEMO_PASSWORD = __ENV.DEMO_PASSWORD || 'welcome01';
const AUTH_ENABLED = String(__ENV.AUTH || 'true').toLowerCase() === 'true';

function buildUrl(path) {
  return `${API_BASE_URL}${path}`;
}

function loginOnce() {
  if (!AUTH_ENABLED) return { token: null };

  const payload = JSON.stringify({ email: DEMO_EMAIL, password: DEMO_PASSWORD });
  const params = {
    headers: { 'Content-Type': 'application/json' },
    tags: { name: 'POST /users/login' },
  };

  const res = http.post(buildUrl('/users/login'), payload, params);
  const ok = check(res, { 'login 200': (r) => r.status === 200 });
  if (!ok) return { token: null };

  const body = res.json();
  return { token: body && body.access_token ? body.access_token : null };
}

function pickDeterministicProductId(items) {
  if (!Array.isArray(items) || items.length === 0) return null;

  // Deterministic selection to spread VUs across items (original behavior).
  const idx = (__VU - 1) % items.length;
  const item = items[idx];
  return item && item.id ? String(item.id) : null;
}

export function setup() {
  return loginOnce();
}

export default function (data) {
  let productId = null;

  group('catalog', () => {
    const res = http.get(buildUrl('/products?page=1'), { tags: { name: 'GET /products' } });
    check(res, { 'products 200': (r) => r.status === 200 });

    if (res.status === 200) {
      const body = res.json();
      const items = body && body.data ? body.data : [];
      productId = pickDeterministicProductId(items);
    }
  });

  group('lists', () => {
    const brands = http.get(buildUrl('/brands'), { tags: { name: 'GET /brands' } });
    check(brands, { 'brands 200': (r) => r.status === 200 });

    const categories = http.get(buildUrl('/categories'), { tags: { name: 'GET /categories' } });
    check(categories, { 'categories 200': (r) => r.status === 200 });
  });

  if (productId) {
    group('product-detail', () => {
      const res = http.get(buildUrl(`/products/${productId}`), { tags: { name: 'GET /products/:id' } });
      check(res, { 'product 200': (r) => r.status === 200 });
    });

    group('product-related', () => {
      const res = http.get(buildUrl(`/products/${productId}/related`), { tags: { name: 'GET /products/:id/related' } });
      check(res, { 'related 200': (r) => r.status === 200 });
    });
  }

  if (AUTH_ENABLED && data && data.token) {
    group('auth', () => {
      const res = http.get(buildUrl('/users/me'), {
        headers: { Authorization: `Bearer ${data.token}` },
        tags: { name: 'GET /users/me' },
      });
      check(res, { 'me 200': (r) => r.status === 200 });
    });
  }

  // Fixed pacing (kept identical).
  sleep(1);
}