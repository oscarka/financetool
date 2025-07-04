import httpx

fund_code = "007339"
url = f"https://fund.eastmoney.com/pingzhongdata/{fund_code}.js"

print(f"请求地址: {url}")

resp = httpx.get(url, timeout=10)
print(f"状态码: {resp.status_code}")
print("--- 内容前500字符 ---")
print(resp.text[:500])
print("--- 内容后500字符 ---")
print(resp.text[-500:]) 