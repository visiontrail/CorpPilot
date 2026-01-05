"""
数据模型定义
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, date


class AnalysisResult(BaseModel):
    """分析结果基础模型"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class AttendanceRecord(BaseModel):
    """考勤记录"""
    date: date
    name: str
    department: str
    status: str  # 上班/出差/休假
    work_hours: Optional[float] = None
    earliest_clock: Optional[str] = None
    latest_clock: Optional[str] = None


class TravelRecord(BaseModel):
    """差旅记录"""
    travel_person: str
    amount: float
    project: Optional[str] = None
    travel_date: date
    travel_type: str  # 机票/酒店/火车票
    is_overbudget: Optional[bool] = None
    advance_days: Optional[int] = None


class CrossCheckAnomaly(BaseModel):
    """交叉验证异常记录"""
    name: str
    date: date
    anomaly_type: str  # A: 上班但有差旅, B: 出差但无差旅
    attendance_status: str
    travel_records: List[str]
    description: str


class ProjectCostSummary(BaseModel):
    """项目成本汇总"""
    project_code: str
    project_name: str
    total_cost: float
    record_count: int
    details: List[Dict[str, Any]]


class DepartmentCostSummary(BaseModel):
    """部门成本汇总"""
    department: str
    total_cost: float
    flight_cost: float
    hotel_cost: float
    train_cost: float
    person_count: int


class BookingBehaviorAnalysis(BaseModel):
    """预订行为分析"""
    avg_advance_days: float
    correlation_advance_cost: float
    advance_day_distribution: Dict[str, int]
    cost_by_advance_days: List[Dict[str, Any]]


class DashboardData(BaseModel):
    """Dashboard 数据汇总"""
    overview: Dict[str, Any]
    department_costs: List[DepartmentCostSummary]
    project_costs: List[ProjectCostSummary]
    anomalies: List[CrossCheckAnomaly]
    booking_behavior: Optional[BookingBehaviorAnalysis] = None
    attendance_summary: Dict[str, Any]


