import React from 'react';
import { Typography } from 'antd';
import { OKXManagement } from '../components/OKXManagement';
import MobileOKXManagement from '../components/MobileOKXManagement';
import { useDeviceDetection } from '../hooks/useDeviceDetection';

const { Title } = Typography;

export const OKXManagementPage: React.FC = () => {
    const deviceInfo = useDeviceDetection();
    if (deviceInfo.isMobile) {
        return <MobileOKXManagement />;
    }
    return (
        <div style={{ padding: '24px' }}>
            <Title level={2}>OKX 接口管理</Title>
            <OKXManagement />
        </div>
    );
}; 