/**
 * API Client for external services
 * @module api
 */

class APIClient {
  constructor(baseURL, options = {}) {
    this.baseURL = baseURL;
    this.timeout = options.timeout || 5000;
    this.retries = options.retries || 3;
  }

  /**
   * Make HTTP request with retry logic
   */
  async request(endpoint, method = 'GET', data = null) {
    const url = `${this.baseURL}${endpoint}`;
    let lastError = null;

    // Retry loop
    for (let attempt = 0; attempt < this.retries; attempt++) {
      try {
        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json',
          },
          body: data ? JSON.stringify(data) : null,
        });

        if (response.ok) {
          return await response.json();
        } else if (response.status === 429) {
          // Rate limited, wait and retry
          await this.sleep(1000 * (attempt + 1));
          continue;
        } else if (response.status >= 500) {
          // Server error, retry
          lastError = new Error(`Server error: ${response.status}`);
          continue;
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        lastError = error;
        if (attempt < this.retries - 1) {
          await this.sleep(500 * (attempt + 1));
        }
      }
    }

    throw lastError || new Error('Request failed');
  }

  async get(endpoint) {
    return this.request(endpoint, 'GET');
  }

  async post(endpoint, data) {
    return this.request(endpoint, 'POST', data);
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Export for use
module.exports = { APIClient };
