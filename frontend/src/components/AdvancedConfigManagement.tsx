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
    Popconfirm,
    Select,
    ColorPicker,
    Upload,
    Divider,
    List,
    Badge,
    Tooltip,
    Progress
} from 'antd';
import {
    SettingOutlined,
    ReloadOutlined,
    CheckCircleOutlined,
    HistoryOutlined,
    EnvironmentOutlined,
    ApiOutlined,
    ClockCircleOutlined,
    UndoOutlined,
    ExportOutlined,
    ImportOutlined,
    SaveOutlined,
    EyeOutlined,
    LockOutlined,
    UnlockOutlined,
    DatabaseOutlined,
    SecurityScanOutlined,
    PerformanceOutlined,
    NotificationOutlined,
    BackupOutlined,
    CleanOutlined,
    UploadOutlined,
    DownloadOutlined,
    SyncOutlined,
    MonitorOutlined
} from '@ant-design/icons';
import { configAPI } from '../services/configAPI';
import type { ConfigInfo, ConfigValidationResult, EnvironmentInfo } from '../services/configAPI';

const { TabPane } = Tabs;
const { Text, Title } = Typography;
const { TextArea } = Input;
const { Option } = Select;

interface AdvancedConfig extends ConfigInfo {
    // 高级配置选项
    theme: {
        primaryColor: string;
        layout: 'side' | 'top' | 'mix';
        compact: boolean;
        darkMode: boolean;
    };
    features: {
        enableNotifications: boolean;
        enableAnalytics: boolean;
        enableBackup: boolean;
        enableAutoSync: boolean;
        enableMultiLanguage: boolean;
    };
    security: {
        enableTwoFactor: boolean;
        sessionTimeout: number;
        maxLoginAttempts: number;
        passwordPolicy: {
            minLength: number;
            requireUppercase: boolean;
            requireLowercase: boolean;
            requireNumbers: boolean;
            requireSpecialChars: boolean;
        };
    };
    performance: {
        enableCaching: boolean;
        cacheSize: number;
        enableCompression: boolean;
        enableGzip: boolean;
        maxConcurrentRequests: number;
    };
}

const AdvancedConfigManagement: React.FC = () => {
    const [loading, setLoading] = useState(false);
    const [config, setConfig] = useState<AdvancedConfig | null>(null);
    const [validationResult, setValidationResult] = useState<ConfigValidationResult | null>(null);
    const [environmentInfo, setEnvironmentInfo] = useState<EnvironmentInfo | null>(null);
    const [configHistory, setConfigHistory] = useState<any[]>([]);
    
    // 模态框状态
    const [editModalVisible, setEditModalVisible] = useState(false);
    const [importModalVisible, setImportModalVisible] = useState(false);
    const [historyDrawerVisible, setHistoryDrawerVisible] = useState(false);
    const [environmentDrawerVisible, setEnvironmentDrawerVisible] = useState(false);
    const [backupModalVisible, setBackupModalVisible] = useState(false);
    const [securityModalVisible, setSecurityModalVisible] = useState(false);
    
    // 表单状态
    const [editForm] = Form.useForm();
    const [importForm] = Form.useForm();
    const [backupForm] = Form.useForm();
    const [securityForm] = Form.useForm();

    useEffect(() => {
        loadConfig();
        loadEnvironmentInfo();
    }, []);

    const loadConfig = async () => {
        setLoading(true);
        try {
            const response = await configAPI.getConfig();
            // 扩展配置对象
            const advancedConfig: AdvancedConfig = {
                ...response,
                theme: {
                    primaryColor: '#1890ff',
                    layout: 'side',
                    compact: false,
                    darkMode: false
                },
                features: {
                    enableNotifications: true,
                    enableAnalytics: false,
                    enableBackup: true,
                    enableAutoSync: true,
                    enableMultiLanguage: false
                },
                security: {
                    enableTwoFactor: false,
                    sessionTimeout: 30,
                    maxLoginAttempts: 5,
                    passwordPolicy: {
                        minLength: 8,
                        requireUppercase: true,
                        requireLowercase: true,
                        requireNumbers: true,
                        requireSpecialChars: false
                    }
                },
                performance: {
                    enableCaching: true,
                    cacheSize: 100,
                    enableCompression: true,
                    enableGzip: true,
                    maxConcurrentRequests: 10
                }
            };
            setConfig(advancedConfig);
        } catch (error) {
            message.error('获取配置失败');
        } finally {
            setLoading(false);
        }
    };

    const loadEnvironmentInfo = async () => {
        try {
            const response = await configAPI.getEnvironmentInfo();
            if (response.success) {
                setEnvironmentInfo(response.data);
            }
        } catch (error) {
            console.error('获取环境信息失败:', error);
        }
    };

    const validateConfig = async () => {
        setLoading(true);
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
            setLoading(false);
        }
    };

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

    const exportConfig = async () => {
        try {
            const response = await configAPI.exportConfig();
            if (response.success) {
                const blob = new Blob([response.data], { type: 'application/json' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `advanced_config_${new Date().toISOString().split('T')[0]}.json`;
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

    const importConfig = async (values: any) => {
        try {
            const response = await configAPI.importConfig(values.configData);
            if (response.success) {
                message.success('配置导入成功');
                setConfig(response.data);
                setImportModalVisible(false);
                importForm.resetFields();
                await loadConfig();
            } else {
                message.error(`导入失败: ${response.error}`);
            }
        } catch (error) {
            message.error('导入配置失败');
        }
    };

    const resetConfig = async () => {
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
        }
    };

    const renderBasicConfig = () => (
        <Card title="基础配置" size="small">
            <Row gutter={16}>
                <Col span={12}>
                    <Statistic
                        title="应用环境"
                        value={config?.app_env || 'N/A'}
                        prefix={<EnvironmentOutlined />}
                    />
                </Col>
                <Col span={12}>
                    <Statistic
                        title="应用版本"
                        value={config?.app_version || 'N/A'}
                        prefix={<ApiOutlined />}
                    />
                </Col>
            </Row>
            <Row gutter={16} style={{ marginTop: 16 }}>
                <Col span={12}>
                    <Statistic
                        title="调试模式"
                        value={config?.debug ? '开启' : '关闭'}
                        valueStyle={{ color: config?.debug ? '#cf1322' : '#3f8600' }}
                    />
                </Col>
                <Col span={12}>
                    <Statistic
                        title="日志级别"
                        value={config?.log_level || 'N/A'}
                        prefix={<HistoryOutlined />}
                    />
                </Col>
            </Row>
        </Card>
    );

    const renderThemeConfig = () => (
        <Card title="主题配置" size="small">
            <Row gutter={16}>
                <Col span={6}>
                    <Form.Item label="主色调">
                        <ColorPicker
                            value={config?.theme?.primaryColor}
                            onChange={(color) => {
                                if (config) {
                                    setConfig({
                                        ...config,
                                        theme: { ...config.theme, primaryColor: color.toHexString() }
                                    });
                                }
                            }}
                        />
                    </Form.Item>
                </Col>
                <Col span={6}>
                    <Form.Item label="布局模式">
                        <Select
                            value={config?.theme?.layout}
                            onChange={(value) => {
                                if (config) {
                                    setConfig({
                                        ...config,
                                        theme: { ...config.theme, layout: value }
                                    });
                                }
                            }}
                        >
                            <Option value="side">侧边栏</Option>
                            <Option value="top">顶部导航</Option>
                            <Option value="mix">混合模式</Option>
                        </Select>
                    </Form.Item>
                </Col>
                <Col span={6}>
                    <Form.Item label="紧凑模式">
                        <Switch
                            checked={config?.theme?.compact}
                            onChange={(checked) => {
                                if (config) {
                                    setConfig({
                                        ...config,
                                        theme: { ...config.theme, compact: checked }
                                    });
                                }
                            }}
                        />
                    </Form.Item>
                </Col>
                <Col span={6}>
                    <Form.Item label="深色模式">
                        <Switch
                            checked={config?.theme?.darkMode}
                            onChange={(checked) => {
                                if (config) {
                                    setConfig({
                                        ...config,
                                        theme: { ...config.theme, darkMode: checked }
                                    });
                                }
                            }}
                        />
                    </Form.Item>
                </Col>
            </Row>
        </Card>
    );

    const renderSecurityConfig = () => (
        <Card title="安全配置" size="small">
            <Row gutter={16}>
                <Col span={8}>
                    <Form.Item label="双因素认证">
                        <Switch
                            checked={config?.security?.enableTwoFactor}
                            onChange={(checked) => {
                                if (config) {
                                    setConfig({
                                        ...config,
                                        security: { ...config.security, enableTwoFactor: checked }
                                    });
                                }
                            }}
                        />
                    </Form.Item>
                </Col>
                <Col span={8}>
                    <Form.Item label="会话超时(分钟)">
                        <InputNumber
                            value={config?.security?.sessionTimeout}
                            onChange={(value) => {
                                if (config) {
                                    setConfig({
                                        ...config,
                                        security: { ...config.security, sessionTimeout: value || 30 }
                                    });
                                }
                            }}
                            min={5}
                            max={1440}
                        />
                    </Form.Item>
                </Col>
                <Col span={8}>
                    <Form.Item label="最大登录尝试">
                        <InputNumber
                            value={config?.security?.maxLoginAttempts}
                            onChange={(value) => {
                                if (config) {
                                    setConfig({
                                        ...config,
                                        security: { ...config.security, maxLoginAttempts: value || 5 }
                                    });
                                }
                            }}
                            min={3}
                            max={10}
                        />
                    </Form.Item>
                </Col>
            </Row>
            <Divider>密码策略</Divider>
            <Row gutter={16}>
                <Col span={6}>
                    <Form.Item label="最小长度">
                        <InputNumber
                            value={config?.security?.passwordPolicy?.minLength}
                            onChange={(value) => {
                                if (config) {
                                    setConfig({
                                        ...config,
                                        security: {
                                            ...config.security,
                                            passwordPolicy: {
                                                ...config.security.passwordPolicy,
                                                minLength: value || 8
                                            }
                                        }
                                    });
                                }
                            }}
                            min={6}
                            max={20}
                        />
                    </Form.Item>
                </Col>
                <Col span={6}>
                    <Form.Item label="大写字母">
                        <Switch
                            checked={config?.security?.passwordPolicy?.requireUppercase}
                            onChange={(checked) => {
                                if (config) {
                                    setConfig({
                                        ...config,
                                        security: {
                                            ...config.security,
                                            passwordPolicy: {
                                                ...config.security.passwordPolicy,
                                                requireUppercase: checked
                                            }
                                        }
                                    });
                                }
                            }}
                        />
                    </Form.Item>
                </Col>
                <Col span={6}>
                    <Form.Item label="小写字母">
                        <Switch
                            checked={config?.security?.passwordPolicy?.requireLowercase}
                            onChange={(checked) => {
                                if (config) {
                                    setConfig({
                                        ...config,
                                        security: {
                                            ...config.security,
                                            passwordPolicy: {
                                                ...config.security.passwordPolicy,
                                                requireLowercase: checked
                                            }
                                        }
                                    });
                                }
                            }}
                        />
                    </Form.Item>
                </Col>
                <Col span={6}>
                    <Form.Item label="特殊字符">
                        <Switch
                            checked={config?.security?.passwordPolicy?.requireSpecialChars}
                            onChange={(checked) => {
                                if (config) {
                                    setConfig({
                                        ...config,
                                        security: {
                                            ...config.security,
                                            passwordPolicy: {
                                                ...config.security.passwordPolicy,
                                                requireSpecialChars: checked
                                            }
                                        }
                                    });
                                }
                            }}
                        />
                    </Form.Item>
                </Col>
            </Row>
        </Card>
    );

    const renderPerformanceConfig = () => (
        <Card title="性能配置" size="small">
            <Row gutter={16}>
                <Col span={6}>
                    <Form.Item label="启用缓存">
                        <Switch
                            checked={config?.performance?.enableCaching}
                            onChange={(checked) => {
                                if (config) {
                                    setConfig({
                                        ...config,
                                        performance: { ...config.performance, enableCaching: checked }
                                    });
                                }
                            }}
                        />
                    </Form.Item>
                </Col>
                <Col span={6}>
                    <Form.Item label="缓存大小(MB)">
                        <InputNumber
                            value={config?.performance?.cacheSize}
                            onChange={(value) => {
                                if (config) {
                                    setConfig({
                                        ...config,
                                        performance: { ...config.performance, cacheSize: value || 100 }
                                    });
                                }
                            }}
                            min={10}
                            max={1000}
                        />
                    </Form.Item>
                </Col>
                <Col span={6}>
                    <Form.Item label="启用压缩">
                        <Switch
                            checked={config?.performance?.enableCompression}
                            onChange={(checked) => {
                                if (config) {
                                    setConfig({
                                        ...config,
                                        performance: { ...config.performance, enableCompression: checked }
                                    });
                                }
                            }}
                        />
                    </Form.Item>
                </Col>
                <Col span={6}>
                    <Form.Item label="最大并发请求">
                        <InputNumber
                            value={config?.performance?.maxConcurrentRequests}
                            onChange={(value) => {
                                if (config) {
                                    setConfig({
                                        ...config,
                                        performance: { ...config.performance, maxConcurrentRequests: value || 10 }
                                    });
                                }
                            }}
                            min={1}
                            max={50}
                        />
                    </Form.Item>
                </Col>
            </Row>
        </Card>
    );

    const renderFeatureConfig = () => (
        <Card title="功能配置" size="small">
            <Row gutter={16}>
                <Col span={8}>
                    <Form.Item label="通知功能">
                        <Switch
                            checked={config?.features?.enableNotifications}
                            onChange={(checked) => {
                                if (config) {
                                    setConfig({
                                        ...config,
                                        features: { ...config.features, enableNotifications: checked }
                                    });
                                }
                            }}
                        />
                    </Form.Item>
                </Col>
                <Col span={8}>
                    <Form.Item label="数据分析">
                        <Switch
                            checked={config?.features?.enableAnalytics}
                            onChange={(checked) => {
                                if (config) {
                                    setConfig({
                                        ...config,
                                        features: { ...config.features, enableAnalytics: checked }
                                    });
                                }
                            }}
                        />
                    </Form.Item>
                </Col>
                <Col span={8}>
                    <Form.Item label="自动备份">
                        <Switch
                            checked={config?.features?.enableBackup}
                            onChange={(checked) => {
                                if (config) {
                                    setConfig({
                                        ...config,
                                        features: { ...config.features, enableBackup: checked }
                                    });
                                }
                            }}
                        />
                    </Form.Item>
                </Col>
            </Row>
            <Row gutter={16}>
                <Col span={8}>
                    <Form.Item label="自动同步">
                        <Switch
                            checked={config?.features?.enableAutoSync}
                            onChange={(checked) => {
                                if (config) {
                                    setConfig({
                                        ...config,
                                        features: { ...config.features, enableAutoSync: checked }
                                    });
                                }
                            }}
                        />
                    </Form.Item>
                </Col>
                <Col span={8}>
                    <Form.Item label="多语言支持">
                        <Switch
                            checked={config?.features?.enableMultiLanguage}
                            onChange={(checked) => {
                                if (config) {
                                    setConfig({
                                        ...config,
                                        features: { ...config.features, enableMultiLanguage: checked }
                                    });
                                }
                            }}
                        />
                    </Form.Item>
                </Col>
            </Row>
        </Card>
    );

    return (
        <div style={{ padding: '24px' }}>
            <Card>
                <Row justify="space-between" align="middle" style={{ marginBottom: '16px' }}>
                    <Col>
                        <Title level={3} style={{ margin: 0 }}>
                            <SettingOutlined /> 高级配置管理
                        </Title>
                        <Text type="secondary">管理系统的高级配置选项</Text>
                    </Col>
                    <Col>
                        <Space>
                            <Button
                                icon={<ReloadOutlined />}
                                onClick={loadConfig}
                                loading={loading}
                            >
                                刷新
                            </Button>
                            <Button
                                icon={<CheckCircleOutlined />}
                                onClick={validateConfig}
                                loading={loading}
                            >
                                验证
                            </Button>
                            <Button
                                icon={<ExportOutlined />}
                                onClick={exportConfig}
                            >
                                导出
                            </Button>
                            <Button
                                icon={<ImportOutlined />}
                                onClick={() => setImportModalVisible(true)}
                            >
                                导入
                            </Button>
                            <Button
                                icon={<UndoOutlined />}
                                onClick={resetConfig}
                                danger
                            >
                                重置
                            </Button>
                        </Space>
                    </Col>
                </Row>

                <Tabs defaultActiveKey="basic">
                    <TabPane tab="基础配置" key="basic">
                        {renderBasicConfig()}
                    </TabPane>
                    <TabPane tab="主题配置" key="theme">
                        {renderThemeConfig()}
                    </TabPane>
                    <TabPane tab="安全配置" key="security">
                        {renderSecurityConfig()}
                    </TabPane>
                    <TabPane tab="性能配置" key="performance">
                        {renderPerformanceConfig()}
                    </TabPane>
                    <TabPane tab="功能配置" key="features">
                        {renderFeatureConfig()}
                    </TabPane>
                </Tabs>
            </Card>

            {/* 导入模态框 */}
            <Modal
                title="导入配置"
                open={importModalVisible}
                onCancel={() => setImportModalVisible(false)}
                footer={null}
            >
                <Form
                    form={importForm}
                    layout="vertical"
                    onFinish={importConfig}
                >
                    <Form.Item
                        name="configData"
                        label="配置数据 (JSON格式)"
                        rules={[{ required: true, message: '请输入配置数据' }]}
                    >
                        <TextArea
                            rows={10}
                            placeholder="请输入JSON格式的配置数据"
                        />
                    </Form.Item>
                    <Form.Item>
                        <Space>
                            <Button type="primary" htmlType="submit">
                                导入
                            </Button>
                            <Button onClick={() => setImportModalVisible(false)}>
                                取消
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default AdvancedConfigManagement;