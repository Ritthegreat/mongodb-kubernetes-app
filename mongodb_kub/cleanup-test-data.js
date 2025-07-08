// cleanup-test-data.js
// Script to remove test customers created by k6 load tests

import http from 'k6/http';
import { check, sleep } from 'k6';

// Test configuration - minimal load for cleanup
export const options = {
  vus: 1,
  iterations: 1,
};

// URL of your application
const BASE_URL = 'http://localhost:5000';

// Helper function to extract customer IDs from HTML
function extractCustomerIds(html) {
  const ids = [];
  const regex = /name="id" value="([^"]+)"/g;
  let match;
  
  while ((match = regex.exec(html)) !== null) {
    ids.push(match[1]);
  }
  
  return ids;
}

// Helper function to check if a customer was created by load test
function isTestCustomer(name) {
  return name && name.includes('Customer ');
}

export default function() {
  console.log('Starting cleanup of test customers...');
  
  // Get the customer list
  const res = http.get(`${BASE_URL}/`);
  check(res, {
    'homepage loaded': (r) => r.status === 200,
  });
  
  // Extract all customer IDs and names
  const customerIds = extractCustomerIds(res.body);
  console.log(`Found ${customerIds.length} total customers`);
  
  // Count of deleted customers
  let deletedCount = 0;
  
  // For each customer ID, check if it's a test customer and delete if it is
  for (const id of customerIds) {
    // Get the customer details page to check the name
    const detailRes = http.get(`${BASE_URL}/edit?id=${id}`);
    
    // Check if this is a test customer by looking for "Customer X" in the name field
    if (detailRes.body.includes('value="Customer ')) {
      // This is a test customer, delete it
      const deleteRes = http.post(`${BASE_URL}/delete`, { id: id });
      
      check(deleteRes, {
        'customer deleted': (r) => r.status === 200 || r.status === 302,
      });
      
      deletedCount++;
      console.log(`Deleted test customer with ID: ${id}`);
      
      // Small pause to avoid overwhelming the server
      sleep(0.2);
    }
  }
  
  console.log(`Cleanup complete. Deleted ${deletedCount} test customers.`);
} 