import React, { useState, useEffect, useRef } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Select,
  InputNumber,
  message,
  Tag,
  Descriptions,
  Row,
  Col,
  Popconfirm,
  Tooltip,
  Badge,
  Alert,
  Divider,
  Statistic
} from 'antd';
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  DeleteOutlined,
  PlusOutlined,
  ReloadOutlined,
  ClockCircleOutlined,
  SettingOutlined,
  CopyOutlined
} from '@ant-design/icons';
import { schedulerAPI } from '../services/schedulerAPI';
import type { TaskDefinition, ScheduledJob, JobConfig } from '../services/schedulerAPI';

const { Option } = Select;
const { TextArea } = Input;

// 解析cron表达式为易读格式
const parseCronToReadable = (cronExpression: string): string => {
  if (!cronExpression) return '无';

  try {
    // 处理cron[month='*', day='*', day_of_week='*', hour='*/4', minute='0']格式
    if (cronExpression.includes('cron[')) {
      return parseCronObjectToReadable(cronExpression);
    }

    // 处理标准cron表达式格式
    const parts = cronExpression.split(' ');
    if (parts.length >= 5) {
      const [minute, hour, day, month, dayOfWeek] = parts;
      return parseCronPartsToReadable(minute, hour, day, month, dayOfWeek);
    }

    return cronExpression;
  } catch (error) {
    return cronExpression;
  }
};

// 解析cron对象格式
const parseCronObjectToReadable = (cronObject: string): string => {
  try {
    // 提取cron对象中的参数
    const hourMatch = cronObject.match(/hour='([^']+)'/);
    const minuteMatch = cronObject.match(/minute='([^']+)'/);
    const dayOfWeekMatch = cronObject.match(/day_of_week='([^']+)'/);
    const dayMatch = cronObject.match(/day='([^']+)'/);
    const monthMatch = cronObject.match(/month='([^']+)'/);

    const hour = hourMatch ? hourMatch[1] : '*';
    const minute = minuteMatch ? minuteMatch[1] : '0';
    const dayOfWeek = dayOfWeekMatch ? dayOfWeekMatch[1] : '*';
    const day = dayMatch ? dayMatch[1] : '*';
    const month = monthMatch ? monthMatch[1] : '*';

    return parseCronPartsToReadable(minute, hour, day, month, dayOfWeek);
  } catch (error) {
    return cronObject;
  }
};

// 解析cron各部分为易读格式
const parseCronPartsToReadable = (minute: string, hour: string, day: string, _month: string, dayOfWeek: string): string => {
  const timeStr = `${hour.padStart(2, '0')}:${minute.padStart(2, '0')}`;

  // 处理间隔执行
  if (hour.includes('*/')) {
    const interval = hour.replace('*/', '');
    return `每${interval}小时执行一次`;
  }

  if (minute.includes('*/')) {
    const interval = minute.replace('*/', '');
    return `每${interval}分钟执行一次`;
  }

  // 处理工作日
  if (dayOfWeek === '1-5' || dayOfWeek === 'mon-fri') {
    return `工作日 ${timeStr}`;
  }

  // 处理特定星期
  if (dayOfWeek !== '*' && dayOfWeek !== '?') {
    const weekMap: { [key: string]: string } = {
      '0': '周日', '1': '周一', '2': '周二', '3': '周三', '4': '周四', '5': '周五', '6': '周六',
      'sun': '周日', 'mon': '周一', 'tue': '周二', 'wed': '周三', 'thu': '周四', 'fri': '周五', 'sat': '周六'
    };

    if (dayOfWeek.includes(',')) {
      const days = dayOfWeek.split(',').map(d => weekMap[d] || d);
      return `${days.join('、')} ${timeStr}`;
    } else {
      return `${weekMap[dayOfWeek] || dayOfWeek} ${timeStr}`;
    }
  }

  // 处理特定日期
  if (day !== '*' && day !== '?') {
    if (day.includes(',')) {
      const days = day.split(',').map(d => `${d}号`);
      return `每月${days.join('、')} ${timeStr}`;
    } else {
      return `每月${day}号 ${timeStr}`;
    }
  }

  // 默认每天执行
  return `每天 ${timeStr}`;
};

// 预设任务配置模板
const TASK_TEMPLATES = {
  'fund_nav_update': {
    name: '基金净值更新',
    description: '更新基金净值数据',
    config: {},
    schedule: {
      type: 'cron',
      hour: 23,
      minute: 0,
      frequency: 'daily'
    }
  },
  'dca_execute': {
    name: '定投计划执行',
    description: '执行到期的定投计划',
    config: {},
    schedule: {
      type: 'cron',
      hour: 10,
      minute: 0,
      frequency: 'weekly',
      day_of_week: 'mon-fri'
    }
  },
  'crypto_exchange_rate_cache': {
    name: '数字货币汇率缓存',
    description: '更新数字货币汇率数据',
    config: {},
    schedule: {
      type: 'cron',
      hour: 0,
      minute: 0,
      frequency: 'interval',
      interval_hours: 4
    }
  },
  'wise_balance_sync': {
    name: 'Wise余额同步',
    description: '同步Wise账户余额',
    config: {},
    schedule: {
      type: 'cron',
      hour: 18,
      minute: 0,
      frequency: 'daily'
    }
  }
};

// 常用时间预设
const TIME_PRESETS = [
  { label: '每天凌晨2点', value: { hour: 2, minute: 0, frequency: 'daily' } },
  { label: '每天上午9点', value: { hour: 9, minute: 0, frequency: 'daily' } },
  { label: '每天下午6点', value: { hour: 18, minute: 0, frequency: 'daily' } },
  { label: '每天晚上11点', value: { hour: 23, minute: 0, frequency: 'daily' } },
  { label: '工作日早上10点', value: { hour: 10, minute: 0, frequency: 'weekly', day_of_week: 'mon-fri' } },
  { label: '每周一早上9点', value: { hour: 9, minute: 0, frequency: 'weekly', day_of_week: 'mon' } },
  { label: '每月1号早上8点', value: { hour: 8, minute: 0, frequency: 'monthly', day: 1 } },
  { label: '每4小时执行', value: { frequency: 'interval', interval_hours: 4 } },
  { label: '每30分钟执行', value: { frequency: 'interval', interval_minutes: 30 } }
];

const SchedulerManagement: React.FC = () => {
  // 状态管理
  const tasksJsonRef = useRef<HTMLDivElement>(null);

  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<any>(null);
  const [tasks, setTasks] = useState<TaskDefinition[]>([]);
  const [jobs, setJobs] = useState<ScheduledJob[]>([]);
  const [plugins, setPlugins] = useState<any[]>([]);

  // 模态框状态
  const [createJobModalVisible, setCreateJobModalVisible] = useState(false);
  const [executeTaskModalVisible, setExecuteTaskModalVisible] = useState(false);
  const [selectedTask, setSelectedTask] = useState<TaskDefinition | null>(null);

  // 表单状态
  const [createJobForm] = Form.useForm();
  const [executeTaskForm] = Form.useForm();

  // 初始化加载
  useEffect(() => {
    if (tasksJsonRef.current) {
      tasksJsonRef.current.innerText = 'tasks: ' + JSON.stringify(tasks);
    }
  }, [tasks]);
  useEffect(() => {
    loadData();
  }, []);

  // 加载所有数据
  const loadData = async () => {
    setLoading(true);
    try {
      const [statusData, tasksData, jobsData, pluginsData] = await Promise.all([
        schedulerAPI.getStatus(),
        schedulerAPI.getTasks(),
        schedulerAPI.getJobs(),
        schedulerAPI.getPlugins()
      ]);

      setStatus(statusData || {});
      const rawTasks = (tasksData as any).tasks;

      try {
        for (let i = 0; i < (rawTasks && rawTasks.length); i++) {
        }
      } catch (e) {
      }
      // setTasks
      let arr = [];
      try {
        arr = JSON.parse(JSON.stringify(rawTasks));
      } catch (e) {
        arr = [];
      }
      setTasks(arr);

      setJobs(Array.isArray(jobsData) ? jobsData : []);
      setPlugins(Array.isArray((pluginsData as any).plugins) ? (pluginsData as any).plugins : []);
    } catch (error) {
      message.error('加载调度器数据失败');
      // setTasks([]);
      // setJobs([]);
      // setPlugins([]);
      console.error('加载数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 应用任务模板
  const applyTaskTemplate = (taskId: string) => {
    const template = TASK_TEMPLATES[taskId as keyof typeof TASK_TEMPLATES];
    if (template) {
      const formData: any = {
        task_id: taskId,
        name: template.name,
        schedule_type: 'cron',
        cron_frequency: template.schedule.frequency,
        cron_hour: template.schedule.hour,
        cron_minute: template.schedule.minute,
        config: JSON.stringify(template.config, null, 2)
      };

      // 安全地添加可选字段
      if ('day_of_week' in template.schedule) {
        formData.cron_day_of_week = template.schedule.day_of_week;
      }
      if ('day' in template.schedule) {
        formData.cron_day = template.schedule.day;
      }

      createJobForm.setFieldsValue(formData);
      message.success('已应用任务模板');
    }
  };

  // 应用时间预设
  const applyTimePreset = (preset: any) => {
    if (preset.frequency === 'interval') {
      createJobForm.setFieldsValue({
        schedule_type: 'interval',
        interval_hours: preset.interval_hours,
        interval_minutes: preset.interval_minutes
      });
    } else {
      createJobForm.setFieldsValue({
        schedule_type: 'cron',
        cron_frequency: preset.frequency,
        cron_hour: preset.hour,
        cron_minute: preset.minute,
        cron_day_of_week: preset.day_of_week,
        cron_day: preset.day
      });
    }
    message.success('已应用时间预设');
  };

  // 复制Cron表达式
  const copyCronExpression = () => {
    const values = createJobForm.getFieldsValue();
    let cronExpression = '';

    if (values.schedule_type === 'cron') {
      const { cron_frequency, cron_hour, cron_minute, cron_day_of_week, cron_day } = values;

      if (cron_frequency === 'daily') {
        cronExpression = `${cron_minute} ${cron_hour} * * *`;
      } else if (cron_frequency === 'weekly') {
        cronExpression = `${cron_minute} ${cron_hour} * * ${cron_day_of_week}`;
      } else if (cron_frequency === 'monthly') {
        cronExpression = `${cron_minute} ${cron_hour} ${cron_day} * *`;
      }
    } else if (values.schedule_type === 'interval') {
      const { interval_hours, interval_minutes } = values;
      if (interval_hours) {
        cronExpression = `0 */${interval_hours} * * *`;
      } else if (interval_minutes) {
        cronExpression = `*/${interval_minutes} * * * *`;
      }
    }

    if (cronExpression) {
      navigator.clipboard.writeText(cronExpression);
      message.success('Cron表达式已复制到剪贴板');
    }
  };

  // 创建定时任务
  const handleCreateJob = async (values: any) => {
    try {
      console.log('创建任务表单数据:', values); // 调试日志

      let scheduleConfig: any = {
        type: values.schedule_type
      };

      if (values.schedule_type === 'interval') {
        scheduleConfig = {
          ...scheduleConfig,
          minutes: values.interval_minutes || 0,
          seconds: values.interval_seconds || 0,
          hours: values.interval_hours || 0
        };
      } else if (values.schedule_type === 'cron') {
        // 基础cron配置
        scheduleConfig = {
          ...scheduleConfig,
          hour: values.cron_hour,
          minute: values.cron_minute
        };

        // 根据频率类型添加相应配置
        if (values.cron_frequency === 'weekly') {
          scheduleConfig.day_of_week = values.cron_day_of_week;
        } else if (values.cron_frequency === 'monthly') {
          scheduleConfig.day = values.cron_day;
        } else if (values.cron_frequency === 'custom') {
          // 自定义模式：只添加有值的字段
          if (values.cron_day) {
            scheduleConfig.day = values.cron_day;
          }
          if (values.cron_day_of_week) {
            scheduleConfig.day_of_week = values.cron_day_of_week;
          }
        }
        // daily模式不需要额外配置，默认每天执行
      }

      const jobConfig: JobConfig = {
        task_id: values.task_id,
        name: values.name,
        schedule: scheduleConfig,
        config: values.config ? JSON.parse(values.config) : {}
      };

      console.log('发送的任务配置:', jobConfig); // 调试日志

      await schedulerAPI.createJob(jobConfig);
      message.success('定时任务创建成功');
      setCreateJobModalVisible(false);
      createJobForm.resetFields();
      loadData();
    } catch (error: any) {
      console.error('创建任务失败详情:', error); // 详细错误日志
      message.error(`创建定时任务失败: ${error?.message || error}`);
    }
  };

  // 立即执行任务
  const handleExecuteTask = async (values: any) => {
    if (!selectedTask) return;

    try {
      const config = values.config ? JSON.parse(values.config) : {};
      const result = await schedulerAPI.executeTask(selectedTask.task_id, config);

      if (result.success) {
        message.success('任务执行成功');
      } else {
        message.error(`任务执行失败: ${result.error}`);
      }

      setExecuteTaskModalVisible(false);
      executeTaskForm.resetFields();
      setSelectedTask(null);
    } catch (error) {
      message.error('执行任务失败');
      console.error('执行任务失败:', error);
    }
  };

  // 移除任务
  const handleRemoveJob = async (jobId: string) => {
    try {
      await schedulerAPI.removeJob(jobId);
      message.success('任务移除成功');
      loadData();
    } catch (error) {
      message.error('移除任务失败');
      console.error('移除任务失败:', error);
    }
  };

  // 暂停/恢复任务
  const handleToggleJob = async (job: ScheduledJob, action: 'pause' | 'resume') => {
    try {
      if (action === 'pause') {
        await schedulerAPI.pauseJob(job.job_id);
        message.success('任务已暂停');
      } else {
        await schedulerAPI.resumeJob(job.job_id);
        message.success('任务已恢复');
      }
      loadData();
    } catch (error) {
      message.error(`${action === 'pause' ? '暂停' : '恢复'}任务失败`);
      console.error('操作任务失败:', error);
    }
  };

  // 表格列定义
  const jobColumns = [
    {
      title: '任务ID',
      dataIndex: 'job_id',
      key: 'job_id',
      width: 120,
    },
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (name: string, record: ScheduledJob) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{name}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>
            {record.job_id}
          </div>
        </div>
      ),
    },
    {
      title: '下次执行时间',
      dataIndex: 'next_run_time',
      key: 'next_run_time',
      width: 180,
      render: (time: string) => time ? new Date(time).toLocaleString() : '无',
    },
    {
      title: '状态',
      dataIndex: 'state',
      key: 'state',
      width: 100,
      render: (state: string) => {
        const statusMap: { [key: string]: { text: string; color: string } } = {
          'running': { text: '运行中', color: '#52c41a' },
          'paused': { text: '已暂停', color: '#faad14' },
          'stopped': { text: '已停止', color: '#ff4d4f' },
          'error': { text: '错误', color: '#ff4d4f' }
        };

        const status = statusMap[state] || { text: state || '未知', color: '#666' };

        return (
          <Tag color={status.color}>
            {status.text}
          </Tag>
        );
      },
    },
    {
      title: '执行计划',
      dataIndex: 'trigger',
      key: 'trigger',
      width: 250,
      render: (trigger: string) => {
        if (!trigger) return '无';

        try {
          // 解析cron表达式并转换为易读格式
          const readableSchedule = parseCronToReadable(trigger);
          return (
            <Tooltip title={`原始表达式: ${trigger}`}>
              <span>{readableSchedule}</span>
            </Tooltip>
          );
        } catch (error) {
          return trigger;
        }
      },
    },
    {
      title: '操作',
      key: 'actions',
      width: 180,
      render: (_: any, record: ScheduledJob) => (
        <Space size="small">
          {record.state && record.state === 'running' ? (
            <Tooltip title="暂停任务">
              <Button
                type="text"
                size="small"
                icon={<PauseCircleOutlined />}
                onClick={() => handleToggleJob(record, 'pause')}
              />
            </Tooltip>
          ) : (
            <Tooltip title="启动任务">
              <Button
                type="text"
                size="small"
                icon={<PlayCircleOutlined />}
                onClick={() => handleToggleJob(record, 'resume')}
              />
            </Tooltip>
          )}
          <Tooltip title="立即执行">
            <Button
              type="text"
              size="small"
              icon={<ClockCircleOutlined />}
              onClick={() => handleExecuteTask({ task_id: record.job_id })}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个任务吗？"
            description="删除后无法恢复"
            onConfirm={() => handleRemoveJob(record.job_id)}
          >
            <Button type="text" size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const taskColumns = [
    {
      title: '任务ID',
      dataIndex: 'task_id',
      key: 'task_id',
      width: 120,
    },
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
      width: 150,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      width: 200,
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_: any, record: TaskDefinition) => (
        <Space size="small">
          <Button
            type="primary"
            size="small"
            onClick={() => {
              setSelectedTask(record);
              setExecuteTaskModalVisible(true);
            }}
          >
            立即执行
          </Button>
          {TASK_TEMPLATES[record.task_id as keyof typeof TASK_TEMPLATES] && (
            <Button
              size="small"
              onClick={() => applyTaskTemplate(record.task_id)}
            >
              应用模板
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={[16, 16]}>
        {/* 调度器状态 */}
        <Col span={24}>
          <Card title="调度器状态" extra={
            <Button icon={<ReloadOutlined />} onClick={loadData} loading={loading}>
              刷新
            </Button>
          }>
            {status && (
              <Descriptions bordered column={4}>
                <Descriptions.Item label="运行状态">
                  <Badge
                    status={status.scheduler_running ? 'success' : 'error'}
                    text={status.scheduler_running ? '运行中' : '已停止'}
                  />
                </Descriptions.Item>
                <Descriptions.Item label="任务数量">{status.job_count}</Descriptions.Item>
                <Descriptions.Item label="插件数量">{status.plugin_count}</Descriptions.Item>
                <Descriptions.Item label="任务定义数量">{status.task_count}</Descriptions.Item>
                <Descriptions.Item label="最后更新时间" span={4}>
                  {status.timestamp && new Date(status.timestamp).toLocaleString()}
                </Descriptions.Item>
              </Descriptions>
            )}
          </Card>
        </Col>

        {/* 任务统计 */}
        <Col span={24}>
          <Card title="任务统计">
            <Row gutter={16}>
              <Col span={6}>
                <Statistic
                  title="总任务数"
                  value={jobs.length}
                  prefix={<SettingOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="运行中"
                  value={jobs.filter(job => job.state && job.state === 'running').length}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="已暂停"
                  value={jobs.filter(job => job.state && job.state === 'paused').length}
                  valueStyle={{ color: '#faad14' }}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="错误状态"
                  value={jobs.filter(job => job.state && job.state === 'error').length}
                  valueStyle={{ color: '#ff4d4f' }}
                />
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 定时任务管理 */}
        <Col span={24}>
          <Card
            title="定时任务管理"
            extra={
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setCreateJobModalVisible(true)}
              >
                创建任务
              </Button>
            }
          >
            <div style={{ marginBottom: 16 }}>
              <Space>
                <Button
                  icon={<PlayCircleOutlined />}
                  onClick={() => {
                    jobs.forEach(job => {
                      if (!job.state || job.state !== 'running') {
                        handleToggleJob(job, 'resume');
                      }
                    });
                  }}
                >
                  启动所有任务
                </Button>
                <Button
                  icon={<PauseCircleOutlined />}
                  onClick={() => {
                    jobs.forEach(job => {
                      if (job.state && job.state === 'running') {
                        handleToggleJob(job, 'pause');
                      }
                    });
                  }}
                >
                  暂停所有任务
                </Button>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={loadData}
                >
                  刷新数据
                </Button>
              </Space>
            </div>
            <Table
              dataSource={jobs}
              columns={jobColumns}
              rowKey="job_id"
              loading={loading}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>

        {/* 可用任务定义 */}
        <Col span={24}>
          <Card title="可用任务定义">
            <Table
              dataSource={tasks}
              columns={taskColumns}
              rowKey="task_id"
              loading={loading}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>

        {/* 插件信息 */}
        <Col span={24}>
          <Card title="已加载插件">
            <Row gutter={[16, 16]}>
              {plugins.map((plugin, index) => (
                <Col key={index} span={8}>
                  <Card size="small">
                    <Descriptions column={1} size="small">
                      <Descriptions.Item label="插件名称">{plugin.name}</Descriptions.Item>
                      <Descriptions.Item label="版本">{plugin.version}</Descriptions.Item>
                      <Descriptions.Item label="状态">
                        <Tag color="green">已加载</Tag>
                      </Descriptions.Item>
                    </Descriptions>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
      </Row>

      {/* 创建定时任务模态框 */}
      <Modal
        title="创建定时任务"
        open={createJobModalVisible}
        onCancel={() => setCreateJobModalVisible(false)}
        footer={null}
        width={800}
      >
        <Form
          form={createJobForm}
          layout="vertical"
          onFinish={handleCreateJob}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="task_id"
                label="选择任务"
                rules={[{ required: true, message: '请选择任务' }]}
              >
                <Select
                  placeholder="请选择要执行的任务"
                  onChange={(value) => {
                    // 自动应用模板
                    if (TASK_TEMPLATES[value as keyof typeof TASK_TEMPLATES]) {
                      applyTaskTemplate(value);
                    }
                  }}
                >
                  {tasks.map(task => (
                    <Option key={task.task_id} value={task.task_id}>
                      {task.name} ({task.task_id})
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="name"
                label="任务名称"
                rules={[{ required: true, message: '请输入任务名称' }]}
              >
                <Input placeholder="请输入任务名称" />
              </Form.Item>
            </Col>
          </Row>

          <Divider orientation="left">
            <Space>
              <ClockCircleOutlined />
              时间配置
            </Space>
          </Divider>

          <Form.Item
            name="schedule_type"
            label="调度类型"
            rules={[{ required: true, message: '请选择调度类型' }]}
          >
            <Select placeholder="请选择调度类型">
              <Option value="interval">间隔执行</Option>
              <Option value="cron">定时执行</Option>
            </Select>
          </Form.Item>

          {/* 时间预设 */}
          <Form.Item label="常用时间预设">
            <Space wrap>
              {TIME_PRESETS.map((preset, index) => (
                <Button
                  key={index}
                  size="small"
                  onClick={() => applyTimePreset(preset.value)}
                >
                  {preset.label}
                </Button>
              ))}
            </Space>
          </Form.Item>

          <Form.Item noStyle shouldUpdate>
            {({ getFieldValue }) => {
              const scheduleType = getFieldValue('schedule_type');

              if (scheduleType === 'interval') {
                return (
                  <Row gutter={16}>
                    <Col span={8}>
                      <Form.Item
                        name="interval_hours"
                        label="小时间隔"
                      >
                        <InputNumber min={0} max={23} style={{ width: '100%' }} placeholder="0-23" />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item
                        name="interval_minutes"
                        label="分钟间隔"
                      >
                        <InputNumber min={0} max={59} style={{ width: '100%' }} placeholder="0-59" />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item
                        name="interval_seconds"
                        label="秒间隔"
                      >
                        <InputNumber min={0} max={59} style={{ width: '100%' }} placeholder="0-59" />
                      </Form.Item>
                    </Col>
                  </Row>
                );
              }

              if (scheduleType === 'cron') {
                return (
                  <>
                    <Form.Item
                      name="cron_frequency"
                      label="执行频率"
                      rules={[{ required: true, message: '请选择执行频率' }]}
                    >
                      <Select placeholder="选择执行频率">
                        <Option value="daily">每天</Option>
                        <Option value="weekly">每周</Option>
                        <Option value="monthly">每月</Option>
                        <Option value="custom">自定义</Option>
                      </Select>
                    </Form.Item>

                    <Form.Item noStyle shouldUpdate>
                      {({ getFieldValue }) => {
                        const cronFrequency = getFieldValue('cron_frequency');

                        if (cronFrequency === 'daily') {
                          return (
                            <Row gutter={16}>
                              <Col span={12}>
                                <Form.Item
                                  name="cron_hour"
                                  label="小时"
                                  rules={[{ required: true, message: '请输入小时' }]}
                                >
                                  <InputNumber min={0} max={23} style={{ width: '100%' }} />
                                </Form.Item>
                              </Col>
                              <Col span={12}>
                                <Form.Item
                                  name="cron_minute"
                                  label="分钟"
                                  rules={[{ required: true, message: '请输入分钟' }]}
                                >
                                  <InputNumber min={0} max={59} style={{ width: '100%' }} />
                                </Form.Item>
                              </Col>
                            </Row>
                          );
                        }

                        if (cronFrequency === 'weekly') {
                          return (
                            <Row gutter={16}>
                              <Col span={8}>
                                <Form.Item
                                  name="cron_day_of_week"
                                  label="星期几"
                                  rules={[{ required: true, message: '请选择星期' }]}
                                >
                                  <Select placeholder="选择星期">
                                    <Option value="mon">星期一</Option>
                                    <Option value="tue">星期二</Option>
                                    <Option value="wed">星期三</Option>
                                    <Option value="thu">星期四</Option>
                                    <Option value="fri">星期五</Option>
                                    <Option value="sat">星期六</Option>
                                    <Option value="sun">星期日</Option>
                                    <Option value="mon-fri">工作日</Option>
                                  </Select>
                                </Form.Item>
                              </Col>
                              <Col span={8}>
                                <Form.Item
                                  name="cron_hour"
                                  label="小时"
                                  rules={[{ required: true, message: '请输入小时' }]}
                                >
                                  <InputNumber min={0} max={23} style={{ width: '100%' }} />
                                </Form.Item>
                              </Col>
                              <Col span={8}>
                                <Form.Item
                                  name="cron_minute"
                                  label="分钟"
                                  rules={[{ required: true, message: '请输入分钟' }]}
                                >
                                  <InputNumber min={0} max={59} style={{ width: '100%' }} />
                                </Form.Item>
                              </Col>
                            </Row>
                          );
                        }

                        if (cronFrequency === 'monthly') {
                          return (
                            <Row gutter={16}>
                              <Col span={8}>
                                <Form.Item
                                  name="cron_day"
                                  label="日期"
                                  rules={[{ required: true, message: '请输入日期' }]}
                                >
                                  <InputNumber min={1} max={31} style={{ width: '100%' }} />
                                </Form.Item>
                              </Col>
                              <Col span={8}>
                                <Form.Item
                                  name="cron_hour"
                                  label="小时"
                                  rules={[{ required: true, message: '请输入小时' }]}
                                >
                                  <InputNumber min={0} max={23} style={{ width: '100%' }} />
                                </Form.Item>
                              </Col>
                              <Col span={8}>
                                <Form.Item
                                  name="cron_minute"
                                  label="分钟"
                                  rules={[{ required: true, message: '请输入分钟' }]}
                                >
                                  <InputNumber min={0} max={59} style={{ width: '100%' }} />
                                </Form.Item>
                              </Col>
                            </Row>
                          );
                        }

                        if (cronFrequency === 'custom') {
                          return (
                            <Row gutter={16}>
                              <Col span={6}>
                                <Form.Item
                                  name="cron_day"
                                  label="日期"
                                >
                                  <InputNumber min={1} max={31} style={{ width: '100%' }} placeholder="1-31" />
                                </Form.Item>
                              </Col>
                              <Col span={6}>
                                <Form.Item
                                  name="cron_day_of_week"
                                  label="星期"
                                >
                                  <Select placeholder="选择星期" allowClear>
                                    <Option value="mon">星期一</Option>
                                    <Option value="tue">星期二</Option>
                                    <Option value="wed">星期三</Option>
                                    <Option value="thu">星期四</Option>
                                    <Option value="fri">星期五</Option>
                                    <Option value="sat">星期六</Option>
                                    <Option value="sun">星期日</Option>
                                  </Select>
                                </Form.Item>
                              </Col>
                              <Col span={6}>
                                <Form.Item
                                  name="cron_hour"
                                  label="小时"
                                  rules={[{ required: true, message: '请输入小时' }]}
                                >
                                  <InputNumber min={0} max={23} style={{ width: '100%' }} />
                                </Form.Item>
                              </Col>
                              <Col span={6}>
                                <Form.Item
                                  name="cron_minute"
                                  label="分钟"
                                  rules={[{ required: true, message: '请输入分钟' }]}
                                >
                                  <InputNumber min={0} max={59} style={{ width: '100%' }} />
                                </Form.Item>
                              </Col>
                            </Row>
                          );
                        }

                        return null;
                      }}
                    </Form.Item>
                  </>
                );
              }

              return null;
            }}
          </Form.Item>

          <Divider orientation="left">
            <Space>
              <SettingOutlined />
              任务配置
            </Space>
          </Divider>

          <Alert
            message="配置说明"
            description={
              <div>
                <p>• 基金净值更新：通常配置为每天执行，无需额外参数</p>
                <p>• 定投执行：通常配置为工作日执行，无需额外参数</p>
                <p>• 数字货币汇率：通常配置为每4小时执行，无需额外参数</p>
                <p>• 其他任务：根据具体需求配置参数</p>
              </div>
            }
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />

          <Form.Item
            name="config"
            label={
              <Space>
                任务配置 (JSON)
                <Tooltip title="点击复制Cron表达式">
                  <Button
                    type="text"
                    size="small"
                    icon={<CopyOutlined />}
                    onClick={copyCronExpression}
                  />
                </Tooltip>
              </Space>
            }
          >
            <TextArea
              rows={4}
              placeholder='{"key": "value"} 或留空使用默认配置'
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                创建任务
              </Button>
              <Button onClick={() => setCreateJobModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 立即执行任务模态框 */}
      <Modal
        title={`立即执行任务: ${selectedTask?.name}`}
        open={executeTaskModalVisible}
        onCancel={() => setExecuteTaskModalVisible(false)}
        footer={null}
        width={600}
      >
        <Alert
          message="执行说明"
          description="立即执行任务会忽略定时配置，直接执行一次。可以传入自定义参数。"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />

        <Form
          form={executeTaskForm}
          layout="vertical"
          onFinish={handleExecuteTask}
        >
          <Form.Item
            name="config"
            label="任务配置 (JSON)"
          >
            <TextArea
              rows={4}
              placeholder='{"key": "value"} 或留空使用默认配置'
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                执行任务
              </Button>
              <Button onClick={() => setExecuteTaskModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default SchedulerManagement; 