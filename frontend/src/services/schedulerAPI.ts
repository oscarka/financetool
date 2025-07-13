import api from './api';

// 调度器状态接口
export interface SchedulerStatus {
  scheduler_running: boolean;
  job_count: number;
  plugin_count: number;
  task_count: number;
  timestamp: string;
}

// 任务定义接口
export interface TaskDefinition {
  task_id: string;
  name: string;
  description: string;
  config_schema?: any;
}

// 定时任务接口
export interface ScheduledJob {
  job_id: string;
  name: string;
  next_run_time: string | null;
  trigger: string;
}

// 任务配置接口
export interface JobConfig {
  job_id?: string;
  task_id: string;
  name?: string;
  schedule: {
    type: 'cron' | 'interval' | 'date';
    [key: string]: any;
  };
  config?: Record<string, any>;
}

// 任务执行结果接口
export interface TaskResult {
  success: boolean;
  error?: string;
  data?: any;
  execution_id: string;
}

/**
 * 调度器API服务
 */
export class SchedulerAPI {
  /**
   * 获取调度器状态
   */
  async getStatus(): Promise<SchedulerStatus> {
    const response = await api.get('/scheduler/status');
    return response.data.data;
  }

  /**
   * 获取所有插件
   */
  async getPlugins(): Promise<any[]> {
    const response = await api.get('/scheduler/plugins');
    return response && response.data ? response.data : [];
  }

  /**
   * 获取所有任务定义
   */
  async getTasks(): Promise<TaskDefinition[]> {
    const response = await api.get('/scheduler/tasks');
    // 直接返回data字段
    return response && response.data ? response.data : [];
  }

  /**
   * 获取所有定时任务
   */
  async getJobs(): Promise<ScheduledJob[]> {
    const response = await api.get('/scheduler/jobs');
    // 兼容 jobs 字段和直接数组两种情况
    if (response && response.data) {
      if (Array.isArray(response.data)) {
        return response.data;
      } else if (Array.isArray(response.data.jobs)) {
        return response.data.jobs;
      }
    }
    return [];
  }

  /**
   * 创建定时任务
   */
  async createJob(jobConfig: JobConfig): Promise<{ job_id: string }> {
    const response = await api.post('/scheduler/jobs', jobConfig);
    return response.data.data;
  }

  /**
   * 立即执行任务
   */
  async executeTask(taskId: string, config?: Record<string, any>): Promise<TaskResult> {
    const response = await api.post(`/scheduler/jobs/${taskId}/execute`, { config });
    return response.data.data;
  }

  /**
   * 移除定时任务
   */
  async removeJob(jobId: string): Promise<boolean> {
    const response = await api.delete(`/scheduler/jobs/${jobId}`);
    return !!(response.data && response.data.success);
  }

  /**
   * 暂停定时任务
   */
  async pauseJob(jobId: string): Promise<boolean> {
    const response = await api.post(`/scheduler/jobs/${jobId}/pause`);
    return !!(response.data && response.data.success);
  }

  /**
   * 恢复定时任务
   */
  async resumeJob(jobId: string): Promise<boolean> {
    const response = await api.post(`/scheduler/jobs/${jobId}/resume`);
    return !!(response.data && response.data.success);
  }

  /**
   * 获取事件历史
   */
  async getEvents(eventType?: string, limit: number = 100): Promise<any[]> {
    const params = new URLSearchParams();
    if (eventType) params.append('event_type', eventType);
    params.append('limit', limit.toString());
    
    const response = await api.get(`/scheduler/events?${params.toString()}`);
    return response.data.data;
  }

  /**
   * 初始化调度器
   */
  async initialize(): Promise<boolean> {
    const response = await api.post('/scheduler/initialize');
    return response.data.success;
  }

  /**
   * 关闭调度器
   */
  async shutdown(): Promise<boolean> {
    const response = await api.post('/scheduler/shutdown');
    return response.data.success;
  }
}

// 导出单例实例
export const schedulerAPI = new SchedulerAPI(); 