import React from 'react';
import { Typography } from 'antd';
import { Web3WalletManagement } from '../components/Web3WalletManagement';
import { useDeviceDetection } from '../hooks/useDeviceDetection';

const { Title } = Typography;

export const Web3WalletsPage: React.FC = () => {
    const deviceInfo = useDeviceDetection();
    
    if (deviceInfo.isMobile) {
        // 暂时使用桌面版组件，后续可以创建移动端专用组件
        return <Web3WalletManagement />;
    }
    
    return (
        <div style={{ padding: '24px' }}>
            <Title level={2}>Web3 钱包管理</Title>
            <Web3WalletManagement />
        </div>
    );
};