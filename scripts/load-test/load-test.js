/**
 * SmartAmazon Load Testing Script
 * Uses k6 for load testing the API
 *
 * Install k6: https://k6.io/docs/getting-started/installation/
 * Run: k6 run load-test.js
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const searchDuration = new Trend('search_duration');
const productDetailDuration = new Trend('product_detail_duration');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 10 },   // Ramp up to 10 users
    { duration: '5m', target: 10 },   // Stay at 10 users
    { duration: '2m', target: 50 },   // Ramp up to 50 users
    { duration: '5m', target: 50 },   // Stay at 50 users
    { duration: '2m', target: 100 },  // Spike to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '3m', target: 0 },    // Ramp down
  ],
  thresholds: {
    'http_req_duration': ['p(95)<2000'],  // 95% of requests should complete under 2s
    'http_req_failed': ['rate<0.05'],     // Less than 5% error rate
    'errors': ['rate<0.1'],                // Less than 10% application errors
  },
};

const BASE_URL = __ENV.API_URL || 'http://localhost:8000';

// Test scenarios
export default function () {
  // Scenario 1: Search products
  group('Search Products', function () {
    const searchQueries = [
      'protein powder',
      'vitamins',
      'coffee beans',
      'dog food',
      'laundry detergent'
    ];

    const query = searchQueries[Math.floor(Math.random() * searchQueries.length)];
    const params = {
      tags: { name: 'Search' },
      timeout: '10s',
    };

    const res = http.get(
      `${BASE_URL}/api/search?q=${query}&sort=unit_price_asc`,
      params
    );

    const success = check(res, {
      'status is 200': (r) => r.status === 200,
      'response has results': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.results && Array.isArray(body.results);
        } catch (e) {
          return false;
        }
      },
      'response time < 2s': (r) => r.timings.duration < 2000,
    });

    errorRate.add(!success);
    searchDuration.add(res.timings.duration);

    sleep(1);
  });

  // Scenario 2: Get product details
  group('Product Details', function () {
    // First, search to get a product ASIN
    const searchRes = http.get(`${BASE_URL}/api/search?q=protein`);

    if (searchRes.status === 200) {
      try {
        const searchBody = JSON.parse(searchRes.body);
        if (searchBody.results && searchBody.results.length > 0) {
          const asin = searchBody.results[0].asin;

          // Now get product details
          const detailRes = http.get(`${BASE_URL}/api/product/${asin}`);

          const success = check(detailRes, {
            'status is 200': (r) => r.status === 200,
            'product has title': (r) => {
              try {
                const body = JSON.parse(r.body);
                return body.title && body.title.length > 0;
              } catch (e) {
                return false;
              }
            },
          });

          errorRate.add(!success);
          productDetailDuration.add(detailRes.timings.duration);
        }
      } catch (e) {
        errorRate.add(true);
      }
    }

    sleep(1);
  });

  // Scenario 3: Filter and sort
  group('Advanced Filtering', function () {
    const filters = [
      'min_price=10&max_price=50',
      'min_rating=4.5&prime_only=true',
      'hide_sponsored=true&min_rating=4.0',
    ];

    const filter = filters[Math.floor(Math.random() * filters.length)];

    const res = http.get(
      `${BASE_URL}/api/search?q=vitamins&${filter}`,
      { tags: { name: 'Filtered Search' } }
    );

    check(res, {
      'status is 200': (r) => r.status === 200,
      'response time < 3s': (r) => r.timings.duration < 3000,
    });

    sleep(1);
  });

  // Scenario 4: Get categories and brands
  group('Metadata Endpoints', function () {
    const categoriesRes = http.get(`${BASE_URL}/api/categories`);
    check(categoriesRes, {
      'categories status is 200': (r) => r.status === 200,
    });

    const brandsRes = http.get(`${BASE_URL}/api/brands`);
    check(brandsRes, {
      'brands status is 200': (r) => r.status === 200,
    });

    sleep(0.5);
  });

  // Random think time between user actions
  sleep(Math.random() * 3);
}

// Setup function - runs once before all VUs
export function setup() {
  console.log('Starting load test...');
  console.log(`Target: ${BASE_URL}`);

  // Warm up the service
  http.get(`${BASE_URL}/health`);
  return { startTime: new Date() };
}

// Teardown function - runs once after all VUs
export function teardown(data) {
  const endTime = new Date();
  const duration = (endTime - data.startTime) / 1000;
  console.log(`Load test completed in ${duration} seconds`);
}
