import React from 'react';
import WiseManagement from '../components/WiseManagement';
import MobileWiseManagement from '../components/MobileWiseManagement';
import { useDeviceDetection } from '../hooks/useDeviceDetection';

const WiseManagementPage: React.FC = () => {
    const deviceInfo = useDeviceDetection();
    if (deviceInfo.isMobile) {
        return <MobileWiseManagement />;
    }
    return (
        <div className="container mx-auto px-4 py-8">
            <WiseManagement />
        </div>
    );
};

export default WiseManagementPage; 