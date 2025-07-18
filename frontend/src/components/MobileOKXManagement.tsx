import React, { useEffect, useState } from 'react';
import { Card, Statistic, Tabs, List, Button, Spin } from 'antd';
import { SettingOutlined, ReloadOutlined } from '@ant-design/icons';
import { okxAPI } from '../services/api';

const { TabPane } = Tabs;

const MobileOKXManagement: React.FC = () => {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [balances, setBalances] = useState<any[]>([]);
  const [positions, setPositions] = useState<any[]>([]);
  const [tab, setTab] = useState('balances');

  useEffect(() => {
    okxAPI.getSummary().then(res => setSummary(res.data)).catch(() => {}).finally(() => setLoading(false));
    okxAPI.getStoredBalances().then(res => setBalances(res.data?.data || res.data || [])).catch(() => {});
    okxAPI.getStoredPositions().then(res => setPositions(res.data?.data || res.data || [])).catch(() => {});
  }, []);

  const refresh = () => {
    setLoading(true);
    okxAPI.getSummary().then(res => setSummary(res.data)).finally(() => setLoading(false));
    okxAPI.getStoredBalances().then(res => setBalances(res.data?.data || res.data || []));
    okxAPI.getStoredPositions().then(res => setPositions(res.data?.data || res.data || []));
  };

  return (
    <div style={{ padding: 0 }}>
      <Card
        title={<span><SettingOutlined /> OKX 汇总</span>}
        extra={<Button icon={<ReloadOutlined />} size="small" onClick={refresh} />}
        style={{ marginBottom: 12 }}
        bodyStyle={{ padding: 12 }}
      >
        {loading ? <Spin /> : (
          <>
            <Statistic title="总资产(USDT)" value={summary?.total_usdt || 0} precision={2} />
            <div style={{ fontSize: 12, color: '#888', marginTop: 4 }}>更新时间: {summary?.update_time || '-'}</div>
          </>
        )}
      </Card>
      <Tabs activeKey={tab} onChange={setTab} size="small" style={{ marginBottom: 8 }}>
        <TabPane tab="余额" key="balances" />
        <TabPane tab="持仓" key="positions" />
      </Tabs>
      {tab === 'balances' && (
        <List
          size="small"
          bordered
          dataSource={balances}
          renderItem={item => (
            <List.Item>
              <div style={{ width: '100%' }}>
                <div style={{ fontWeight: 500 }}>{item.currency} <span style={{ color: '#888', fontSize: 12 }}>({item.account_type})</span></div>
                <div style={{ fontSize: 13, color: '#1890ff' }}>{item.balance}</div>
              </div>
            </List.Item>
          )}
        />
      )}
      {tab === 'positions' && (
        <List
          size="small"
          bordered
          dataSource={positions}
          renderItem={item => (
            <List.Item>
              <div style={{ width: '100%' }}>
                <div style={{ fontWeight: 500 }}>{item.instId}</div>
                <div style={{ fontSize: 13, color: '#faad14' }}>数量: {item.pos}</div>
              </div>
            </List.Item>
          )}
        />
      )}
    </div>
  );
};

export default MobileOKXManagement;