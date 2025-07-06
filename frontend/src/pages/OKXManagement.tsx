import React from 'react';
import { Typography } from 'antd';
import { OKXManagement } from '../components/OKXManagement';

const { Title } = Typography;

export const OKXManagementPage: React.FC = () => {
    return (
        <div style={{ padding: '24px' }}>
            <Title level={2}>OKX 接口管理</Title>
            <OKXManagement />
        </div>
    );
}; 