from okx import Account

# 使用您的API信息
api_key = "e7292bd4-9c4e-4e8b-874c-43e35fd639c0"
secret_key = "F27B517D356A3E1CBADA9CA4EA9160A7"
passphrase = "Okx13579@"  # 新的passphrase
flag = "1"  # 1表示沙盒环境

try:
    # 初始化账户API
    account_api = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
    
    # 获取账户配置
    print("获取账户配置...")
    result = account_api.get_account_config()
    print(f"账户配置结果: {result}")
    
    # 获取账户余额
    print("\n获取账户余额...")
    balance_result = account_api.get_account_balance()
    print(f"账户余额结果: {balance_result}")
    
except Exception as e:
    print(f"账户接口异常: {e}") 