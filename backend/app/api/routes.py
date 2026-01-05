"""
API 路由定义
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from typing import Dict, Any
import os
import shutil
from datetime import datetime

from app.services.excel_processor import ExcelProcessor
from app.models.schemas import AnalysisResult, DashboardData
from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version
    }


@router.post("/upload", response_model=AnalysisResult)
async def upload_file(file: UploadFile = File(...)):
    """
    上传 Excel 文件
    """
    # 验证文件类型
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="仅支持 .xlsx 或 .xls 文件")
    
    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(settings.upload_dir, safe_filename)
    
    try:
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 验证文件可读性
        processor = ExcelProcessor(file_path)
        sheets = processor.load_all_sheets()
        
        return AnalysisResult(
            success=True,
            message="文件上传成功",
            data={
                "file_path": file_path,
                "file_name": file.filename,
                "sheets": list(sheets.keys()),
                "upload_time": timestamp
            }
        )
    
    except Exception as e:
        # 清理失败的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_excel(file_path: str):
    """
    分析 Excel 文件，返回完整的 Dashboard 数据
    """
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    try:
        processor = ExcelProcessor(file_path)
        processor.load_all_sheets()
        
        # 执行各项分析
        project_costs = processor.aggregate_project_costs()
        department_costs = processor.calculate_department_costs()
        anomalies = processor.cross_check_attendance_travel()
        booking_behavior = processor.analyze_booking_behavior()
        attendance_summary = processor.get_attendance_summary()
        
        # 计算总览数据
        total_cost = sum(item['total_cost'] for item in department_costs)
        total_projects = len(project_costs)
        total_anomalies = len(anomalies)
        
        overview = {
            'total_cost': round(total_cost, 2),
            'total_projects': total_projects,
            'total_departments': len(department_costs),
            'total_anomalies': total_anomalies,
            'analysis_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        dashboard_data = {
            'overview': overview,
            'department_costs': department_costs[:10],  # Top 10
            'project_costs': project_costs[:20],  # Top 20
            'anomalies': anomalies[:50],  # Top 50
            'booking_behavior': booking_behavior,
            'attendance_summary': attendance_summary
        }
        
        return AnalysisResult(
            success=True,
            message="分析完成",
            data=dashboard_data
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.post("/export")
async def export_results(file_path: str):
    """
    导出分析结果到 Excel（追加新 Sheet）
    """
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    try:
        processor = ExcelProcessor(file_path)
        processor.load_all_sheets()
        
        # 执行分析
        results = {
            'project_costs': processor.aggregate_project_costs(),
            'department_costs': processor.calculate_department_costs(),
            'anomalies': processor.cross_check_attendance_travel()
        }
        
        # 回写到 Excel
        output_path = processor.write_analysis_results(results)
        
        # 返回文件
        return FileResponse(
            path=output_path,
            filename=os.path.basename(output_path),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.get("/sheets/{file_path:path}")
async def get_sheets(file_path: str):
    """
    获取文件中所有 Sheet 名称
    """
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    try:
        processor = ExcelProcessor(file_path)
        sheets = processor.load_all_sheets()
        
        return {
            "success": True,
            "sheets": [
                {
                    "name": name,
                    "rows": len(df),
                    "columns": len(df.columns)
                }
                for name, df in sheets.items()
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取失败: {str(e)}")


@router.delete("/files/{file_path:path}")
async def delete_file(file_path: str):
    """
    删除上传的文件
    """
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    try:
        os.remove(file_path)
        return {"success": True, "message": "文件已删除"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


