"""
智能图表配置生成器
独立测试环节3: 将查询结果转换为Flutter图表配置
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class ChartConfig:
    """图表配置数据类"""
    chart_type: str
    title: str
    description: str
    data: List[Dict[str, Any]]
    style: Dict[str, Any]
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    color_field: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

class ChartConfigGenerator:
    """智能图表配置生成器"""
    
    def __init__(self):
        # 图表类型识别规则
        self.chart_type_rules = {
            'pie': {
                'keywords': ['分布', '占比', '比例', '份额', '结构'],
                'data_patterns': ['categorical_with_values'],
                'description': '饼图 - 适合显示分类数据的比例关系'
            },
            'bar': {
                'keywords': ['对比', '比较', '排名', '排行', '最多', '最少'],
                'data_patterns': ['categorical_with_values', 'grouped_data'],
                'description': '柱状图 - 适合对比不同类别的数值'
            },
            'line': {
                'keywords': ['趋势', '变化', '走势', '时间', '历史', '发展'],
                'data_patterns': ['time_series', 'sequential_data'],
                'description': '折线图 - 适合显示时间序列和趋势'
            },
            'table': {
                'keywords': ['详细', '明细', '列表', '记录'],
                'data_patterns': ['detailed_data', 'multiple_columns'],
                'description': '表格 - 适合显示详细数据'
            }
        }
        
        # 预设的颜色主题
        self.color_themes = {
            'default': ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6'],
            'green': ['#10B981', '#059669', '#047857', '#065F46', '#064E3B'],
            'blue': ['#3B82F6', '#2563EB', '#1D4ED8', '#1E40AF', '#1E3A8A'],
            'rainbow': ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6'],
            'monochrome': ['#374151', '#4B5563', '#6B7280', '#9CA3AF', '#D1D5DB']
        }
    
    def generate_config(self, 
                       query_result: List[Dict[str, Any]], 
                       user_question: str = "",
                       sql: str = "") -> ChartConfig:
        """生成图表配置"""
        
        if not query_result:
            return self._create_empty_config(user_question)
        
        # 1. 分析数据结构
        data_analysis = self._analyze_data_structure(query_result)
        
        # 2. 确定图表类型
        chart_type = self._determine_chart_type(user_question, data_analysis)
        
        # 3. 生成图表标题和描述
        title, description = self._generate_title_and_description(user_question, chart_type, data_analysis)
        
        # 4. 处理数据格式
        formatted_data = self._format_data_for_chart(query_result, chart_type, data_analysis)
        
        # 5. 生成样式配置
        style = self._generate_style_config(chart_type, len(formatted_data))
        
        # 6. 确定轴配置
        x_axis, y_axis = self._determine_axes(data_analysis, chart_type)
        
        return ChartConfig(
            chart_type=chart_type,
            title=title,
            description=description,
            data=formatted_data,
            style=style,
            x_axis=x_axis,
            y_axis=y_axis,
            color_field=data_analysis.get('color_field')
        )
    
    def _analyze_data_structure(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析数据结构"""
        if not data:
            return {}
        
        sample_row = data[0]
        columns = list(sample_row.keys())
        
        analysis = {
            'row_count': len(data),
            'column_count': len(columns),
            'columns': columns,
            'numeric_columns': [],
            'categorical_columns': [],
            'date_columns': [],
            'primary_value_column': None,
            'primary_label_column': None,
            'has_time_series': False,
            'data_pattern': 'unknown'
        }
        
        # 分析每列的数据类型
        for col in columns:
            sample_values = [row.get(col) for row in data[:5] if row.get(col) is not None]
            
            if not sample_values:
                continue
            
            # 检查是否为数值列
            if all(isinstance(v, (int, float)) for v in sample_values):
                analysis['numeric_columns'].append(col)
                
                # 寻找主要数值列（通常是value, total, amount等）
                if any(keyword in col.lower() for keyword in ['value', 'total', 'amount', 'count', 'sum']):
                    analysis['primary_value_column'] = col
            
            # 检查是否为日期列
            elif any(keyword in col.lower() for keyword in ['date', 'time', 'created', 'updated']):
                analysis['date_columns'].append(col)
                analysis['has_time_series'] = True
            
            # 其他列归类为分类列
            else:
                analysis['categorical_columns'].append(col)
                
                # 寻找主要标签列
                if any(keyword in col.lower() for keyword in ['name', 'type', 'platform', 'category']):
                    analysis['primary_label_column'] = col
        
        # 确定数据模式
        analysis['data_pattern'] = self._determine_data_pattern(analysis)
        
        return analysis
    
    def _determine_data_pattern(self, analysis: Dict[str, Any]) -> str:
        """确定数据模式"""
        if analysis['has_time_series']:
            return 'time_series'
        elif len(analysis['categorical_columns']) >= 1 and len(analysis['numeric_columns']) >= 1:
            if analysis['row_count'] <= 10:
                return 'categorical_with_values'
            else:
                return 'grouped_data'
        elif len(analysis['columns']) > 4:
            return 'detailed_data'
        else:
            return 'simple_data'
    
    def _determine_chart_type(self, user_question: str, data_analysis: Dict[str, Any]) -> str:
        """确定图表类型"""
        question_lower = user_question.lower()
        data_pattern = data_analysis.get('data_pattern', 'unknown')
        
        # 1. 基于用户问题的关键词匹配
        for chart_type, rules in self.chart_type_rules.items():
            if any(keyword in question_lower for keyword in rules['keywords']):
                if data_pattern in rules['data_patterns'] or not rules['data_patterns']:
                    return chart_type
        
        # 2. 基于数据模式的自动推断
        if data_pattern == 'time_series':
            return 'line'
        elif data_pattern == 'categorical_with_values' and data_analysis['row_count'] <= 8:
            return 'pie'
        elif data_pattern in ['categorical_with_values', 'grouped_data']:
            return 'bar'
        elif data_pattern == 'detailed_data':
            return 'table'
        else:
            return 'bar'  # 默认柱状图
    
    def _generate_title_and_description(self, user_question: str, chart_type: str, data_analysis: Dict[str, Any]) -> Tuple[str, str]:
        """生成图表标题和描述"""
        
        # 从用户问题中提取关键信息
        if user_question:
            # 简单的标题生成
            title = user_question.strip('?？')
            if not title.endswith('分析') and not title.endswith('图表'):
                title += '分析'
        else:
            # 基于数据结构生成标题
            if data_analysis.get('primary_label_column') and data_analysis.get('primary_value_column'):
                label_col = data_analysis['primary_label_column']
                value_col = data_analysis['primary_value_column']
                title = f"{label_col}与{value_col}分析"
            else:
                title = "数据分析图表"
        
        # 生成描述
        chart_desc = self.chart_type_rules.get(chart_type, {}).get('description', '')
        row_count = data_analysis.get('row_count', 0)
        description = f"{chart_desc}，包含{row_count}项数据"
        
        return title, description
    
    def _format_data_for_chart(self, data: List[Dict[str, Any]], chart_type: str, data_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """格式化数据以适应图表"""
        
        if chart_type == 'table':
            # 表格直接返回原始数据
            return data
        
        # 确定标签和数值字段
        label_field = data_analysis.get('primary_label_column') or data_analysis.get('categorical_columns', [None])[0]
        value_field = data_analysis.get('primary_value_column') or data_analysis.get('numeric_columns', [None])[0]
        
        if not label_field or not value_field:
            return data  # 无法确定字段，返回原始数据
        
        formatted_data = []
        
        for row in data:
            label = row.get(label_field, 'Unknown')
            value = row.get(value_field, 0)
            
            # 确保value是数值类型
            if not isinstance(value, (int, float)):
                try:
                    value = float(value) if value else 0
                except (ValueError, TypeError):
                    value = 0
            
            formatted_item = {
                'name': str(label),
                'value': value,
                'label': str(label)  # 为了兼容性
            }
            
            # 添加其他字段作为额外信息
            for key, val in row.items():
                if key not in [label_field, value_field]:
                    formatted_item[key] = val
            
            formatted_data.append(formatted_item)
        
        # 排序数据（按值降序）
        if chart_type in ['bar', 'pie']:
            formatted_data.sort(key=lambda x: x['value'], reverse=True)
        
        return formatted_data
    
    def _generate_style_config(self, chart_type: str, data_count: int) -> Dict[str, Any]:
        """生成样式配置"""
        
        # 选择颜色主题
        if data_count <= 3:
            colors = self.color_themes['green']
        elif data_count <= 5:
            colors = self.color_themes['default']
        else:
            colors = self.color_themes['rainbow']
        
        base_style = {
            'colors': colors,
            'fontSize': 12,
            'fontFamily': 'PingFang SC',
            'animation': True,
            'animationDuration': 1000
        }
        
        # 图表类型特定样式
        if chart_type == 'pie':
            base_style.update({
                'showPercentage': True,
                'showLegend': True,
                'centerText': '总计'
            })
        elif chart_type == 'line':
            base_style.update({
                'lineWidth': 3,
                'showPoints': True,
                'smooth': True,
                'fillArea': False
            })
        elif chart_type == 'bar':
            base_style.update({
                'barWidth': 20,
                'showValues': True,
                'borderRadius': 4
            })
        elif chart_type == 'table':
            base_style.update({
                'alternateRowColor': True,
                'headerStyle': {'fontWeight': 'bold'},
                'cellPadding': 8
            })
        
        return base_style
    
    def _determine_axes(self, data_analysis: Dict[str, Any], chart_type: str) -> Tuple[Optional[str], Optional[str]]:
        """确定X轴和Y轴标签"""
        
        if chart_type in ['pie', 'table']:
            return None, None  # 饼图和表格不需要轴标签
        
        # X轴：通常是分类或时间
        x_axis = None
        if data_analysis.get('primary_label_column'):
            x_axis = data_analysis['primary_label_column']
        elif data_analysis.get('date_columns'):
            x_axis = '时间'
        elif data_analysis.get('categorical_columns'):
            x_axis = '分类'
        
        # Y轴：通常是数值
        y_axis = None
        if data_analysis.get('primary_value_column'):
            y_axis = data_analysis['primary_value_column']
        elif data_analysis.get('numeric_columns'):
            y_axis = '数值'
        
        return x_axis, y_axis
    
    def _create_empty_config(self, user_question: str) -> ChartConfig:
        """创建空配置（当没有数据时）"""
        return ChartConfig(
            chart_type='table',
            title='无数据',
            description=f'查询"{user_question}"未返回数据',
            data=[{'提示': '未找到匹配的数据'}],
            style={'colors': ['#9CA3AF']},
            x_axis=None,
            y_axis=None
        )

# 独立测试类
class ChartConfigTester:
    """图表配置生成器测试器"""
    
    def __init__(self):
        self.generator = ChartConfigGenerator()
        
    def test_data_analysis(self) -> bool:
        """测试数据结构分析"""
        print("🔍 测试数据结构分析...")
        
        # 测试数据样本
        test_data = [
            {
                'platform': '支付宝',
                'total_value': 158460.30,
                'asset_count': 5
            },
            {
                'platform': 'Wise',
                'total_value': 8158.23,
                'asset_count': 2
            },
            {
                'platform': 'IBKR',
                'total_value': 42.03,
                'asset_count': 1
            }
        ]
        
        analysis = self.generator._analyze_data_structure(test_data)
        
        expected_keys = ['row_count', 'column_count', 'numeric_columns', 'categorical_columns']
        
        if all(key in analysis for key in expected_keys):
            print("✅ 数据结构分析成功")
            print(f"   - 发现 {analysis['row_count']} 行数据")
            print(f"   - 发现 {len(analysis['numeric_columns'])} 个数值列")
            print(f"   - 发现 {len(analysis['categorical_columns'])} 个分类列")
            return True
        else:
            print("❌ 数据结构分析失败")
            return False
    
    def test_chart_type_determination(self) -> bool:
        """测试图表类型判断"""
        print("🔍 测试图表类型判断...")
        
        test_cases = [
            ("显示各平台的资产分布", "bar"),
            ("各资产类型的占比", "pie"),
            ("最近30天的变化趋势", "line"),
            ("详细的交易记录", "table")
        ]
        
        # 模拟数据分析结果
        mock_analysis = {
            'row_count': 5,
            'data_pattern': 'categorical_with_values',
            'has_time_series': False
        }
        
        success_count = 0
        
        for question, expected_type in test_cases:
            determined_type = self.generator._determine_chart_type(question, mock_analysis)
            
            if determined_type == expected_type:
                print(f"   ✅ '{question}' → {determined_type}")
                success_count += 1
            else:
                print(f"   ❌ '{question}' → {determined_type} (期望: {expected_type})")
        
        success_rate = success_count / len(test_cases)
        print(f"📊 图表类型判断准确率: {success_rate:.1%}")
        
        return success_rate >= 0.75  # 75%准确率
    
    def test_config_generation(self) -> bool:
        """测试完整配置生成"""
        print("🔍 测试完整配置生成...")
        
        # 平台分布数据
        test_data = [
            {'platform': '支付宝', 'total_value': 158460.30},
            {'platform': 'Wise', 'total_value': 8158.23},
            {'platform': 'IBKR', 'total_value': 42.03}
        ]
        
        question = "显示各平台的资产分布"
        
        config = self.generator.generate_config(test_data, question)
        
        # 验证配置完整性
        required_fields = ['chart_type', 'title', 'data', 'style']
        
        if all(hasattr(config, field) and getattr(config, field) for field in required_fields):
            print("✅ 配置生成成功")
            print(f"   - 图表类型: {config.chart_type}")
            print(f"   - 标题: {config.title}")
            print(f"   - 数据点数: {len(config.data)}")
            print(f"   - 样式主题: {len(config.style.get('colors', []))} 种颜色")
            return True
        else:
            print("❌ 配置生成失败")
            return False
    
    def test_data_formatting(self) -> bool:
        """测试数据格式化"""
        print("🔍 测试数据格式化...")
        
        # 原始数据
        raw_data = [
            {'asset_type': '基金', 'total_value': 158460.30},
            {'asset_type': '外汇', 'total_value': 8158.23}
        ]
        
        # 模拟分析结果
        analysis = {
            'primary_label_column': 'asset_type',
            'primary_value_column': 'total_value'
        }
        
        formatted = self.generator._format_data_for_chart(raw_data, 'pie', analysis)
        
        # 验证格式化结果
        if all('name' in item and 'value' in item for item in formatted):
            print("✅ 数据格式化成功")
            print(f"   - 格式化 {len(formatted)} 个数据点")
            for item in formatted:
                print(f"   - {item['name']}: {item['value']}")
            return True
        else:
            print("❌ 数据格式化失败")
            return False
    
    def test_style_generation(self) -> bool:
        """测试样式生成"""
        print("🔍 测试样式生成...")
        
        chart_types = ['bar', 'line', 'pie', 'table']
        success_count = 0
        
        for chart_type in chart_types:
            style = self.generator._generate_style_config(chart_type, 5)
            
            # 验证基础样式字段
            if 'colors' in style and 'fontSize' in style:
                print(f"   ✅ {chart_type} 样式生成成功")
                success_count += 1
            else:
                print(f"   ❌ {chart_type} 样式生成失败")
        
        return success_count == len(chart_types)
    
    async def run_full_test(self) -> Dict[str, bool]:
        """运行完整的配置生成器测试"""
        print("=" * 50)
        print("🧪 图表配置生成器测试套件")
        print("=" * 50)
        
        results = {}
        
        # 1. 数据分析测试
        results["data_analysis"] = self.test_data_analysis()
        
        # 2. 图表类型判断测试
        results["chart_type"] = self.test_chart_type_determination()
        
        # 3. 完整配置生成测试
        results["config_generation"] = self.test_config_generation()
        
        # 4. 数据格式化测试
        results["data_formatting"] = self.test_data_formatting()
        
        # 5. 样式生成测试
        results["style_generation"] = self.test_style_generation()
        
        # 输出测试结果
        print("\n" + "=" * 50)
        print("📊 测试结果汇总:")
        print("=" * 50)
        
        for test_name, passed in results.items():
            status = "✅ 通过" if passed else "❌ 失败"
            print(f"{test_name:18}: {status}")
        
        overall_success = all(results.values())
        print(f"\n整体状态: {'✅ 全部通过' if overall_success else '❌ 存在失败'}")
        
        return results

# 独立测试脚本
async def main():
    """独立测试入口"""
    tester = ChartConfigTester()
    results = await tester.run_full_test()
    
    if all(results.values()):
        print("\n🎉 图表配置生成器测试完成，可以进入下一步！")
        exit(0)
    else:
        print("\n❌ 配置生成器测试中存在问题，请检查错误信息后重试")
        exit(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())