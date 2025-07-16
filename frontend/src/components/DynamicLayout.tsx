import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Layout as AntLayout, Menu, Spin, Alert } from 'antd';
import { menuAPI } from '../services/menuAPI';
import type { MenuItem, MenuConfig } from './MenuManagement';

const { Sider, Content } = AntLayout;

// 图标映射
const iconMap: Record<string, any> = {
    HomeOutlined: require('@ant-design/icons').HomeOutlined,
    PlusCircleOutlined: require('@ant-design/icons').PlusCircleOutlined,
    BarChartOutlined: require('@ant-design/icons').BarChartOutlined,
    DollarOutlined: require('@ant-design/icons').DollarOutlined,
    PieChartOutlined: require('@ant-design/icons').PieChartOutlined,
    SettingOutlined: require('@ant-design/icons').SettingOutlined,
    GlobalOutlined: require('@ant-design/icons').GlobalOutlined,
    BankOutlined: require('@ant-design/icons').BankOutlined,
    PayCircleOutlined: require('@ant-design/icons').PayCircleOutlined,
    StockOutlined: require('@ant-design/icons').StockOutlined,
    ToolOutlined: require('@ant-design/icons').ToolOutlined,
    ClockCircleOutlined: require('@ant-design/icons').ClockCircleOutlined,
    UserOutlined: require('@ant-design/icons').UserOutlined,
    TeamOutlined: require('@ant-design/icons').TeamOutlined,
    SafetyOutlined: require('@ant-design/icons').SafetyOutlined,
    MenuOutlined: require('@ant-design/icons').MenuOutlined,
    LinkOutlined: require('@ant-design/icons').LinkOutlined
};

interface DynamicLayoutProps {
    children: React.ReactNode;
}

const DynamicLayout: React.FC<DynamicLayoutProps> = ({ children }) => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [menuConfig, setMenuConfig] = useState<MenuConfig | null>(null);
    const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
    const location = useLocation();

    // 加载菜单配置
    useEffect(() => {
        loadMenuConfig();
    }, []);

    const loadMenuConfig = async () => {
        try {
            setLoading(true);
            setError(null);

            // 尝试获取激活的菜单配置
            const activeConfigResponse = await menuAPI.getActiveMenuConfig();
            
            if (activeConfigResponse.success && activeConfigResponse.data) {
                setMenuConfig(activeConfigResponse.data);
                setMenuItems(activeConfigResponse.data.items || []);
            } else {
                // 如果没有激活的配置，使用默认配置
                await loadDefaultMenuConfig();
            }
        } catch (err) {
            console.error('加载菜单配置失败:', err);
            setError('加载菜单配置失败，使用默认配置');
            await loadDefaultMenuConfig();
        } finally {
            setLoading(false);
        }
    };

    const loadDefaultMenuConfig = async () => {
        // 默认菜单配置
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
            },
            {
                id: 'menu',
                name: '菜单管理',
                href: '/menu',
                icon: 'MenuOutlined',
                order: 13,
                visible: true,
                enabled: true,
                requireAuth: true,
                permissions: ['menu:manage'],
                description: '菜单配置管理',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            }
        ];

        setMenuItems(defaultItems);
        setMenuConfig({
            id: 'default',
            name: '默认菜单',
            description: '系统默认菜单配置',
            items: defaultItems,
            isDefault: true,
            isActive: true,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        });
    };

    // 检查用户权限（简化版本）
    const hasPermission = (permissions: string[]): boolean => {
        // 这里应该根据实际的用户权限系统来实现
        // 目前简化处理，假设用户有所有权限
        return true;
    };

    // 过滤菜单项
    const filteredMenuItems = menuItems
        .filter(item => item.visible && item.enabled)
        .filter(item => !item.requireAuth || hasPermission(item.permissions))
        .sort((a, b) => a.order - b.order);

    // 生成菜单项
    const menuItemsForAntd = filteredMenuItems.map((item) => {
        const IconComponent = iconMap[item.icon];
        return {
            key: item.href,
            icon: IconComponent ? React.createElement(IconComponent) : null,
            label: (
                <Link to={item.href}>
                    {item.name}
                    {item.badge && (
                        <span style={{ 
                            marginLeft: '8px',
                            backgroundColor: item.badgeColor || '#1890ff',
                            color: 'white',
                            padding: '2px 6px',
                            borderRadius: '10px',
                            fontSize: '12px'
                        }}>
                            {item.badge}
                        </span>
                    )}
                </Link>
            ),
        };
    });

    if (loading) {
        return (
            <div style={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center', 
                height: '100vh' 
            }}>
                <Spin size="large" tip="加载菜单配置中..." />
            </div>
        );
    }

    return (
        <AntLayout style={{ minHeight: '100vh' }}>
            <Sider
                width={256}
                style={{
                    background: '#fff',
                    borderRight: '1px solid #f0f0f0',
                }}
                breakpoint="lg"
                collapsedWidth="0"
            >
                <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0' }}>
                    <h1 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: '#262626' }}>
                        {menuConfig?.name || '个人财务管理系统'}
                    </h1>
                    {menuConfig?.description && (
                        <p style={{ margin: '4px 0 0 0', fontSize: '12px', color: '#666' }}>
                            {menuConfig.description}
                        </p>
                    )}
                </div>
                
                {error && (
                    <Alert
                        message="配置加载警告"
                        description={error}
                        type="warning"
                        showIcon
                        style={{ margin: '8px' }}
                    />
                )}

                <Menu
                    mode="inline"
                    selectedKeys={[location.pathname]}
                    style={{ height: '100%', borderRight: 0 }}
                    items={menuItemsForAntd}
                />
            </Sider>
            <AntLayout>
                <Content style={{ margin: '24px 16px', padding: 24, background: '#f5f5f5' }}>
                    {children}
                </Content>
            </AntLayout>
        </AntLayout>
    );
};

export default DynamicLayout;