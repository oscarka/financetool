import React from 'react'
import { Card, Row, Col } from 'antd'
import { 
    SearchOutlined, 
    PlusCircleOutlined, 
    BarChartOutlined, 
    LineChartOutlined,
    DollarOutlined,
    CalendarOutlined,
    RightOutlined
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

const MobileFunds: React.FC = () => {
    const navigate = useNavigate()

    const fundModules = [
        {
            title: '基金搜索',
            description: '搜索和添加基金信息',
            icon: SearchOutlined,
            color: '#1890ff',
            path: '/funds/search',
            isComingSoon: false
        },
        {
            title: '操作记录',
            description: '查看基金买卖记录',
            icon: PlusCircleOutlined,
            color: '#52c41a',
            path: '/operations',
            isComingSoon: false
        },
        {
            title: '持仓管理',
            description: '查看基金持仓情况',
            icon: BarChartOutlined,
            color: '#faad14',
            path: '/positions',
            isComingSoon: false
        },
        {
            title: '收益分析',
            description: '分析投资收益表现',
            icon: LineChartOutlined,
            color: '#722ed1',
            path: '/funds/analysis',
            isComingSoon: false
        },
        {
            title: '净值管理',
            description: '管理基金净值数据',
            icon: DollarOutlined,
            color: '#fa541c',
            path: '/funds/nav',
            isComingSoon: false
        },
        {
            title: '定投计划',
            description: '设置和管理定投计划',
            icon: CalendarOutlined,
            color: '#13c2c2',
            path: '/funds/dca',
            isComingSoon: false
        }
    ]

    const handleModuleClick = (module: any) => {
        if (module.isComingSoon) {
            // TODO: 显示敬请期待提示
            return
        }
        navigate(module.path)
    }

    return (
        <div style={{ paddingBottom: '20px' }}>
            {/* 页面标题 */}
            <Card 
                bordered={false}
                style={{ marginBottom: 16 }}
                bodyStyle={{ padding: '16px' }}
            >
                <div>
                    <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>基金管理</h2>
                    <p style={{ margin: '4px 0 0 0', fontSize: '12px', color: '#666' }}>
                        管理基金投资、净值同步和定投计划
                    </p>
                </div>
            </Card>

            {/* 功能模块网格 */}
            <div style={{ padding: '0 16px' }}>
                <Row gutter={[12, 12]}>
                    {fundModules.map((module, index) => {
                        const IconComponent = module.icon
                        return (
                            <Col span={12} key={index}>
                                <Card
                                    hoverable
                                    style={{ 
                                        height: '120px',
                                        cursor: 'pointer',
                                        border: `1px solid ${module.color}20`,
                                        background: `${module.color}05`
                                    }}
                                    bodyStyle={{ 
                                        padding: '16px 12px',
                                        height: '100%',
                                        display: 'flex',
                                        flexDirection: 'column',
                                        justifyContent: 'center',
                                        alignItems: 'center',
                                        textAlign: 'center'
                                    }}
                                    onClick={() => handleModuleClick(module)}
                                >
                                    <div style={{
                                        width: '40px',
                                        height: '40px',
                                        borderRadius: '50%',
                                        background: module.color,
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        marginBottom: '8px'
                                    }}>
                                        <IconComponent style={{ color: 'white', fontSize: '18px' }} />
                                    </div>
                                    
                                    <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '4px' }}>
                                        {module.title}
                                    </div>
                                    
                                    <div style={{ 
                                        fontSize: '11px', 
                                        color: '#666', 
                                        lineHeight: '1.2',
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis',
                                        display: '-webkit-box',
                                        WebkitLineClamp: 2,
                                        WebkitBoxOrient: 'vertical'
                                    }}>
                                        {module.description}
                                    </div>
                                    
                                    {module.isComingSoon && (
                                        <div style={{
                                            position: 'absolute',
                                            top: '8px',
                                            right: '8px',
                                            background: '#faad14',
                                            color: 'white',
                                            fontSize: '10px',
                                            padding: '2px 6px',
                                            borderRadius: '8px'
                                        }}>
                                            敬请期待
                                        </div>
                                    )}
                                </Card>
                            </Col>
                        )
                    })}
                </Row>
            </div>

            {/* 快速入口 */}
            <Card 
                title="快速入口"
                bordered={false}
                style={{ margin: '16px 16px 0 16px' }}
                bodyStyle={{ padding: '16px' }}
            >
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div 
                        style={{ 
                            display: 'flex', 
                            justifyContent: 'space-between', 
                            alignItems: 'center',
                            padding: '12px',
                            background: '#f6ffed',
                            borderRadius: '8px',
                            border: '1px solid #b7eb8f',
                            cursor: 'pointer'
                        }}
                        onClick={() => navigate('/operations')}
                    >
                        <div>
                            <div style={{ fontWeight: 'bold', color: '#52c41a', marginBottom: '2px' }}>
                                记录新操作
                            </div>
                            <div style={{ fontSize: '12px', color: '#666' }}>
                                快速记录买入、卖出操作
                            </div>
                        </div>
                        <RightOutlined style={{ color: '#52c41a' }} />
                    </div>

                    <div 
                        style={{ 
                            display: 'flex', 
                            justifyContent: 'space-between', 
                            alignItems: 'center',
                            padding: '12px',
                            background: '#f0f5ff',
                            borderRadius: '8px',
                            border: '1px solid #adc6ff',
                            cursor: 'pointer'
                        }}
                        onClick={() => navigate('/positions')}
                    >
                        <div>
                            <div style={{ fontWeight: 'bold', color: '#1890ff', marginBottom: '2px' }}>
                                查看持仓
                            </div>
                            <div style={{ fontSize: '12px', color: '#666' }}>
                                查看当前持仓和收益
                            </div>
                        </div>
                        <RightOutlined style={{ color: '#1890ff' }} />
                    </div>

                    <div 
                        style={{ 
                            display: 'flex', 
                            justifyContent: 'space-between', 
                            alignItems: 'center',
                            padding: '12px',
                            background: '#fff7e6',
                            borderRadius: '8px',
                            border: '1px solid #ffd591',
                            cursor: 'pointer'
                        }}
                        onClick={() => navigate('/analysis')}
                    >
                        <div>
                            <div style={{ fontWeight: 'bold', color: '#faad14', marginBottom: '2px' }}>
                                收益分析
                            </div>
                            <div style={{ fontSize: '12px', color: '#666' }}>
                                分析投资收益和趋势
                            </div>
                        </div>
                        <RightOutlined style={{ color: '#faad14' }} />
                    </div>
                </div>
            </Card>
        </div>
    )
}

export default MobileFunds