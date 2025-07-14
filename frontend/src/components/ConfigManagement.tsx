import React, { useState, useEffect } from 'react';
import {
    Card,
    Button,
    
    Tabs,
    
    Alert,
    Row,
    Col,
    Statistic,
    Tag,
    
    message,
    Modal,
    Form,
    Input,
    Switch,
    InputNumber,
    
    Space,
    
    Typography,
    Descriptions,
    
    
    Drawer,
    Timeline,
    Popconfirm
} from 'antd';
import {
    SettingOutlined,
    ReloadOutlined,
    CheckCircleOutlined,
    HistoryOutlined,
    EnvironmentOutlined,
    // PerformanceOutlined, // 修正：该图标未被实际使用，且 antd 没有此导出
    ApiOutlined,
    ClockCircleOutlined,
    UndoOutlined,
    ExportOutlined,
    ImportOutlined,
} from '@ant-design/icons';
import { configAPI } from '../services/configAPI';
import type { ConfigInfo, ConfigValidationResult, EnvironmentInfo } from '../services/configAPI';

const { TabPane } = Tabs;
const { Text, Title } = Typography;
const { TextArea } = Input;

const ConfigManagement: React.FC = () => {
    // 状态管理
    const [loading, setLoading] = useState(false);
    const [config, setConfig] = useState<ConfigInfo | null>(null);
    const [validationResult, setValidationResult] = useState<ConfigValidationResult | null>(null);
    const [environmentInfo, setEnvironmentInfo] = useState<EnvironmentInfo | null>(null);
    const [configHistory, setConfigHistory] = useState<any[]>([]);
    
    // 模态框状态
    const [editModalVisible, setEditModalVisible] = useState(false);
    const [importModalVisible, setImportModalVisible] = useState(false);
    const [historyDrawerVisible, setHistoryDrawerVisible] = useState(false);
    const [environmentDrawerVisible, setEnvironmentDrawerVisible] = useState(false);
    
    // 表单状态
    const [editForm] = Form.useForm();
    const [importForm] = Form.useForm();
    
    // 加载状态
    const [configLoading, setConfigLoading] = useState(true);
    const [validationLoading, setValidationLoading] = useState(false);

    // 组件全量日志
    console.log('[ConfigManagement] 组件渲染，props: 无props, state config:', config, 'validationResult:', validationResult, 'environmentInfo:', environmentInfo, 'configHistory:', configHistory);
    console.log('[ConfigManagement] 当前 config state:', config);
    // 初始化加载
    useEffect(() => {
        console.log('[ConfigManagement] useEffect: 组件挂载，开始请求配置和环境信息', Date.now());
        loadConfig();
        loadEnvironmentInfo();
        return () => {
            console.log('[ConfigManagement] useEffect: 组件卸载', Date.now());
        };
    }, []);
    // config 状态变化日志
    useEffect(() => {
        console.log('[ConfigManagement] useEffect: config 状态变化:', config, '类型:', typeof config, 'keys:', config && Object.keys(config));
    }, [config]);

    // 加载配置信息
    const loadConfig = async () => {
        setConfigLoading(true);
        try {
            console.log('[ConfigManagement] loadConfig: 调用 configAPI.getConfig');
            const response = await configAPI.getConfig();
            console.log('[ConfigManagement] loadConfig: configAPI.getConfig 返回:', response, '类型:', typeof response, 'keys:', response && Object.keys(response));
            setConfig(response); // 直接赋值
            console.log('[ConfigManagement] loadConfig: setConfig 赋值:', response, '类型:', typeof response, 'keys:', response && Object.keys(response));
        } catch (error) {
            message.error('获取配置失败');
            console.error('[ConfigManagement] loadConfig: getConfig 报错:', error);
        } finally {
            setConfigLoading(false);
        }
    };

    // 加载环境信息
    const loadEnvironmentInfo = async () => {
        setEnvironmentInfo(null);
        try {
            const response = await configAPI.getEnvironmentInfo();
            if (response.success) {
                setEnvironmentInfo(response.data);
            }
        } catch (error) {
            console.error('获取环境信息失败:', error);
        } finally {
            setEnvironmentInfo(null);
        }
    };

    // 验证配置
    const validateConfig = async () => {
        setValidationLoading(true);
        try {
            const response = await configAPI.validateConfig();
            if (response.success) {
                setValidationResult(response.data);
                if (response.data.valid) {
                    message.success('配置验证通过');
                } else {
                    message.warning('配置验证发现问题');
                }
            } else {
                message.error(`配置验证失败: ${response.error}`);
            }
        } catch (error) {
            message.error('配置验证失败');
        } finally {
            setValidationLoading(false);
        }
    };

    // 重新加载配置
    const reloadConfig = async () => {
        setLoading(true);
        try {
            const response = await configAPI.reloadConfig();
            if (response.success) {
                message.success('配置重新加载成功');
                await loadConfig();
            } else {
                message.error(`重新加载失败: ${response.error}`);
            }
        } catch (error) {
            message.error('重新加载配置失败');
        } finally {
            setLoading(false);
        }
    };

    // 更新配置
    const updateConfig = async (values: any) => {
        setLoading(true);
        try {
            const response = await configAPI.updateConfig(values);
            if (response.success) {
                message.success('配置更新成功');
                setConfig(response.data);
                setEditModalVisible(false);
                editForm.resetFields();
            } else {
                message.error(`更新失败: ${response.error}`);
            }
        } catch (error) {
            message.error('更新配置失败');
        } finally {
            setLoading(false);
        }
    };

    // 导出配置
    const exportConfig = async () => {
        try {
            const response = await configAPI.exportConfig();
            if (response.success) {
                // 创建下载链接
                const blob = new Blob([response.data], { type: 'application/json' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `config_${new Date().toISOString().split('T')[0]}.json`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                message.success('配置导出成功');
            } else {
                message.error(`导出失败: ${response.error}`);
            }
        } catch (error) {
            message.error('导出配置失败');
        }
    };

    // 导入配置
    const importConfig = async (values: any) => {
        setLoading(true);
        try {
            const response = await configAPI.importConfig(values.config_data);
            if (response.success) {
                message.success('配置导入成功');
                setConfig(response.data);
                setImportModalVisible(false);
                importForm.resetFields();
            } else {
                message.error(`导入失败: ${response.error}`);
            }
        } catch (error) {
            message.error('导入配置失败');
        } finally {
            setLoading(false);
        }
    };

    // 重置配置
    const resetConfig = async () => {
        Modal.confirm({
            title: '确认重置配置',
            content: '这将重置所有配置到默认值，确定要继续吗？',
            onOk: async () => {
                setLoading(true);
                try {
                    const response = await configAPI.resetConfig();
                    if (response.success) {
                        message.success('配置重置成功');
                        setConfig(response.data);
                    } else {
                        message.error(`重置失败: ${response.error}`);
                    }
                } catch (error) {
                    message.error('重置配置失败');
                } finally {
                    setLoading(false);
                }
            }
        });
    };

    // 查看配置历史
    const viewConfigHistory = async () => {
        try {
            const response = await configAPI.getConfigHistory();
            if (response.success) {
                setConfigHistory(response.data);
                setHistoryDrawerVisible(true);
            } else {
                message.error(`获取历史失败: ${response.error}`);
            }
        } catch (error) {
            message.error('获取配置历史失败');
        }
    };

    // 渲染统计卡片
    const renderStatistics = () => {
        console.log('[调试] renderStatistics 渲染时 config：', config);
        return (
            <Row gutter={16} style={{ marginBottom: 24 }}>
                <Col span={6}>
                    <Card>
                        <Statistic
                            title="当前环境"
                            value={config?.app_env || 'unknown'}
                            prefix={<EnvironmentOutlined />}
                            valueStyle={{ color: config?.app_env === 'prod' ? '#cf1322' : '#3f8600' }}
                        />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic
                            title="API配置状态"
                            value={[
                                config?.okx_api_configured,
                                config?.wise_api_configured,
                                config?.paypal_api_configured,
                                config?.ibkr_api_configured
                            ].filter(Boolean).length}
                            suffix={`/ 4`}
                            prefix={<ApiOutlined />}
                        />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic
                            title="调度器状态"
                            value={config?.enable_scheduler ? '启用' : '禁用'}
                            prefix={<ClockCircleOutlined />}
                            valueStyle={{ color: config?.enable_scheduler ? '#3f8600' : '#cf1322' }}
                        />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic
                            title="配置验证"
                            value={validationResult?.valid ? '通过' : '未验证'}
                            prefix={<CheckCircleOutlined />}
                            valueStyle={{ color: validationResult?.valid ? '#3f8600' : '#faad14' }}
                        />
                    </Card>
                </Col>
            </Row>
        );
    };

    // 渲染前日志
    console.log('[ConfigManagement] 渲染前 config:', config);
    if (!config) {
        console.warn('[ConfigManagement] config 为空，渲染 loading/空白');
        return <div>加载中...</div>;
    }
    if (typeof config !== 'object') {
        console.error('[ConfigManagement] config 不是对象:', config);
    }

    // 渲染基础配置
    const renderBasicConfig = () => {
        console.log('[ConfigManagement] renderBasicConfig 渲染，config:', config);
        return (
            <Card title="基础配置" extra={
                <Button type="primary" icon={<SettingOutlined />} onClick={() => {
                    editForm.setFieldsValue(config);
                    setEditModalVisible(true);
                }}>
                    编辑配置
                </Button>
            }>
                <Descriptions bordered column={2}>
                    <Descriptions.Item label="应用名称">{config?.app_name}</Descriptions.Item>
                    <Descriptions.Item label="应用版本">{config?.app_version}</Descriptions.Item>
                    <Descriptions.Item label="调试模式">
                        <Tag color={config?.debug ? 'green' : 'red'}>
                            {config?.debug ? '启用' : '禁用'}
                        </Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="日志级别">
                        <Tag color={config?.log_level === 'DEBUG' ? 'blue' : 'green'}>
                            {config?.log_level}
                        </Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="数据库URL" span={2}>
                        <Text code>{config?.database_url}</Text>
                    </Descriptions.Item>
                    <Descriptions.Item label="CORS Origins" span={2}>
                        {config?.cors_origins?.map((origin, index) => (
                            <Tag key={index} color="blue">{origin}</Tag>
                        ))}
                    </Descriptions.Item>
                </Descriptions>
            </Card>
        );
    };

    // 渲染API配置
    const renderAPIConfig = () => (
        <Card title="API配置">
            <Row gutter={16}>
                <Col span={12}>
                    <Card size="small" title="基金API">
                        <Descriptions column={1}>
                            <Descriptions.Item label="超时时间">{config?.fund_api_timeout}秒</Descriptions.Item>
                            <Descriptions.Item label="重试次数">{config?.fund_api_retry_times}次</Descriptions.Item>
                        </Descriptions>
                    </Card>
                </Col>
                <Col span={12}>
                    <Card size="small" title="第三方API状态">
                        <Space direction="vertical" style={{ width: '100%' }}>
                            <div>
                                <Text>OKX API: </Text>
                                <Tag color={config?.okx_api_configured ? 'green' : 'red'}>
                                    {config?.okx_api_configured ? '已配置' : '未配置'}
                                </Tag>
                            </div>
                            <div>
                                <Text>Wise API: </Text>
                                <Tag color={config?.wise_api_configured ? 'green' : 'red'}>
                                    {config?.wise_api_configured ? '已配置' : '未配置'}
                                </Tag>
                            </div>
                            <div>
                                <Text>PayPal API: </Text>
                                <Tag color={config?.paypal_api_configured ? 'green' : 'red'}>
                                    {config?.paypal_api_configured ? '已配置' : '未配置'}
                                </Tag>
                            </div>
                            <div>
                                <Text>IBKR API: </Text>
                                <Tag color={config?.ibkr_api_configured ? 'green' : 'red'}>
                                    {config?.ibkr_api_configured ? '已配置' : '未配置'}
                                </Tag>
                            </div>
                        </Space>
                    </Card>
                </Col>
            </Row>
        </Card>
    );

    // 渲染系统配置
    const renderSystemConfig = () => (
        <Card title="系统配置">
            <Row gutter={16}>
                <Col span={8}>
                    <Card size="small" title="调度器">
                        <Descriptions column={1}>
                            <Descriptions.Item label="状态">
                                <Tag color={config?.enable_scheduler ? 'green' : 'red'}>
                                    {config?.enable_scheduler ? '启用' : '禁用'}
                                </Tag>
                            </Descriptions.Item>
                            <Descriptions.Item label="时区">{config?.scheduler_timezone}</Descriptions.Item>
                        </Descriptions>
                    </Card>
                </Col>
                <Col span={8}>
                    <Card size="small" title="安全">
                        <Descriptions column={1}>
                            <Descriptions.Item label="速率限制">
                                <Tag color={config?.security_enable_rate_limiting ? 'green' : 'red'}>
                                    {config?.security_enable_rate_limiting ? '启用' : '禁用'}
                                </Tag>
                            </Descriptions.Item>
                            <Descriptions.Item label="限制值">{config?.security_rate_limit_per_minute}/分钟</Descriptions.Item>
                        </Descriptions>
                    </Card>
                </Col>
                <Col span={8}>
                    <Card size="small" title="性能">
                        <Descriptions column={1}>
                            <Descriptions.Item label="监控">
                                <Tag color={config?.performance_monitoring_enabled ? 'green' : 'red'}>
                                    {config?.performance_monitoring_enabled ? '启用' : '禁用'}
                                </Tag>
                            </Descriptions.Item>
                            <Descriptions.Item label="缓存">
                                <Tag color={config?.cache_enabled ? 'green' : 'red'}>
                                    {config?.cache_enabled ? '启用' : '禁用'}
                                </Tag>
                            </Descriptions.Item>
                        </Descriptions>
                    </Card>
                </Col>
            </Row>
        </Card>
    );

    // 渲染验证结果
    const renderValidationResult = () => {
        if (!validationResult) return null;

        return (
            <Card title="配置验证结果">
                <Alert
                    message={validationResult.valid ? '配置验证通过' : '配置验证发现问题'}
                    type={validationResult.valid ? 'success' : 'warning'}
                    showIcon
                    style={{ marginBottom: 16 }}
                />
                
                {validationResult.errors.length > 0 && (
                    <div style={{ marginBottom: 16 }}>
                        <Title level={5}>错误:</Title>
                        <ul>
                            {validationResult.errors.map((error, index) => (
                                <li key={index} style={{ color: '#cf1322' }}>{error}</li>
                            ))}
                        </ul>
                    </div>
                )}
                
                {validationResult.warnings.length > 0 && (
                    <div>
                        <Title level={5}>警告:</Title>
                        <ul>
                            {validationResult.warnings.map((warning, index) => (
                                <li key={index} style={{ color: '#faad14' }}>{warning}</li>
                            ))}
                        </ul>
                    </div>
                )}
            </Card>
        );
    };

    return (
        <div>
            <div style={{ marginBottom: 16 }}>
                <Space>
                    <Button 
                        type="primary" 
                        icon={<ReloadOutlined />} 
                        onClick={loadConfig}
                        loading={configLoading}
                    >
                        刷新配置
                    </Button>
                    <Button 
                        icon={<CheckCircleOutlined />} 
                        onClick={validateConfig}
                        loading={validationLoading}
                    >
                        验证配置
                    </Button>
                    <Button 
                        icon={<ReloadOutlined />} 
                        onClick={reloadConfig}
                        loading={loading}
                    >
                        重新加载
                    </Button>
                    <Button 
                        icon={<ExportOutlined />} 
                        onClick={exportConfig}
                    >
                        导出配置
                    </Button>
                    <Button 
                        icon={<ImportOutlined />} 
                        onClick={() => setImportModalVisible(true)}
                    >
                        导入配置
                    </Button>
                    <Button 
                        icon={<HistoryOutlined />} 
                        onClick={viewConfigHistory}
                    >
                        配置历史
                    </Button>
                    <Button 
                        icon={<EnvironmentOutlined />} 
                        onClick={() => setEnvironmentDrawerVisible(true)}
                    >
                        环境信息
                    </Button>
                    <Popconfirm
                        title="确定要重置配置吗？"
                        onConfirm={resetConfig}
                        okText="确定"
                        cancelText="取消"
                    >
                        <Button 
                            danger 
                            icon={<UndoOutlined />}
                        >
                            重置配置
                        </Button>
                    </Popconfirm>
                </Space>
            </div>

            {renderStatistics()}

            <Tabs defaultActiveKey="basic">
                <TabPane tab="基础配置" key="basic">
                    {renderBasicConfig()}
                </TabPane>
                <TabPane tab="API配置" key="api">
                    {renderAPIConfig()}
                </TabPane>
                <TabPane tab="系统配置" key="system">
                    {renderSystemConfig()}
                </TabPane>
                <TabPane tab="验证结果" key="validation">
                    {renderValidationResult()}
                </TabPane>
            </Tabs>

            {/* 编辑配置模态框 */}
            <Modal
                title="编辑配置"
                open={editModalVisible}
                onCancel={() => setEditModalVisible(false)}
                footer={null}
                width={800}
            >
                <Form
                    form={editForm}
                    layout="vertical"
                    onFinish={updateConfig}
                >
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item label="应用名称" name="app_name">
                                <Input />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item label="调试模式" name="debug" valuePropName="checked">
                                <Switch />
                            </Form.Item>
                        </Col>
                    </Row>
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item label="基金API超时时间" name="fund_api_timeout">
                                <InputNumber min={1} max={60} />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item label="基金API重试次数" name="fund_api_retry_times">
                                <InputNumber min={1} max={10} />
                            </Form.Item>
                        </Col>
                    </Row>
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item label="启用调度器" name="enable_scheduler" valuePropName="checked">
                                <Switch />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item label="启用速率限制" name="security_enable_rate_limiting" valuePropName="checked">
                                <Switch />
                            </Form.Item>
                        </Col>
                    </Row>
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item label="启用性能监控" name="performance_monitoring_enabled" valuePropName="checked">
                                <Switch />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item label="启用缓存" name="cache_enabled" valuePropName="checked">
                                <Switch />
                            </Form.Item>
                        </Col>
                    </Row>
                    <Form.Item>
                        <Space>
                            <Button type="primary" htmlType="submit" loading={loading}>
                                保存配置
                            </Button>
                            <Button onClick={() => setEditModalVisible(false)}>
                                取消
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Modal>

            {/* 导入配置模态框 */}
            <Modal
                title="导入配置"
                open={importModalVisible}
                onCancel={() => setImportModalVisible(false)}
                footer={null}
                width={600}
            >
                <Form
                    form={importForm}
                    layout="vertical"
                    onFinish={importConfig}
                >
                    <Form.Item
                        label="配置数据 (JSON格式)"
                        name="config_data"
                        rules={[{ required: true, message: '请输入配置数据' }]}
                    >
                        <TextArea rows={10} placeholder="请输入JSON格式的配置数据..." />
                    </Form.Item>
                    <Form.Item>
                        <Space>
                            <Button type="primary" htmlType="submit" loading={loading}>
                                导入配置
                            </Button>
                            <Button onClick={() => setImportModalVisible(false)}>
                                取消
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Modal>

            {/* 配置历史抽屉 */}
            <Drawer
                title="配置历史"
                placement="right"
                width={600}
                open={historyDrawerVisible}
                onClose={() => setHistoryDrawerVisible(false)}
            >
                <Timeline>
                    {configHistory.map((item, index) => (
                        <Timeline.Item key={index}>
                            <p><strong>{item.timestamp}</strong></p>
                            <p>{item.action}</p>
                            <p>{item.description}</p>
                        </Timeline.Item>
                    ))}
                </Timeline>
            </Drawer>

            {/* 环境信息抽屉 */}
            <Drawer
                title="环境信息"
                placement="right"
                width={600}
                open={environmentDrawerVisible}
                onClose={() => setEnvironmentDrawerVisible(false)}
            >
                {environmentInfo && (
                    <div>
                        <Card title="系统信息" style={{ marginBottom: 16 }}>
                            <Descriptions column={1}>
                                <Descriptions.Item label="当前环境">{environmentInfo.current_env}</Descriptions.Item>
                                <Descriptions.Item label="Python版本">{environmentInfo.system_info.python_version}</Descriptions.Item>
                                <Descriptions.Item label="平台">{environmentInfo.system_info.platform}</Descriptions.Item>
                                <Descriptions.Item label="内存使用">{environmentInfo.system_info.memory_usage}</Descriptions.Item>
                                <Descriptions.Item label="磁盘使用">{environmentInfo.system_info.disk_usage}</Descriptions.Item>
                            </Descriptions>
                        </Card>
                        
                        <Card title="环境变量">
                            {Object.entries(environmentInfo.env_variables).map(([key, value]) => (
                                <div key={key} style={{ marginBottom: 8 }}>
                                    <Text strong>{key}:</Text> <Text code>{value}</Text>
                                </div>
                            ))}
                        </Card>
                    </div>
                )}
            </Drawer>
        </div>
    );
};

export default ConfigManagement; 