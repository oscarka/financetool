import React, { useEffect, useState } from 'react';
import { Card, Statistic, Tabs, List, Button, Spin } from 'antd';
import { BankOutlined, ReloadOutlined } from '@ant-design/icons';
import api from '../services/api';

const { TabPane } = Tabs;

const MobileWiseManagement: React.FC = () => {
  const [summary, setSummary] = useState<any>(null);
  const [balances, setBalances] = useState<any[]>([]);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [tab, setTab] = useState('balances');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/wise/summary').then(res => setSummary(res.data?.data || res.data)).catch(() => {});
    api.get('/wise/stored-balances').then(res => setBalances(res.data?.data || res.data || [])).catch(() => {});
    api.get('/wise/stored-transactions', { params: { limit: 20 } }).then(res => setTransactions(res.data?.data || res.data || [])).catch(() => {});
    setLoading(false);
  }, []);

  const refresh = () => {
    setLoading(true);
    api.get('/wise/summary').then(res => setSummary(res.data?.data || res.data)).finally(() => setLoading(false));
    api.get('/wise/stored-balances').then(res => setBalances(res.data?.data || res.data || []));
    api.get('/wise/stored-transactions', { params: { limit: 20 } }).then(res => setTransactions(res.data?.data || res.data || []));
  };

  return (
    <div style={{ padding: 0 }}>
      <Card
        title={<span><BankOutlined /> Wise 汇总</span>}
        extra={<Button icon={<ReloadOutlined />} size="small" onClick={refresh} />}
        style={{ marginBottom: 12 }}
        bodyStyle={{ padding: 12 }}
      >
        {loading ? <Spin /> : (
          <>
            <Statistic title="总资产(本币)" value={summary?.total_worth || 0} precision={2} />
            <div style={{ fontSize: 12, color: '#888', marginTop: 4 }}>更新时间: {summary?.update_time || '-'}</div>
          </>
        )}
      </Card>
      <Tabs activeKey={tab} onChange={setTab} size="small" style={{ marginBottom: 8 }}>
        <TabPane tab="余额" key="balances" />
        <TabPane tab="交易" key="transactions" />
      </Tabs>
      {tab === 'balances' && (
        <List
          size="small"
          bordered
          dataSource={balances}
          renderItem={item => (
            <List.Item>
              <div style={{ width: '100%' }}>
                <div style={{ fontWeight: 500 }}>{item.currency}</div>
                <div style={{ fontSize: 13, color: '#1890ff' }}>{item.amount}</div>
              </div>
            </List.Item>
          )}
        />
      )}
      {tab === 'transactions' && (
        <List
          size="small"
          bordered
          dataSource={transactions}
          renderItem={item => (
            <List.Item>
              <div style={{ width: '100%' }}>
                <div style={{ fontWeight: 500 }}>{item.type} - {item.currency}</div>
                <div style={{ fontSize: 13, color: '#faad14' }}>金额: {item.amount}</div>
                <div style={{ fontSize: 12, color: '#888' }}>{item.date}</div>
              </div>
            </List.Item>
          )}
        />
      )}
    </div>
  );
};

export default MobileWiseManagement;