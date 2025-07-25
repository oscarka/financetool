import React, { useEffect, useState, useCallback } from 'react';
import { Card, Statistic, Tabs, List, Button, Spin, Row, Col, Divider, message, Space } from 'antd';
import { SettingOutlined, ReloadOutlined, DollarCircleOutlined, SyncOutlined } from '@ant-design/icons';
import { okxAPI } from '../services/api';

const { TabPane } = Tabs;

const MobileOKXManagement: React.FC = () => {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
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

  // 从数据库加载数据
  const loadDataFromDB = useCallback(async () => {
    setLoading(true);
    try {
      const [summaryRes, balRes, posRes, web3Res] = await Promise.all([
        okxAPI.getSummary(),
        okxAPI.getStoredBalances(),
        okxAPI.getStoredPositions(),
        okxAPI.getStoredWeb3Balance(),
        fetchExchangeRates()
      ]);
      
      setSummary(summaryRes.data);
      setBalances(balRes.data || []);
      setPositions(posRes.data || []);
      setWeb3(web3Res.data || null);
    } catch (error) {
      message.error('加载数据失败');
    } finally {
      setLoading(false);
    }
  }, [fetchExchangeRates]);

  // 同步数据到数据库（调用外部API）
  const syncData = async () => {
    setSyncing(true);
    try {
      message.loading('正在同步数据...', 0);
      
      // 并行同步所有数据
      const syncPromises = [
        okxAPI.syncBalances(),
        okxAPI.syncPositions(),
        okxAPI.syncMarketData(),
        okxAPI.syncWeb3Balance()
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

  useEffect(() => {
    loadDataFromDB();
  }, [loadDataFromDB]);

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
        <div>
          {web3 ? (
            <Card style={{ marginBottom: 12 }}>
              <Row gutter={16}>
                <Col span={12}>
                  <Statistic
                    title="Web3账户总价值"
                    value={web3.total_value || 0}
                    precision={2}
                    valueStyle={{ color: '#3f8600', fontSize: '18px' }}
                    suffix="USD"
                  />
                  <div style={{ marginTop: '4px', color: '#666', fontSize: '12px' }}>
                    货币: {web3.currency || 'USD'}
                  </div>
                </Col>
                <Col span={12}>
                  <div style={{ fontSize: '14px', color: '#666', marginTop: '8px' }}>
                    <div>最后更新:</div>
                    <div>{web3.update_time ? new Date(web3.update_time).toLocaleString() : '未知'}</div>
                    <div style={{ marginTop: '4px' }}>来源: {web3.source || '未知'}</div>
                  </div>
                </Col>
              </Row>
            </Card>
          ) : (
            <div style={{ textAlign: 'center', padding: '20px', color: '#888' }}>暂无Web3数据</div>
          )}
        </div>
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