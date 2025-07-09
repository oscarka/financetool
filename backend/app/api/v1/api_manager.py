from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/api-manager", response_class=HTMLResponse)
async def api_manager_page(request: Request):
    """API管理页面"""
    
    # 直接返回HTML内容
    html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API管理控制台</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
            color: white;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-number {
            font-size: 2rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 5px;
        }

        .stat-label {
            color: #666;
            font-size: 0.9rem;
        }

        .categories {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
        }

        .category-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }

        .category-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }

        .category-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }

        .category-icon {
            font-size: 2rem;
            margin-right: 15px;
        }

        .category-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #333;
        }

        .category-description {
            color: #666;
            font-size: 0.9rem;
            margin-top: 5px;
        }

        .endpoints {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .endpoint-item {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            border-left: 4px solid #667eea;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .endpoint-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }

        .endpoint-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .endpoint-name {
            font-weight: 600;
            color: #333;
            flex: 1;
        }

        .method-badge {
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
        }

        .method-get { background: #d4edda; color: #155724; }
        .method-post { background: #d1ecf1; color: #0c5460; }
        .method-put { background: #fff3cd; color: #856404; }
        .method-delete { background: #f8d7da; color: #721c24; }

        .endpoint-path {
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.85rem;
            color: #666;
            background: #e9ecef;
            padding: 4px 8px;
            border-radius: 4px;
            margin-bottom: 8px;
        }

        .endpoint-description {
            color: #666;
            font-size: 0.9rem;
            line-height: 1.4;
        }

        .test-button {
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: background 0.3s ease;
            margin-top: 10px;
        }

        .test-button:hover {
            background: #5a6fd8;
        }

        .test-button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }

        .response-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
        }

        .modal-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 30px;
            border-radius: 12px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
        }

        .modal-title {
            font-size: 1.2rem;
            font-weight: 600;
        }

        .close-button {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #666;
        }

        .response-content {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9rem;
            white-space: pre-wrap;
            max-height: 400px;
            overflow-y: auto;
        }

        .loading {
            text-align: center;
            color: #666;
        }

        .success { color: #28a745; }
        .error { color: #dc3545; }
        .warning { color: #ffc107; }

        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .categories {
                grid-template-columns: 1fr;
            }
            
            .stat-card {
                padding: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 API管理控制台</h1>
            <p>管理您的 32 个API接口</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">32</div>
                <div class="stat-label">总接口数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">5</div>
                <div class="stat-label">功能模块</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">100%</div>
                <div class="stat-label">可用性</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">实时</div>
                <div class="stat-label">状态监控</div>
            </div>
        </div>

        <div class="categories">
            <div class="category-card">
                <div class="category-header">
                    <div class="category-icon">🔧</div>
                    <div>
                        <div class="category-title">系统接口</div>
                        <div class="category-description">系统基础功能</div>
                    </div>
                </div>
                
                <div class="endpoints">
                    <div class="endpoint-item" onclick="testEndpoint('GET', '/health', '健康检查')">
                        <div class="endpoint-header">
                            <div class="endpoint-name">健康检查</div>
                            <div class="method-badge method-get">GET</div>
                        </div>
                        <div class="endpoint-path">/health</div>
                        <div class="endpoint-description">检查系统健康状态</div>
                        <button class="test-button" onclick="event.stopPropagation(); testEndpoint('GET', '/health', '健康检查')">
                            测试接口
                        </button>
                    </div>
                    <div class="endpoint-item" onclick="testEndpoint('GET', '/', '根路径')">
                        <div class="endpoint-header">
                            <div class="endpoint-name">根路径</div>
                            <div class="method-badge method-get">GET</div>
                        </div>
                        <div class="endpoint-path">/</div>
                        <div class="endpoint-description">API根路径信息</div>
                        <button class="test-button" onclick="event.stopPropagation(); testEndpoint('GET', '/', '根路径')">
                            测试接口
                        </button>
                    </div>
                </div>
            </div>

            <div class="category-card">
                <div class="category-header">
                    <div class="category-icon">📈</div>
                    <div>
                        <div class="category-title">基金管理</div>
                        <div class="category-description">基金操作、持仓、净值管理</div>
                    </div>
                </div>
                
                <div class="endpoints">
                    <div class="endpoint-item" onclick="testEndpoint('GET', '/api/v1/funds/operations', '基金操作列表')">
                        <div class="endpoint-header">
                            <div class="endpoint-name">基金操作列表</div>
                            <div class="method-badge method-get">GET</div>
                        </div>
                        <div class="endpoint-path">/api/v1/funds/operations</div>
                        <div class="endpoint-description">获取所有基金操作记录</div>
                        <button class="test-button" onclick="event.stopPropagation(); testEndpoint('GET', '/api/v1/funds/operations', '基金操作列表')">
                            测试接口
                        </button>
                    </div>
                    <div class="endpoint-item" onclick="testEndpoint('GET', '/api/v1/funds/positions', '持仓信息')">
                        <div class="endpoint-header">
                            <div class="endpoint-name">持仓信息</div>
                            <div class="method-badge method-get">GET</div>
                        </div>
                        <div class="endpoint-path">/api/v1/funds/positions</div>
                        <div class="endpoint-description">获取当前持仓信息</div>
                        <button class="test-button" onclick="event.stopPropagation(); testEndpoint('GET', '/api/v1/funds/positions', '持仓信息')">
                            测试接口
                        </button>
                    </div>
                    <div class="endpoint-item" onclick="testEndpoint('GET', '/api/v1/funds/positions/summary', '持仓汇总')">
                        <div class="endpoint-header">
                            <div class="endpoint-name">持仓汇总</div>
                            <div class="method-badge method-get">GET</div>
                        </div>
                        <div class="endpoint-path">/api/v1/funds/positions/summary</div>
                        <div class="endpoint-description">获取持仓汇总统计</div>
                        <button class="test-button" onclick="event.stopPropagation(); testEndpoint('GET', '/api/v1/funds/positions/summary', '持仓汇总')">
                            测试接口
                        </button>
                    </div>
                    <div class="endpoint-item" onclick="testEndpoint('GET', '/api/v1/funds/info', '基金信息')">
                        <div class="endpoint-header">
                            <div class="endpoint-name">基金信息</div>
                            <div class="method-badge method-get">GET</div>
                        </div>
                        <div class="endpoint-path">/api/v1/funds/info</div>
                        <div class="endpoint-description">获取基金基本信息</div>
                        <button class="test-button" onclick="event.stopPropagation(); testEndpoint('GET', '/api/v1/funds/info', '基金信息')">
                            测试接口
                        </button>
                    </div>
                </div>
            </div>

            <div class="category-card">
                <div class="category-header">
                    <div class="category-icon">💱</div>
                    <div>
                        <div class="category-title">汇率管理</div>
                        <div class="category-description">汇率查询和转换</div>
                    </div>
                </div>
                
                <div class="endpoints">
                    <div class="endpoint-item" onclick="testEndpoint('GET', '/api/v1/exchange-rates/currencies', '支持货币')">
                        <div class="endpoint-header">
                            <div class="endpoint-name">支持货币</div>
                            <div class="method-badge method-get">GET</div>
                        </div>
                        <div class="endpoint-path">/api/v1/exchange-rates/currencies</div>
                        <div class="endpoint-description">获取支持的货币列表</div>
                        <button class="test-button" onclick="event.stopPropagation(); testEndpoint('GET', '/api/v1/exchange-rates/currencies', '支持货币')">
                            测试接口
                        </button>
                    </div>
                    <div class="endpoint-item" onclick="testEndpoint('GET', '/api/v1/exchange-rates/rates', '汇率查询')">
                        <div class="endpoint-header">
                            <div class="endpoint-name">汇率查询</div>
                            <div class="method-badge method-get">GET</div>
                        </div>
                        <div class="endpoint-path">/api/v1/exchange-rates/rates</div>
                        <div class="endpoint-description">获取当前汇率信息</div>
                        <button class="test-button" onclick="event.stopPropagation(); testEndpoint('GET', '/api/v1/exchange-rates/rates', '汇率查询')">
                            测试接口
                        </button>
                    </div>
                    <div class="endpoint-item" onclick="testEndpoint('GET', '/api/v1/exchange-rates/rates/USD', 'USD汇率')">
                        <div class="endpoint-header">
                            <div class="endpoint-name">USD汇率</div>
                            <div class="method-badge method-get">GET</div>
                        </div>
                        <div class="endpoint-path">/api/v1/exchange-rates/rates/USD</div>
                        <div class="endpoint-description">获取美元汇率</div>
                        <button class="test-button" onclick="event.stopPropagation(); testEndpoint('GET', '/api/v1/exchange-rates/rates/USD', 'USD汇率')">
                            测试接口
                        </button>
                    </div>
                </div>
            </div>

            <div class="category-card">
                <div class="category-header">
                    <div class="category-icon">💳</div>
                    <div>
                        <div class="category-title">PayPal管理</div>
                        <div class="category-description">PayPal账户和交易管理</div>
                    </div>
                </div>
                
                <div class="endpoints">
                    <div class="endpoint-item" onclick="testEndpoint('GET', '/api/v1/paypal/config', '配置信息')">
                        <div class="endpoint-header">
                            <div class="endpoint-name">配置信息</div>
                            <div class="method-badge method-get">GET</div>
                        </div>
                        <div class="endpoint-path">/api/v1/paypal/config</div>
                        <div class="endpoint-description">获取PayPal配置信息</div>
                        <button class="test-button" onclick="event.stopPropagation(); testEndpoint('GET', '/api/v1/paypal/config', '配置信息')">
                            测试接口
                        </button>
                    </div>
                    <div class="endpoint-item" onclick="testEndpoint('GET', '/api/v1/paypal/test', '连接测试')">
                        <div class="endpoint-header">
                            <div class="endpoint-name">连接测试</div>
                            <div class="method-badge method-get">GET</div>
                        </div>
                        <div class="endpoint-path">/api/v1/paypal/test</div>
                        <div class="endpoint-description">测试PayPal连接</div>
                        <button class="test-button" onclick="event.stopPropagation(); testEndpoint('GET', '/api/v1/paypal/test', '连接测试')">
                            测试接口
                        </button>
                    </div>
                    <div class="endpoint-item" onclick="testEndpoint('GET', '/api/v1/paypal/summary', '账户汇总')">
                        <div class="endpoint-header">
                            <div class="endpoint-name">账户汇总</div>
                            <div class="method-badge method-get">GET</div>
                        </div>
                        <div class="endpoint-path">/api/v1/paypal/summary</div>
                        <div class="endpoint-description">获取账户汇总信息</div>
                        <button class="test-button" onclick="event.stopPropagation(); testEndpoint('GET', '/api/v1/paypal/summary', '账户汇总')">
                            测试接口
                        </button>
                    </div>
                </div>
            </div>

            <div class="category-card">
                <div class="category-header">
                    <div class="category-icon">🏦</div>
                    <div>
                        <div class="category-title">Wise管理</div>
                        <div class="category-description">Wise账户和转账管理</div>
                    </div>
                </div>
                
                <div class="endpoints">
                    <div class="endpoint-item" onclick="testEndpoint('GET', '/api/v1/wise/config', '配置信息')">
                        <div class="endpoint-header">
                            <div class="endpoint-name">配置信息</div>
                            <div class="method-badge method-get">GET</div>
                        </div>
                        <div class="endpoint-path">/api/v1/wise/config</div>
                        <div class="endpoint-description">获取Wise配置信息</div>
                        <button class="test-button" onclick="event.stopPropagation(); testEndpoint('GET', '/api/v1/wise/config', '配置信息')">
                            测试接口
                        </button>
                    </div>
                    <div class="endpoint-item" onclick="testEndpoint('GET', '/api/v1/wise/test', '连接测试')">
                        <div class="endpoint-header">
                            <div class="endpoint-name">连接测试</div>
                            <div class="method-badge method-get">GET</div>
                        </div>
                        <div class="endpoint-path">/api/v1/wise/test</div>
                        <div class="endpoint-description">测试Wise连接</div>
                        <button class="test-button" onclick="event.stopPropagation(); testEndpoint('GET', '/api/v1/wise/test', '连接测试')">
                            测试接口
                        </button>
                    </div>
                    <div class="endpoint-item" onclick="testEndpoint('GET', '/api/v1/wise/summary', '账户汇总')">
                        <div class="endpoint-header">
                            <div class="endpoint-name">账户汇总</div>
                            <div class="method-badge method-get">GET</div>
                        </div>
                        <div class="endpoint-path">/api/v1/wise/summary</div>
                        <div class="endpoint-description">获取账户汇总</div>
                        <button class="test-button" onclick="event.stopPropagation(); testEndpoint('GET', '/api/v1/wise/summary', '账户汇总')">
                            测试接口
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 响应模态框 -->
    <div id="responseModal" class="response-modal">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title" id="modalTitle">接口测试结果</div>
                <button class="close-button" onclick="closeModal()">&times;</button>
            </div>
            <div id="responseContent" class="response-content">
                <div class="loading">正在测试接口...</div>
            </div>
        </div>
    </div>

    <script>
        function testEndpoint(method, path, name) {
            const modal = document.getElementById('responseModal');
            const modalTitle = document.getElementById('modalTitle');
            const responseContent = document.getElementById('responseContent');
            
            modalTitle.textContent = `测试: ${name}`;
            responseContent.innerHTML = '<div class="loading">正在测试接口...</div>';
            modal.style.display = 'block';
            
            // 构建完整URL
            const baseUrl = window.location.origin;
            const url = baseUrl + path;
            
            // 发送请求
            fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            })
            .then(response => {
                const status = response.status;
                const statusText = response.statusText;
                
                return response.text().then(text => {
                    let jsonData;
                    try {
                        jsonData = JSON.parse(text);
                    } catch (e) {
                        jsonData = null;
                    }
                    
                    return {
                        status,
                        statusText,
                        text,
                        jsonData,
                        ok: response.ok
                    };
                });
            })
            .then(data => {
                let content = '';
                
                // 状态信息
                const statusClass = data.ok ? 'success' : 'error';
                content += `<div class="${statusClass}">`;
                content += `<strong>状态码:</strong> ${data.status} ${data.statusText}\\n`;
                content += `<strong>URL:</strong> ${url}\\n`;
                content += `<strong>方法:</strong> ${method}\\n`;
                content += `<strong>时间:</strong> ${new Date().toLocaleString()}\\n\\n`;
                content += '</div>';
                
                // 响应内容
                content += '<strong>响应内容:</strong>\\n';
                if (data.jsonData) {
                    content += JSON.stringify(data.jsonData, null, 2);
                } else {
                    content += data.text;
                }
                
                responseContent.innerHTML = content;
            })
            .catch(error => {
                responseContent.innerHTML = `<div class="error">请求失败: ${error.message}</div>`;
            });
        }
        
        function closeModal() {
            document.getElementById('responseModal').style.display = 'none';
        }
        
        // 点击模态框外部关闭
        document.getElementById('responseModal').addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });
        
        // ESC键关闭模态框
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeModal();
            }
        });
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html_content)