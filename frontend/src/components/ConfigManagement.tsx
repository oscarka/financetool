import React, { useState, useEffect } from 'react';
import { Card, Button, Space, message, Modal, Form, Input, Upload, Drawer, Table, Statistic, Row, Col, Tag, Typography } from 'antd';
import { configAPI } from '../services/configAPI';
import { ReloadOutlined, EditOutlined, ExportOutlined, ImportOutlined, ResetOutlined, HistoryOutlined, EnvironmentOutlined, CheckCircleOutlined, CloseCircleOutlined, WarningOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;
const { TextArea } = Input;

interface ConfigData {
    app_env?: string;
    api_base_url?: string;
    database_url?: string;
    redis_url?: string;
    log_level?: string;
    [key: string]: any;
}

interface ValidationResult {
    valid: boolean;
    errors?: string[];
    warnings?: string[];
}

interface EnvironmentInfo {
    python_version?: string;
    platform?: string;
    memory_usage?: string;
    disk_usage?: string;
    uptime?: string;
}

interface ConfigHistory {
    id: number;
    timestamp: string;
    action: string;
    user: string;
    changes: string;
}

const ConfigManagement: React.FC = () => {
    const [config, setConfig] = useState<ConfigData | null>(null);
    const [loading, setLoading] = useState(false);
    const [configLoading, setConfigLoading] = useState(true);
    const [validationLoading, setValidationLoading] = useState(false);
    const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
    const [environmentInfo, setEnvironmentInfo] = useState<EnvironmentInfo | null>(null);
    const [editModalVisible, setEditModalVisible] = useState(false);
    const [importModalVisible, setImportModalVisible] = useState(false);
    const [historyDrawerVisible, setHistoryDrawerVisible] = useState(false);
    const [configHistory, setConfigHistory] = useState<ConfigHistory[]>([]);
    const [editForm] = Form.useForm();
    const [importForm] = Form.useForm();

    // 初始化加载
    useEffect(() => {
        loadConfig();
        loadEnvironmentInfo();
    }, []);

    // 加载配置信息
    const loadConfig = async () => {
        setConfigLoading(true);
        try {
            const response = await configAPI.getConfig();
            setConfig(response);
        } catch (error) {
            message.error('获取配置失败');
            console.error('获取配置失败:', error);
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
                            title="配置状态"
                            value={validationResult?.valid ? '有效' : '无效'}
                            prefix={validationResult?.valid ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
                            valueStyle={{ color: validationResult?.valid ? '#3f8600' : '#cf1322' }}
                        />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic
                            title="Python版本"
                            value={environmentInfo?.python_version || 'unknown'}
                            prefix={<EnvironmentOutlined />}
                        />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic
                            title="运行时间"
                            value={environmentInfo?.uptime || 'unknown'}
                            prefix={<EnvironmentOutlined />}
                        />
                    </Card>
                </Col>
            </Row>
        );
    };

    // 渲染基本配置
    const renderBasicConfig = () => {
        if (!config) {
            return <div>配置加载中...</div>;
        }

        return (
            <Card title="基本配置" style={{ marginBottom: 16 }}>
                <Row gutter={16}>
                    <Col span={12}>
                        <div style={{ marginBottom: 16 }}>
                            <Text strong>应用环境:</Text>
                            <div>
                                <Tag color={config.app_env === 'prod' ? 'red' : 'green'}>
                                    {config.app_env || 'unknown'}
                                </Tag>
                            </div>
                        </div>
                    </Col>
                    <Col span={12}>
                        <div style={{ marginBottom: 16 }}>
                            <Text strong>API基础URL:</Text>
                            <div>{config.api_base_url || '未设置'}</div>
                        </div>
                    </Col>
                </Row>
                <Row gutter={16}>
                    <Col span={12}>
                        <div style={{ marginBottom: 16 }}>
                            <Text strong>数据库URL:</Text>
                            <div>{config.database_url ? '已设置' : '未设置'}</div>
                        </div>
                    </Col>
                    <Col span={12}>
                        <div style={{ marginBottom: 16 }}>
                            <Text strong>Redis URL:</Text>
                            <div>{config.redis_url ? '已设置' : '未设置'}</div>
                        </div>
                    </Col>
                </Row>
                <Row gutter={16}>
                    <Col span={12}>
                        <div style={{ marginBottom: 16 }}>
                            <Text strong>日志级别:</Text>
                            <div>
                                <Tag color={config.log_level === 'DEBUG' ? 'blue' : 'default'}>
                                    {config.log_level || 'INFO'}
                                </Tag>
                            </div>
                        </div>
                    </Col>
                </Row>
            </Card>
        );
    };

    // 渲染API配置
    const renderAPIConfig = () => (
        <Card title="API配置" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
                <Col span={12}>
                    <div style={{ marginBottom: 16 }}>
                        <Text strong>API基础URL:</Text>
                        <div>{config?.api_base_url || '未设置'}</div>
                    </div>
                </Col>
                <Col span={12}>
                    <div style={{ marginBottom: 16 }}>
                        <Text strong>超时设置:</Text>
                        <div>{config?.timeout || '默认'}</div>
                    </div>
                </Col>
            </Row>
        </Card>
    );

    // 渲染系统配置
    const renderSystemConfig = () => (
        <Card title="系统配置" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
                <Col span={12}>
                    <div style={{ marginBottom: 16 }}>
                        <Text strong>数据库连接:</Text>
                        <div>{config?.database_url ? '已配置' : '未配置'}</div>
                    </div>
                </Col>
                <Col span={12}>
                    <div style={{ marginBottom: 16 }}>
                        <Text strong>Redis连接:</Text>
                        <div>{config?.redis_url ? '已配置' : '未配置'}</div>
                    </div>
                </Col>
            </Row>
            <Row gutter={16}>
                <Col span={12}>
                    <div style={{ marginBottom: 16 }}>
                        <Text strong>日志配置:</Text>
                        <div>
                            <Tag color={config?.log_level === 'DEBUG' ? 'blue' : 'default'}>
                                {config?.log_level || 'INFO'}
                            </Tag>
                        </div>
                    </div>
                </Col>
            </Row>
        </Card>
    );

    // 渲染验证结果
    const renderValidationResult = () => {
        if (!validationResult) return null;

        return (
            <Card title="配置验证结果" style={{ marginBottom: 16 }}>
                <div style={{ marginBottom: 16 }}>
                    <Text strong>验证状态:</Text>
                    <div>
                        <Tag color={validationResult.valid ? 'green' : 'red'}>
                            {validationResult.valid ? '通过' : '失败'}
                        </Tag>
                    </div>
                </div>
                {validationResult.errors && validationResult.errors.length > 0 && (
                    <div style={{ marginBottom: 16 }}>
                        <Text strong>错误信息:</Text>
                        <ul>
                            {validationResult.errors.map((error, index) => (
                                <li key={index} style={{ color: '#cf1322' }}>{error}</li>
                            ))}
                        </ul>
                    </div>
                )}
                {validationResult.warnings && validationResult.warnings.length > 0 && (
                    <div>
                        <Text strong>警告信息:</Text>
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

    // 渲染环境信息
    const renderEnvironmentInfo = () => {
        if (!environmentInfo) return null;

        return (
            <Card title="环境信息" style={{ marginBottom: 16 }}>
                <Row gutter={16}>
                    <Col span={12}>
                        <div style={{ marginBottom: 16 }}>
                            <Text strong>Python版本:</Text>
                            <div>{environmentInfo.python_version}</div>
                        </div>
                    </Col>
                    <Col span={12}>
                        <div style={{ marginBottom: 16 }}>
                            <Text strong>平台:</Text>
                            <div>{environmentInfo.platform}</div>
                        </div>
                    </Col>
                </Row>
                <Row gutter={16}>
                    <Col span={12}>
                        <div style={{ marginBottom: 16 }}>
                            <Text strong>内存使用:</Text>
                            <div>{environmentInfo.memory_usage}</div>
                        </div>
                    </Col>
                    <Col span={12}>
                        <div style={{ marginBottom: 16 }}>
                            <Text strong>磁盘使用:</Text>
                            <div>{environmentInfo.disk_usage}</div>
                        </div>
                    </Col>
                </Row>
                <Row gutter={16}>
                    <Col span={12}>
                        <div style={{ marginBottom: 16 }}>
                            <Text strong>运行时间:</Text>
                            <div>{environmentInfo.uptime}</div>
                        </div>
                    </Col>
                </Row>
            </Card>
        );
    };

    // 配置历史表格列定义
    const historyColumns = [
        {
            title: '时间',
            dataIndex: 'timestamp',
            key: 'timestamp',
            render: (timestamp: string) => new Date(timestamp).toLocaleString()
        },
        {
            title: '操作',
            dataIndex: 'action',
            key: 'action',
            render: (action: string) => {
                const actionMap: { [key: string]: { text: string; color: string } } = {
                    'update': { text: '更新', color: 'blue' },
                    'import': { text: '导入', color: 'green' },
                    'reset': { text: '重置', color: 'red' },
                    'reload': { text: '重载', color: 'orange' }
                };
                const config = actionMap[action] || { text: action, color: 'default' };
                return <Tag color={config.color}>{config.text}</Tag>;
            }
        },
        {
            title: '用户',
            dataIndex: 'user',
            key: 'user'
        },
        {
            title: '变更内容',
            dataIndex: 'changes',
            key: 'changes',
            render: (changes: string) => (
                <Text style={{ fontSize: '12px' }}>{changes}</Text>
            )
        }
    ];

    if (configLoading) {
        return (
            <div style={{ padding: '20px', textAlign: 'center' }}>
                <div>配置加载中...</div>
            </div>
        );
    }

    return (
        <div style={{ padding: '16px' }}>
            <Title level={2}>配置管理</Title>
            
            {/* 操作按钮 */}
            <Card style={{ marginBottom: 16 }}>
                <Space>
                    <Button
                        icon={<ReloadOutlined />}
                        onClick={reloadConfig}
                        loading={loading}
                    >
                        重新加载
                    </Button>
                    <Button
                        icon={<EditOutlined />}
                        onClick={() => setEditModalVisible(true)}
                    >
                        编辑配置
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
                        icon={<ResetOutlined />}
                        onClick={resetConfig}
                        loading={loading}
                        danger
                    >
                        重置配置
                    </Button>
                    <Button
                        icon={<HistoryOutlined />}
                        onClick={viewConfigHistory}
                    >
                        配置历史
                    </Button>
                    <Button
                        icon={<CheckCircleOutlined />}
                        onClick={validateConfig}
                        loading={validationLoading}
                    >
                        验证配置
                    </Button>
                </Space>
            </Card>

            {/* 统计信息 */}
            {renderStatistics()}

            {/* 配置详情 */}
            {renderBasicConfig()}
            {renderAPIConfig()}
            {renderSystemConfig()}

            {/* 验证结果 */}
            {renderValidationResult()}

            {/* 环境信息 */}
            {renderEnvironmentInfo()}

            {/* 编辑配置弹窗 */}
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
                    initialValues={config || {}}
                >
                    <Form.Item
                        name="app_env"
                        label="应用环境"
                        rules={[{ required: true, message: '请输入应用环境' }]}
                    >
                        <Input placeholder="例如: dev, test, prod" />
                    </Form.Item>
                    <Form.Item
                        name="api_base_url"
                        label="API基础URL"
                        rules={[{ required: true, message: '请输入API基础URL' }]}
                    >
                        <Input placeholder="例如: http://localhost:8000/api/v1" />
                    </Form.Item>
                    <Form.Item
                        name="database_url"
                        label="数据库URL"
                    >
                        <Input placeholder="数据库连接字符串" />
                    </Form.Item>
                    <Form.Item
                        name="redis_url"
                        label="Redis URL"
                    >
                        <Input placeholder="Redis连接字符串" />
                    </Form.Item>
                    <Form.Item
                        name="log_level"
                        label="日志级别"
                    >
                        <Input placeholder="例如: DEBUG, INFO, WARNING, ERROR" />
                    </Form.Item>
                    <Form.Item>
                        <Space>
                            <Button type="primary" htmlType="submit" loading={loading}>
                                保存
                            </Button>
                            <Button onClick={() => setEditModalVisible(false)}>
                                取消
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Modal>

            {/* 导入配置弹窗 */}
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
                        name="config_data"
                        label="配置数据 (JSON格式)"
                        rules={[
                            { required: true, message: '请输入配置数据' },
                            {
                                validator: (_, value) => {
                                    if (value) {
                                        try {
                                            JSON.parse(value);
                                            return Promise.resolve();
                                        } catch (error) {
                                            return Promise.reject(new Error('请输入有效的JSON格式'));
                                        }
                                    }
                                    return Promise.resolve();
                                }
                            }
                        ]}
                    >
                        <TextArea
                            rows={10}
                            placeholder="请输入JSON格式的配置数据"
                        />
                    </Form.Item>
                    <Form.Item>
                        <Space>
                            <Button type="primary" htmlType="submit" loading={loading}>
                                导入
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
                width={800}
                open={historyDrawerVisible}
                onClose={() => setHistoryDrawerVisible(false)}
            >
                <Table
                    columns={historyColumns}
                    dataSource={configHistory}
                    rowKey="id"
                    pagination={{ pageSize: 20 }}
                />
            </Drawer>
        </div>
    );
};

export default ConfigManagement; 