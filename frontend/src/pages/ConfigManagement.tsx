import React from 'react';
import ConfigManagement from '../components/ConfigManagement';

const ConfigManagementPage: React.FC = () => {
    React.useEffect(() => {
        console.log('[调试] ConfigManagementPage 组件挂载', Date.now());
        return () => {
            console.log('[调试] ConfigManagementPage 组件卸载', Date.now());
        };
    }, []);
    return <ConfigManagement />;
};

export default ConfigManagementPage; 