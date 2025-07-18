import React, { useEffect, useState } from 'react';
import { Card, Statistic, Tabs, List, Button, Spin, Row, Col, Divider } from 'antd';
import { BankOutlined, ReloadOutlined, DollarCircleOutlined } from '@ant-design/icons';
import api from '../services/api';

const { TabPane } = Tabs;

const formatCurrency = (amount: number, currency: string) => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
};
const formatDate = (dateString: string) => new Date(dateString).toLocaleString('zh-CN');

const MobileWiseManagement: React.FC = () => {
  const [summary, setSummary] = useState<any>(null);
  const [balances, setBalances] = useState<any[]>([]);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [tab, setTab] = useState('balances');
  const [loading, setLoading] = useState(true);

  // 总览快速加载（只从数据库）
  useEffect(() => {
    api.get('/wise/summary').then(res => {
      setSummary(res.data?.data || res.data);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  // 下方数据加载
  useEffect(() => {
    api.get('/wise/stored-balances').then(res => {
      setBalances(res.data?.data || res.data || []);
    }).catch(() => {});
    api.get('/wise/stored-transactions', { params: { limit: 20 } }).then(res => {
      setTransactions(res.data?.data || res.data || []);
    }).catch(() => {});
  }, []);

  const refresh = () => {
    setLoading(true);
    Promise.all([
      api.get('/wise/summary'),
      api.get('/wise/stored-balances'),
      api.get('/wise/stored-transactions', { params: { limit: 20 } })
    ]).then(([summaryRes, balRes, txRes]) => {
      setSummary(summaryRes.data?.data || summaryRes.data);
      setBalances(balRes.data?.data || balRes.data || []);
      setTransactions(txRes.data?.data || txRes.data || []);
    }).finally(() => setLoading(false));
  };

  // 总资产
  const getTotalWorth = () => {
    if (!summary || !summary.balance_by_currency) return 0;
    return Object.values(summary.balance_by_currency as Record<string, number>).reduce((a: any, b: any) => Number(a) + Number(b), 0);
  };

  return (
    <div style={{ padding: 0 }}>
      <Card
        title={<span><BankOutlined /> Wise 汇总</span>}
        extra={<Button icon={<ReloadOutlined />} size="small" onClick={refresh} />}
        style={{ marginBottom: 12, borderRadius: 12, boxShadow: '0 2px 8px #f0f1f2' }}
        bodyStyle={{ padding: 12 }}
      >
        {loading ? <Spin /> : (
          <>
            <Row gutter={8}>
              <Col span={12}>
                <Statistic title="总账户数" value={summary?.total_accounts || 0} valueStyle={{ color: '#3f8600', fontWeight: 700 }} prefix={<BankOutlined />} />
              </Col>
              <Col span={12}>
                <Statistic title="支持货币" value={summary?.total_currencies || 0} valueStyle={{ color: '#1890ff' }} prefix={<DollarCircleOutlined />} />
              </Col>
            </Row>
            <Row gutter={8} style={{ marginTop: 8 }}>
              <Col span={12}>
                <Statistic title="总资产(本币)" value={getTotalWorth().toFixed(2)} valueStyle={{ color: '#3f8600' }} prefix="$" />
              </Col>
              <Col span={12}>
                <Statistic title="最近交易数" value={summary?.recent_transactions_count || 0} valueStyle={{ color: '#722ed1' }} />
              </Col>
            </Row>
            <Divider style={{ margin: '10px 0' }} />
            <div style={{ fontSize: 12, color: '#888' }}>更新时间: {summary?.update_time || '-'}</div>
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
            <List.Item style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', padding: 10 }}>
              <Row style={{ width: '100%' }}>
                <Col flex="auto">
                  <span style={{ fontWeight: 600 }}>{item.currency}</span>
                  <span style={{ color: '#888', fontSize: 12, marginLeft: 8 }}>{item.account_id}</span>
                </Col>
                <Col>
                  <span style={{ color: '#1890ff', fontWeight: 500 }}>{formatCurrency(item.available_balance, item.currency)}</span>
                </Col>
              </Row>
              <Row style={{ width: '100%', marginTop: 2 }}>
                <Col flex="auto">
                  <span style={{ color: '#3f8600', fontSize: 13 }}>总价值: {formatCurrency(item.total_worth, item.currency)}</span>
                </Col>
                <Col>
                  <span style={{ color: '#aaa', fontSize: 12 }}>{item.update_time ? formatDate(item.update_time) : ''}</span>
                </Col>
              </Row>
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
            <List.Item style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', padding: 10 }}>
              <Row style={{ width: '100%' }}>
                <Col flex="auto">
                  <span style={{ fontWeight: 600 }}>{item.type}</span>
                  <span style={{ color: '#888', fontSize: 12, marginLeft: 8 }}>{item.currency}</span>
                </Col>
                <Col>
                  <span style={{ color: item.type === 'credit' ? '#3f8600' : '#cf1322', fontWeight: 500 }}>{formatCurrency(item.amount, item.currency)}</span>
                </Col>
              </Row>
              <Row style={{ width: '100%', marginTop: 2 }}>
                <Col flex="auto">
                  <span style={{ color: '#888', fontSize: 12 }}>{item.description || ''}</span>
                </Col>
                <Col>
                  <span style={{ color: '#aaa', fontSize: 12 }}>{item.date ? formatDate(item.date) : ''}</span>
                </Col>
              </Row>
            </List.Item>
          )}
        />
      )}
    </div>
  );
};

export default MobileWiseManagement;