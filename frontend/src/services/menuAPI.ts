import api from './api';
import type { MenuItem, MenuConfig } from '../components/MenuManagement';

export interface MenuAPIResponse<T = any> {
    success: boolean;
    data: T;
    message?: string;
    error?: string;
}

class MenuAPI {
    /**
     * 获取所有菜单配置
     */
    async getMenuConfigs(): Promise<MenuAPIResponse<MenuConfig[]>> {
        try {
            const response = await api.get('/menu/configs');
            return response.data;
        } catch (error: any) {
            console.error('获取菜单配置失败:', error);
            return {
                success: false,
                data: [],
                error: error.response?.data?.detail || error.message
            };
        }
    }

    /**
     * 获取当前激活的菜单配置
     */
    async getActiveMenuConfig(): Promise<MenuAPIResponse<MenuConfig>> {
        try {
            const response = await api.get('/menu/active');
            return response.data;
        } catch (error: any) {
            console.error('获取激活菜单配置失败:', error);
            return {
                success: false,
                data: {} as MenuConfig,
                error: error.response?.data?.detail || error.message
            };
        }
    }

    /**
     * 创建菜单配置
     */
    async createMenuConfig(config: Partial<MenuConfig>): Promise<MenuAPIResponse<MenuConfig>> {
        try {
            const response = await api.post('/menu/configs', config);
            return response.data;
        } catch (error: any) {
            console.error('创建菜单配置失败:', error);
            return {
                success: false,
                data: {} as MenuConfig,
                error: error.response?.data?.detail || error.message
            };
        }
    }

    /**
     * 更新菜单配置
     */
    async updateMenuConfig(configId: string, config: Partial<MenuConfig>): Promise<MenuAPIResponse<MenuConfig>> {
        try {
            const response = await api.put(`/menu/configs/${configId}`, config);
            return response.data;
        } catch (error: any) {
            console.error('更新菜单配置失败:', error);
            return {
                success: false,
                data: {} as MenuConfig,
                error: error.response?.data?.detail || error.message
            };
        }
    }

    /**
     * 删除菜单配置
     */
    async deleteMenuConfig(configId: string): Promise<MenuAPIResponse<boolean>> {
        try {
            const response = await api.delete(`/menu/configs/${configId}`);
            return response.data;
        } catch (error: any) {
            console.error('删除菜单配置失败:', error);
            return {
                success: false,
                data: false,
                error: error.response?.data?.detail || error.message
            };
        }
    }

    /**
     * 激活菜单配置
     */
    async activateMenuConfig(configId: string): Promise<MenuAPIResponse<boolean>> {
        try {
            const response = await api.post(`/menu/configs/${configId}/activate`);
            return response.data;
        } catch (error: any) {
            console.error('激活菜单配置失败:', error);
            return {
                success: false,
                data: false,
                error: error.response?.data?.detail || error.message
            };
        }
    }

    /**
     * 获取菜单项列表
     */
    async getMenuItems(configId?: string): Promise<MenuAPIResponse<MenuItem[]>> {
        try {
            const url = configId ? `/menu/configs/${configId}/items` : '/menu/items';
            const response = await api.get(url);
            return response.data;
        } catch (error: any) {
            console.error('获取菜单项失败:', error);
            return {
                success: false,
                data: [],
                error: error.response?.data?.detail || error.message
            };
        }
    }

    /**
     * 创建菜单项
     */
    async createMenuItem(item: Partial<MenuItem>, configId?: string): Promise<MenuAPIResponse<MenuItem>> {
        try {
            const url = configId ? `/menu/configs/${configId}/items` : '/menu/items';
            const response = await api.post(url, item);
            return response.data;
        } catch (error: any) {
            console.error('创建菜单项失败:', error);
            return {
                success: false,
                data: {} as MenuItem,
                error: error.response?.data?.detail || error.message
            };
        }
    }

    /**
     * 更新菜单项
     */
    async updateMenuItem(itemId: string, item: Partial<MenuItem>, configId?: string): Promise<MenuAPIResponse<MenuItem>> {
        try {
            const url = configId ? `/menu/configs/${configId}/items/${itemId}` : `/menu/items/${itemId}`;
            const response = await api.put(url, item);
            return response.data;
        } catch (error: any) {
            console.error('更新菜单项失败:', error);
            return {
                success: false,
                data: {} as MenuItem,
                error: error.response?.data?.detail || error.message
            };
        }
    }

    /**
     * 删除菜单项
     */
    async deleteMenuItem(itemId: string, configId?: string): Promise<MenuAPIResponse<boolean>> {
        try {
            const url = configId ? `/menu/configs/${configId}/items/${itemId}` : `/menu/items/${itemId}`;
            const response = await api.delete(url);
            return response.data;
        } catch (error: any) {
            console.error('删除菜单项失败:', error);
            return {
                success: false,
                data: false,
                error: error.response?.data?.detail || error.message
            };
        }
    }

    /**
     * 更新菜单项排序
     */
    async updateMenuItemsOrder(items: MenuItem[], configId?: string): Promise<MenuAPIResponse<boolean>> {
        try {
            const url = configId ? `/menu/configs/${configId}/items/order` : '/menu/items/order';
            const response = await api.put(url, { items });
            return response.data;
        } catch (error: any) {
            console.error('更新菜单项排序失败:', error);
            return {
                success: false,
                data: false,
                error: error.response?.data?.detail || error.message
            };
        }
    }

    /**
     * 导出菜单配置
     */
    async exportMenuConfig(configId?: string): Promise<MenuAPIResponse<string>> {
        try {
            const url = configId ? `/menu/configs/${configId}/export` : '/menu/export';
            const response = await api.get(url);
            return response.data;
        } catch (error: any) {
            console.error('导出菜单配置失败:', error);
            return {
                success: false,
                data: '',
                error: error.response?.data?.detail || error.message
            };
        }
    }

    /**
     * 导入菜单配置
     */
    async importMenuConfig(configData: any, configId?: string): Promise<MenuAPIResponse<MenuConfig>> {
        try {
            const url = configId ? `/menu/configs/${configId}/import` : '/menu/import';
            const response = await api.post(url, configData);
            return response.data;
        } catch (error: any) {
            console.error('导入菜单配置失败:', error);
            return {
                success: false,
                data: {} as MenuConfig,
                error: error.response?.data?.detail || error.message
            };
        }
    }

    /**
     * 获取菜单权限列表
     */
    async getMenuPermissions(): Promise<MenuAPIResponse<string[]>> {
        try {
            const response = await api.get('/menu/permissions');
            return response.data;
        } catch (error: any) {
            console.error('获取菜单权限失败:', error);
            return {
                success: false,
                data: [],
                error: error.response?.data?.detail || error.message
            };
        }
    }

    /**
     * 验证菜单配置
     */
    async validateMenuConfig(config: MenuConfig): Promise<MenuAPIResponse<{ valid: boolean; errors: string[]; warnings: string[] }>> {
        try {
            const response = await api.post('/menu/validate', config);
            return response.data;
        } catch (error: any) {
            console.error('验证菜单配置失败:', error);
            return {
                success: false,
                data: { valid: false, errors: [], warnings: [] },
                error: error.response?.data?.detail || error.message
            };
        }
    }

    /**
     * 重置菜单配置到默认值
     */
    async resetMenuConfig(): Promise<MenuAPIResponse<MenuConfig>> {
        try {
            const response = await api.post('/menu/reset');
            return response.data;
        } catch (error: any) {
            console.error('重置菜单配置失败:', error);
            return {
                success: false,
                data: {} as MenuConfig,
                error: error.response?.data?.detail || error.message
            };
        }
    }
}

export const menuAPI = new MenuAPI();