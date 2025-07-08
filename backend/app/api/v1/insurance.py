from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.utils.database import get_db
from app.models.schemas import (
    # 保险产品相关
    InsuranceProductCreate, InsuranceProductUpdate, InsuranceProduct,
    InsuranceProductResponse, InsuranceProductListResponse,
    
    # 保险保单相关
    InsurancePolicyCreate, InsurancePolicyUpdate, InsurancePolicy, PolicyValueUpdate,
    InsurancePolicyResponse, InsurancePolicyListResponse,
    
    # 保险操作相关
    InsuranceOperationCreate, InsuranceOperation, PremiumPaymentCreate, 
    TopUpCreate, WithdrawalCreate,
    InsuranceOperationResponse, InsuranceOperationListResponse,
    
    # 保险收益相关
    InsuranceReturnCreate, InsuranceReturn, DividendProcessCreate,
    InsuranceReturnResponse, InsuranceReturnListResponse,
    
    # 统计相关
    InsuranceStatisticsResponse, PolicyPerformanceResponse, ReturnsAnalysisResponse,
    
    # 基础响应
    BaseResponse
)
from app.services.insurance_service import (
    InsuranceProductService, InsurancePolicyService, InsuranceOperationService,
    UniversalLifeService, HongKongInsuranceService, InsuranceStatisticsService
)

router = APIRouter()


# ============ 保险产品管理API ============

@router.post("/products", response_model=InsuranceProductResponse)
def create_insurance_product(
    product: InsuranceProductCreate,
    db: Session = Depends(get_db)
):
    """创建保险产品"""
    try:
        result = InsuranceProductService.create_product(db, product)
        return InsuranceProductResponse(
            success=True,
            message="保险产品创建成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/products", response_model=InsuranceProductListResponse)
def get_insurance_products(
    company: Optional[str] = Query(None, description="保险公司"),
    product_type: Optional[str] = Query(None, description="产品类型"),
    db: Session = Depends(get_db)
):
    """获取保险产品列表"""
    try:
        products = InsuranceProductService.get_products(db, company, product_type)
        return InsuranceProductListResponse(
            success=True,
            message=f"获取到 {len(products)} 个保险产品",
            data=products,
            total=len(products)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/products/{product_code}", response_model=InsuranceProductResponse)
def get_insurance_product(
    product_code: str,
    db: Session = Depends(get_db)
):
    """获取保险产品详情"""
    try:
        product = InsuranceProductService.get_product(db, product_code)
        if not product:
            raise HTTPException(status_code=404, detail="保险产品不存在")
        
        return InsuranceProductResponse(
            success=True,
            message="获取保险产品成功",
            data=product
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/products/{product_code}", response_model=InsuranceProductResponse)
def update_insurance_product(
    product_code: str,
    update_data: InsuranceProductUpdate,
    db: Session = Depends(get_db)
):
    """更新保险产品"""
    try:
        result = InsuranceProductService.update_product(db, product_code, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="保险产品不存在")
        
        return InsuranceProductResponse(
            success=True,
            message="保险产品更新成功",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ 保险保单管理API ============

@router.post("/policies", response_model=InsurancePolicyResponse)
def create_insurance_policy(
    policy: InsurancePolicyCreate,
    db: Session = Depends(get_db)
):
    """创建保险保单"""
    try:
        result = InsurancePolicyService.create_policy(db, policy)
        return InsurancePolicyResponse(
            success=True,
            message="保险保单创建成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/policies", response_model=InsurancePolicyListResponse)
def get_insurance_policies(
    status: Optional[str] = Query(None, description="保单状态"),
    company: Optional[str] = Query(None, description="保险公司"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取保险保单列表"""
    try:
        policies, total = InsurancePolicyService.get_policies(
            db, status, company, page, page_size
        )
        return InsurancePolicyListResponse(
            success=True,
            message=f"获取到 {len(policies)} 个保单",
            data=policies,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/policies/{policy_id}", response_model=InsurancePolicyResponse)
def get_insurance_policy(
    policy_id: int,
    db: Session = Depends(get_db)
):
    """获取保险保单详情"""
    try:
        policy = InsurancePolicyService.get_policy(db, policy_id)
        if not policy:
            raise HTTPException(status_code=404, detail="保单不存在")
        
        return InsurancePolicyResponse(
            success=True,
            message="获取保单成功",
            data=policy
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/policies/{policy_id}", response_model=InsurancePolicyResponse)
def update_insurance_policy(
    policy_id: int,
    update_data: InsurancePolicyUpdate,
    db: Session = Depends(get_db)
):
    """更新保险保单"""
    try:
        result = InsurancePolicyService.update_policy(db, policy_id, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="保单不存在")
        
        return InsurancePolicyResponse(
            success=True,
            message="保单更新成功",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/policies/{policy_id}/value", response_model=InsurancePolicyResponse)
def update_policy_value(
    policy_id: int,
    value_update: PolicyValueUpdate,
    db: Session = Depends(get_db)
):
    """更新保单价值"""
    try:
        result = InsurancePolicyService.update_policy_value(db, policy_id, value_update)
        if not result:
            raise HTTPException(status_code=404, detail="保单不存在")
        
        return InsurancePolicyResponse(
            success=True,
            message="保单价值更新成功",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ 保险操作记录API ============

@router.post("/operations", response_model=InsuranceOperationResponse)
def create_insurance_operation(
    operation: InsuranceOperationCreate,
    db: Session = Depends(get_db)
):
    """创建保险操作记录"""
    try:
        result = InsuranceOperationService.create_operation(db, operation)
        return InsuranceOperationResponse(
            success=True,
            message="保险操作记录创建成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/operations", response_model=InsuranceOperationListResponse)
def get_insurance_operations(
    policy_id: Optional[int] = Query(None, description="保单ID"),
    operation_type: Optional[str] = Query(None, description="操作类型"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取保险操作记录"""
    try:
        operations, total = InsuranceOperationService.get_operations(
            db, policy_id, operation_type, start_date, end_date, page, page_size
        )
        return InsuranceOperationListResponse(
            success=True,
            message=f"获取到 {len(operations)} 条操作记录",
            data=operations,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/operations/{policy_id}/premium", response_model=InsuranceOperationResponse)
def pay_premium(
    policy_id: int,
    premium_payment: PremiumPaymentCreate,
    db: Session = Depends(get_db)
):
    """缴费操作"""
    try:
        result = InsuranceOperationService.pay_premium(db, policy_id, premium_payment)
        return InsuranceOperationResponse(
            success=True,
            message="保费缴纳成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/operations/{policy_id}/topup", response_model=InsuranceOperationResponse)
def top_up_policy(
    policy_id: int,
    topup: TopUpCreate,
    db: Session = Depends(get_db)
):
    """追加投资"""
    try:
        result = InsuranceOperationService.top_up_policy(db, policy_id, topup)
        return InsuranceOperationResponse(
            success=True,
            message="追加投资成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/operations/{policy_id}/withdrawal", response_model=InsuranceOperationResponse)
def partial_withdrawal(
    policy_id: int,
    withdrawal: WithdrawalCreate,
    db: Session = Depends(get_db)
):
    """部分提取"""
    try:
        result = InsuranceOperationService.partial_withdrawal(db, policy_id, withdrawal)
        return InsuranceOperationResponse(
            success=True,
            message="部分提取成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ 收益管理API ============

@router.post("/returns/calculate-monthly/{policy_id}", response_model=BaseResponse)
def calculate_monthly_interest(
    policy_id: int,
    calculation_date: date = Query(..., description="计算日期"),
    db: Session = Depends(get_db)
):
    """计算月度利息（万能险）"""
    try:
        result = UniversalLifeService.calculate_monthly_interest(db, policy_id, calculation_date)
        return BaseResponse(
            success=True,
            message="月度利息计算成功",
            data={
                "return_id": result.id,
                "interest_amount": float(result.return_amount),
                "return_rate": float(result.return_rate) if result.return_rate else None
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/returns/process-dividend/{policy_id}", response_model=BaseResponse)
def process_annual_dividend(
    policy_id: int,
    dividend_data: DividendProcessCreate,
    db: Session = Depends(get_db)
):
    """处理年度分红（港险）"""
    try:
        result = HongKongInsuranceService.process_annual_dividend(db, policy_id, dividend_data)
        return BaseResponse(
            success=True,
            message="年度分红处理成功",
            data={
                "return_id": result.id,
                "dividend_amount": float(result.return_amount),
                "distribution_method": result.distribution_method
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ 统计分析API ============

@router.get("/statistics/summary", response_model=InsuranceStatisticsResponse)
def get_insurance_summary(db: Session = Depends(get_db)):
    """获取保险投资汇总"""
    try:
        summary_data = InsuranceStatisticsService.get_insurance_summary(db)
        
        from app.models.schemas import InsuranceStatistics
        summary = InsuranceStatistics(
            total_policies=summary_data["total_policies"],
            total_invested=summary_data["total_invested"],
            total_current_value=summary_data["total_current_value"],
            total_profit=summary_data["total_profit"],
            total_profit_rate=summary_data["total_profit_rate"],
            universal_life_count=summary_data["universal_life_count"],
            whole_life_count=summary_data["whole_life_count"],
            endowment_count=summary_data["endowment_count"]
        )
        
        return InsuranceStatisticsResponse(
            success=True,
            message="获取保险投资汇总成功",
            data=summary
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/statistics/performance/{policy_id}", response_model=PolicyPerformanceResponse)
def get_policy_performance(
    policy_id: int,
    db: Session = Depends(get_db)
):
    """获取保单投资表现"""
    try:
        performance_data = InsuranceStatisticsService.get_policy_performance(db, policy_id)
        
        from app.models.schemas import PolicyPerformance
        performance = PolicyPerformance(
            policy_id=performance_data["policy_id"],
            policy_number=performance_data["policy_number"],
            total_premium_paid=performance_data["total_premium_paid"],
            current_value=performance_data["current_value"],
            total_profit=performance_data["total_profit"],
            profit_rate=performance_data["profit_rate"],
            irr=performance_data["irr"],
            years_held=performance_data["years_held"]
        )
        
        return PolicyPerformanceResponse(
            success=True,
            message="获取保单表现成功",
            data=performance
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/statistics/returns-analysis", response_model=ReturnsAnalysisResponse)
def get_returns_analysis(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    db: Session = Depends(get_db)
):
    """收益分析"""
    try:
        # 这里可以实现更复杂的收益分析逻辑
        # 暂时返回基础统计信息
        summary_data = InsuranceStatisticsService.get_insurance_summary(db)
        
        analysis_data = {
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "summary": summary_data,
            "monthly_returns": [],  # 可以添加月度收益分析
            "product_comparison": []  # 可以添加产品对比分析
        }
        
        return ReturnsAnalysisResponse(
            success=True,
            message="收益分析完成",
            data=analysis_data
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ 批量操作API ============

@router.post("/bulk/calculate-interest", response_model=BaseResponse)
def bulk_calculate_monthly_interest(
    calculation_date: date = Query(..., description="计算日期"),
    product_type: str = Query("universal", description="产品类型"),
    db: Session = Depends(get_db)
):
    """批量计算月度利息"""
    try:
        from app.models.database import InsurancePolicy, InsuranceProduct
        
        # 获取指定类型的所有有效保单
        policies = db.query(InsurancePolicy).join(InsuranceProduct).filter(
            InsurancePolicy.status == "active",
            InsuranceProduct.product_type == product_type
        ).all()
        
        results = []
        errors = []
        
        for policy in policies:
            try:
                result = UniversalLifeService.calculate_monthly_interest(
                    db, policy.id, calculation_date
                )
                results.append({
                    "policy_id": policy.id,
                    "policy_number": policy.policy_number,
                    "interest_amount": float(result.return_amount)
                })
            except Exception as e:
                errors.append({
                    "policy_id": policy.id,
                    "policy_number": policy.policy_number,
                    "error": str(e)
                })
        
        return BaseResponse(
            success=True,
            message=f"批量计算完成，成功 {len(results)} 个，失败 {len(errors)} 个",
            data={
                "success_count": len(results),
                "error_count": len(errors),
                "results": results,
                "errors": errors
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))