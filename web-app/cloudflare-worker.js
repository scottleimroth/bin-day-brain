// Bin Day Brain - Cloudflare Worker Proxy
// This proxies requests to the Wollongong Waste API to bypass CORS

const API_BASE = 'https://wollongong.waste-info.com.au/api/v1';

// Allowed endpoints (security - only proxy what we need)
const ALLOWED_PATHS = [
  '/localities.json',
  '/streets.json',
  '/properties.json',
  '/materials.json',
  '/events.json'
];

export default {
  async fetch(request) {
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Access-Control-Max-Age': '86400',
        }
      });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    // Check if path is allowed
    const isAllowed = ALLOWED_PATHS.some(allowed => path.startsWith(allowed.replace('.json', ''))) ||
                      path.match(/^\/properties\/\d+\.json$/);

    if (!isAllowed) {
      return new Response(JSON.stringify({ error: 'Not allowed' }), {
        status: 403,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }

    // Build the API URL
    const apiUrl = API_BASE + path + url.search;

    try {
      // Fetch from the real API
      const response = await fetch(apiUrl, {
        headers: {
          'User-Agent': 'BinDayBrain/1.0',
          'Accept': 'application/json'
        }
      });

      // Get the response body
      const data = await response.text();

      // Return with CORS headers
      return new Response(data, {
        status: response.status,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Cache-Control': 'public, max-age=300' // Cache for 5 minutes
        }
      });
    } catch (error) {
      return new Response(JSON.stringify({ error: 'Proxy error' }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
  }
};
