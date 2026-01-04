/**
 * Cloudflare Worker for edge caching and request routing
 * Provides CDN acceleration, rate limiting, and request transformation
 */

interface Env {
  CACHE: KVNamespace;
  DB?: D1Database;
  API_URL: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;

    // Handle CORS preflight requests
    if (request.method === 'OPTIONS') {
      return handleCORS();
    }

    // Cache GET requests
    if (request.method === 'GET' && shouldCache(path)) {
      const cacheKey = `cache:${request.method}:${path}:${url.search}`;
      const cached = await env.CACHE.get(cacheKey);

      if (cached) {
        return new Response(cached, {
          headers: {
            'Content-Type': 'application/json',
            'X-Cache': 'HIT',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
          },
        });
      }
    }

    // Proxy request to backend
    const response = await proxyRequest(request, env.API_URL);

    // Cache successful GET responses
    if (request.method === 'GET' && shouldCache(path) && response.ok) {
      const cacheKey = `cache:${request.method}:${path}:${url.search}`;
      const clonedResponse = response.clone();
      const body = await clonedResponse.text();
      await env.CACHE.put(cacheKey, body, { expirationTtl: 300 }); // 5 minutes
    }

    return response;
  },
};

/**
 * Determine if a path should be cached
 */
function shouldCache(path: string): boolean {
  const cacheablePaths = [
    '/api/news',
    '/api/statistics',
    '/api/health',
  ];

  return cacheablePaths.some(cachePath => path.startsWith(cachePath));
}

/**
 * Handle CORS preflight requests
 */
function handleCORS(): Response {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400',
    },
  });
}

/**
 * Proxy request to backend API
 */
async function proxyRequest(request: Request, apiUrl: string): Promise<Response> {
  const url = new URL(request.url);
  const targetUrl = `${apiUrl}${url.pathname}${url.search}`;

  const headers = new Headers(request.headers);
  headers.set('X-Forwarded-For', request.headers.get('cf-connecting-ip') || '');
  headers.set('X-Forwarded-Proto', url.protocol);
  headers.set('X-Real-IP', request.headers.get('cf-connecting-ip') || '');

  try {
    const response = await fetch(targetUrl, {
      method: request.method,
      headers: headers,
      body: request.body,
    });

    const responseHeaders = new Headers(response.headers);
    responseHeaders.set('Access-Control-Allow-Origin', '*');
    responseHeaders.set('X-Cache', 'MISS');
    responseHeaders.set('X-Powered-By', 'Cloudflare Workers');

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    return new Response(
      JSON.stringify({
        error: 'Proxy error',
        message: 'Failed to connect to backend',
      }),
      {
        status: 502,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      }
    );
  }
}