// 配置文件，用于不同环境的API端点设置
window.config = {
  // 生产环境：使用nginx代理到后端
  production: {
    apiBaseUrl: '/api/v1'
  },
  // 开发环境：直接连接到本地后端
  development: {
    apiBaseUrl: 'http://localhost:8000/api/v1'
  }
};

// 自动检测环境
window.getApiBaseUrl = function() {
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return window.config.development.apiBaseUrl;
  } else {
    return window.config.production.apiBaseUrl;
  }
};
