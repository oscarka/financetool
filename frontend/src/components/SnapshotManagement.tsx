import React, { useState } from 'react';
import { Card, Button, Space, message, Alert } from 'antd';
import { ReloadOutlined, CameraOutlined } from '@ant-design/icons';
import { snapshotAPI } from '../services/api';

const SnapshotManagement: React.FC = () => {
    const [assetLoading, setAssetLoading] = useState(false);
    const [rateLoading, setRateLoading] = useState(false);

    // 手动触发资产快照
    const handleExtractAssetSnapshot = async () => {
        setAssetLoading(true);
        try {
            const response = await snapshotAPI.extractAssetSnapshot();
            if (response.success) {
                message.success(`资产快照提取成功: ${response.message}`);
            } else {
                message.error(`资产快照提取失败: ${response.message}`);
            }
        } catch (error) {
            console.error('资产快照提取失败:', error);
            message.error('资产快照提取失败，请检查网络连接');
        } finally {
            setAssetLoading(false);
        }
    };

    // 手动触发汇率快照
    const handleExtractExchangeRateSnapshot = async () => {
        setRateLoading(true);
        try {
            const response = await snapshotAPI.extractExchangeRateSnapshot();
            if (response.success) {
                message.success(`汇率快照提取成功: ${response.message}`);
            } else {
                message.error(`汇率快照提取失败: ${response.message}`);
            }
        } catch (error) {
            console.error('汇率快照提取失败:', error);
            message.error('汇率快照提取失败，请检查网络连接');
        } finally {
            setRateLoading(false);
        }
    };

    return (
        <Card title="快照管理" size="small">
            <Alert
                message="快照说明"
                description="资产快照和汇率快照会定时自动生成。您也可以手动触发快照来获取最新数据。快照数据用于趋势分析和历史记录。"
                type="info"
                showIcon
                style={{ marginBottom: 16 }}
            />
            
            <Space direction="vertical" style={{ width: '100%' }}>
                <Button
                    type="primary"
                    icon={<CameraOutlined />}
                    loading={assetLoading}
                    onClick={handleExtractAssetSnapshot}
                    block
                >
                    手动触发资产快照
                </Button>
                
                <Button
                    type="default"
                    icon={<CameraOutlined />}
                    loading={rateLoading}
                    onClick={handleExtractExchangeRateSnapshot}
                    block
                >
                    手动触发汇率快照
                </Button>
            </Space>
        </Card>
    );
};

export default SnapshotManagement;