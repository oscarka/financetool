from okx import PublicData

# 不需要API Key
public_api = PublicData.PublicAPI()

# 获取现货产品列表
try:
    result = public_api.get_instruments(instType='SPOT')
    print(result)
except Exception as e:
    print(f"请求异常: {e}") 