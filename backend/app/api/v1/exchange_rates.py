from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from datetime import date
from app.models.schemas import BaseResponse
from app.services.exchange_rate_service import ExchangeRateService

router = APIRouter(prefix="/exchange-rates", tags=["汇率管理"])


@router.get("/currencies", response_model=BaseResponse)
def get_currency_list():
    """获取支持的货币列表"""
    try:
        currencies = ExchangeRateService.get_currency_list()
        return BaseResponse(
            success=True,
            message=f"获取到 {len(currencies)} 种货币",
            data={"currencies": currencies}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rates", response_model=BaseResponse)
def get_all_exchange_rates():
    """获取所有货币的汇率"""
    try:
        rates = ExchangeRateService.get_all_exchange_rates()
        return BaseResponse(
            success=True,
            message=f"获取到 {len(rates)} 种货币的汇率",
            data={"rates": rates}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rates/{currency}", response_model=BaseResponse)
def get_exchange_rate(currency: str):
    """获取指定货币的汇率"""
    try:
        rate_data = ExchangeRateService.get_exchange_rate(currency)
        if rate_data:
            return BaseResponse(
                success=True,
                message=f"获取 {currency} 汇率成功",
                data={"rate": rate_data}
            )
        else:
            raise HTTPException(status_code=404, detail=f"未找到 {currency} 的汇率数据")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rates/{currency}/history", response_model=BaseResponse)
def get_historical_exchange_rate(
    currency: str,
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)")
):
    """获取指定货币的历史汇率"""
    try:
        historical_data = ExchangeRateService.get_historical_exchange_rate(
            currency, start_date, end_date
        )
        return BaseResponse(
            success=True,
            message=f"获取 {currency} 历史汇率成功",
            data={"history": historical_data}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/convert", response_model=BaseResponse)
def convert_currency(
    amount: float = Query(..., description="转换金额"),
    from_currency: str = Query(..., description="源货币"),
    to_currency: str = Query("CNY", description="目标货币")
):
    """货币转换"""
    try:
        converted_amount = ExchangeRateService.convert_currency(amount, from_currency, to_currency)
        if converted_amount is not None:
            return BaseResponse(
                success=True,
                message="货币转换成功",
                data={
                    "original_amount": amount,
                    "original_currency": from_currency,
                    "converted_amount": converted_amount,
                    "target_currency": to_currency
                }
            )
        else:
            raise HTTPException(status_code=400, detail="货币转换失败")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 