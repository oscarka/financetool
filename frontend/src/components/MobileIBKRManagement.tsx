import React, { useEffect, useState } from 'react';
import { Card, Statistic, Tabs, List, Button, Spin } from 'antd';
import { StockOutlined, ReloadOutlined } from '@ant-design/icons';
import { ibkrAPI } from '../services/api';

const { TabPane } = Tabs;

const MobileIBKRManagement: React.FC = () => {
  const [summary, setSummary] = useState<any>(null);
  const [balances, setBalances] = useState<any[]>([]);
  const [positions, setPositions] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [tab, setTab] = useState('balances');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    ibkrAPI.getSummary().then(res => setSummary(res.data?.data || res.data)).catch(() => {});
    ibkrAPI.getBalances().then(res => setBalances(res.data || [])).catch(() => {});
    ibkrAPI.getPositions().then(res => setPositions(res.data || [])).catch(() => {});
    ibkrAPI.getLogs({ limit: 10 }).then(res => setLogs(res.data || [])).catch(() => {});
    setLoading(false);
  }, []);

  const refresh = () => {
    setLoading(true);
    ibkrAPI.getSummary().then(res => setSummary(res.data?.data || res.data)).finally(() => setLoading(false));
    ibkrAPI.getBalances().then(res => setBalances(res.data || []));
    ibkrAPI.getPositions().then(res => setPositions(res.data || []));
    ibkrAPI.getLogs({ limit: 10 }).then(res => setLogs(res.data || []));
  };

  return (
    <div style={{ padding: 0 }}>
      <Card
        title={<span><StockOutlined /> IBKR 汇总</span>}
        extra={<Button icon={<ReloadOutlined />} size="small" onClick={refresh} />}
        style={{ marginBottom: 12 }}
        bodyStyle={{ padding: 12 }}
      >
        {loading ? <Spin /> : (
          <>
            <Statistic title="净清算价值(USD)" value={summary?.total_net_liquidation || 0} precision={2} />
            <div style={{ fontSize: 12, color: '#888', marginTop: 4 }}>更新时间: {summary?.update_time || '-'}</div>
          </>
        )}
      </Card>
      <Tabs activeKey={tab} onChange={setTab} size="small" style={{ marginBottom: 8 }}>
        <TabPane tab="余额" key="balances" />
        <TabPane tab="持仓" key="positions" />
        <TabPane tab="日志" key="logs" />
      </Tabs>
      {tab === 'balances' && (
        <List
          size="small"
          bordered
          dataSource={balances}
          renderItem={item => (
            <List.Item>
              <div style={{ width: '100%' }}>
                <div style={{ fontWeight: 500 }}>{item.account_id}</div>
                <div style={{ fontSize: 13, color: '#1890ff' }}>现金: {item.total_cash}</div>
                <div style={{ fontSize: 12, color: '#888' }}>净清算: {item.net_liquidation}</div>
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
                <div style={{ fontWeight: 500 }}>{item.symbol}</div>
                <div style={{ fontSize: 13, color: '#faad14' }}>数量: {item.quantity}</div>
                <div style={{ fontSize: 12, color: '#888' }}>市值: {item.market_value}</div>
              </div>
            </List.Item>
          )}
        />
      )}
      {tab === 'logs' && (
        <List
          size="small"
          bordered
          dataSource={logs}
          renderItem={item => (
            <List.Item>
              <div style={{ width: '100%' }}>
                <div style={{ fontWeight: 500 }}>{item.status}</div>
                <div style={{ fontSize: 12, color: '#888' }}>{item.message}</div>
                <div style={{ fontSize: 12, color: '#aaa' }}>{item.timestamp}</div>
              </div>
            </List.Item>
          )}
        />
      )}
    </div>
  );
};

export default MobileIBKRManagement;