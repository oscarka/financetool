import React from 'react';
import IBKRManagement from '../components/IBKRManagement';
import MobileIBKRManagement from '../components/MobileIBKRManagement';
import { useDeviceDetection } from '../hooks/useDeviceDetection';

const IBKRManagementPage: React.FC = () => {
    const deviceInfo = useDeviceDetection();
    if (deviceInfo.isMobile) {
        return <MobileIBKRManagement />;
    }
    return (
        <div style={{ padding: '0 24px' }}>
            <IBKRManagement />
        </div>
    );
};

export default IBKRManagementPage;