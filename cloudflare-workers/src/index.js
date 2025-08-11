/**
 * Cloudflare Worker 代理脚本
 * 用于代理 Railway 后端 API 请求
 */

// 缓存配置
const CACHE_TTL = 300; // 5分钟缓存
const ENABLE_CACHE = true;

// 支持的请求方法
const ALLOWED_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'];

// 健康检查路径
const HEALTH_CHECK_PATH = '/health';

addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
    const url = new URL(request.url);
    const path = url.pathname;

    // 健康检查
    if (path === HEALTH_CHECK_PATH) {
        return new Response(JSON.stringify({
            status: 'healthy',
            timestamp: new Date().toISOString(),
            worker: 'financetool-proxy'
        }), {
            status: 200,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        });
    }

    // 处理 CORS 预检请求
    if (request.method === 'OPTIONS') {
        return handleCORS();
    }

    // 验证请求方法
    if (!ALLOWED_METHODS.includes(request.method)) {
        return new Response('Method Not Allowed', { status: 405 });
    }

    try {
        return await proxyRequest(request);
    } catch (error) {
        console.error('Proxy error:', error);
        return new Response(`Proxy Error: ${error.message}`, {
            status: 500,
            headers: {
                'Content-Type': 'text/plain',
                'Access-Control-Allow-Origin': '*'
            }
        });
    }
}

async function proxyRequest(request) {
    const url = new URL(request.url);
    const path = url.pathname;
    const targetUrl = new URL(url.pathname + url.search, RAILWAY_API_URL);

    // 构建请求头
    const headers = new Headers(request.headers);

    // 移除可能导致问题的头部
    headers.delete('host');
    headers.delete('origin');
    headers.delete('referer');

    // 添加代理标识
    headers.set('X-Forwarded-By', 'Cloudflare-Worker');
    headers.set('X-Forwarded-For', request.headers.get('CF-Connecting-IP') || 'unknown');

    // 检查是否需要缓存
    const shouldCache = ENABLE_CACHE &&
        request.method === 'GET' &&
        !path.includes('/sync') &&
        !path.includes('/execute');

    if (shouldCache) {
        const cacheKey = new Request(targetUrl.toString(), {
            method: 'GET',
            headers: headers
        });

        const cache = caches.default;
        let response = await cache.match(cacheKey);

        if (response) {
            console.log('Cache hit for:', targetUrl.toString());
            return addCORSHeaders(response);
        }
    }

    // 创建代理请求
    const proxyRequest = new Request(targetUrl, {
        method: request.method,
        headers: headers,
        body: request.body
    });

    // 发送请求到 Railway
    const response = await fetch(proxyRequest);

    // 如果请求成功且需要缓存，则缓存响应
    if (shouldCache && response.ok) {
        const cache = caches.default;
        const cacheKey = new Request(targetUrl.toString(), {
            method: 'GET',
            headers: headers
        });

        const cacheResponse = new Response(response.body, {
            status: response.status,
            statusText: response.statusText,
            headers: response.headers
        });

        // 设置缓存时间
        cacheResponse.headers.set('Cache-Control', `public, max-age=${CACHE_TTL}`);

        event.waitUntil(cache.put(cacheKey, cacheResponse.clone()));
    }

    return addCORSHeaders(response);
}

function addCORSHeaders(response) {
    const newResponse = new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: response.headers
    });

    // 添加 CORS 头
    newResponse.headers.set('Access-Control-Allow-Origin', '*');
    newResponse.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS');
    newResponse.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-API-Key');
    newResponse.headers.set('Access-Control-Max-Age', '86400');

    return newResponse;
}

function handleCORS() {
    return new Response(null, {
        status: 204,
        headers: {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
            'Access-Control-Max-Age': '86400'
        }
    });
}
