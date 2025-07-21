import React, { useEffect, useState, useCallback } from 'react';
import { Card, Statistic, Tabs, List, Button, Spin, Row, Col, Divider, message, Space } from 'antd';
import { BankOutlined, ReloadOutlined, DollarCircleOutlined, SyncOutlined } from '@ant-design/icons';
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
  const [syncing, setSyncing] = useState(false);

  // 从数据库加载数据
  const loadDataFromDB = useCallback(async () => {
    setLoading(true);
    try {
      const [summaryRes, balRes, txRes] = await Promise.all([
        api.get('/wise/summary'),
        api.get('/wise/stored-balances'),
        api.get('/wise/stored-transactions', { params: { limit: 20 } })
      ]);
      
      setSummary(summaryRes.data?.data || summaryRes.data);
      setBalances(balRes.data?.data || balRes.data || []);
      setTransactions(txRes.data?.data || txRes.data || []);
    } catch (error) {
      message.error('加载数据失败');
    } finally {
      setLoading(false);
    }
  }, []);

  // 同步数据到数据库（调用外部API）
  const syncData = async () => {
    setSyncing(true);
    try {
      message.loading('正在同步数据...', 0);
      
      // 并行同步所有数据
      const syncPromises = [
        api.post('/wise/sync-balances'),
        api.post('/wise/sync-transactions')
      ];
      
      await Promise.all(syncPromises);
      
      message.destroy();
      message.success('数据同步成功');
      
      // 同步完成后重新加载数据
      await loadDataFromDB();
    } catch (error) {
      message.destroy();
      message.error('数据同步失败');
      console.error('同步失败:', error);
    } finally {
      setSyncing(false);
    }
  };

  // 总览快速加载（只从数据库）
  useEffect(() => {
    loadDataFromDB();
  }, [loadDataFromDB]);

  // 总资产
  const getTotalWorth = () => {
    if (!summary || !summary.balance_by_currency) return 0;
    return Object.values(summary.balance_by_currency as Record<string, number>).reduce((a: any, b: any) => Number(a) + Number(b), 0);
  };

  return (
    <div style={{ padding: 0 }}>
      <Card
        title={<span><BankOutlined /> Wise 汇总</span>}
        extra={
          <Space>
            <Button 
              icon={<SyncOutlined spin={syncing} />} 
              size="small" 
              onClick={syncData}
              loading={syncing}
              type="primary"
            >
              同步
            </Button>
            <Button 
              icon={<ReloadOutlined />} 
              size="small" 
              onClick={loadDataFromDB}
              disabled={syncing}
            >
              刷新
            </Button>
          </Space>
        }
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