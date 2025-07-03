import http from 'k6/http';
import { check, sleep } from 'k6';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Test configuration
export const options = {
  // Test scenarios
  scenarios: {
    // Constant load test
    constant_load: {
      executor: 'constant-vus',  // Virtual Users
      vus: 50,                   // 50 concurrent users
      duration: '30s',           // Test for 30 seconds
    },
    // Ramp-up test
    ramp_up: {
      executor: 'ramping-vus',   // Gradually increasing users
      startVUs: 0,               // Start with 0 users
      stages: [
        { duration: '10s', target: 20 },  // Ramp up to 20 users over 10s
        { duration: '20s', target: 50 },  // Ramp up to 50 users over 20s
        { duration: '10s', target: 0 },   // Ramp down to 0 users
      ],
      startTime: '30s',          // Start after the constant load test
    },
    // Stress test
    stress_test: {
      executor: 'ramping-arrival-rate',  // Constant request rate, not constant users
      startRate: 10,             // 10 requests per second
      timeUnit: '1s',
      preAllocatedVUs: 50,       // Initial pool of VUs
      maxVUs: 100,               // Maximum number of VUs to handle the load
      stages: [
        { duration: '10s', target: 50 },  // Ramp up to 50 requests per second
        { duration: '30s', target: 50 },  // Stay at 50 requests per second
        { duration: '10s', target: 0 },   // Ramp down to 0
      ],
      startTime: '70s',          // Start after the ramp-up test
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests should be below 500ms
    http_req_failed: ['rate<0.1'],    // Less than 10% of requests should fail
  },
};

// URL of your application
const BASE_URL = 'http://localhost:5000';

// Generate a random customer
function generateCustomer() {
  const id = Math.floor(Math.random() * 10000);
  return {
    name: `Customer ${id}`,
    email: `customer${id}@example.com`,
    phone: `${Math.floor(1000000000 + Math.random() * 9000000000)}`,
    age: Math.floor(18 + Math.random() * 50)
  };
}

// Main test function
export default function() {
  // Choose a random action with weighted probability
  const action = Math.random();
  
  if (action < 0.6) {
    // 60% chance: View customer list (GET request)
    const res = http.get(`${BASE_URL}/`);
    check(res, {
      'homepage status is 200': (r) => r.status === 200,
      'homepage contains Customer Management': (r) => r.body.includes('Customer Management'),
    });
  } 
  else if (action < 0.9) {
    // 30% chance: Add a new customer (POST request)
    const customer = generateCustomer();
    const payload = {
      name: customer.name,
      email: customer.email,
      phone: customer.phone,
      age: customer.age
    };
    
    const res = http.post(`${BASE_URL}/`, payload);
    check(res, {
      'add customer status is 200': (r) => r.status === 200,
      'customer added successfully': (r) => r.body.includes('Customer added successfully') || r.body.includes('Customer Management'),
    });
  } 
  else {
    // 10% chance: First get the list, then try to edit a customer if any exist
    const listRes = http.get(`${BASE_URL}/`);
    
    // Check if there are any customers to edit (look for edit button)
    if (listRes.body.includes('value="Edit"') || listRes.body.includes('Edit</button>')) {
      // This is a simplification - in a real test, you'd parse the HTML to extract IDs
      // For this demo, we'll just simulate an edit with a random ID
      const randomId = '123456789abcdef'; // This won't work in reality but demonstrates the concept
      
      // First get the edit form
      const editRes = http.get(`${BASE_URL}/edit?id=${randomId}`);
      
      // Then submit the edit form
      if (editRes.status === 200) {
        const customer = generateCustomer();
        const payload = {
          customer_id: randomId,
          name: customer.name,
          email: customer.email,
          phone: customer.phone,
          age: customer.age
        };
        
        const updateRes = http.post(`${BASE_URL}/update`, payload);
        check(updateRes, {
          'update request accepted': (r) => r.status === 200 || r.status === 302,
        });
      }
    }
  }
  
  // Sleep between 1-5 seconds between iterations
  sleep(Math.random() * 4 + 1);
} 