"""
配置文件
存储项目全局配置参数
"""

from typing import Dict, List


class Config:
    """应用配置类"""
    
    # API 配置
    API_TITLE = "CostMatrix - 企业差旅分析平台"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "基于 Excel 数据的差旅成本分析与异常检测 API"
    
    # 服务器配置
    HOST = "0.0.0.0"
    PORT = 8000
    RELOAD = True  # 开发模式启用热重载
    
    # CORS 配置
    CORS_ORIGINS = ["*"]  # 生产环境应限制具体域名
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_METHODS = ["*"]
    CORS_ALLOW_HEADERS = ["*"]
    
    # 文件上传配置
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = [".xlsx"]
    
    # Excel Sheet 名称配置
    SHEET_NAMES = {
        "attendance": "状态明细",
        "flight": "机票",
        "hotel": "酒店",
        "train": "火车票"
    }
    
    # 分析参数配置
    ANALYSIS_CONFIG = {
        # 标准工时（小时/月）
        "standard_hours_per_month": 176,  # 8小时/天 * 22天/月
        
        # 紧急预订阈值（天）
        "urgent_booking_threshold": 2,
        
        # 异常检测时间窗口（天）
        "anomaly_time_window": 3,
        
        # Top N 项目数量
        "top_projects_count": 10,
        
        # 最大返回异常记录数
        "max_anomaly_records": 100
    }
    
    # 数据清洗规则
    CLEANING_RULES = {
        # 金额字段需要去除的字符
        "amount_remove_chars": ["¥", ",", " "],
        
        # 日期格式
        "date_format": "%Y-%m-%d",
        
        # 默认值
        "default_values": {
            "name": "未知",
            "department": "未知",
            "project_code": "未知",
            "status": "未知"
        }
    }
    
    # Excel 导出样式配置
    EXPORT_STYLES = {
        "title": {
            "font_name": "微软雅黑",
            "font_size": 14,
            "font_bold": True,
            "font_color": "FFFFFF",
            "fill_color": "4472C4"
        },
        "header": {
            "font_name": "微软雅黑",
            "font_size": 11,
            "font_bold": True,
            "font_color": "000000",
            "fill_color": "D9E1F2"
        },
        "content": {
            "font_name": "微软雅黑",
            "font_size": 10,
            "font_color": "000000"
        },
        "anomaly_colors": {
            "Conflict": "FFC7CE",  # 红色
            "NoExpense": "FFEB9C"  # 黄色
        }
    }
    
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


# 创建全局配置实例
config = Config()


