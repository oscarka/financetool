import React, { useEffect, useState, useCallback } from 'react';
import { Card, Statistic, Tabs, List, Button, Spin, Row, Col, Divider } from 'antd';
import { SettingOutlined, ReloadOutlined, DollarCircleOutlined } from '@ant-design/icons';
import { okxAPI } from '../services/api';

const { TabPane } = Tabs;

const MobileOKXManagement: React.FC = () => {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [balances, setBalances] = useState<any[]>([]);
  const [positions, setPositions] = useState<any[]>([]);
  const [web3, setWeb3] = useState<any>(null);
  const [exchangeRates, setExchangeRates] = useState<{ [key: string]: number }>({});
  const [tab, setTab] = useState('trading');

  // 汇率获取
  const fetchExchangeRates = useCallback(async () => {
    try {
      const res = await okxAPI.getStoredMarketData();
      const rates: { [key: string]: number } = {};
      (res.data || []).forEach((item: any) => {
        if (item.inst_id && item.last_price) {
          const currency = item.inst_id.replace('-USDT', '');
          rates[currency] = Number(item.last_price);
        }
      });
      setExchangeRates(rates);
    } catch {}
  }, []);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      okxAPI.getSummary(),
      okxAPI.getStoredBalances(),
      okxAPI.getStoredPositions(),
      okxAPI.getStoredWeb3Balance(),
      fetchExchangeRates()
    ]).then(([summaryRes, balRes, posRes, web3Res]) => {
      setSummary(summaryRes.data);
      setBalances(balRes.data || []);
      setPositions(posRes.data || []);
      setWeb3(web3Res.data || null);
    }).finally(() => setLoading(false));
  }, [fetchExchangeRates]);

  const refresh = () => {
    setLoading(true);
    Promise.all([
      okxAPI.getSummary(),
      okxAPI.getStoredBalances(),
      okxAPI.getStoredPositions(),
      okxAPI.getStoredWeb3Balance(),
      fetchExchangeRates()
    ]).then(([summaryRes, balRes, posRes, web3Res]) => {
      setSummary(summaryRes.data);
      setBalances(balRes.data || []);
      setPositions(posRes.data || []);
      setWeb3(web3Res.data || null);
    }).finally(() => setLoading(false));
  };

  // 余额分组
  const trading = balances.filter(b => b.account_type === 'trading');
  const funding = balances.filter(b => b.account_type === 'funding');
  const savings = balances.filter(b => b.account_type === 'savings');

  // USDT估值
  const calcUSDT = (currency: string, amount: number) => {
    if (currency === 'USDT' || currency === 'USD') return amount;
    const rate = exchangeRates[currency];
    return rate ? amount * rate : 0;
  };

  // OKX总资产（不含Web3）
  const okxTotalUSDT = [trading, funding, savings].flat().reduce((sum, item) => sum + calcUSDT(item.currency, Number(item.total_balance)), 0);

  // 美化列表
  const renderBalanceList = (data: any[]) => (
    <List
      size="small"
      bordered
      dataSource={data.filter(item => calcUSDT(item.currency, Number(item.total_balance)) >= 1)}
      renderItem={item => (
        <List.Item style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', padding: 10 }}>
          <Row style={{ width: '100%' }}>
            <Col flex="auto">
              <span style={{ fontWeight: 600 }}>{item.currency}</span>
              <span style={{ color: '#888', fontSize: 12, marginLeft: 8 }}>({item.account_type})</span>
            </Col>
            <Col>
              <span style={{ color: '#1890ff', fontWeight: 500 }}>{Number(item.total_balance).toFixed(4)}</span>
            </Col>
          </Row>
          <Row style={{ width: '100%', marginTop: 2 }}>
            <Col flex="auto">
              <span style={{ color: '#3f8600', fontSize: 13 }}>≈ ${calcUSDT(item.currency, Number(item.total_balance)).toFixed(2)} USDT</span>
            </Col>
            <Col>
              <span style={{ color: '#aaa', fontSize: 12 }}>{item.update_time ? new Date(item.update_time).toLocaleString() : ''}</span>
            </Col>
          </Row>
        </List.Item>
      )}
    />
  );

  return (
    <div style={{ padding: 0 }}>
      <Card
        title={<span><SettingOutlined /> OKX 账户汇总</span>}
        extra={<Button icon={<ReloadOutlined />} size="small" onClick={refresh} />}
        style={{ marginBottom: 12, borderRadius: 12, boxShadow: '0 2px 8px #f0f1f2' }}
        bodyStyle={{ padding: 12 }}
      >
        {loading ? <Spin /> : (
          <>
            <Row gutter={8}>
              <Col span={12}>
                <Statistic title="总资产(USD)" value={okxTotalUSDT.toFixed(2)} precision={2} valueStyle={{ color: '#3f8600', fontWeight: 700 }} prefix={<DollarCircleOutlined />} />
              </Col>
              <Col span={12}>
                <Statistic title="总资产(CNY)" value={summary?.total_balance_cny?.toFixed(2) || 0} precision={2} valueStyle={{ color: '#3f8600' }} prefix="¥" />
              </Col>
            </Row>
            <Row gutter={8} style={{ marginTop: 8 }}>
              <Col span={12}>
                <Statistic title="24h交易数" value={summary?.transaction_count_24h || 0} valueStyle={{ color: '#722ed1' }} />
              </Col>
              <Col span={12}>
                <Statistic title="持仓数量" value={summary?.position_count || 0} valueStyle={{ color: '#1890ff' }} />
              </Col>
            </Row>
            <Divider style={{ margin: '10px 0' }} />
            <div style={{ fontSize: 12, color: '#888' }}>更新时间: {summary?.update_time || '-'}</div>
          </>
        )}
      </Card>
      <Tabs activeKey={tab} onChange={setTab} size="small" style={{ marginBottom: 8 }}>
        <TabPane tab="交易账户" key="trading" />
        <TabPane tab="资金账户" key="funding" />
        <TabPane tab="储蓄账户" key="savings" />
        <TabPane tab="Web3账户" key="web3" />
        <TabPane tab="持仓" key="positions" />
      </Tabs>
      {tab === 'trading' && renderBalanceList(trading)}
      {tab === 'funding' && renderBalanceList(funding)}
      {tab === 'savings' && renderBalanceList(savings)}
      {tab === 'web3' && (
        <List
          size="small"
          bordered
          dataSource={web3?.tokens || []}
          renderItem={(item: any) => (
            <List.Item style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', padding: 10 }}>
              <Row style={{ width: '100%' }}>
                <Col flex="auto">
                  <span style={{ fontWeight: 600 }}>{item.symbol}</span>
                  <span style={{ color: '#888', fontSize: 12, marginLeft: 8 }}>({item.chain})</span>
                </Col>
                <Col>
                  <span style={{ color: '#faad14', fontWeight: 500 }}>{Number(item.balance).toFixed(4)}</span>
                </Col>
              </Row>
              <Row style={{ width: '100%', marginTop: 2 }}>
                <Col flex="auto">
                  <span style={{ color: '#3f8600', fontSize: 13 }}>≈ ${Number(item.usd_value || 0).toFixed(2)} USD</span>
                </Col>
              </Row>
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
            <List.Item style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', padding: 10 }}>
              <Row style={{ width: '100%' }}>
                <Col flex="auto">
                  <span style={{ fontWeight: 600 }}>{item.instId}</span>
                </Col>
                <Col>
                  <span style={{ color: '#faad14', fontWeight: 500 }}>数量: {item.pos}</span>
                </Col>
              </Row>
            </List.Item>
          )}
        />
      )}
    </div>
  );
};

export default MobileOKXManagement;