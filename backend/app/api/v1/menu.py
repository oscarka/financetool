from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime
from loguru import logger
from pydantic import BaseModel

from app.settings import settings
from app.utils.database import SessionLocal
from app.models.database import SystemConfig

router = APIRouter()

# 数据模型
class MenuItem(BaseModel):
    id: str
    name: str
    href: str
    icon: str
    order: int
    visible: bool
    enabled: bool
    requireAuth: bool
    permissions: List[str]
    description: Optional[str] = None
    badge: Optional[str] = None
    badgeColor: Optional[str] = None
    parentId: Optional[str] = None
    children: Optional[List['MenuItem']] = None
    createdAt: str
    updatedAt: str

class MenuConfig(BaseModel):
    id: str
    name: str
    description: str
    items: List[MenuItem]
    isDefault: bool
    isActive: bool
    createdAt: str
    updatedAt: str

# 默认菜单配置
DEFAULT_MENU_ITEMS = [
    {
        "id": "dashboard",
        "name": "总览",
        "href": "/",
        "icon": "HomeOutlined",
        "order": 1,
        "visible": True,
        "enabled": True,
        "requireAuth": False,
        "permissions": [],
        "description": "系统总览页面",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    },
    {
        "id": "operations",
        "name": "操作记录",
        "href": "/operations",
        "icon": "PlusCircleOutlined",
        "order": 2,
        "visible": True,
        "enabled": True,
        "requireAuth": True,
        "permissions": ["operations:read"],
        "description": "投资操作记录管理",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    },
    {
        "id": "positions",
        "name": "持仓",
        "href": "/positions",
        "icon": "BarChartOutlined",
        "order": 3,
        "visible": True,
        "enabled": True,
        "requireAuth": True,
        "permissions": ["positions:read"],
        "description": "持仓信息查看",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    },
    {
        "id": "funds",
        "name": "基金",
        "href": "/funds",
        "icon": "DollarOutlined",
        "order": 4,
        "visible": True,
        "enabled": True,
        "requireAuth": True,
        "permissions": ["funds:read"],
        "description": "基金投资管理",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    },
    {
        "id": "exchange-rates",
        "name": "汇率",
        "href": "/exchange-rates",
        "icon": "GlobalOutlined",
        "order": 5,
        "visible": True,
        "enabled": True,
        "requireAuth": False,
        "permissions": [],
        "description": "汇率信息查看",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    },
    {
        "id": "analysis",
        "name": "分析",
        "href": "/analysis",
        "icon": "PieChartOutlined",
        "order": 6,
        "visible": True,
        "enabled": True,
        "requireAuth": True,
        "permissions": ["analysis:read"],
        "description": "投资分析报告",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    },
    {
        "id": "okx",
        "name": "OKX管理",
        "href": "/okx",
        "icon": "SettingOutlined",
        "order": 7,
        "visible": True,
        "enabled": True,
        "requireAuth": True,
        "permissions": ["okx:manage"],
        "description": "OKX账户管理",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    },
    {
        "id": "wise",
        "name": "Wise管理",
        "href": "/wise",
        "icon": "BankOutlined",
        "order": 8,
        "visible": True,
        "enabled": True,
        "requireAuth": True,
        "permissions": ["wise:manage"],
        "description": "Wise账户管理",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    },
    {
        "id": "paypal",
        "name": "PayPal管理",
        "href": "/paypal",
        "icon": "PayCircleOutlined",
        "order": 9,
        "visible": True,
        "enabled": True,
        "requireAuth": True,
        "permissions": ["paypal:manage"],
        "description": "PayPal账户管理",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    },
    {
        "id": "ibkr",
        "name": "IBKR管理",
        "href": "/ibkr",
        "icon": "StockOutlined",
        "order": 10,
        "visible": True,
        "enabled": True,
        "requireAuth": True,
        "permissions": ["ibkr:manage"],
        "description": "IBKR账户管理",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    },
    {
        "id": "config",
        "name": "配置管理",
        "href": "/config",
        "icon": "ToolOutlined",
        "order": 11,
        "visible": True,
        "enabled": True,
        "requireAuth": True,
        "permissions": ["config:manage"],
        "description": "系统配置管理",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    },
    {
        "id": "scheduler",
        "name": "调度器管理",
        "href": "/scheduler",
        "icon": "ClockCircleOutlined",
        "order": 12,
        "visible": True,
        "enabled": True,
        "requireAuth": True,
        "permissions": ["scheduler:manage"],
        "description": "定时任务管理",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    },
    {
        "id": "menu",
        "name": "菜单管理",
        "href": "/menu",
        "icon": "MenuOutlined",
        "order": 13,
        "visible": True,
        "enabled": True,
        "requireAuth": True,
        "permissions": ["menu:manage"],
        "description": "菜单配置管理",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    }
]

DEFAULT_MENU_CONFIG = {
    "id": "default",
    "name": "默认菜单",
    "description": "系统默认菜单配置",
    "items": DEFAULT_MENU_ITEMS,
    "isDefault": True,
    "isActive": True,
    "createdAt": datetime.now().isoformat(),
    "updatedAt": datetime.now().isoformat()
}

# 内存中的菜单配置存储（实际项目中应该使用数据库）
menu_configs = {
    "default": DEFAULT_MENU_CONFIG
}

def get_menu_configs_from_db():
    """从数据库获取菜单配置"""
    try:
        db = SessionLocal()
        config_record = db.query(SystemConfig).filter(
            SystemConfig.config_key == "menu_configs"
        ).first()
        
        if config_record:
            return json.loads(config_record.config_value)
        else:
            # 如果没有配置，创建默认配置
            default_configs = {"default": DEFAULT_MENU_CONFIG}
            config_record = SystemConfig(
                config_key="menu_configs",
                config_value=json.dumps(default_configs),
                description="菜单配置"
            )
            db.add(config_record)
            db.commit()
            return default_configs
    except Exception as e:
        logger.error(f"从数据库获取菜单配置失败: {e}")
        return {"default": DEFAULT_MENU_CONFIG}
    finally:
        db.close()

def save_menu_configs_to_db(configs: Dict[str, Any]):
    """保存菜单配置到数据库"""
    try:
        db = SessionLocal()
        config_record = db.query(SystemConfig).filter(
            SystemConfig.config_key == "menu_configs"
        ).first()
        
        if config_record:
            config_record.config_value = json.dumps(configs)
            config_record.updated_at = datetime.now()
        else:
            config_record = SystemConfig(
                config_key="menu_configs",
                config_value=json.dumps(configs),
                description="菜单配置"
            )
            db.add(config_record)
        
        db.commit()
        return True
    except Exception as e:
        logger.error(f"保存菜单配置到数据库失败: {e}")
        return False
    finally:
        db.close()

@router.get("/configs")
async def get_menu_configs():
    """获取所有菜单配置"""
    try:
        configs = get_menu_configs_from_db()
        return {
            "success": True,
            "data": list(configs.values())
        }
    except Exception as e:
        logger.error(f"获取菜单配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取菜单配置失败: {str(e)}")

@router.get("/active")
async def get_active_menu_config():
    """获取当前激活的菜单配置"""
    try:
        configs = get_menu_configs_from_db()
        active_config = None
        
        for config in configs.values():
            if config.get("isActive", False):
                active_config = config
                break
        
        if not active_config:
            # 如果没有激活的配置，使用默认配置
            active_config = configs.get("default", DEFAULT_MENU_CONFIG)
        
        return {
            "success": True,
            "data": active_config
        }
    except Exception as e:
        logger.error(f"获取激活菜单配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取激活菜单配置失败: {str(e)}")

@router.post("/configs")
async def create_menu_config(config_data: Dict[str, Any]):
    """创建菜单配置"""
    try:
        configs = get_menu_configs_from_db()
        
        new_config = {
            "id": f"config_{int(datetime.now().timestamp())}",
            "name": config_data.get("name", "新配置"),
            "description": config_data.get("description", ""),
            "items": config_data.get("items", []),
            "isDefault": False,
            "isActive": False,
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat()
        }
        
        configs[new_config["id"]] = new_config
        save_menu_configs_to_db(configs)
        
        return {
            "success": True,
            "data": new_config
        }
    except Exception as e:
        logger.error(f"创建菜单配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建菜单配置失败: {str(e)}")

@router.put("/configs/{config_id}")
async def update_menu_config(config_id: str, config_data: Dict[str, Any]):
    """更新菜单配置"""
    try:
        configs = get_menu_configs_from_db()
        
        if config_id not in configs:
            raise HTTPException(status_code=404, detail="菜单配置不存在")
        
        configs[config_id].update(config_data)
        configs[config_id]["updatedAt"] = datetime.now().isoformat()
        
        save_menu_configs_to_db(configs)
        
        return {
            "success": True,
            "data": configs[config_id]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新菜单配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新菜单配置失败: {str(e)}")

@router.delete("/configs/{config_id}")
async def delete_menu_config(config_id: str):
    """删除菜单配置"""
    try:
        configs = get_menu_configs_from_db()
        
        if config_id not in configs:
            raise HTTPException(status_code=404, detail="菜单配置不存在")
        
        if configs[config_id].get("isDefault", False):
            raise HTTPException(status_code=400, detail="不能删除默认配置")
        
        del configs[config_id]
        save_menu_configs_to_db(configs)
        
        return {
            "success": True,
            "data": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除菜单配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除菜单配置失败: {str(e)}")

@router.post("/configs/{config_id}/activate")
async def activate_menu_config(config_id: str):
    """激活菜单配置"""
    try:
        configs = get_menu_configs_from_db()
        
        if config_id not in configs:
            raise HTTPException(status_code=404, detail="菜单配置不存在")
        
        # 取消其他配置的激活状态
        for config in configs.values():
            config["isActive"] = False
        
        # 激活指定配置
        configs[config_id]["isActive"] = True
        configs[config_id]["updatedAt"] = datetime.now().isoformat()
        
        save_menu_configs_to_db(configs)
        
        return {
            "success": True,
            "data": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"激活菜单配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"激活菜单配置失败: {str(e)}")

@router.get("/items")
async def get_menu_items():
    """获取菜单项列表"""
    try:
        configs = get_menu_configs_from_db()
        active_config = None
        
        for config in configs.values():
            if config.get("isActive", False):
                active_config = config
                break
        
        if not active_config:
            active_config = configs.get("default", DEFAULT_MENU_CONFIG)
        
        return {
            "success": True,
            "data": active_config.get("items", [])
        }
    except Exception as e:
        logger.error(f"获取菜单项失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取菜单项失败: {str(e)}")

@router.post("/items")
async def create_menu_item(item_data: Dict[str, Any]):
    """创建菜单项"""
    try:
        configs = get_menu_configs_from_db()
        active_config = None
        
        for config in configs.values():
            if config.get("isActive", False):
                active_config = config
                break
        
        if not active_config:
            active_config = configs.get("default", DEFAULT_MENU_CONFIG)
        
        new_item = {
            "id": f"item_{int(datetime.now().timestamp())}",
            "name": item_data.get("name", "新菜单项"),
            "href": item_data.get("href", "/"),
            "icon": item_data.get("icon", "LinkOutlined"),
            "order": len(active_config.get("items", [])) + 1,
            "visible": item_data.get("visible", True),
            "enabled": item_data.get("enabled", True),
            "requireAuth": item_data.get("requireAuth", False),
            "permissions": item_data.get("permissions", []),
            "description": item_data.get("description", ""),
            "badge": item_data.get("badge"),
            "badgeColor": item_data.get("badgeColor"),
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat()
        }
        
        if "items" not in active_config:
            active_config["items"] = []
        
        active_config["items"].append(new_item)
        active_config["updatedAt"] = datetime.now().isoformat()
        
        save_menu_configs_to_db(configs)
        
        return {
            "success": True,
            "data": new_item
        }
    except Exception as e:
        logger.error(f"创建菜单项失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建菜单项失败: {str(e)}")

@router.put("/items/{item_id}")
async def update_menu_item(item_id: str, item_data: Dict[str, Any]):
    """更新菜单项"""
    try:
        configs = get_menu_configs_from_db()
        active_config = None
        
        for config in configs.values():
            if config.get("isActive", False):
                active_config = config
                break
        
        if not active_config:
            active_config = configs.get("default", DEFAULT_MENU_CONFIG)
        
        items = active_config.get("items", [])
        item_index = None
        
        for i, item in enumerate(items):
            if item["id"] == item_id:
                item_index = i
                break
        
        if item_index is None:
            raise HTTPException(status_code=404, detail="菜单项不存在")
        
        items[item_index].update(item_data)
        items[item_index]["updatedAt"] = datetime.now().isoformat()
        active_config["updatedAt"] = datetime.now().isoformat()
        
        save_menu_configs_to_db(configs)
        
        return {
            "success": True,
            "data": items[item_index]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新菜单项失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新菜单项失败: {str(e)}")

@router.delete("/items/{item_id}")
async def delete_menu_item(item_id: str):
    """删除菜单项"""
    try:
        configs = get_menu_configs_from_db()
        active_config = None
        
        for config in configs.values():
            if config.get("isActive", False):
                active_config = config
                break
        
        if not active_config:
            active_config = configs.get("default", DEFAULT_MENU_CONFIG)
        
        items = active_config.get("items", [])
        item_index = None
        
        for i, item in enumerate(items):
            if item["id"] == item_id:
                item_index = i
                break
        
        if item_index is None:
            raise HTTPException(status_code=404, detail="菜单项不存在")
        
        del items[item_index]
        active_config["updatedAt"] = datetime.now().isoformat()
        
        save_menu_configs_to_db(configs)
        
        return {
            "success": True,
            "data": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除菜单项失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除菜单项失败: {str(e)}")

@router.put("/items/order")
async def update_menu_items_order(order_data: Dict[str, Any]):
    """更新菜单项排序"""
    try:
        configs = get_menu_configs_from_db()
        active_config = None
        
        for config in configs.values():
            if config.get("isActive", False):
                active_config = config
                break
        
        if not active_config:
            active_config = configs.get("default", DEFAULT_MENU_CONFIG)
        
        new_items = order_data.get("items", [])
        active_config["items"] = new_items
        active_config["updatedAt"] = datetime.now().isoformat()
        
        save_menu_configs_to_db(configs)
        
        return {
            "success": True,
            "data": True
        }
    except Exception as e:
        logger.error(f"更新菜单项排序失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新菜单项排序失败: {str(e)}")

@router.get("/export")
async def export_menu_config():
    """导出菜单配置"""
    try:
        configs = get_menu_configs_from_db()
        active_config = None
        
        for config in configs.values():
            if config.get("isActive", False):
                active_config = config
                break
        
        if not active_config:
            active_config = configs.get("default", DEFAULT_MENU_CONFIG)
        
        return {
            "success": True,
            "data": json.dumps(active_config, ensure_ascii=False, indent=2)
        }
    except Exception as e:
        logger.error(f"导出菜单配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出菜单配置失败: {str(e)}")

@router.post("/import")
async def import_menu_config(config_data: Dict[str, Any]):
    """导入菜单配置"""
    try:
        configs = get_menu_configs_from_db()
        
        new_config = {
            "id": f"imported_{int(datetime.now().timestamp())}",
            "name": config_data.get("name", "导入的配置"),
            "description": config_data.get("description", "从文件导入的配置"),
            "items": config_data.get("items", []),
            "isDefault": False,
            "isActive": False,
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat()
        }
        
        configs[new_config["id"]] = new_config
        save_menu_configs_to_db(configs)
        
        return {
            "success": True,
            "data": new_config
        }
    except Exception as e:
        logger.error(f"导入菜单配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"导入菜单配置失败: {str(e)}")

@router.get("/permissions")
async def get_menu_permissions():
    """获取菜单权限列表"""
    try:
        # 这里应该从实际的权限系统中获取
        permissions = [
            "operations:read",
            "positions:read",
            "funds:read",
            "analysis:read",
            "okx:manage",
            "wise:manage",
            "paypal:manage",
            "ibkr:manage",
            "config:manage",
            "scheduler:manage",
            "menu:manage"
        ]
        
        return {
            "success": True,
            "data": permissions
        }
    except Exception as e:
        logger.error(f"获取菜单权限失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取菜单权限失败: {str(e)}")

@router.post("/validate")
async def validate_menu_config(config: Dict[str, Any]):
    """验证菜单配置"""
    try:
        errors = []
        warnings = []
        
        # 验证必需字段
        if not config.get("name"):
            errors.append("配置名称不能为空")
        
        items = config.get("items", [])
        if not items:
            warnings.append("菜单项列表为空")
        
        # 验证菜单项
        for i, item in enumerate(items):
            if not item.get("name"):
                errors.append(f"第{i+1}个菜单项名称不能为空")
            
            if not item.get("href"):
                errors.append(f"第{i+1}个菜单项路径不能为空")
            
            if not item.get("icon"):
                warnings.append(f"第{i+1}个菜单项没有设置图标")
        
        valid = len(errors) == 0
        
        return {
            "success": True,
            "data": {
                "valid": valid,
                "errors": errors,
                "warnings": warnings
            }
        }
    except Exception as e:
        logger.error(f"验证菜单配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"验证菜单配置失败: {str(e)}")

@router.post("/reset")
async def reset_menu_config():
    """重置菜单配置到默认值"""
    try:
        configs = {"default": DEFAULT_MENU_CONFIG}
        save_menu_configs_to_db(configs)
        
        return {
            "success": True,
            "data": DEFAULT_MENU_CONFIG
        }
    except Exception as e:
        logger.error(f"重置菜单配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"重置菜单配置失败: {str(e)}")