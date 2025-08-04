from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import date
import json

from app.utils.database import get_db
from app.models.schemas import (
    FundOperationCreate, FundOperationUpdate, FundOperation,
    FundOperationListResponse, FundOperationResponse,
    FundPositionResponse, FundPosition, FundNavCreate, FundNav,
    OperationQuery, BaseResponse, FundInfoCreate, FundInfo,
    FundListResponse, DCAPlanCreate, DCAPlanUpdate, DCAPlan,
    DCAPlanResponse, DCAPlanListResponse, PositionSummaryResponse,
    PositionSummary
)
from app.models.database import UserOperation, FundNav, FundDividend
from app.services.fund_service import FundOperationService, FundInfoService, FundNavService, DCAService, FundDividendService
from app.services.fund_api_service import FundSyncService, FundAPIService
from app.services.scheduler_service import scheduler_service
from app.services.okx_api_service import OKXAPIService

router = APIRouter()


@router.post("/operations", response_model=FundOperationResponse)
def create_fund_operation(
    operation: FundOperationCreate,
    db: Session = Depends(get_db)
):
    """创建基金操作记录"""
    try:
        result = FundOperationService.create_operation(db, operation)
        
        # 重新计算持仓（新增操作记录会影响持仓）
        try:
            recalculate_result = FundOperationService.recalculate_all_positions(db)
            if recalculate_result["success"]:
                return FundOperationResponse(
                    success=True,
                    message="基金操作记录创建成功，持仓已重新计算",
                    data=result
                )
            else:
                return FundOperationResponse(
                    success=True,
                    message="基金操作记录创建成功，但持仓重新计算失败",
                    data=result
                )
        except Exception as e:
            print(f"重新计算持仓失败: {e}")
            return FundOperationResponse(
                success=True,
                message="基金操作记录创建成功，但持仓重新计算失败",
                data=result
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/operations", response_model=FundOperationListResponse)
def get_fund_operations(
    asset_code: Optional[str] = Query(None, description="基金代码"),
    operation_type: Optional[str] = Query(None, description="操作类型"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    dca_plan_id: Optional[int] = Query(None, description="定投计划ID"),
    status: Optional[str] = Query(None, description="操作状态"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取基金操作记录 - 优化版本"""
    try:
        print(f"[调试] 开始查询基金操作记录: asset_code={asset_code}, page={page}, page_size={page_size}")
        
        operations, total = FundOperationService.get_operations(
            db=db,
            fund_code=asset_code,
            operation_type=operation_type,
            start_date=start_date,
            end_date=end_date,
            dca_plan_id=dca_plan_id,
            status=status,
            page=page,
            page_size=page_size
        )
        
        print(f"[调试] 查询到 {len(operations)} 条记录，总数: {total}")
        
        # 手动转换数据库对象为Pydantic模型 - 优化版本（移除单独的API调用）
        from app.models.schemas import FundOperation
        fund_operations = []
        
        # 批量获取最新净值 - 优化：只查询数据库，避免外部API调用
        fund_codes = list(set(op.asset_code for op in operations))
        latest_nav_map = {}
        
        if fund_codes:
            # 批量查询数据库中的最新净值
            for fund_code in fund_codes:
                latest_nav_obj = FundNavService.get_latest_nav(db, fund_code)
                if latest_nav_obj and latest_nav_obj.nav:
                    latest_nav_map[fund_code] = float(latest_nav_obj.nav)
        
        for i, op in enumerate(operations):
            print(f"[调试] 转换第 {i+1} 条记录: id={op.id}, asset_code={op.asset_code}, nav={op.nav}")
            try:
                # 使用批量查询的结果
                latest_nav = latest_nav_map.get(op.asset_code, None)
                
                print(f"[调试] 构造FundOperation前: op.id={op.id}, op.asset_code={op.asset_code}, op.nav={op.nav}, latest_nav={latest_nav}")
                fund_op = FundOperation(
                    id=op.id,
                    operation_date=op.operation_date,
                    platform=op.platform,
                    asset_type=op.asset_type,
                    operation_type=op.operation_type,
                    asset_code=op.asset_code,
                    asset_name=op.asset_name,
                    amount=op.amount,
                    currency=op.currency,
                    quantity=op.quantity,
                    price=op.price,
                    nav=op.nav,
                    fee=op.fee,
                    strategy=op.strategy,
                    emotion_score=op.emotion_score,
                    tags=op.tags,
                    notes=op.notes,
                    status=op.status,
                    dca_plan_id=op.dca_plan_id,
                    dca_execution_type=op.dca_execution_type,
                    created_at=op.created_at,
                    updated_at=op.updated_at,
                    latest_nav=latest_nav
                )
                print(f"[调试] 构造FundOperation后: fund_op.id={fund_op.id}, fund_op.asset_code={fund_op.asset_code}, fund_op.nav={fund_op.nav}, fund_op.latest_nav={getattr(fund_op, 'latest_nav', None)}")
                fund_operations.append(fund_op)
                print(f"[调试] 第 {i+1} 条记录转换成功")
            except Exception as convert_error:
                print(f"[调试] 第 {i+1} 条记录转换失败: {convert_error}")
                raise convert_error
        
        print(f"[调试] 成功转换 {len(fund_operations)} 条记录")
        # 新增日志，打印每条记录的 nav 和 latest_nav
        for idx, op in enumerate(fund_operations):
            print(f"[调试] 返回第{idx+1}条: id={op.id}, asset_code={op.asset_code}, nav={op.nav}, latest_nav={getattr(op, 'latest_nav', None)}")
        
        return FundOperationListResponse(
            success=True,
            message=f"获取到 {len(fund_operations)} 条记录",
            data=fund_operations,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        print(f"[调试] API异常: {e}")
        import traceback
        print(f"[调试] 异常堆栈: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/operations/{operation_id}", response_model=FundOperationResponse)
def update_fund_operation(
    operation_id: int,
    update_data: FundOperationUpdate,
    db: Session = Depends(get_db)
):
    """更新基金操作记录"""
    try:
        result = FundOperationService.update_operation(db, operation_id, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="操作记录不存在")
        
        # 重新计算持仓（更新操作记录会影响持仓）
        try:
            recalculate_result = FundOperationService.recalculate_all_positions(db)
            if recalculate_result["success"]:
                return FundOperationResponse(
                    success=True,
                    message="基金操作记录更新成功，持仓已重新计算",
                    data=result
                )
            else:
                return FundOperationResponse(
                    success=True,
                    message="基金操作记录更新成功，但持仓重新计算失败",
                    data=result
                )
        except Exception as e:
            print(f"重新计算持仓失败: {e}")
            return FundOperationResponse(
                success=True,
                message="基金操作记录更新成功，但持仓重新计算失败",
                data=result
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/operations/{operation_id}", response_model=BaseResponse)
def delete_fund_operation(
    operation_id: int,
    db: Session = Depends(get_db)
):
    """删除基金操作记录"""
    try:
        operation = db.query(UserOperation).filter(UserOperation.id == operation_id).first()
        if not operation:
            raise HTTPException(status_code=404, detail="操作记录不存在")
        
        # 记录操作信息用于后续重新计算持仓
        asset_code = operation.asset_code
        operation_type = operation.operation_type
        
        # 删除操作记录
        db.delete(operation)
        db.commit()
        
        # 重新计算该基金的持仓
        try:
            # 重新计算所有持仓（包括被删除操作的基金）
            result = FundOperationService.recalculate_all_positions(db)
            if result["success"]:
                return BaseResponse(
                    success=True,
                    message=f"基金操作记录删除成功，持仓已重新计算"
                )
            else:
                return BaseResponse(
                    success=True,
                    message=f"基金操作记录删除成功，但持仓重新计算失败：{result['message']}"
                )
        except Exception as e:
            print(f"重新计算持仓失败: {e}")
            return BaseResponse(
                success=True,
                message=f"基金操作记录删除成功，但持仓重新计算失败"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/positions", response_model=FundPositionResponse)
def get_fund_positions(db: Session = Depends(get_db)):
    """获取基金持仓列表"""
    try:
        positions = FundOperationService.get_fund_positions(db)
        return FundPositionResponse(
            success=True,
            message=f"获取到 {len(positions)} 个基金持仓",
            data=positions
        )
    except Exception as e:
        print(f"[调试] 持仓列表API异常: {e}")
        import traceback
        print(f"[调试] 异常堆栈: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/positions/summary", response_model=PositionSummaryResponse)
def get_position_summary(db: Session = Depends(get_db)):
    """获取持仓汇总信息"""
    try:
        summary_data = FundOperationService.get_position_summary(db)
        
        # 包装数据到模型中
        summary = PositionSummary(
            total_invested=summary_data["total_invested"],
            total_value=summary_data["total_value"],
            total_profit=summary_data["total_profit"],
            total_profit_rate=summary_data["total_profit_rate"],
            asset_count=summary_data["asset_count"],
            profitable_count=summary_data["profitable_count"],
            loss_count=summary_data["loss_count"]
        )
        
        return PositionSummaryResponse(
            success=True,
            message="获取持仓汇总成功",
            data=summary
        )
    except Exception as e:
        print(f"[调试] 持仓汇总API异常: {e}")
        import traceback
        print(f"[调试] 异常堆栈: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/positions/available", response_model=FundPositionResponse)
def get_available_positions(db: Session = Depends(get_db)):
    """获取可卖出的持仓列表（用于卖出操作选择）"""
    try:
        positions = FundOperationService.get_fund_positions(db)
        # 过滤掉份额为0的持仓
        available_positions = [pos for pos in positions if pos.total_shares > 0]
        return FundPositionResponse(
            success=True,
            message=f"获取到 {len(available_positions)} 个可卖出的持仓",
            data=available_positions
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/positions/recalculate", response_model=BaseResponse)
def recalculate_positions(db: Session = Depends(get_db)):
    """重新计算所有持仓（基于所有已确认的操作记录）"""
    try:
        result = FundOperationService.recalculate_all_positions(db)
        
        if result["success"]:
            return BaseResponse(
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/nav", response_model=BaseResponse)
def create_fund_nav(
    nav_data: FundNavCreate,
    db: Session = Depends(get_db)
):
    """手动录入基金净值"""
    try:
        result = FundNavService.create_nav(
            db=db,
            fund_code=nav_data.fund_code,
            nav_date=nav_data.nav_date,
            nav=nav_data.nav,
            accumulated_nav=nav_data.accumulated_nav,
            growth_rate=nav_data.growth_rate,
            source=nav_data.source
        )
        
        return BaseResponse(
            success=True,
            message="基金净值录入成功",
            data={"id": result.id}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/nav/{fund_code}", response_model=BaseResponse)
def get_fund_nav_history(
    fund_code: str,
    days: int = Query(30, ge=1, le=365, description="获取天数"),
    db: Session = Depends(get_db)
):
    """获取基金净值历史"""
    try:
        nav_history = FundNavService.get_nav_history(db, fund_code, days)
        return BaseResponse(
            success=True,
            message=f"获取到 {len(nav_history)} 条净值记录",
            data={"nav_history": nav_history}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/nav/{fund_code}/latest", response_model=BaseResponse)
def get_latest_nav(
    fund_code: str,
    db: Session = Depends(get_db)
):
    """获取基金最新净值（含估算净值）"""
    nav_obj = FundNavService.get_latest_nav(db, fund_code)
    if not nav_obj:
        raise HTTPException(status_code=404, detail="未找到净值")
    nav_dict = {
        "fund_code": nav_obj.fund_code,
        "nav_date": nav_obj.nav_date,
        "nav": float(nav_obj.nav) if nav_obj.nav is not None else None,
        "accumulated_nav": float(nav_obj.accumulated_nav) if nav_obj.accumulated_nav is not None else None,
        "growth_rate": float(nav_obj.growth_rate) if nav_obj.growth_rate is not None else None,
        "source": nav_obj.source,
        "estimated_nav": None,
        "estimated_time": None,
    }
    # 实时拉取天天基金API估算净值
    try:
        api_service = FundAPIService()
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        api_data = loop.run_until_complete(api_service.get_fund_nav_latest_tiantian(fund_code))
        if api_data:
            nav_dict["estimated_nav"] = float(api_data.get("gsz")) if api_data.get("gsz") else None
            nav_dict["estimated_time"] = api_data.get("gztime")
    except Exception as e:
        print(f"[调试] 获取估算净值异常: {e}")
    return BaseResponse(success=True, data={"fund_nav": nav_dict})


@router.post("/nav/{fund_code}/sync", response_model=BaseResponse)
async def sync_fund_nav(
    fund_code: str,
    nav_date: date = Query(..., description="净值日期"),
    db: Session = Depends(get_db)
):
    """同步基金净值"""
    try:
        sync_service = FundSyncService()
        success = await sync_service.sync_fund_nav(db, fund_code, nav_date)
        
        if success:
            return BaseResponse(
                success=True,
                message="基金净值同步成功"
            )
        else:
            raise HTTPException(status_code=400, detail="基金净值同步失败")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/nav/{fund_code}/sync/latest", response_model=BaseResponse)
async def sync_latest_fund_nav(
    fund_code: str,
    db: Session = Depends(get_db)
):
    """同步最新基金净值（只用API返回的最新净值）"""
    try:
        sync_service = FundSyncService()
        success = await sync_service.api_service.sync_latest_fund_nav(db, fund_code)
        if success:
            return BaseResponse(
                success=True,
                message="最新基金净值同步成功"
            )
        else:
            raise HTTPException(status_code=400, detail="最新基金净值同步失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/info", response_model=BaseResponse)
def create_fund_info(
    fund_info: FundInfoCreate,
    db: Session = Depends(get_db)
):
    """创建基金信息"""
    try:
        result = FundInfoService.create_fund_info(
            db=db,
            fund_code=fund_info.fund_code,
            fund_name=fund_info.fund_name,
            fund_type=fund_info.fund_type,
            management_fee=fund_info.management_fee,
            purchase_fee=fund_info.purchase_fee,
            redemption_fee=fund_info.redemption_fee,
            min_purchase=fund_info.min_purchase,
            risk_level=fund_info.risk_level
        )
        
        return BaseResponse(
            success=True,
            message="基金信息创建成功",
            data={"id": result.id}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/info", response_model=FundListResponse)
def get_all_funds(db: Session = Depends(get_db)):
    """获取所有基金信息"""
    try:
        funds = FundInfoService.get_all_funds(db)
        
        # 将SQLAlchemy模型列表转换为字典列表
        funds_list = []
        for fund in funds:
            fund_dict = {
                "id": fund.id,
                "fund_code": fund.fund_code,
                "fund_name": fund.fund_name,
                "fund_type": fund.fund_type,
                "management_fee": float(fund.management_fee) if fund.management_fee else None,
                "purchase_fee": float(fund.purchase_fee) if fund.purchase_fee else None,
                "redemption_fee": float(fund.redemption_fee) if fund.redemption_fee else None,
                "min_purchase": float(fund.min_purchase) if fund.min_purchase else None,
                "risk_level": fund.risk_level,
                "created_at": fund.created_at.isoformat() if fund.created_at else None
            }
            funds_list.append(fund_dict)
        
        return FundListResponse(
            success=True,
            message=f"获取到 {len(funds_list)} 个基金",
            data=funds_list
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/info/{fund_code}", response_model=BaseResponse)
def get_fund_info(
    fund_code: str,
    db: Session = Depends(get_db)
):
    """获取基金信息，查不到自动同步"""
    try:
        fund_info = FundInfoService.get_fund_info(db, fund_code)
        if not fund_info:
            # 自动同步
            sync_service = FundSyncService()
            import asyncio
            asyncio.run(sync_service.sync_fund_info(db, fund_code))
            # 再查一次
            fund_info = FundInfoService.get_fund_info(db, fund_code)
            if not fund_info:
                raise HTTPException(status_code=404, detail="基金不存在")
        # 将SQLAlchemy模型转换为字典
        fund_info_dict = {
            "id": fund_info.id,
            "fund_code": fund_info.fund_code,
            "fund_name": fund_info.fund_name,
            "fund_type": fund_info.fund_type,
            "management_fee": float(fund_info.management_fee) if fund_info.management_fee else None,
            "purchase_fee": float(fund_info.purchase_fee) if fund_info.purchase_fee else None,
            "redemption_fee": float(fund_info.redemption_fee) if fund_info.redemption_fee else None,
            "min_purchase": float(fund_info.min_purchase) if fund_info.min_purchase else None,
            "risk_level": fund_info.risk_level,
            "created_at": fund_info.created_at.isoformat() if fund_info.created_at else None
        }
        return BaseResponse(
            success=True,
            message="获取基金信息成功",
            data={"fund_info": fund_info_dict}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/info/{fund_code}", response_model=BaseResponse)
def update_fund_info(
    fund_code: str,
    fund_info: FundInfoCreate,
    db: Session = Depends(get_db)
):
    """更新基金信息"""
    try:
        existing = FundInfoService.get_fund_info(db, fund_code)
        if not existing:
            raise HTTPException(status_code=404, detail="基金不存在")
        
        # 更新字段
        for field, value in fund_info.dict(exclude_unset=True).items():
            setattr(existing, field, value)
        
        db.commit()
        db.refresh(existing)
        
        return BaseResponse(
            success=True,
            message="基金信息更新成功",
            data={"id": existing.id}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/info/{fund_code}/sync", response_model=BaseResponse)
async def sync_fund_info(
    fund_code: str,
    db: Session = Depends(get_db)
):
    """同步基金信息"""
    try:
        sync_service = FundSyncService()
        success = await sync_service.sync_fund_info(db, fund_code)
        
        if success:
            return BaseResponse(
                success=True,
                message="基金信息同步成功"
            )
        else:
            raise HTTPException(status_code=400, detail="基金信息同步失败")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# 定投计划相关API
@router.post("/dca/plans", response_model=DCAPlanResponse)
def create_dca_plan(
    plan: DCAPlanCreate,
    db: Session = Depends(get_db)
):
    """创建定投计划"""
    print(f"[API调试] 开始创建定投计划")
    print(f"[API调试] 接收到的计划数据: {plan}")
    try:
        print(f"[API调试] 调用DCAService.create_dca_plan")
        result = DCAService.create_dca_plan(db, plan)
        print(f"[API调试] DCAService.create_dca_plan调用成功")
        
        # 修正：确保exclude_dates为List[str]类型
        if result and result.exclude_dates and isinstance(result.exclude_dates, str):
            import json
            try:
                result.exclude_dates = json.loads(result.exclude_dates)
            except Exception:
                result.exclude_dates = []
        
        print(f"[API调试] 准备返回成功响应")
        return DCAPlanResponse(
            success=True,
            message="定投计划创建成功",
            data=result
        )
    except Exception as e:
        print(f"[API错误] 创建定投计划失败: {str(e)}")
        print(f"[API错误] 错误类型: {type(e)}")
        import traceback
        print(f"[API错误] 完整错误堆栈:")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dca/plans", response_model=DCAPlanListResponse)
def get_dca_plans(
    status: Optional[str] = Query(None, description="计划状态"),
    db: Session = Depends(get_db)
):
    """获取定投计划列表"""
    try:
        plans = DCAService.get_dca_plans(db, status)
        return DCAPlanListResponse(
            success=True,
            message=f"获取到 {len(plans)} 个定投计划",
            data=plans
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dca/plans/{plan_id}", response_model=DCAPlanResponse)
def get_dca_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """获取定投计划详情"""
    try:
        plan = DCAService.get_dca_plan_by_id(db, plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="定投计划不存在")
        
        return DCAPlanResponse(
            success=True,
            message="获取定投计划成功",
            data=plan
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/dca/plans/{plan_id}", response_model=DCAPlanResponse)
def update_dca_plan(
    plan_id: int,
    update_data: DCAPlanUpdate,
    db: Session = Depends(get_db)
):
    """更新定投计划"""
    try:
        result = DCAService.update_dca_plan(db, plan_id, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="定投计划不存在")
        # 修正：确保exclude_dates为List[str]类型
        if result and result.exclude_dates and isinstance(result.exclude_dates, str):
            import json
            try:
                result.exclude_dates = json.loads(result.exclude_dates)
            except Exception:
                result.exclude_dates = []
        return DCAPlanResponse(
            success=True,
            message="定投计划更新成功",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[调试] update_dca_plan异常: {e}")
        print(f"[调试] update_dca_plan堆栈: {traceback.format_exc()}")
        print(f"[调试] update_data: {update_data}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/dca/plans/{plan_id}", response_model=BaseResponse)
def delete_dca_plan(
    plan_id: int,
    delete_operations: bool = Query(False, description="是否一并删除所有关联定投操作"),
    db: Session = Depends(get_db)
):
    """删除定投计划，支持批量删除操作记录"""
    print(f"[API调试] 开始删除定投计划，ID: {plan_id}, delete_operations: {delete_operations}")
    try:
        if delete_operations:
            print(f"[API调试] 调用delete_dca_plan_with_operations")
            success = DCAService.delete_dca_plan_with_operations(db, plan_id)
        else:
            print(f"[API调试] 调用delete_dca_plan")
            success = DCAService.delete_dca_plan(db, plan_id)
        
        print(f"[API调试] 删除操作结果: {success}")
        
        if not success:
            print(f"[API调试] 删除失败，返回404")
            raise HTTPException(status_code=404, detail="定投计划不存在")
        
        print(f"[API调试] 删除成功，准备返回响应")
        return BaseResponse(
            success=True,
            message="定投计划删除成功"
        )
    except HTTPException:
        print(f"[API调试] 捕获HTTPException，重新抛出")
        raise
    except Exception as e:
        print(f"[API错误] 删除定投计划异常: {str(e)}")
        import traceback
        print(f"[API错误] 完整错误堆栈:")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/dca/plans/{plan_id}/execute", response_model=FundOperationResponse)
def execute_dca_plan(
    plan_id: int,
    execution_type: str = Query("manual", description="执行类型: manual, scheduled, smart"),
    db: Session = Depends(get_db)
):
    """手动执行定投计划"""
    try:
        operation = DCAService.execute_dca_plan(db, plan_id, execution_type)
        if not operation:
            raise HTTPException(status_code=400, detail="定投计划执行失败")
        
        # 重新计算持仓（定投执行会产生新的操作记录）
        try:
            recalculate_result = FundOperationService.recalculate_all_positions(db)
            if recalculate_result["success"]:
                return FundOperationResponse(
                    success=True,
                    message="定投计划执行成功，持仓已重新计算",
                    data=operation
                )
            else:
                return FundOperationResponse(
                    success=True,
                    message="定投计划执行成功，但持仓重新计算失败",
                    data=operation
                )
        except Exception as e:
            print(f"重新计算持仓失败: {e}")
            return FundOperationResponse(
                success=True,
                message="定投计划执行成功，但持仓重新计算失败",
                data=operation
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/dca/plans/execute-all", response_model=BaseResponse)
def execute_all_dca_plans(
    db: Session = Depends(get_db)
):
    """执行所有到期的定投计划"""
    try:
        operations = DCAService.check_and_execute_dca_plans(db)
        
        # 重新计算持仓（批量执行定投会产生多个操作记录）
        try:
            recalculate_result = FundOperationService.recalculate_all_positions(db)
            if recalculate_result["success"]:
                return BaseResponse(
                    success=True,
                    message=f"执行了 {len(operations)} 个定投计划，持仓已重新计算",
                    data={"executed_count": len(operations)}
                )
            else:
                return BaseResponse(
                    success=True,
                    message=f"执行了 {len(operations)} 个定投计划，但持仓重新计算失败",
                    data={"executed_count": len(operations)}
                )
        except Exception as e:
            print(f"重新计算持仓失败: {e}")
            return BaseResponse(
                success=True,
                message=f"执行了 {len(operations)} 个定投计划，但持仓重新计算失败",
                data={"executed_count": len(operations)}
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dca/plans/{plan_id}/statistics", response_model=BaseResponse)
def get_dca_statistics(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """获取定投计划统计信息"""
    try:
        stats = DCAService.get_dca_statistics(db, plan_id)
        if not stats:
            raise HTTPException(status_code=404, detail="定投计划不存在")
        
        return BaseResponse(
            success=True,
            message="获取统计信息成功",
            data=stats
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/nav_history", response_model=BaseResponse)
def get_fund_nav_history_with_cache(
    fund_code: str = Query(..., description="基金代码"),
    force_update: bool = Query(False, description="是否强制用akshare拉取最新历史净值"),
    include_dividend: bool = Query(False, description="是否合并分红数据"),
    db: Session = Depends(get_db)
):
    """获取基金历史净值，支持按需用akshare拉取并缓存，支持合并分红数据"""
    try:
        if force_update:
            count = FundNavService.fetch_and_cache_nav_history(db, fund_code)
        
        navs = db.query(FundNav).filter_by(fund_code=fund_code).order_by(FundNav.nav_date.desc()).all()
        data = [
            {
                "id": nav.id,
                "fund_code": nav.fund_code,
                "nav_date": str(nav.nav_date),
                "nav": float(nav.nav) if nav.nav else None,
                "accumulated_nav": float(nav.accumulated_nav) if nav.accumulated_nav else None,
                "source": nav.source or "akshare"
            }
            for nav in navs
        ]
        
        # 合并分红数据
        if include_dividend:
            # 只查询数据库中已有的分红数据，不自动拉取
            dividends = FundDividendService.get_dividends_by_fund(db, fund_code)
            
            # 合并分红数据到净值数据
            dividend_map = {str(div.dividend_date): div for div in dividends}
            for item in data:
                div = dividend_map.get(item['nav_date'])
                if div is not None:
                    item['dividend_amount'] = float(div.dividend_amount) if div.dividend_amount else None
                    item['dividend_date'] = str(div.dividend_date) if div.dividend_date else None
                    item['record_date'] = str(div.record_date) if div.record_date else None
                else:
                    item['dividend_amount'] = None
                    item['dividend_date'] = None
                    item['record_date'] = None
        
        return BaseResponse(success=True, message=f"获取到 {len(data)} 条历史净值记录", data={"nav_history": data})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dividends/{fund_code}", response_model=BaseResponse)
def get_fund_dividends(
    fund_code: str,
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    force_update: bool = Query(False, description="是否强制从API更新分红数据"),
    db: Session = Depends(get_db)
):
    """获取基金分红记录"""
    try:
        from app.services.fund_service import FundDividendService
        
        # 如果强制更新，先清空现有数据并从API重新拉取
        if force_update:
            # 删除现有分红数据
            db.query(FundDividend).filter(FundDividend.fund_code == fund_code).delete()
            db.commit()
            
            # 从API拉取最新分红数据
            import akshare as ak
            import pandas as pd
            try:
                print(f"[调试] 强制更新分红数据: {fund_code}")
                df = ak.fund_fh_em()
                df = df[df['基金代码'] == fund_code]
                
                if not df.empty:
                    dividend_data = []
                    for _, row in df.iterrows():
                        try:
                            dividend_data.append({
                                'dividend_date': pd.to_datetime(row['权益登记日']).date(),
                                'record_date': pd.to_datetime(row['权益登记日']).date(),
                                'dividend_amount': float(row['分红']) if pd.notna(row['分红']) else 0,
                                'total_dividend': None,
                                'announcement_date': None
                            })
                        except Exception as e:
                            print(f"[调试] 转换分红数据失败: {e}")
                            continue
                    
                    if dividend_data:
                        saved_count = FundDividendService.save_dividend_data(db, fund_code, dividend_data)
                        print(f"[调试] 强制更新保存了 {saved_count} 条分红记录")
                
            except Exception as e:
                print(f"[调试] 强制更新分红数据失败: {e}")
        
        # 查询分红数据
        dividends = FundDividendService.get_dividends_by_fund(db, fund_code, start_date, end_date)
        
        data = [
            {
                "id": div.id,
                "fund_code": div.fund_code,
                "dividend_date": str(div.dividend_date),
                "record_date": str(div.record_date) if div.record_date else None,
                "dividend_amount": float(div.dividend_amount) if div.dividend_amount else None,
                "total_dividend": float(div.total_dividend) if div.total_dividend else None,
                "announcement_date": str(div.announcement_date) if div.announcement_date else None,
                "created_at": div.created_at.isoformat() if div.created_at else None
            }
            for div in dividends
        ]
        
        return BaseResponse(
            success=True, 
            message=f"获取到 {len(data)} 条分红记录", 
            data={"dividends": data}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/dividends/{fund_code}/sync", response_model=BaseResponse)
async def sync_fund_dividends(
    fund_code: str,
    db: Session = Depends(get_db)
):
    """同步基金分红数据"""
    try:
        from app.services.fund_service import FundDividendService
        import akshare as ak
        import pandas as pd
        
        print(f"[调试] 开始同步分红数据: {fund_code}")
        
        # 使用异步方式拉取数据，避免阻塞
        import asyncio
        import concurrent.futures
        
        def fetch_dividend_data():
            try:
                df = ak.fund_fh_em()
                df = df[df['基金代码'] == fund_code]
                return df
            except Exception as e:
                print(f"[调试] 拉取分红数据失败: {e}")
                return pd.DataFrame()
        
        # 在线程池中执行akshare调用
        with concurrent.futures.ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(executor, fetch_dividend_data)
        
        if df.empty:
            return BaseResponse(
                success=True,
                message="未找到分红数据",
                data={"saved_count": 0}
            )
        
        # 转换数据格式
        dividend_data = []
        for _, row in df.iterrows():
            try:
                dividend_data.append({
                    'dividend_date': pd.to_datetime(row['权益登记日']).date(),
                    'record_date': pd.to_datetime(row['权益登记日']).date(),
                    'dividend_amount': float(row['分红']) if pd.notna(row['分红']) else 0,
                    'total_dividend': None,
                    'announcement_date': None
                })
            except Exception as e:
                print(f"[调试] 转换分红数据失败: {e}")
                continue
        
        # 保存到数据库
        saved_count = FundDividendService.save_dividend_data(db, fund_code, dividend_data)
        
        print(f"[调试] 分红数据同步完成，保存了 {saved_count} 条记录")
        
        return BaseResponse(
            success=True,
            message=f"同步分红数据成功，保存了 {saved_count} 条记录",
            data={"saved_count": saved_count}
        )
    except Exception as e:
        print(f"[调试] 同步分红数据异常: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/dca/plans/update-pending", response_model=BaseResponse)
def update_pending_operations(
    db: Session = Depends(get_db)
):
    """更新所有待确认的定投操作记录"""
    try:
        updated_count = DCAService.update_pending_operations(db)
        return BaseResponse(
            success=True,
            message=f"更新了 {updated_count} 条待确认的操作记录",
            data={"updated_count": updated_count}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/dca/plans/{plan_id}/generate-history", response_model=BaseResponse)
def generate_historical_operations(
    plan_id: int,
    end_date: Optional[date] = Query(None, description="结束日期，默认为计划结束日期或今天"),
    exclude_dates: Optional[List[str]] = Query(None, description="排除的日期列表（如定投失败日）"),
    db: Session = Depends(get_db)
):
    """批量生成历史定投记录"""
    from datetime import datetime
    try:
        print(f"[历史生成] exclude_dates原始: {exclude_dates}, 类型: {type(exclude_dates)}")
        if exclude_dates:
            for i, d in enumerate(exclude_dates):
                print(f"[历史生成] exclude_dates[{i}]: {d}, 类型: {type(d)}")
        # 如果未传exclude_dates，则自动用计划本身的exclude_dates
        if exclude_dates is None:
            plan = DCAService.get_dca_plan_by_id(db, plan_id)
            if plan and plan.get('exclude_dates'):
                exclude_dates = plan['exclude_dates']
        # 强制转换exclude_dates为date类型
        exclude_dates_parsed = []
        if exclude_dates:
            for d in exclude_dates:
                # 兼容直接传date类型
                if isinstance(d, str):
                    exclude_dates_parsed.append(datetime.strptime(d, "%Y-%m-%d").date())
                elif isinstance(d, date):
                    exclude_dates_parsed.append(d)
                else:
                    try:
                        exclude_dates_parsed.append(datetime.strptime(str(d), "%Y-%m-%d").date())
                    except Exception as e:
                        print(f"[历史生成] exclude_dates解析失败: {d}, 错误: {e}")
        print(f"[历史生成] exclude_dates_parsed: {exclude_dates_parsed}, 类型: {type(exclude_dates_parsed)}")
        created_count = DCAService.generate_historical_operations(db, plan_id, end_date, exclude_dates=exclude_dates_parsed)
        
        # 重新计算持仓（生成历史操作记录会影响持仓）
        try:
            recalculate_result = FundOperationService.recalculate_all_positions(db)
            if recalculate_result["success"]:
                return BaseResponse(
                    success=True,
                    message=f"生成了 {created_count} 条历史定投记录，持仓已重新计算",
                    data={"created_count": created_count}
                )
            else:
                return BaseResponse(
                    success=True,
                    message=f"生成了 {created_count} 条历史定投记录，但持仓重新计算失败",
                    data={"created_count": created_count}
                )
        except Exception as e:
            print(f"重新计算持仓失败: {e}")
            return BaseResponse(
                success=True,
                message=f"生成了 {created_count} 条历史定投记录，但持仓重新计算失败",
                data={"created_count": created_count}
            )
    except Exception as e:
        import traceback
        print(f"[历史生成] 生成历史异常: {e}")
        print(f"[历史生成] 异常堆栈: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/dca/plans/update-status", response_model=BaseResponse)
def update_plan_statuses(
    db: Session = Depends(get_db)
):
    """批量更新定投计划状态"""
    try:
        updated_count = DCAService.update_all_plan_statuses(db)
        return BaseResponse(
            success=True,
            message=f"更新了 {updated_count} 个定投计划状态",
            data={"updated_count": updated_count}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/dca/plans/{plan_id}/operations", response_model=BaseResponse)
def delete_plan_operations(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """删除定投计划的所有操作记录"""
    try:
        deleted_count = DCAService.delete_plan_operations(db, plan_id)
        
        # 重新计算持仓（删除操作记录会影响持仓）
        try:
            recalculate_result = FundOperationService.recalculate_all_positions(db)
            if recalculate_result["success"]:
                return BaseResponse(
                    success=True,
                    message=f"删除了 {deleted_count} 条操作记录，持仓已重新计算",
                    data={"deleted_count": deleted_count}
                )
            else:
                return BaseResponse(
                    success=True,
                    message=f"删除了 {deleted_count} 条操作记录，但持仓重新计算失败",
                    data={"deleted_count": deleted_count}
                )
        except Exception as e:
            print(f"重新计算持仓失败: {e}")
            return BaseResponse(
                success=True,
                message=f"删除了 {deleted_count} 条操作记录，但持仓重新计算失败",
                data={"deleted_count": deleted_count}
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/dca/plans/{plan_id}/update-statistics", response_model=BaseResponse)
def update_plan_statistics(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """手动更新定投计划统计信息"""
    try:
        success = DCAService.update_plan_statistics(db, plan_id)
        if success:
            return BaseResponse(
                success=True,
                message="定投计划统计信息更新成功"
            )
        else:
            raise HTTPException(status_code=404, detail="定投计划不存在")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/dca/plans/{plan_id}/clean-operations", response_model=BaseResponse)
def clean_plan_operations(
    plan_id: int,
    start_date: date = Query(..., description="新的开始日期"),
    end_date: date = Query(..., description="新的结束日期"),
    db: Session = Depends(get_db)
):
    """清理定投计划超出新区间的历史操作记录"""
    try:
        deleted_count = DCAService.clean_plan_operations_by_date_range(db, plan_id, start_date, end_date)
        
        # 重新计算持仓（清理操作记录会影响持仓）
        try:
            recalculate_result = FundOperationService.recalculate_all_positions(db)
            if recalculate_result["success"]:
                return BaseResponse(
                    success=True,
                    message=f"清理了 {deleted_count} 条超出区间的历史操作记录，持仓已重新计算",
                    data={"deleted_count": deleted_count}
                )
            else:
                return BaseResponse(
                    success=True,
                    message=f"清理了 {deleted_count} 条超出区间的历史操作记录，但持仓重新计算失败",
                    data={"deleted_count": deleted_count}
                )
        except Exception as e:
            print(f"重新计算持仓失败: {e}")
            return BaseResponse(
                success=True,
                message=f"清理了 {deleted_count} 条超出区间的历史操作记录，但持仓重新计算失败",
                data={"deleted_count": deleted_count}
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/operations/{operation_id}/process-dividend", response_model=BaseResponse)
def process_dividend_operation(
    operation_id: int,
    process_type: str = Query(..., description="处理方式: reinvest(转投入), withdraw(提现), skip(暂不处理)"),
    db: Session = Depends(get_db)
):
    """处理分红操作"""
    try:
        # 查找分红操作记录
        operation = db.query(UserOperation).filter(
            and_(
                UserOperation.id == operation_id,
                UserOperation.operation_type == "dividend"
            )
        ).first()
        
        if not operation:
            raise HTTPException(status_code=404, detail="分红操作记录不存在")
        
        if process_type == "reinvest":
            # 转投入：创建买入操作
            buy_operation = UserOperation(
                operation_date=operation.operation_date,
                platform=operation.platform,
                asset_type=operation.asset_type,
                operation_type="buy",
                asset_code=operation.asset_code,
                asset_name=operation.asset_name,
                amount=operation.amount,
                currency=operation.currency,
                strategy=f"分红转投入: {operation.notes or '分红转投入'}",
                status="pending"
            )
            db.add(buy_operation)
            operation.status = "processed"
            operation.notes = f"{operation.notes or ''} - 已转投入"
            
        elif process_type == "withdraw":
            # 提现：创建卖出操作
            sell_operation = UserOperation(
                operation_date=operation.operation_date,
                platform=operation.platform,
                asset_type=operation.asset_type,
                operation_type="sell",
                asset_code=operation.asset_code,
                asset_name=operation.asset_name,
                amount=operation.amount,
                currency=operation.currency,
                strategy=f"分红提现: {operation.notes or '分红提现'}",
                status="confirmed"
            )
            db.add(sell_operation)
            operation.status = "processed"
            operation.notes = f"{operation.notes or ''} - 已提现"
            
        elif process_type == "skip":
            # 暂不处理：标记为已处理
            operation.status = "processed"
            operation.notes = f"{operation.notes or ''} - 暂不处理"
            
        else:
            raise HTTPException(status_code=400, detail="无效的处理方式")
        
        db.commit()
        
        return BaseResponse(
            success=True,
            message="分红处理成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# 定时任务管理API
# 删除以下冲突的路由，统一使用 scheduler.py 中的新接口
# @router.get("/scheduler/jobs", response_model=BaseResponse)
# def get_scheduler_jobs():
#     """获取所有定时任务信息"""
#     try:
#         jobs = scheduler_service.get_jobs()
#         return BaseResponse(
#             success=True,
#             message="获取定时任务信息成功",
#             data={"jobs": jobs}
#         )
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.post("/scheduler/jobs/{job_id}/update", response_model=BaseResponse)
# def update_job_schedule(
#     job_id: str,
#     hour: int = Query(..., ge=0, le=23, description="小时"),
#     minute: int = Query(..., ge=0, le=59, description="分钟")
# ):
#     """更新定时任务执行时间"""
#     try:
#         success = scheduler_service.update_job_schedule(job_id, hour, minute)
#         if success:
#             return BaseResponse(
#                 success=True,
#                 message=f"任务 {job_id} 执行时间已更新为 {hour:02d}:{minute:02d}"
#             )
#         else:
#             raise HTTPException(status_code=400, detail="更新任务执行时间失败")
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.post("/scheduler/start", response_model=BaseResponse)
# async def start_scheduler():
#     """启动定时任务调度器"""
#     try:
#         await scheduler_service.start_async()
#         return BaseResponse(
#             success=True,
#             message="定时任务调度器已启动"
#         )
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.post("/scheduler/stop", response_model=BaseResponse)
# async def stop_scheduler():
#     """停止定时任务调度器"""
#     try:
#         await scheduler_service.stop_async()
#         return BaseResponse(
#             success=True,
#             message="定时任务调度器已停止"
#         )
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.post("/scheduler/restart", response_model=BaseResponse)
# async def restart_scheduler():
#     """重启定时任务调度器"""
#     try:
#         await scheduler_service.restart_async()
#         return BaseResponse(
#             success=True,
#             message="定时任务调度器已重启"
#         )
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.post("/scheduler/update-navs", response_model=BaseResponse)
# async def manual_update_navs():
#     """手动执行净值更新任务"""
#     try:
#         await scheduler_service._update_fund_navs()
#         return BaseResponse(
#             success=True,
#             message="手动净值更新任务执行完成"
#         )
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


@router.get("/okx/account", response_model=BaseResponse)
async def get_okx_account():
    """获取OKX账户资产信息"""
    try:
        service = OKXAPIService()
        data = await service.get_account_balance()
        if data is None:
            return BaseResponse(success=False, message="OKX账户资产获取失败，请检查API配置", data=None)
        return BaseResponse(success=True, message="OKX账户资产获取成功", data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/okx/positions", response_model=BaseResponse)
async def get_okx_positions():
    """获取OKX持仓信息"""
    try:
        service = OKXAPIService()
        data = await service.get_account_positions()
        if data is None:
            return BaseResponse(success=False, message="OKX持仓信息获取失败，请检查API配置", data=None)
        return BaseResponse(success=True, message="OKX持仓信息获取成功", data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/okx/bills", response_model=BaseResponse)
async def get_okx_bills(
    inst_type: Optional[str] = Query(None, description="产品类型"),
    limit: int = Query(100, ge=1, le=100, description="返回结果数量")
):
    """获取OKX账单流水"""
    try:
        service = OKXAPIService()
        data = await service.get_bills(inst_type=inst_type, limit=limit)
        if data is None:
            return BaseResponse(success=False, message="OKX账单流水获取失败，请检查API配置", data=None)
        return BaseResponse(success=True, message="OKX账单流水获取成功", data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/okx/ticker", response_model=BaseResponse)
async def get_okx_ticker(inst_id: str):
    """获取OKX币种行情"""
    try:
        service = OKXAPIService()
        data = await service.get_ticker(inst_id)
        if data is None:
            return BaseResponse(success=False, message="OKX行情获取失败", data=None)
        return BaseResponse(success=True, message="OKX行情获取成功", data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/okx/tickers", response_model=BaseResponse)
async def get_okx_all_tickers(inst_type: str = Query("SPOT", description="产品类型")):
    """获取OKX所有币种行情"""
    try:
        service = OKXAPIService()
        data = await service.get_all_tickers(inst_type=inst_type)
        if data is None:
            return BaseResponse(success=False, message="OKX行情获取失败", data=None)
        return BaseResponse(success=True, message="OKX行情获取成功", data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/okx/instruments", response_model=BaseResponse)
async def get_okx_instruments(inst_type: str = Query("SPOT", description="产品类型")):
    """获取OKX交易产品基础信息"""
    try:
        service = OKXAPIService()
        data = await service.get_instruments(inst_type=inst_type)
        if data is None:
            return BaseResponse(success=False, message="OKX交易产品信息获取失败", data=None)
        return BaseResponse(success=True, message="OKX交易产品信息获取成功", data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/okx/config", response_model=BaseResponse)
async def get_okx_config():
    """获取OKX API配置信息"""
    try:
        service = OKXAPIService()
        data = await service.get_config()
        return BaseResponse(success=True, message="OKX配置信息获取成功", data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/okx/test", response_model=BaseResponse)
async def test_okx_connection():
    """测试OKX API连接状态"""
    try:
        service = OKXAPIService()
        data = await service.test_connection()
        success = data.get("public_api", False) or data.get("private_api", False)
        message = "OKX连接测试完成"
        if not success:
            message += " - 连接失败"
        return BaseResponse(success=success, message=message, data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/okx/asset-balances", response_model=BaseResponse)
async def get_okx_asset_balances(ccy: Optional[str] = Query(None, description="币种")):
    """获取OKX资金账户余额 (GET /api/v5/asset/balances)"""
    try:
        service = OKXAPIService()
        data = await service.get_asset_balances(ccy=ccy)
        if data is None:
            return BaseResponse(success=False, message="OKX资金账户余额获取失败，请检查API配置", data=None)
        return BaseResponse(success=True, message="OKX资金账户余额获取成功", data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/okx/savings-balance", response_model=BaseResponse)
async def get_okx_savings_balance(ccy: Optional[str] = Query(None, description="币种")):
    """获取OKX储蓄账户余额 (GET /api/v5/finance/savings/balance)"""
    try:
        service = OKXAPIService()
        data = await service.get_savings_balance(ccy=ccy)
        if data is None:
            return BaseResponse(success=False, message="OKX储蓄账户余额获取失败，请检查API配置", data=None)
        return BaseResponse(success=True, message="OKX储蓄账户余额获取成功", data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/nav/batch-latest", response_model=BaseResponse)
def get_batch_latest_nav(
    fund_codes: List[str],
    db: Session = Depends(get_db)
):
    """批量获取基金最新净值 - 优化性能"""
    try:
        nav_map = {}
        
        # 批量查询数据库中的最新净值
        for fund_code in fund_codes:
            try:
                latest_nav_obj = FundNavService.get_latest_nav(db, fund_code)
                if latest_nav_obj and latest_nav_obj.nav:
                    nav_map[fund_code] = {
                        "nav": float(latest_nav_obj.nav),
                        "nav_date": latest_nav_obj.nav_date.isoformat(),
                        "accumulated_nav": float(latest_nav_obj.accumulated_nav) if latest_nav_obj.accumulated_nav else None,
                        "growth_rate": float(latest_nav_obj.growth_rate) if latest_nav_obj.growth_rate else None,
                        "source": latest_nav_obj.source
                    }
            except Exception as e:
                print(f"[调试] 获取基金 {fund_code} 最新净值失败: {e}")
                continue
        
        return BaseResponse(
            success=True,
            message=f"获取到 {len(nav_map)} 个基金的最新净值",
            data={"nav_map": nav_map}
        )
    except Exception as e:
        print(f"[调试] 批量获取净值异常: {e}")
        raise HTTPException(status_code=400, detail=str(e)) 

@router.get("/operations/export-csv")
def export_fund_operations_csv(
    fund_code: Optional[str] = Query(None, description="基金代码，不填则导出所有基金"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    operation_type: Optional[str] = Query(None, description="操作类型"),
    include_nav: bool = Query(True, description="是否包含净值信息"),
    include_dividend: bool = Query(True, description="是否包含分红信息"),
    db: Session = Depends(get_db)
):
    """导出基金操作记录为CSV文件，包含所有计算因素"""
    from fastapi.responses import StreamingResponse
    import csv
    import io
    from datetime import datetime
    
    try:
        # 获取所有操作记录（不分页）
        operations, total = FundOperationService.get_operations(
            db=db,
            fund_code=fund_code,
            operation_type=operation_type,
            start_date=start_date,
            end_date=end_date,
            page=1,
            page_size=10000  # 获取大量数据
        )
        
        if not operations:
            raise HTTPException(status_code=404, detail="没有找到符合条件的操作记录")
        
        # 创建CSV文件
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入CSV头部
        headers = [
            "操作ID", "操作日期", "平台", "资产类型", "操作类型", "基金代码", "基金名称",
            "金额", "货币", "数量", "价格", "净值", "手续费", "策略", "情绪评分",
            "标签", "备注", "状态", "定投计划ID", "定投执行类型", "创建时间", "更新时间"
        ]
        
        # 如果需要包含净值信息，添加净值相关字段
        if include_nav:
            headers.extend([
                "净值日期", "累计净值", "净值增长率", "净值来源"
            ])
        
        # 如果需要包含分红信息，添加分红相关字段
        if include_dividend:
            headers.extend([
                "分红日期", "分红金额", "总分红", "公告日期"
            ])
        
        writer.writerow(headers)
        
        # 批量获取净值信息
        fund_codes = list(set(op.asset_code for op in operations))
        nav_map = {}
        if include_nav and fund_codes:
            for fund_code in fund_codes:
                nav_records = FundNavService.get_nav_history(db, fund_code, days=365)
                nav_map[fund_code] = {nav.nav_date: nav for nav in nav_records}
        
        # 批量获取分红信息
        dividend_map = {}
        if include_dividend and fund_codes:
            for fund_code in fund_codes:
                dividend_records = FundDividendService.get_dividends_by_fund(
                    db, fund_code, start_date=start_date, end_date=end_date
                )
                dividend_map[fund_code] = {div.dividend_date: div for div in dividend_records}
        
        # 写入数据行
        for operation in operations:
            row = [
                operation.id,
                operation.operation_date.strftime("%Y-%m-%d %H:%M:%S") if operation.operation_date else "",
                operation.platform,
                operation.asset_type,
                operation.operation_type,
                operation.asset_code,
                operation.asset_name,
                float(operation.amount) if operation.amount else 0,
                operation.currency,
                float(operation.quantity) if operation.quantity else 0,
                float(operation.price) if operation.price else 0,
                float(operation.nav) if operation.nav else 0,
                float(operation.fee) if operation.fee else 0,
                operation.strategy or "",
                operation.emotion_score or 0,
                operation.tags or "",
                operation.notes or "",
                operation.status,
                operation.dca_plan_id or "",
                operation.dca_execution_type or "",
                operation.created_at.strftime("%Y-%m-%d %H:%M:%S") if operation.created_at else "",
                operation.updated_at.strftime("%Y-%m-%d %H:%M:%S") if operation.updated_at else ""
            ]
            
            # 添加净值信息
            if include_nav:
                nav_date = operation.operation_date.date() if operation.operation_date else None
                nav_info = nav_map.get(operation.asset_code, {}).get(nav_date) if nav_date else None
                
                row.extend([
                    nav_info.nav_date.strftime("%Y-%m-%d") if nav_info and nav_info.nav_date else "",
                    float(nav_info.accumulated_nav) if nav_info and nav_info.accumulated_nav else "",
                    float(nav_info.growth_rate) if nav_info and nav_info.growth_rate else "",
                    nav_info.source if nav_info else ""
                ])
            
            # 添加分红信息
            if include_dividend:
                op_date = operation.operation_date.date() if operation.operation_date else None
                dividend_info = dividend_map.get(operation.asset_code, {}).get(op_date) if op_date else None
                
                row.extend([
                    dividend_info.dividend_date.strftime("%Y-%m-%d") if dividend_info and dividend_info.dividend_date else "",
                    float(dividend_info.dividend_amount) if dividend_info and dividend_info.dividend_amount else "",
                    float(dividend_info.total_dividend) if dividend_info and dividend_info.total_dividend else "",
                    dividend_info.announcement_date.strftime("%Y-%m-%d") if dividend_info and dividend_info.announcement_date else ""
                ])
            
            writer.writerow(row)
        
        # 准备文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fund_suffix = f"_{fund_code}" if fund_code else "_all"
        filename = f"fund_operations{fund_suffix}_{timestamp}.csv"
        
        # 返回CSV文件
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),  # 使用UTF-8-BOM确保Excel正确显示中文
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        print(f"导出CSV失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.get("/positions/export-csv")
def export_fund_positions_csv(
    db: Session = Depends(get_db)
):
    """导出基金持仓信息为CSV文件"""
    from fastapi.responses import StreamingResponse
    import csv
    import io
    from datetime import datetime
    
    try:
        # 获取所有持仓信息
        positions = FundOperationService.get_fund_positions(db)
        
        if not positions:
            raise HTTPException(status_code=404, detail="没有找到持仓信息")
        
        # 创建CSV文件
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入CSV头部
        headers = [
            "持仓ID", "平台", "资产类型", "基金代码", "基金名称", "货币",
            "持仓数量", "平均成本", "当前价格", "当前价值", "总投入", "总盈亏", "盈亏率",
            "最后更新时间"
        ]
        writer.writerow(headers)
        
        # 写入数据行
        for position in positions:
            row = [
                position.id,
                position.platform,
                position.asset_type,
                position.asset_code,
                position.asset_name,
                position.currency,
                float(position.quantity) if position.quantity else 0,
                float(position.avg_cost) if position.avg_cost else 0,
                float(position.current_price) if position.current_price else 0,
                float(position.current_value) if position.current_value else 0,
                float(position.total_invested) if position.total_invested else 0,
                float(position.total_profit) if position.total_profit else 0,
                float(position.profit_rate) if position.profit_rate else 0,
                position.last_updated.strftime("%Y-%m-%d %H:%M:%S") if position.last_updated else ""
            ]
            writer.writerow(row)
        
        # 准备文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fund_positions_{timestamp}.csv"
        
        # 返回CSV文件
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        print(f"导出持仓CSV失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.get("/nav/{fund_code}/estimate", response_model=BaseResponse)
async def get_fund_estimate(
    fund_code: str,
    db: Session = Depends(get_db)
):
    """获取基金当天估算净值（不入库）"""
    try:
        from app.services.fund_api_service import FundAPIService
        
        # 调用天天基金API获取估算数据
        api_service = FundAPIService()
        nav_data = await api_service.get_fund_nav_latest_tiantian(fund_code)
        
        if not nav_data:
            return BaseResponse(
                success=False, 
                message=f"获取基金 {fund_code} 估算数据失败",
                data=None
            )
        
        # 构建返回数据
        estimate_data = {
            "fund_code": fund_code,
            "estimate_nav": nav_data.get('gsz'),  # 估算净值
            "estimate_time": nav_data.get('gztime'),  # 估算时间
            "confirmed_nav": nav_data.get('dwjz'),  # 确认净值
            "confirmed_date": nav_data.get('jzrq'),  # 确认日期
            "growth_rate": nav_data.get('gszzl'),  # 涨跌幅
            "source": "tiantian_estimated"
        }
        
        return BaseResponse(
            success=True,
            message=f"获取基金 {fund_code} 估算数据成功",
            data=estimate_data
        )
        
    except Exception as e:
        print(f"获取基金估算数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取估算数据失败: {str(e)}")


@router.get("/nav-stats", response_model=BaseResponse)
def get_nav_data_stats(db: Session = Depends(get_db)):
    """获取净值数据统计信息"""
    try:
        from sqlalchemy import func
        
        # 统计数据来源分布
        source_stats = db.query(
            FundNav.source,
            func.count(FundNav.id).label('count')
        ).group_by(FundNav.source).all()
        
        # 统计基金数量
        fund_count = db.query(func.count(func.distinct(FundNav.fund_code))).scalar()
        
        # 统计总记录数
        total_count = db.query(func.count(FundNav.id)).scalar()
        
        # 构建统计结果
        stats = {
            'total_count': total_count,
            'fund_count': fund_count,
            'source_distribution': {}
        }
        
        for source, count in source_stats:
            stats['source_distribution'][source] = count
            if source == 'akshare':
                stats['akshare_count'] = count
            elif source == 'api':
                stats['api_count'] = count
        
        return BaseResponse(
            success=True,
            message="获取数据统计成功",
            data=stats
        )
        
    except Exception as e:
        print(f"获取数据统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据统计失败: {str(e)}")


@router.delete("/nav-source/{source}", response_model=BaseResponse)
def delete_nav_by_source(source: str, db: Session = Depends(get_db)):
    """删除指定来源的净值数据"""
    try:
        # 安全检查：只允许删除api来源的数据
        if source != 'api':
            raise HTTPException(status_code=400, detail="只能删除api来源的数据")
        
        # 删除指定来源的数据
        deleted_count = db.query(FundNav).filter(FundNav.source == source).delete()
        db.commit()
        
        return BaseResponse(
            success=True,
            message=f"成功删除 {deleted_count} 条{source}来源的数据",
            data={'deleted_count': deleted_count}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"删除数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除数据失败: {str(e)}")


@router.post("/nav/{fund_code}/incremental-update", response_model=BaseResponse)
def incremental_update_nav(fund_code: str, db: Session = Depends(get_db)):
    """增量更新基金净值数据"""
    try:
        # 获取最新的净值日期
        latest_nav = db.query(FundNav).filter(
            FundNav.fund_code == fund_code,
            FundNav.source == 'akshare'
        ).order_by(FundNav.nav_date.desc()).first()
        
        latest_date = latest_nav.nav_date if latest_nav else None
        
        # 使用akshare获取增量数据
        import akshare as ak
        df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
        
        new_count = 0
        if not df.empty:
            for _, row in df.iterrows():
                nav_date = row['净值日期']
                nav_value = row['单位净值']
                
                # 检查是否已存在该日期的数据
                existing = db.query(FundNav).filter(
                    FundNav.fund_code == fund_code,
                    FundNav.nav_date == nav_date,
                    FundNav.source == 'akshare'
                ).first()
                
                if not existing:
                    # 创建新记录
                    nav_record = FundNavService.create_nav(
                        db, fund_code, nav_date, nav_value, source="akshare"
                    )
                    if nav_record:
                        new_count += 1
        
        return BaseResponse(
            success=True,
            message=f"增量更新成功，新增 {new_count} 条记录",
            data={'new_count': new_count}
        )
        
    except Exception as e:
        print(f"增量更新失败: {e}")
        raise HTTPException(status_code=500, detail=f"增量更新失败: {str(e)}") 