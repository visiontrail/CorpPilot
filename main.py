"""
FastAPI 主入口
提供差旅分析 API 服务
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from typing import Dict
import traceback

from data_loader import DataLoader
from analysis_service import TravelAnalyzer
from export_service import ExcelExporter


# 创建 FastAPI 应用
app = FastAPI(
    title="CorpPilot - 企业差旅分析平台",
    description="基于 Excel 数据的差旅成本分析与异常检测 API",
    version="1.0.0"
)

# 配置 CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径，返回 API 信息"""
    return {
        "message": "Welcome to CorpPilot API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/api/analyze",
            "export": "/api/export",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "CorpPilot API"
    }


@app.post("/api/analyze")
async def analyze_travel_data(file: UploadFile = File(...)) -> Dict:
    """
    分析差旅数据
    
    接收上传的 .xlsx 文件，返回 Dashboard 所需的 JSON 数据
    
    Args:
        file: 上传的 Excel 文件
        
    Returns:
        包含分析结果的 JSON 数据
    """
    # 验证文件格式
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(
            status_code=400,
            detail="只支持 .xlsx 格式的 Excel 文件"
        )
    
    temp_file = None
    
    try:
        # 保存上传文件到临时目录
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # 加载数据
        loader = DataLoader(temp_file_path)
        data_sheets = loader.load_all_sheets()
        
        # 执行分析
        analyzer = TravelAnalyzer(
            attendance_df=data_sheets['attendance'],
            flight_df=data_sheets['flight'],
            hotel_df=data_sheets['hotel'],
            train_df=data_sheets['train']
        )
        
        # 生成 Dashboard 数据
        dashboard_data = analyzer.generate_dashboard_data()
        
        return JSONResponse(
            content={
                "success": True,
                "data": dashboard_data,
                "message": "分析完成"
            }
        )
    
    except Exception as e:
        # 记录错误详情
        error_detail = traceback.format_exc()
        print(f"分析失败: {error_detail}")
        
        raise HTTPException(
            status_code=500,
            detail=f"数据分析失败: {str(e)}"
        )
    
    finally:
        # 清理临时文件
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                print(f"清理临时文件失败: {str(e)}")


@app.post("/api/export")
async def export_with_analysis(file: UploadFile = File(...)):
    """
    导出带分析结果的 Excel 文件
    
    接收上传的 .xlsx 文件，追加分析结果 Sheet，返回修改后的文件流
    
    Args:
        file: 上传的 Excel 文件
        
    Returns:
        包含分析结果的 Excel 文件流
    """
    # 验证文件格式
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(
            status_code=400,
            detail="只支持 .xlsx 格式的 Excel 文件"
        )
    
    temp_file = None
    
    try:
        # 保存上传文件到临时目录
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # 加载数据
        loader = DataLoader(temp_file_path)
        data_sheets = loader.load_all_sheets()
        
        # 执行分析
        analyzer = TravelAnalyzer(
            attendance_df=data_sheets['attendance'],
            flight_df=data_sheets['flight'],
            hotel_df=data_sheets['hotel'],
            train_df=data_sheets['train']
        )
        
        # 生成分析数据
        dashboard_data = analyzer.generate_dashboard_data()
        anomalies = dashboard_data.get('anomalies', [])
        
        # 导出 Excel
        exporter = ExcelExporter(temp_file_path)
        output_stream = exporter.export_with_analysis(dashboard_data, anomalies)
        
        # 生成输出文件名
        original_filename = file.filename.replace('.xlsx', '')
        output_filename = f"{original_filename}_分析结果.xlsx"
        
        # 返回文件流
        return StreamingResponse(
            output_stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}"
            }
        )
    
    except Exception as e:
        # 记录错误详情
        error_detail = traceback.format_exc()
        print(f"导出失败: {error_detail}")
        
        raise HTTPException(
            status_code=500,
            detail=f"文件导出失败: {str(e)}"
        )
    
    finally:
        # 清理临时文件
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                print(f"清理临时文件失败: {str(e)}")


@app.post("/api/preview")
async def preview_data(file: UploadFile = File(...)) -> Dict:
    """
    预览 Excel 数据结构
    
    返回各个 Sheet 的列名和前几行数据，用于调试
    
    Args:
        file: 上传的 Excel 文件
        
    Returns:
        数据预览信息
    """
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(
            status_code=400,
            detail="只支持 .xlsx 格式的 Excel 文件"
        )
    
    temp_file = None
    
    try:
        # 保存上传文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # 加载数据
        loader = DataLoader(temp_file_path)
        data_sheets = loader.load_all_sheets()
        
        # 构建预览数据
        preview = {}
        for sheet_name, df in data_sheets.items():
            preview[sheet_name] = {
                "columns": df.columns.tolist(),
                "row_count": len(df),
                "sample_data": df.head(3).to_dict('records') if not df.empty else []
            }
        
        return JSONResponse(
            content={
                "success": True,
                "data": preview,
                "message": "数据预览加载成功"
            }
        )
    
    except Exception as e:
        error_detail = traceback.format_exc()
        print(f"预览失败: {error_detail}")
        
        raise HTTPException(
            status_code=500,
            detail=f"数据预览失败: {str(e)}"
        )
    
    finally:
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                print(f"清理临时文件失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式启用热重载
        log_level="info"
    )


