"""
多链区块链资产查询服务
"""
import httpx
import asyncio
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from loguru import logger
import json


class BlockchainService:
    """区块链资产查询服务"""
    
    def __init__(self):
        # RPC节点配置
        self.rpc_urls = {
            'ethereum': 'https://eth.llamarpc.com',
            'bsc': 'https://bsc-dataseed.binance.org/',
            'polygon': 'https://polygon-rpc.com/',
            'arbitrum': 'https://arb1.arbitrum.io/rpc'
        }
        
        # 常用代币合约地址
        self.token_contracts = {
            'ethereum': {
                'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
                'USDC': '0xA0b86a33E6417aB1a04b0078f6E6Ee6B4f3e0aB4',
                'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
                'LINK': '0x514910771AF9Ca656af840dff83E8264EcF986CA',
                'UNI': '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
                'AAVE': '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9',
            },
            'bsc': {
                'USDT': '0x55d398326f99059fF775485246999027B3197955',
                'USDC': '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d',
                'DAI': '0x1AF3F329e8BE154074D8769D1FFa4eE058B1DBc3',
                'BUSD': '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56',
            },
            'polygon': {
                'USDT': '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
                'USDC': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
                'DAI': '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063',
            }
        }
        
        # 原生代币信息
        self.native_tokens = {
            'ethereum': {'symbol': 'ETH', 'name': 'Ethereum', 'decimals': 18},
            'bsc': {'symbol': 'BNB', 'name': 'BNB', 'decimals': 18},
            'polygon': {'symbol': 'MATIC', 'name': 'Polygon', 'decimals': 18},
            'arbitrum': {'symbol': 'ETH', 'name': 'Ethereum', 'decimals': 18}
        }
    
    async def get_native_balance(self, chain: str, address: str) -> Tuple[Decimal, str]:
        """获取原生代币余额"""
        try:
            if chain not in self.rpc_urls:
                return Decimal('0'), ''
            
            rpc_url = self.rpc_urls[chain]
            native_info = self.native_tokens[chain]
            
            # 构造JSON-RPC请求
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBalance",
                "params": [address, "latest"],
                "id": 1
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(rpc_url, json=payload)
                response.raise_for_status()
                data = response.json()
            
            if 'error' in data:
                logger.error(f"RPC错误: {data['error']}")
                return Decimal('0'), ''
            
            # 将wei转换为以太币
            balance_wei = int(data['result'], 16)
            balance = Decimal(balance_wei) / Decimal(10 ** native_info['decimals'])
            
            return balance, native_info['symbol']
            
        except Exception as e:
            logger.error(f"获取 {chain} 原生代币余额失败: {e}")
            return Decimal('0'), ''
    
    async def get_erc20_balance(self, chain: str, address: str, token_address: str, decimals: int = 18) -> Decimal:
        """获取ERC20代币余额"""
        try:
            if chain not in self.rpc_urls:
                return Decimal('0')
            
            rpc_url = self.rpc_urls[chain]
            
            # ERC20 balanceOf方法的函数签名
            method_signature = "0x70a08231"  # balanceOf(address)
            padded_address = address[2:].lower().zfill(64)  # 移除0x并填充到64位
            
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_call",
                "params": [{
                    "to": token_address,
                    "data": method_signature + padded_address
                }, "latest"],
                "id": 1
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(rpc_url, json=payload)
                response.raise_for_status()
                data = response.json()
            
            if 'error' in data:
                logger.error(f"ERC20余额查询错误: {data['error']}")
                return Decimal('0')
            
            # 解析返回的余额
            balance_hex = data['result']
            if balance_hex == '0x':
                return Decimal('0')
                
            balance_wei = int(balance_hex, 16)
            balance = Decimal(balance_wei) / Decimal(10 ** decimals)
            
            return balance
            
        except Exception as e:
            logger.error(f"获取ERC20代币余额失败: {e}")
            return Decimal('0')
    
    async def get_wallet_assets(self, chain: str, address: str) -> List[Dict]:
        """获取钱包所有资产"""
        assets = []
        
        try:
            # 1. 获取原生代币余额
            native_balance, native_symbol = await self.get_native_balance(chain, address)
            if native_balance > 0:
                assets.append({
                    'chain': chain,
                    'token_symbol': native_symbol,
                    'token_name': self.native_tokens[chain]['name'],
                    'token_address': None,
                    'balance': native_balance,
                    'is_native_token': True,
                    'decimals': self.native_tokens[chain]['decimals']
                })
            
            # 2. 获取常用ERC20代币余额
            if chain in self.token_contracts:
                token_tasks = []
                for symbol, contract_address in self.token_contracts[chain].items():
                    task = self.get_erc20_balance(chain, address, contract_address)
                    token_tasks.append((symbol, contract_address, task))
                
                # 并行查询所有代币余额
                for symbol, contract_address, task in token_tasks:
                    try:
                        balance = await task
                        if balance > 0:
                            # 获取代币的decimals（大部分ERC20都是18位）
                            decimals = 18
                            if symbol in ['USDT', 'USDC'] and chain == 'ethereum':
                                decimals = 6  # USDT和USDC在以太坊上是6位小数
                            
                            assets.append({
                                'chain': chain,
                                'token_symbol': symbol,
                                'token_name': symbol,  # 简化处理
                                'token_address': contract_address,
                                'balance': balance,
                                'is_native_token': False,
                                'decimals': decimals
                            })
                    except Exception as e:
                        logger.error(f"查询代币 {symbol} 余额失败: {e}")
            
            logger.info(f"成功查询 {chain} 地址 {address[:10]}... 的资产，找到 {len(assets)} 个代币")
            return assets
            
        except Exception as e:
            logger.error(f"查询钱包资产失败: {e}")
            return []
    
    def is_valid_address(self, address: str, chain: str) -> bool:
        """验证地址格式"""
        try:
            if chain in ['ethereum', 'bsc', 'polygon', 'arbitrum']:
                # EVM地址验证
                if not address.startswith('0x'):
                    return False
                if len(address) != 42:
                    return False
                # 检查是否为有效的十六进制
                int(address[2:], 16)
                return True
            elif chain == 'solana':
                # Solana地址验证（简化版）
                if len(address) >= 32 and len(address) <= 44:
                    return True
                return False
            else:
                return False
        except:
            return False


# 全局实例
blockchain_service = BlockchainService()