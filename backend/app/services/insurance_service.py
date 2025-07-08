from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from typing import List, Optional, Tuple
from datetime import date, datetime
from decimal import Decimal
import json

from app.models.database import (
    InsuranceProduct, InsurancePolicy, InsuranceOperation, 
    InsuranceReturn, InsuranceDividendHistory
)
from app.models.schemas import (
    InsuranceProductCreate, InsuranceProductUpdate,
    InsurancePolicyCreate, InsurancePolicyUpdate, PolicyValueUpdate,
    InsuranceOperationCreate, PremiumPaymentCreate, TopUpCreate, WithdrawalCreate,
    InsuranceReturnCreate, DividendProcessCreate,
    InsuranceDividendHistoryCreate
)


class InsuranceProductService:
    """保险产品服务"""
    
    @staticmethod
    def create_product(db: Session, product_data: InsuranceProductCreate) -> InsuranceProduct:
        """创建保险产品"""
        db_product = InsuranceProduct(**product_data.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    
    @staticmethod
    def get_product(db: Session, product_code: str) -> Optional[InsuranceProduct]:
        """获取保险产品"""
        return db.query(InsuranceProduct).filter(
            InsuranceProduct.product_code == product_code
        ).first()
    
    @staticmethod
    def get_products(db: Session, company: Optional[str] = None, 
                    product_type: Optional[str] = None) -> List[InsuranceProduct]:
        """获取保险产品列表"""
        query = db.query(InsuranceProduct)
        
        if company:
            query = query.filter(InsuranceProduct.insurance_company == company)
        if product_type:
            query = query.filter(InsuranceProduct.product_type == product_type)
            
        return query.order_by(InsuranceProduct.created_at.desc()).all()
    
    @staticmethod
    def update_product(db: Session, product_code: str, 
                      update_data: InsuranceProductUpdate) -> Optional[InsuranceProduct]:
        """更新保险产品"""
        db_product = db.query(InsuranceProduct).filter(
            InsuranceProduct.product_code == product_code
        ).first()
        
        if not db_product:
            return None
            
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_product, field, value)
            
        db.commit()
        db.refresh(db_product)
        return db_product


class InsurancePolicyService:
    """保险保单服务"""
    
    @staticmethod
    def create_policy(db: Session, policy_data: InsurancePolicyCreate) -> InsurancePolicy:
        """创建保险保单"""
        db_policy = InsurancePolicy(**policy_data.dict())
        db.add(db_policy)
        db.commit()
        db.refresh(db_policy)
        return db_policy
    
    @staticmethod
    def get_policy(db: Session, policy_id: int) -> Optional[InsurancePolicy]:
        """获取保险保单"""
        return db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
    
    @staticmethod
    def get_policy_by_number(db: Session, policy_number: str) -> Optional[InsurancePolicy]:
        """根据保单号获取保单"""
        return db.query(InsurancePolicy).filter(
            InsurancePolicy.policy_number == policy_number
        ).first()
    
    @staticmethod
    def get_policies(db: Session, status: Optional[str] = None, 
                    company: Optional[str] = None, page: int = 1, 
                    page_size: int = 20) -> Tuple[List[InsurancePolicy], int]:
        """获取保险保单列表"""
        query = db.query(InsurancePolicy)
        
        if status:
            query = query.filter(InsurancePolicy.status == status)
        if company:
            query = query.filter(InsurancePolicy.insurance_company == company)
            
        total = query.count()
        
        policies = query.order_by(InsurancePolicy.created_at.desc())\
                       .offset((page - 1) * page_size)\
                       .limit(page_size).all()
        
        return policies, total
    
    @staticmethod
    def update_policy(db: Session, policy_id: int, 
                     update_data: InsurancePolicyUpdate) -> Optional[InsurancePolicy]:
        """更新保险保单"""
        db_policy = db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
        
        if not db_policy:
            return None
            
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_policy, field, value)
            
        db.commit()
        db.refresh(db_policy)
        return db_policy
    
    @staticmethod
    def update_policy_value(db: Session, policy_id: int, 
                           value_update: PolicyValueUpdate) -> Optional[InsurancePolicy]:
        """更新保单价值"""
        db_policy = db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
        
        if not db_policy:
            return None
        
        # 更新价值
        if value_update.current_cash_value is not None:
            db_policy.current_cash_value = value_update.current_cash_value
        if value_update.guaranteed_cash_value is not None:
            db_policy.guaranteed_cash_value = value_update.guaranteed_cash_value
        if value_update.account_value is not None:
            db_policy.account_value = value_update.account_value
            
        db.commit()
        db.refresh(db_policy)
        
        # 记录价值更新操作
        operation = InsuranceOperation(
            policy_id=policy_id,
            policy_number=db_policy.policy_number,
            operation_date=datetime.combine(value_update.valuation_date, datetime.min.time()),
            operation_type="value_update",
            amount=Decimal("0"),
            currency=db_policy.currency,
            description=f"保单价值更新 - {value_update.notes or ''}",
            notes=value_update.notes,
            cash_value_after=value_update.current_cash_value,
            account_value_after=value_update.account_value
        )
        db.add(operation)
        db.commit()
        
        return db_policy


class InsuranceOperationService:
    """保险操作服务"""
    
    @staticmethod
    def create_operation(db: Session, operation_data: InsuranceOperationCreate) -> InsuranceOperation:
        """创建保险操作记录"""
        # 获取保单信息
        policy = db.query(InsurancePolicy).filter(InsurancePolicy.id == operation_data.policy_id).first()
        if not policy:
            raise ValueError("保单不存在")
            
        # 创建操作记录
        db_operation = InsuranceOperation(
            **operation_data.dict(),
            policy_number=policy.policy_number
        )
        db.add(db_operation)
        db.commit()
        db.refresh(db_operation)
        return db_operation
    
    @staticmethod
    def get_operations(db: Session, policy_id: Optional[int] = None,
                      operation_type: Optional[str] = None,
                      start_date: Optional[date] = None,
                      end_date: Optional[date] = None,
                      page: int = 1, page_size: int = 20) -> Tuple[List[InsuranceOperation], int]:
        """获取保险操作记录"""
        query = db.query(InsuranceOperation)
        
        if policy_id:
            query = query.filter(InsuranceOperation.policy_id == policy_id)
        if operation_type:
            query = query.filter(InsuranceOperation.operation_type == operation_type)
        if start_date:
            query = query.filter(InsuranceOperation.operation_date >= start_date)
        if end_date:
            query = query.filter(InsuranceOperation.operation_date <= end_date)
            
        total = query.count()
        
        operations = query.order_by(InsuranceOperation.operation_date.desc())\
                         .offset((page - 1) * page_size)\
                         .limit(page_size).all()
        
        return operations, total
    
    @staticmethod
    def pay_premium(db: Session, policy_id: int, payment_data: PremiumPaymentCreate) -> InsuranceOperation:
        """缴费操作"""
        policy = db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
        if not policy:
            raise ValueError("保单不存在")
        
        # 创建缴费记录
        operation = InsuranceOperation(
            policy_id=policy_id,
            policy_number=policy.policy_number,
            operation_date=payment_data.payment_date,
            operation_type="premium_payment",
            amount=payment_data.amount,
            currency=policy.currency,
            description=f"保费缴纳 - {payment_data.payment_method or ''}",
            notes=payment_data.notes,
            account_value_before=policy.account_value
        )
        
        # 对于万能险，扣除初始费用后增加账户价值
        if policy.product_code.startswith("UL"):  # 假设万能险产品代码以UL开头
            # 获取产品信息以计算费用
            product = db.query(InsuranceProduct).filter(
                InsuranceProduct.product_code == policy.product_code
            ).first()
            
            if product and product.initial_charge_rate:
                initial_charge = payment_data.amount * product.initial_charge_rate
                net_amount = payment_data.amount - initial_charge
                operation.initial_charge = initial_charge
            else:
                net_amount = payment_data.amount
                
            # 更新账户价值
            policy.account_value += net_amount
            operation.account_value_after = policy.account_value
        
        db.add(operation)
        db.commit()
        db.refresh(operation)
        return operation
    
    @staticmethod
    def top_up_policy(db: Session, policy_id: int, topup_data: TopUpCreate) -> InsuranceOperation:
        """追加投资"""
        policy = db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
        if not policy:
            raise ValueError("保单不存在")
            
        # 创建追加投资记录
        operation = InsuranceOperation(
            policy_id=policy_id,
            policy_number=policy.policy_number,
            operation_date=topup_data.topup_date,
            operation_type="top_up",
            amount=topup_data.amount,
            currency=policy.currency,
            description="追加投资",
            notes=topup_data.notes,
            account_value_before=policy.account_value
        )
        
        # 更新账户价值（追加投资通常也有费用）
        net_amount = topup_data.amount * Decimal("0.99")  # 假设有1%的费用
        operation.initial_charge = topup_data.amount - net_amount
        policy.account_value += net_amount
        operation.account_value_after = policy.account_value
        
        db.add(operation)
        db.commit()
        db.refresh(operation)
        return operation
    
    @staticmethod
    def partial_withdrawal(db: Session, policy_id: int, withdrawal_data: WithdrawalCreate) -> InsuranceOperation:
        """部分提取"""
        policy = db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
        if not policy:
            raise ValueError("保单不存在")
            
        if policy.account_value < withdrawal_data.amount:
            raise ValueError("账户价值不足")
            
        # 创建部分提取记录
        operation = InsuranceOperation(
            policy_id=policy_id,
            policy_number=policy.policy_number,
            operation_date=withdrawal_data.withdrawal_date,
            operation_type="partial_withdrawal",
            amount=withdrawal_data.amount,
            currency=policy.currency,
            description=f"部分提取 - {withdrawal_data.withdrawal_reason or ''}",
            notes=withdrawal_data.notes,
            account_value_before=policy.account_value
        )
        
        # 更新账户价值
        policy.account_value -= withdrawal_data.amount
        operation.account_value_after = policy.account_value
        
        db.add(operation)
        db.commit()
        db.refresh(operation)
        return operation


class UniversalLifeService:
    """万能险业务服务"""
    
    @staticmethod
    def calculate_monthly_interest(db: Session, policy_id: int, calculation_date: date) -> InsuranceReturn:
        """计算月度复利收益"""
        policy = db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
        if not policy:
            raise ValueError("保单不存在")
            
        # 获取产品信息
        product = db.query(InsuranceProduct).filter(
            InsuranceProduct.product_code == policy.product_code
        ).first()
        
        if not product or not product.current_rate:
            raise ValueError("无法获取结算利率")
            
        # 计算月利率
        monthly_rate = product.current_rate / 12
        
        # 计算利息
        interest_amount = policy.account_value * monthly_rate
        
        # 扣除管理费和保险成本
        management_fee = Decimal("0")
        insurance_cost = Decimal("0")
        
        if product.management_fee_rate:
            management_fee = policy.account_value * product.management_fee_rate / 12
            
        # 简化的保险成本计算（实际应该根据年龄、保额等计算）
        insurance_cost = policy.sum_insured * Decimal("0.0001")  # 0.01%的月保险成本
        
        net_interest = interest_amount - management_fee - insurance_cost
        
        # 更新账户价值
        old_account_value = policy.account_value
        policy.account_value += net_interest
        
        # 创建收益记录
        interest_return = InsuranceReturn(
            policy_id=policy_id,
            policy_number=policy.policy_number,
            return_date=calculation_date,
            return_type="interest",
            return_amount=interest_amount,
            return_rate=monthly_rate,
            base_amount=old_account_value,
            currency=policy.currency,
            distribution_method="reinvest",
            account_value_change=net_interest,
            description=f"月度利息结算 - 利率{monthly_rate:.4%}",
            source="calculated"
        )
        
        # 创建费用扣除操作
        if management_fee > 0 or insurance_cost > 0:
            fee_operation = InsuranceOperation(
                policy_id=policy_id,
                policy_number=policy.policy_number,
                operation_date=datetime.combine(calculation_date, datetime.min.time()),
                operation_type="fee_charged",
                amount=management_fee + insurance_cost,
                currency=policy.currency,
                description="月度费用扣除",
                management_fee=management_fee,
                insurance_cost=insurance_cost,
                account_value_before=old_account_value + interest_amount,
                account_value_after=policy.account_value
            )
            db.add(fee_operation)
        
        db.add(interest_return)
        db.commit()
        db.refresh(interest_return)
        return interest_return


class HongKongInsuranceService:
    """港险业务服务"""
    
    @staticmethod
    def process_annual_dividend(db: Session, policy_id: int, dividend_data: DividendProcessCreate) -> InsuranceReturn:
        """处理年度分红"""
        policy = db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
        if not policy:
            raise ValueError("保单不存在")
            
        # 计算分红金额（基于保额）
        dividend_amount = policy.sum_insured * dividend_data.dividend_rate
        
        # 创建分红记录
        dividend_return = InsuranceReturn(
            policy_id=policy_id,
            policy_number=policy.policy_number,
            return_date=dividend_data.dividend_date,
            return_type="dividend",
            return_amount=dividend_amount,
            return_rate=dividend_data.dividend_rate,
            base_amount=policy.sum_insured,
            currency=policy.currency,
            distribution_method=dividend_data.distribution_method,
            description=f"{dividend_data.dividend_year}年度分红",
            source="manual"
        )
        
        # 根据分红处理方式更新保单价值
        if dividend_data.distribution_method == "reinvest":
            # 增额分红
            policy.current_cash_value += dividend_amount
            dividend_return.cash_value_change = dividend_amount
        elif dividend_data.distribution_method == "cash":
            # 现金分红，不增加保单价值
            dividend_return.cash_value_change = Decimal("0")
        elif dividend_data.distribution_method == "premium_offset":
            # 抵缴保费，创建相应的保费操作
            premium_operation = InsuranceOperation(
                policy_id=policy_id,
                policy_number=policy.policy_number,
                operation_date=datetime.combine(dividend_data.dividend_date, datetime.min.time()),
                operation_type="premium_payment",
                amount=dividend_amount,
                currency=policy.currency,
                description=f"分红抵缴保费 - {dividend_data.dividend_year}年度",
                notes=dividend_data.notes
            )
            db.add(premium_operation)
        
        db.add(dividend_return)
        db.commit()
        db.refresh(dividend_return)
        return dividend_return


class InsuranceStatisticsService:
    """保险统计服务"""
    
    @staticmethod
    def get_insurance_summary(db: Session) -> dict:
        """获取保险投资汇总"""
        # 获取所有有效保单
        policies = db.query(InsurancePolicy).filter(InsurancePolicy.status == "active").all()
        
        if not policies:
            return {
                "total_policies": 0,
                "total_invested": Decimal("0"),
                "total_current_value": Decimal("0"),
                "total_profit": Decimal("0"),
                "total_profit_rate": Decimal("0"),
                "universal_life_count": 0,
                "whole_life_count": 0,
                "endowment_count": 0
            }
        
        total_invested = Decimal("0")
        total_current_value = Decimal("0")
        universal_life_count = 0
        whole_life_count = 0
        endowment_count = 0
        
        for policy in policies:
            # 计算总投入（所有保费和追加投资）
            premium_operations = db.query(InsuranceOperation).filter(
                InsuranceOperation.policy_id == policy.id,
                InsuranceOperation.operation_type.in_(["premium_payment", "top_up"])
            ).all()
            
            policy_invested = sum(op.amount for op in premium_operations)
            total_invested += policy_invested
            
            # 当前价值（取现金价值和账户价值的较大者）
            current_value = max(policy.current_cash_value, policy.account_value)
            total_current_value += current_value
            
            # 统计产品类型
            product = db.query(InsuranceProduct).filter(
                InsuranceProduct.product_code == policy.product_code
            ).first()
            
            if product:
                if product.product_type == "universal":
                    universal_life_count += 1
                elif product.product_type == "whole_life":
                    whole_life_count += 1
                elif product.product_type == "endowment":
                    endowment_count += 1
        
        total_profit = total_current_value - total_invested
        total_profit_rate = (total_profit / total_invested * 100) if total_invested > 0 else Decimal("0")
        
        return {
            "total_policies": len(policies),
            "total_invested": total_invested,
            "total_current_value": total_current_value,
            "total_profit": total_profit,
            "total_profit_rate": total_profit_rate,
            "universal_life_count": universal_life_count,
            "whole_life_count": whole_life_count,
            "endowment_count": endowment_count
        }
    
    @staticmethod
    def get_policy_performance(db: Session, policy_id: int) -> dict:
        """获取保单投资表现"""
        policy = db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
        if not policy:
            raise ValueError("保单不存在")
        
        # 计算总投入
        premium_operations = db.query(InsuranceOperation).filter(
            InsuranceOperation.policy_id == policy_id,
            InsuranceOperation.operation_type.in_(["premium_payment", "top_up"])
        ).all()
        
        total_premium_paid = sum(op.amount for op in premium_operations)
        
        # 当前价值
        current_value = max(policy.current_cash_value, policy.account_value)
        
        # 计算收益
        total_profit = current_value - total_premium_paid
        profit_rate = (total_profit / total_premium_paid * 100) if total_premium_paid > 0 else Decimal("0")
        
        # 计算持有年数
        years_held = (date.today() - policy.policy_start_date).days / 365.25
        
        return {
            "policy_id": policy_id,
            "policy_number": policy.policy_number,
            "total_premium_paid": total_premium_paid,
            "current_value": current_value,
            "total_profit": total_profit,
            "profit_rate": profit_rate,
            "irr": None,  # 需要复杂的IRR计算
            "years_held": Decimal(str(years_held))
        }