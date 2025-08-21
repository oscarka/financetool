"""
智能图表配置生成器
MCP服务专用版本
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
            color_field=self._determine_color_field(data_analysis)
        )
    
    def _create_empty_config(self, user_question: str) -> ChartConfig:
        """创建空数据配置"""
        return ChartConfig(
            chart_type="table",
            title="无数据",
            description=f"查询'{user_question}'未返回任何数据",
            data=[],
            style={"colors": self.color_themes["default"]}
        )
    
    def _analyze_data_structure(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析数据结构"""
        if not data:
            return {"type": "empty", "columns": [], "row_count": 0}
        
        columns = list(data[0].keys()) if data else []
        row_count = len(data)
        
        # 分析列类型
        column_types = {}
        for col in columns:
            sample_values = [row.get(col) for row in data[:5] if row.get(col) is not None]
            if sample_values:
                if all(isinstance(v, (int, float)) for v in sample_values):
                    column_types[col] = "numeric"
                elif all(isinstance(v, str) for v in sample_values):
                    column_types[col] = "categorical"
                else:
                    column_types[col] = "mixed"
            else:
                column_types[col] = "unknown"
        
        return {
            "type": "structured",
            "columns": columns,
            "column_types": column_types,
            "row_count": row_count,
            "has_numeric": any(t == "numeric" for t in column_types.values()),
            "has_categorical": any(t == "categorical" for t in column_types.values())
        }
    
    def _determine_chart_type(self, question: str, data_analysis: Dict[str, Any]) -> str:
        """确定图表类型"""
        question_lower = question.lower()
        
        # 根据问题关键词判断
        for chart_type, rules in self.chart_type_rules.items():
            if any(keyword in question_lower for keyword in rules['keywords']):
                return chart_type
        
        # 根据数据结构判断
        if data_analysis.get("has_numeric") and data_analysis.get("has_categorical"):
            if data_analysis.get("row_count", 0) > 10:
                return "bar"
            else:
                return "pie"
        elif data_analysis.get("has_numeric"):
            return "line"
        else:
            return "table"
    
    def _generate_title_and_description(self, question: str, chart_type: str, data_analysis: Dict[str, Any]) -> Tuple[str, str]:
        """生成标题和描述"""
        if question:
            title = question
        else:
            title = f"{chart_type.title()}图表"
        
        description = f"基于{data_analysis.get('row_count', 0)}条数据的{chart_type}图表"
        
        return title, description
    
    def _format_data_for_chart(self, data: List[Dict[str, Any]], chart_type: str, data_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """格式化数据以适应图表"""
        if not data:
            return []
        
        if chart_type == "pie":
            return self._format_for_pie(data, data_analysis)
        elif chart_type == "bar":
            return self._format_for_bar(data, data_analysis)
        elif chart_type == "line":
            return self._format_for_line(data, data_analysis)
        else:
            return data
    
    def _format_for_pie(self, data: List[Dict[str, Any]], data_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """格式化为饼图数据"""
        formatted = []
        for row in data:
            # 查找分类字段和数值字段
            category_field = None
            value_field = None
            
            for col, col_type in data_analysis.get("column_types", {}).items():
                if col_type == "categorical":
                    category_field = col
                elif col_type == "numeric":
                    value_field = col
            
            if category_field and value_field:
                formatted.append({
                    "category": row.get(category_field, "未知"),
                    "value": row.get(value_field, 0),
                    "percentage": 0  # 稍后计算
                })
        
        # 计算百分比
        total = sum(item["value"] for item in formatted)
        if total > 0:
            for item in formatted:
                item["percentage"] = round((item["value"] / total) * 100, 2)
        
        return formatted
    
    def _format_for_bar(self, data: List[Dict[str, Any]], data_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """格式化为柱状图数据"""
        formatted = []
        for row in data:
            # 查找分类字段和数值字段
            category_field = None
            value_field = None
            
            for col, col_type in data_analysis.get("column_types", {}).items():
                if col_type == "categorical":
                    category_field = col
                elif col_type == "numeric":
                    value_field = col
            
            if category_field and value_field:
                formatted.append({
                    "category": row.get(category_field, "未知"),
                    "value": row.get(value_field, 0)
                })
        
        return formatted
    
    def _format_for_line(self, data: List[Dict[str, Any]], data_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """格式化为折线图数据"""
        formatted = []
        for row in data:
            # 查找时间字段和数值字段
            time_field = None
            value_field = None
            
            for col, col_type in data_analysis.get("column_types", {}).items():
                if col_type == "categorical" and any(time_keyword in col.lower() for time_keyword in ["time", "date", "时间", "日期"]):
                    time_field = col
                elif col_type == "numeric":
                    value_field = col
            
            if time_field and value_field:
                formatted.append({
                    "time": row.get(time_field, "未知"),
                    "value": row.get(value_field, 0)
                })
        
        return formatted
    
    def _generate_style_config(self, chart_type: str, data_count: int) -> Dict[str, Any]:
        """生成样式配置"""
        colors = self.color_themes["default"][:data_count]
        
        style = {
            "colors": colors,
            "fontSize": 14,
            "showLegend": True,
            "showGrid": True
        }
        
        if chart_type == "pie":
            style.update({
                "donut": False,
                "showLabels": True
            })
        elif chart_type == "bar":
            style.update({
                "orientation": "vertical",
                "showValues": True
            })
        elif chart_type == "line":
            style.update({
                "smooth": True,
                "showPoints": True
            })
        
        return style
    
    def _determine_axes(self, data_analysis: Dict[str, Any], chart_type: str) -> Tuple[Optional[str], Optional[str]]:
        """确定轴配置"""
        if chart_type in ["pie", "table"]:
            return None, None
        
        columns = data_analysis.get("columns", [])
        column_types = data_analysis.get("column_types", {})
        
        x_axis = None
        y_axis = None
        
        for col, col_type in column_types.items():
            if col_type == "categorical":
                x_axis = col
            elif col_type == "numeric":
                y_axis = col
        
        return x_axis, y_axis
    
    def _determine_color_field(self, data_analysis: Dict[str, Any]) -> Optional[str]:
        """确定颜色字段"""
        column_types = data_analysis.get("column_types", {})
        
        for col, col_type in column_types.items():
            if col_type == "categorical":
                return col
        
        return None
