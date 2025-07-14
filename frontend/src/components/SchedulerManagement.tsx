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
  Badge
} from 'antd';
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  DeleteOutlined,
  PlusOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { schedulerAPI } from '../services/schedulerAPI';
import type { TaskDefinition, ScheduledJob, JobConfig } from '../services/schedulerAPI';


const { Option } = Select;
const { TextArea } = Input;



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
          minutes: values.interval_minutes,
          seconds: values.interval_seconds
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
      width: 150,
    },
    {
      title: '下次执行时间',
      dataIndex: 'next_run_time',
      key: 'next_run_time',
      width: 180,
      render: (time: string) => time ? new Date(time).toLocaleString() : '无',
    },
    {
      title: '触发器',
      dataIndex: 'trigger',
      key: 'trigger',
      width: 200,
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_: any, record: ScheduledJob) => (
        <Space size="small">
          <Tooltip title="暂停任务">
            <Button
              type="text"
              icon={<PauseCircleOutlined />}
              onClick={() => handleToggleJob(record, 'pause')}
            />
          </Tooltip>
          <Tooltip title="恢复任务">
            <Button
              type="text"
              icon={<PlayCircleOutlined />}
              onClick={() => handleToggleJob(record, 'resume')}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个任务吗？"
            onConfirm={() => handleRemoveJob(record.job_id)}
          >
            <Button type="text" danger icon={<DeleteOutlined />} />
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
      width: 120,
      render: (_: any, record: TaskDefinition) => (
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
            <div style={{ fontSize: 12, color: '#888', marginBottom: 8 }}>
              jobs: {JSON.stringify(jobs)}
            </div>
            <Table
              dataSource={jobs}
              columns={jobColumns}
              rowKey="job_id"
              loading={loading}
              pagination={false}
              size="small"
            />
            <div ref={tasksJsonRef} style={{ fontSize: 12, color: '#888', marginTop: 8 }}></div>
          </Card>
        </Col>

        {/* 可用任务定义 */}
        <Col span={24}>
          <Card title="可用任务定义">
            <div style={{ fontSize: 12, color: '#888', marginBottom: 8 }}>
              tasks: {JSON.stringify(tasks)}
            </div>
            <div style={{ fontSize: 12, color: '#f00', marginBottom: 8 }}>
              [Table渲染前] typeof tasks: {typeof tasks}, Array.isArray: {Array.isArray(tasks).toString()}, length: {tasks.length}, first: {tasks[0] && JSON.stringify(tasks[0])}
            </div>
            {/* 原有Table */}
            <Table
              dataSource={tasks}
              columns={taskColumns}
              rowKey="task_id"
              loading={loading}
              pagination={false}
              size="small"
            />
            <div style={{ fontSize: 12, color: '#f00', marginTop: 8 }}>
              [Table渲染后] typeof tasks: {typeof tasks}, Array.isArray: {Array.isArray(tasks).toString()}, length: {tasks.length}, first: {tasks[0] && JSON.stringify(tasks[0])}
            </div>
          </Card>
        </Col>

        {/* 插件信息 */}
        <Col span={24}>
          <Card title="已加载插件">
            <div style={{ fontSize: 12, color: '#888', marginBottom: 8 }}>
              plugins: {JSON.stringify(plugins)}
            </div>
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
        width={600}
      >
        <Form
          form={createJobForm}
          layout="vertical"
          onFinish={handleCreateJob}
        >
          <Form.Item
            name="task_id"
            label="选择任务"
            rules={[{ required: true, message: '请选择任务' }]}
          >
            <Select placeholder="请选择要执行的任务">
              {tasks.map(task => (
                <Option key={task.task_id} value={task.task_id}>
                  {task.name} ({task.task_id})
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="name"
            label="任务名称"
            rules={[{ required: true, message: '请输入任务名称' }]}
          >
            <Input placeholder="请输入任务名称" />
          </Form.Item>

          <Form.Item
            name="schedule_type"
            label="调度类型"
            rules={[{ required: true, message: '请选择调度类型' }]}
          >
            <Select placeholder="请选择调度类型">
              <Option value="interval">间隔执行</Option>
              <Option value="cron">Cron表达式</Option>
            </Select>
          </Form.Item>

          <Form.Item noStyle shouldUpdate>
            {({ getFieldValue }) => {
              const scheduleType = getFieldValue('schedule_type');

              if (scheduleType === 'interval') {
                return (
                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item
                        name="interval_minutes"
                        label="分钟间隔"
                        rules={[{ required: true, message: '请输入分钟间隔' }]}
                      >
                        <InputNumber min={1} max={59} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item
                        name="interval_seconds"
                        label="秒间隔"
                      >
                        <InputNumber min={0} max={59} style={{ width: '100%' }} />
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

          <Form.Item
            name="config"
            label="任务配置 (JSON)"
          >
            <TextArea
              rows={4}
              placeholder='{"key": "value"}'
            />
          </Form.Item>

          {/* 调试信息 */}
          <Form.Item label="调试信息">
            <div style={{ fontSize: 12, color: '#666', backgroundColor: '#f5f5f5', padding: 8, borderRadius: 4 }}>
              <div><strong>当前表单数据：</strong></div>
              <pre style={{ margin: 0, fontSize: 10 }}>
                {JSON.stringify(createJobForm.getFieldsValue(), null, 2)}
              </pre>
            </div>
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
        width={500}
      >
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
              placeholder='{"key": "value"}'
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