const CACHE_NAME = 'investment-app-v2.2-optimized'
const urlsToCache = [
  '/',
  '/manifest.json'
]

// 安装Service Worker
self.addEventListener('install', (event) => {
  console.log('SW安装中, 版本:', CACHE_NAME)
  // 强制跳过等待，立即激活新版本
  self.skipWaiting()
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('✅ SW缓存已创建:', CACHE_NAME)
        return cache.addAll(urlsToCache)
      })
      .catch((error) => {
        console.log('❌ Cache addAll failed:', error)
      })
  )
})

// 拦截请求 - 缓存优先策略
self.addEventListener('fetch', (event) => {
  // 对于API请求，使用网络优先策略
  const isAPIRequest = event.request.url.includes('/api/')
  
  if (isAPIRequest) {
    // API请求使用网络优先，但增加缓存时间
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // 检查响应是否有效
          if (!response || response.status !== 200) {
            return response
          }
          
          // 克隆响应用于缓存
          const responseToCache = response.clone()
          
          caches.open(CACHE_NAME)
            .then((cache) => {
              cache.put(event.request, responseToCache)
            })
          
          return response
        })
        .catch(() => {
          // 网络失败时，尝试返回缓存的内容
          return caches.match(event.request)
        })
    )
  } else {
    // 静态资源使用缓存优先策略
    event.respondWith(
      caches.match(event.request)
        .then((response) => {
          if (response) {
            return response
          }
          
          return fetch(event.request)
            .then((response) => {
              if (!response || response.status !== 200) {
                return response
              }
              
              const responseToCache = response.clone()
              
              caches.open(CACHE_NAME)
                .then((cache) => {
                  cache.put(event.request, responseToCache)
                })
              
              return response
            })
        })
    )
  }
})

// 清理旧缓存
self.addEventListener('activate', (event) => {
  console.log('🚀 SW激活中, 版本:', CACHE_NAME)
  // 立即控制所有客户端
  event.waitUntil(
    Promise.all([
      // 清理旧缓存
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME) {
              console.log('🗑️ 删除旧缓存:', cacheName)
              return caches.delete(cacheName)
            }
          })
        )
      }),
      // 立即控制所有页面
      self.clients.claim()
    ]).then(() => {
      console.log('✅ SW已激活并控制所有页面, 版本:', CACHE_NAME)
    })
  )
})