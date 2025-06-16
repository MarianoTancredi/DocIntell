import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '1m', target: 20 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.1'],
  },
};

const BASE_URL = 'http://localhost:8000';

export default function () {
  // Health check
  let healthResponse = http.get(`${BASE_URL}/health`);
  check(healthResponse, {
    'health check status is 200': (r) => r.status === 200,
    'health response time < 100ms': (r) => r.timings.duration < 100,
  });

  // API endpoint tests
  let apiResponse = http.get(`${BASE_URL}/api/v1/auth/login`);
  check(apiResponse, {
    'auth endpoint accessible': (r) => r.status === 422, // Expected for GET without credentials
  });

  sleep(1);
}