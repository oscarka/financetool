import React, { useState, useEffect } from 'react';
import {
    Card,
    Button,
    Table,
    Modal,
    Form,
    Input,
    Select,
    Switch,
    Space,
    message,
    Popconfirm,
    Tag,
    Tooltip,
    Drawer,
    Row,
    Col,
    Typography,
    Divider,
    Alert,
    Badge,
    InputNumber,
    ColorPicker
} from 'antd';
import {
    PlusOutlined,
    EditOutlined,
    DeleteOutlined,
    EyeOutlined,
    EyeInvisibleOutlined,
    DragOutlined,
    SettingOutlined,
    SaveOutlined,
    ReloadOutlined,
    ExportOutlined,
    ImportOutlined,
    LockOutlined,
    UnlockOutlined,
    MenuOutlined,
    LinkOutlined,
    HomeOutlined,
    PlusCircleOutlined,
    BarChartOutlined,
    DollarOutlined,
    PieChartOutlined,
    SettingOutlined as SettingIcon,
    GlobalOutlined,
    BankOutlined,
    PayCircleOutlined,
    StockOutlined,
    ToolOutlined,
    ClockCircleOutlined,
    UserOutlined,
    TeamOutlined,
    SafetyOutlined
} from '@ant-design/icons';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

// 图标映射
const iconMap = {
    HomeOutlined,
    PlusCircleOutlined,
    BarChartOutlined,
    DollarOutlined,
    PieChartOutlined,
    SettingOutlined: SettingIcon,
    GlobalOutlined,
    BankOutlined,
    PayCircleOutlined,
    StockOutlined,
    ToolOutlined,
    ClockCircleOutlined,
    UserOutlined,
    TeamOutlined,
    SafetyOutlined,
    MenuOutlined,
    LinkOutlined
};

export interface MenuItem {
    id: string;
    name: string;
    href: string;
    icon: string;
    order: number;
    visible: boolean;
    enabled: boolean;
    requireAuth: boolean;
    permissions: string[];
    description?: string;
    badge?: string;
    badgeColor?: string;
    parentId?: string;
    children?: MenuItem[];
    createdAt: string;
    updatedAt: string;
}

export interface MenuConfig {
    id: string;
    name: string;
    description: string;
    items: MenuItem[];
    isDefault: boolean;
    isActive: boolean;
    createdAt: string;
    updatedAt: string;
}

const MenuManagement: React.FC = () => {
    // 状态管理
    const [loading, setLoading] = useState(false);
    const [menuConfigs, setMenuConfigs] = useState<MenuConfig[]>([]);
    const [currentConfig, setCurrentConfig] = useState<MenuConfig | null>(null);
    const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
    
    // 模态框状态
    const [configModalVisible, setConfigModalVisible] = useState(false);
    const [itemModalVisible, setItemModalVisible] = useState(false);
    const [previewDrawerVisible, setPreviewDrawerVisible] = useState(false);
    const [importModalVisible, setImportModalVisible] = useState(false);
    
    // 表单状态
    const [configForm] = Form.useForm();
    const [itemForm] = Form.useForm();
    const [importForm] = Form.useForm();
    
    // 编辑状态
    const [editingItem, setEditingItem] = useState<MenuItem | null>(null);
    const [editingConfig, setEditingConfig] = useState<MenuConfig | null>(null);

    // DnD传感器
    const sensors = useSensors(
        useSensor(PointerSensor),
        useSensor(KeyboardSensor, {
            coordinateGetter: sortableKeyboardCoordinates,
        })
    );

    // 初始化数据
    useEffect(() => {
        loadMenuConfigs();
        loadDefaultMenuItems();
    }, []);

    // 加载菜单配置
    const loadMenuConfigs = async () => {
        setLoading(true);
        try {
            // 模拟API调用
            const mockConfigs: MenuConfig[] = [
                {
                    id: 'default',
                    name: '默认菜单',
                    description: '系统默认菜单配置',
                    items: [],
                    isDefault: true,
                    isActive: true,
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString()
                },
                {
                    id: 'custom1',
                    name: '自定义菜单1',
                    description: '用户自定义菜单配置',
                    items: [],
                    isDefault: false,
                    isActive: false,
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString()
                }
            ];
            setMenuConfigs(mockConfigs);
            setCurrentConfig(mockConfigs[0]);
        } catch (error) {
            message.error('加载菜单配置失败');
        } finally {
            setLoading(false);
        }
    };

    // 加载默认菜单项
    const loadDefaultMenuItems = () => {
        const defaultItems: MenuItem[] = [
            {
                id: 'dashboard',
                name: '总览',
                href: '/',
                icon: 'HomeOutlined',
                order: 1,
                visible: true,
                enabled: true,
                requireAuth: false,
                permissions: [],
                description: '系统总览页面',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            },
            {
                id: 'operations',
                name: '操作记录',
                href: '/operations',
                icon: 'PlusCircleOutlined',
                order: 2,
                visible: true,
                enabled: true,
                requireAuth: true,
                permissions: ['operations:read'],
                description: '投资操作记录管理',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            },
            {
                id: 'positions',
                name: '持仓',
                href: '/positions',
                icon: 'BarChartOutlined',
                order: 3,
                visible: true,
                enabled: true,
                requireAuth: true,
                permissions: ['positions:read'],
                description: '持仓信息查看',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            },
            {
                id: 'funds',
                name: '基金',
                href: '/funds',
                icon: 'DollarOutlined',
                order: 4,
                visible: true,
                enabled: true,
                requireAuth: true,
                permissions: ['funds:read'],
                description: '基金投资管理',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            },
            {
                id: 'exchange-rates',
                name: '汇率',
                href: '/exchange-rates',
                icon: 'GlobalOutlined',
                order: 5,
                visible: true,
                enabled: true,
                requireAuth: false,
                permissions: [],
                description: '汇率信息查看',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            },
            {
                id: 'analysis',
                name: '分析',
                href: '/analysis',
                icon: 'PieChartOutlined',
                order: 6,
                visible: true,
                enabled: true,
                requireAuth: true,
                permissions: ['analysis:read'],
                description: '投资分析报告',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            },
            {
                id: 'okx',
                name: 'OKX管理',
                href: '/okx',
                icon: 'SettingOutlined',
                order: 7,
                visible: true,
                enabled: true,
                requireAuth: true,
                permissions: ['okx:manage'],
                description: 'OKX账户管理',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            },
            {
                id: 'wise',
                name: 'Wise管理',
                href: '/wise',
                icon: 'BankOutlined',
                order: 8,
                visible: true,
                enabled: true,
                requireAuth: true,
                permissions: ['wise:manage'],
                description: 'Wise账户管理',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            },
            {
                id: 'paypal',
                name: 'PayPal管理',
                href: '/paypal',
                icon: 'PayCircleOutlined',
                order: 9,
                visible: true,
                enabled: true,
                requireAuth: true,
                permissions: ['paypal:manage'],
                description: 'PayPal账户管理',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            },
            {
                id: 'ibkr',
                name: 'IBKR管理',
                href: '/ibkr',
                icon: 'StockOutlined',
                order: 10,
                visible: true,
                enabled: true,
                requireAuth: true,
                permissions: ['ibkr:manage'],
                description: 'IBKR账户管理',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            },
            {
                id: 'config',
                name: '配置管理',
                href: '/config',
                icon: 'ToolOutlined',
                order: 11,
                visible: true,
                enabled: true,
                requireAuth: true,
                permissions: ['config:manage'],
                description: '系统配置管理',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            },
            {
                id: 'scheduler',
                name: '调度器管理',
                href: '/scheduler',
                icon: 'ClockCircleOutlined',
                order: 12,
                visible: true,
                enabled: true,
                requireAuth: true,
                permissions: ['scheduler:manage'],
                description: '定时任务管理',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            }
        ];
        setMenuItems(defaultItems);
    };

    // 处理拖拽排序
    const handleDragEnd = (event: any) => {
        const { active, over } = event;

        if (active.id !== over.id) {
            setMenuItems((items) => {
                const oldIndex = items.findIndex((item) => item.id === active.id);
                const newIndex = items.findIndex((item) => item.id === over.id);

                const newItems = arrayMove(items, oldIndex, newIndex);
                // 更新order字段
                return newItems.map((item, index) => ({
                    ...item,
                    order: index + 1
                }));
            });
        }
    };

    // 创建新配置
    const createConfig = async (values: any) => {
        try {
            const newConfig: MenuConfig = {
                id: `config_${Date.now()}`,
                name: values.name,
                description: values.description,
                items: [...menuItems],
                isDefault: false,
                isActive: false,
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            };
            
            setMenuConfigs([...menuConfigs, newConfig]);
            setConfigModalVisible(false);
            configForm.resetFields();
            message.success('菜单配置创建成功');
        } catch (error) {
            message.error('创建配置失败');
        }
    };

    // 创建新菜单项
    const createMenuItem = async (values: any) => {
        try {
            const newItem: MenuItem = {
                id: `item_${Date.now()}`,
                name: values.name,
                href: values.href,
                icon: values.icon,
                order: menuItems.length + 1,
                visible: values.visible,
                enabled: values.enabled,
                requireAuth: values.requireAuth,
                permissions: values.permissions || [],
                description: values.description,
                badge: values.badge,
                badgeColor: values.badgeColor,
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            };
            
            setMenuItems([...menuItems, newItem]);
            setItemModalVisible(false);
            itemForm.resetFields();
            message.success('菜单项创建成功');
        } catch (error) {
            message.error('创建菜单项失败');
        }
    };

    // 更新菜单项
    const updateMenuItem = async (values: any) => {
        if (!editingItem) return;
        
        try {
            const updatedItems = menuItems.map(item => 
                item.id === editingItem.id 
                    ? { ...item, ...values, updatedAt: new Date().toISOString() }
                    : item
            );
            setMenuItems(updatedItems);
            setItemModalVisible(false);
            setEditingItem(null);
            itemForm.resetFields();
            message.success('菜单项更新成功');
        } catch (error) {
            message.error('更新菜单项失败');
        }
    };

    // 删除菜单项
    const deleteMenuItem = async (id: string) => {
        try {
            setMenuItems(menuItems.filter(item => item.id !== id));
            message.success('菜单项删除成功');
        } catch (error) {
            message.error('删除菜单项失败');
        }
    };

    // 切换菜单项状态
    const toggleMenuItemStatus = (id: string, field: 'visible' | 'enabled') => {
        setMenuItems(menuItems.map(item => 
            item.id === id 
                ? { ...item, [field]: !item[field], updatedAt: new Date().toISOString() }
                : item
        ));
    };

    // 激活配置
    const activateConfig = (configId: string) => {
        setMenuConfigs(menuConfigs.map(config => ({
            ...config,
            isActive: config.id === configId
        })));
        const config = menuConfigs.find(c => c.id === configId);
        if (config) {
            setCurrentConfig(config);
            setMenuItems(config.items);
        }
        message.success('配置已激活');
    };

    // 导出配置
    const exportConfig = () => {
        const configData = {
            config: currentConfig,
            items: menuItems
        };
        const blob = new Blob([JSON.stringify(configData, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `menu_config_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        message.success('配置导出成功');
    };

    // 导入配置
    const importConfig = async (values: any) => {
        try {
            const configData = JSON.parse(values.configData);
            if (configData.items) {
                setMenuItems(configData.items);
            }
            if (configData.config) {
                setCurrentConfig(configData.config);
            }
            setImportModalVisible(false);
            importForm.resetFields();
            message.success('配置导入成功');
        } catch (error) {
            message.error('配置导入失败');
        }
    };

    // 表格列定义
    const columns = [
        {
            title: '排序',
            dataIndex: 'order',
            width: 60,
            render: (order: number) => (
                <Badge count={order} style={{ backgroundColor: '#52c41a' }} />
            )
        },
        {
            title: '图标',
            dataIndex: 'icon',
            width: 80,
            render: (icon: string) => {
                const IconComponent = iconMap[icon as keyof typeof iconMap];
                return IconComponent ? <IconComponent style={{ fontSize: '16px' }} /> : <LinkOutlined />;
            }
        },
        {
            title: '名称',
            dataIndex: 'name',
            render: (name: string, record: MenuItem) => (
                <Space>
                    <Text strong>{name}</Text>
                    {record.badge && (
                        <Tag color={record.badgeColor || 'blue'}>{record.badge}</Tag>
                    )}
                </Space>
            )
        },
        {
            title: '路径',
            dataIndex: 'href',
            render: (href: string) => (
                <Text code>{href}</Text>
            )
        },
        {
            title: '描述',
            dataIndex: 'description',
            ellipsis: true
        },
        {
            title: '权限',
            dataIndex: 'permissions',
            render: (permissions: string[]) => (
                <Space wrap>
                    {permissions.map(perm => (
                        <Tag key={perm} color="orange" size="small">{perm}</Tag>
                    ))}
                </Space>
            )
        },
        {
            title: '状态',
            key: 'status',
            width: 120,
            render: (record: MenuItem) => (
                <Space direction="vertical" size="small">
                    <Switch
                        checked={record.visible}
                        onChange={() => toggleMenuItemStatus(record.id, 'visible')}
                        checkedChildren={<EyeOutlined />}
                        unCheckedChildren={<EyeInvisibleOutlined />}
                    />
                    <Switch
                        checked={record.enabled}
                        onChange={() => toggleMenuItemStatus(record.id, 'enabled')}
                        checkedChildren={<UnlockOutlined />}
                        unCheckedChildren={<LockOutlined />}
                    />
                </Space>
            )
        },
        {
            title: '操作',
            key: 'actions',
            width: 120,
            render: (record: MenuItem) => (
                <Space>
                    <Tooltip title="编辑">
                        <Button
                            type="text"
                            icon={<EditOutlined />}
                            onClick={() => {
                                setEditingItem(record);
                                itemForm.setFieldsValue(record);
                                setItemModalVisible(true);
                            }}
                        />
                    </Tooltip>
                    <Popconfirm
                        title="确定要删除这个菜单项吗？"
                        onConfirm={() => deleteMenuItem(record.id)}
                    >
                        <Tooltip title="删除">
                            <Button type="text" danger icon={<DeleteOutlined />} />
                        </Tooltip>
                    </Popconfirm>
                </Space>
            )
        }
    ];

    // 可拖拽行组件
    const DraggableRow = ({ record }: { record: MenuItem }) => {
        const {
            attributes,
            listeners,
            setNodeRef,
            transform,
            transition,
            isDragging,
        } = useSortable({ id: record.id });

        const style = {
            transform: CSS.Transform.toString(transform),
            transition,
            opacity: isDragging ? 0.5 : 1,
        };

        return (
            <tr ref={setNodeRef} style={style} {...attributes} {...listeners}>
                <td style={{ cursor: 'grab' }}>
                    <DragOutlined style={{ color: '#999' }} />
                </td>
                {columns.slice(1).map((col, index) => (
                    <td key={index}>
                        {col.render ? col.render(record[col.dataIndex as keyof MenuItem], record) : record[col.dataIndex as keyof MenuItem]}
                    </td>
                ))}
            </tr>
        );
    };

    return (
        <div style={{ padding: '24px' }}>
            <Card>
                <Row justify="space-between" align="middle" style={{ marginBottom: '16px' }}>
                    <Col>
                        <Title level={3} style={{ margin: 0 }}>
                            <MenuOutlined /> 菜单管理
                        </Title>
                        <Text type="secondary">管理系统菜单配置和权限</Text>
                    </Col>
                    <Col>
                        <Space>
                            <Button
                                icon={<PlusOutlined />}
                                onClick={() => setConfigModalVisible(true)}
                            >
                                新建配置
                            </Button>
                            <Button
                                icon={<PlusOutlined />}
                                type="primary"
                                onClick={() => setItemModalVisible(true)}
                            >
                                添加菜单项
                            </Button>
                            <Button
                                icon={<EyeOutlined />}
                                onClick={() => setPreviewDrawerVisible(true)}
                            >
                                预览
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
                        </Space>
                    </Col>
                </Row>

                {/* 配置选择 */}
                <Card size="small" style={{ marginBottom: '16px' }}>
                    <Row justify="space-between" align="middle">
                        <Col>
                            <Text strong>当前配置: </Text>
                            <Select
                                value={currentConfig?.id}
                                style={{ width: 200 }}
                                onChange={activateConfig}
                            >
                                {menuConfigs.map(config => (
                                    <Option key={config.id} value={config.id}>
                                        <Space>
                                            {config.name}
                                            {config.isDefault && <Tag color="blue">默认</Tag>}
                                            {config.isActive && <Tag color="green">激活</Tag>}
                                        </Space>
                                    </Option>
                                ))}
                            </Select>
                        </Col>
                        <Col>
                            <Text type="secondary">
                                共 {menuItems.length} 个菜单项
                            </Text>
                        </Col>
                    </Row>
                </Card>

                {/* 菜单项表格 */}
                <DndContext
                    sensors={sensors}
                    collisionDetection={closestCenter}
                    onDragEnd={handleDragEnd}
                >
                    <SortableContext
                        items={menuItems.map(item => item.id)}
                        strategy={verticalListSortingStrategy}
                    >
                        <Table
                            dataSource={menuItems}
                            columns={columns}
                            rowKey="id"
                            pagination={false}
                            components={{
                                body: {
                                    row: DraggableRow,
                                },
                            }}
                        />
                    </SortableContext>
                </DndContext>
            </Card>

            {/* 配置模态框 */}
            <Modal
                title="新建菜单配置"
                open={configModalVisible}
                onCancel={() => setConfigModalVisible(false)}
                footer={null}
            >
                <Form
                    form={configForm}
                    layout="vertical"
                    onFinish={createConfig}
                >
                    <Form.Item
                        name="name"
                        label="配置名称"
                        rules={[{ required: true, message: '请输入配置名称' }]}
                    >
                        <Input placeholder="请输入配置名称" />
                    </Form.Item>
                    <Form.Item
                        name="description"
                        label="配置描述"
                    >
                        <TextArea rows={3} placeholder="请输入配置描述" />
                    </Form.Item>
                    <Form.Item>
                        <Space>
                            <Button type="primary" htmlType="submit">
                                创建
                            </Button>
                            <Button onClick={() => setConfigModalVisible(false)}>
                                取消
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Modal>

            {/* 菜单项模态框 */}
            <Modal
                title={editingItem ? "编辑菜单项" : "新建菜单项"}
                open={itemModalVisible}
                onCancel={() => {
                    setItemModalVisible(false);
                    setEditingItem(null);
                    itemForm.resetFields();
                }}
                footer={null}
                width={600}
            >
                <Form
                    form={itemForm}
                    layout="vertical"
                    onFinish={editingItem ? updateMenuItem : createMenuItem}
                >
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                name="name"
                                label="菜单名称"
                                rules={[{ required: true, message: '请输入菜单名称' }]}
                            >
                                <Input placeholder="请输入菜单名称" />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item
                                name="href"
                                label="路由路径"
                                rules={[{ required: true, message: '请输入路由路径' }]}
                            >
                                <Input placeholder="/path" />
                            </Form.Item>
                        </Col>
                    </Row>
                    
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                name="icon"
                                label="图标"
                                rules={[{ required: true, message: '请选择图标' }]}
                            >
                                <Select placeholder="请选择图标">
                                    {Object.keys(iconMap).map(iconName => (
                                        <Option key={iconName} value={iconName}>
                                            <Space>
                                                {React.createElement(iconMap[iconName as keyof typeof iconMap])}
                                                {iconName}
                                            </Space>
                                        </Option>
                                    ))}
                                </Select>
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item
                                name="permissions"
                                label="所需权限"
                            >
                                <Select
                                    mode="tags"
                                    placeholder="请输入权限标识"
                                    allowClear
                                />
                            </Form.Item>
                        </Col>
                    </Row>

                    <Form.Item
                        name="description"
                        label="描述"
                    >
                        <TextArea rows={2} placeholder="请输入菜单描述" />
                    </Form.Item>

                    <Row gutter={16}>
                        <Col span={8}>
                            <Form.Item
                                name="visible"
                                label="是否可见"
                                valuePropName="checked"
                                initialValue={true}
                            >
                                <Switch />
                            </Form.Item>
                        </Col>
                        <Col span={8}>
                            <Form.Item
                                name="enabled"
                                label="是否启用"
                                valuePropName="checked"
                                initialValue={true}
                            >
                                <Switch />
                            </Form.Item>
                        </Col>
                        <Col span={8}>
                            <Form.Item
                                name="requireAuth"
                                label="需要认证"
                                valuePropName="checked"
                                initialValue={false}
                            >
                                <Switch />
                            </Form.Item>
                        </Col>
                    </Row>

                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                name="badge"
                                label="徽章文本"
                            >
                                <Input placeholder="如：New, Hot" />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item
                                name="badgeColor"
                                label="徽章颜色"
                                initialValue="#1890ff"
                            >
                                <ColorPicker />
                            </Form.Item>
                        </Col>
                    </Row>

                    <Form.Item>
                        <Space>
                            <Button type="primary" htmlType="submit">
                                {editingItem ? '更新' : '创建'}
                            </Button>
                            <Button onClick={() => {
                                setItemModalVisible(false);
                                setEditingItem(null);
                                itemForm.resetFields();
                            }}>
                                取消
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Modal>

            {/* 预览抽屉 */}
            <Drawer
                title="菜单预览"
                placement="right"
                width={400}
                open={previewDrawerVisible}
                onClose={() => setPreviewDrawerVisible(false)}
            >
                <div style={{ padding: '16px' }}>
                    <Title level={4}>个人财务管理系统</Title>
                    <Divider />
                    {menuItems
                        .filter(item => item.visible && item.enabled)
                        .sort((a, b) => a.order - b.order)
                        .map(item => {
                            const IconComponent = iconMap[item.icon as keyof typeof iconMap];
                            return (
                                <div
                                    key={item.id}
                                    style={{
                                        padding: '12px 16px',
                                        margin: '4px 0',
                                        borderRadius: '6px',
                                        backgroundColor: '#f5f5f5',
                                        cursor: 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'space-between'
                                    }}
                                >
                                    <Space>
                                        {IconComponent && <IconComponent />}
                                        <span>{item.name}</span>
                                        {item.badge && (
                                            <Tag color={item.badgeColor || 'blue'} size="small">
                                                {item.badge}
                                            </Tag>
                                        )}
                                    </Space>
                                    {item.requireAuth && <LockOutlined style={{ color: '#999' }} />}
                                </div>
                            );
                        })}
                </div>
            </Drawer>

            {/* 导入模态框 */}
            <Modal
                title="导入菜单配置"
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

export default MenuManagement;