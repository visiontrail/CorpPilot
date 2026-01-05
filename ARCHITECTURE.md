# CorpPilot 架构文档

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   React 18 + Vite + Ant Design Pro + ECharts       │  │
│  │   - Upload Page: 文件上传与验证                      │  │
│  │   - Dashboard: 数据可视化看板                        │  │
│  │   - API Service: Axios 封装                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/REST API
┌─────────────────────────────────────────────────────────────┐
│                         Backend                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              FastAPI Application                     │  │
│  │   ┌─────────────┬─────────────┬──────────────┐     │  │
│  │   │ API Routes  │   Models    │   Config     │     │  │
│  │   │ - Upload    │ - Schemas   │ - Settings   │     │  │
│  │   │ - Analyze   │ - Validation│ - CORS       │     │  │
│  │   │ - Export    │             │              │     │  │
│  │   └─────────────┴─────────────┴──────────────┘     │  │
│  │                                                      │  │
│  │   ┌──────────────────────────────────────────┐     │  │
│  │   │      Business Logic Layer                │     │  │
│  │   │   ExcelProcessor Service                 │     │  │
│  │   │   - load_all_sheets()                    │     │  │
│  │   │   - aggregate_project_costs()            │     │  │
│  │   │   - cross_check_attendance_travel()      │     │  │
│  │   │   - analyze_booking_behavior()           │     │  │
│  │   │   - write_analysis_results()             │     │  │
│  │   └──────────────────────────────────────────┘     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↕ File I/O
┌─────────────────────────────────────────────────────────────┐
│                    Data Processing Layer                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   Pandas + Openpyxl                                  │  │
│  │   - Excel 读取与解析                                  │  │
│  │   - 数据清洗与转换                                    │  │
│  │   - 多维度聚合分析                                    │  │
│  │   - 格式保留回写                                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                      Storage Layer                          │
│  - uploads/: 上传的 Excel 文件                              │
│  - localStorage: 前端缓存 Dashboard 数据                    │
└─────────────────────────────────────────────────────────────┘
```

## 核心模块说明

### 1. Frontend（前端层）

#### 1.1 技术栈
- **React 18**: 现代化组件框架
- **Vite**: 极速构建工具
- **Ant Design Pro**: 企业级 UI 组件
- **ECharts**: 专业可视化库
- **Axios**: HTTP 客户端

#### 1.2 目录结构
```
frontend/
├── src/
│   ├── main.tsx              # 应用入口
│   ├── App.tsx               # 根组件
│   ├── layouts/              # 布局组件
│   │   └── MainLayout.tsx    # 主布局（Header + Content + Footer）
│   ├── pages/                # 页面组件
│   │   ├── Dashboard.tsx     # 数据看板页面
│   │   └── Upload.tsx        # 文件上传页面
│   ├── services/             # API 服务层
│   │   └── api.ts            # API 封装
│   └── utils/                # 工具函数
├── package.json
└── vite.config.ts
```

#### 1.3 关键功能

**Upload 页面**
- Dragger 拖拽上传组件
- 文件类型验证（.xlsx/.xls）
- 上传进度显示
- 自动触发分析
- 步骤引导（Steps）

**Dashboard 页面**
- 4 个关键指标卡片（总成本、项目数、部门数、异常数）
- 部门成本饼图（Pie Chart）
- 项目成本柱状图（Bar Chart）
- 差旅类型堆叠图（Stacked Bar）
- 预订行为折线图（Line Chart）
- 异常记录表格（Table）
- 考勤数据汇总（Statistics）

### 2. Backend（后端层）

#### 2.1 技术栈
- **FastAPI**: 现代异步 Web 框架
- **Pydantic**: 数据验证
- **Pandas**: 数据分析
- **Openpyxl**: Excel 操作

#### 2.2 目录结构
```
backend/
├── app/
│   ├── main.py               # FastAPI 应用入口
│   ├── config.py             # 配置管理
│   ├── api/                  # API 路由层
│   │   ├── __init__.py
│   │   └── routes.py         # REST API 定义
│   ├── models/               # 数据模型层
│   │   ├── __init__.py
│   │   └── schemas.py        # Pydantic 模型
│   └── services/             # 业务逻辑层
│       ├── __init__.py
│       └── excel_processor.py # Excel 处理核心
├── requirements.txt
└── .env
```

#### 2.3 API 端点

| 端点 | 方法 | 功能 | 参数 |
|------|------|------|------|
| `/api/health` | GET | 健康检查 | - |
| `/api/upload` | POST | 上传文件 | file: UploadFile |
| `/api/analyze` | POST | 分析数据 | file_path: str |
| `/api/export` | POST | 导出结果 | file_path: str |
| `/api/sheets/{file_path}` | GET | 获取 Sheet 列表 | file_path: str |
| `/api/files/{file_path}` | DELETE | 删除文件 | file_path: str |

### 3. Data Processing Layer（数据处理层）

#### 3.1 ExcelProcessor 核心方法

```python
class ExcelProcessor:
    def load_all_sheets() -> Dict[str, pd.DataFrame]
        """加载所有 Sheet，同时用 openpyxl 保留格式"""
    
    def clean_attendance_data() -> pd.DataFrame
        """清洗考勤数据（状态明细 Sheet）"""
    
    def clean_travel_data(sheet_name) -> pd.DataFrame
        """清洗差旅数据（机票/酒店/火车票）"""
    
    def extract_project_code(project_str) -> Tuple[str, str]
        """提取项目代码和名称"""
    
    def aggregate_project_costs() -> List[Dict]
        """项目成本归集"""
    
    def cross_check_attendance_travel() -> List[Dict]
        """交叉验证：考勤 vs 差旅"""
    
    def analyze_booking_behavior() -> Dict
        """预订行为分析（提前天数与成本）"""
    
    def calculate_department_costs() -> List[Dict]
        """部门成本汇总"""
    
    def get_attendance_summary() -> Dict
        """考勤数据汇总"""
    
    def write_analysis_results(results, output_path) -> str
        """回写分析结果到 Excel（保留格式）"""
```

#### 3.2 数据处理流程

```
Excel 文件
    ↓
1. load_all_sheets()
    ↓ 读取所有 Sheet
    ├─ 状态明细 → clean_attendance_data()
    ├─ 机票 → clean_travel_data('机票')
    ├─ 酒店 → clean_travel_data('酒店')
    └─ 火车票 → clean_travel_data('火车票')
    ↓
2. 分析任务（并行执行）
    ├─ aggregate_project_costs()        # 项目成本归集
    ├─ cross_check_attendance_travel()  # 交叉验证
    ├─ analyze_booking_behavior()       # 预订行为分析
    ├─ calculate_department_costs()     # 部门成本
    └─ get_attendance_summary()         # 考勤汇总
    ↓
3. 返回 Dashboard 数据
    ↓
4. write_analysis_results()             # 可选：回写到 Excel
```

## 数据流

### 上传与分析流程

```
用户 → 选择文件 
     ↓
前端 → 调用 uploadFile()
     ↓
后端 → POST /api/upload
     ↓ 保存文件到 uploads/
     ↓ 验证文件可读性
     ↓ 返回 file_path
     ↓
前端 → 调用 analyzeExcel(file_path)
     ↓
后端 → POST /api/analyze
     ↓ ExcelProcessor.load_all_sheets()
     ↓ 执行 5 个分析任务
     ↓ 返回 DashboardData
     ↓
前端 → 保存到 localStorage
     ↓ 跳转到 Dashboard
     ↓ 渲染可视化图表
```

### 导出流程

```
用户 → 点击"导出分析结果"
     ↓
前端 → 调用 exportResults(file_path)
     ↓
后端 → POST /api/export
     ↓ ExcelProcessor.load_all_sheets()
     ↓ 执行分析
     ↓ write_analysis_results()
     ↓   ├─ 使用 openpyxl 加载原文件
     ↓   ├─ 创建新 Sheet "分析结果"
     ↓   ├─ 写入项目成本、部门成本、异常记录
     ↓   └─ 保存为新文件（保留原格式）
     ↓ 返回 FileResponse (Blob)
     ↓
前端 → 创建下载链接
     ↓ 触发浏览器下载
```

## 关键技术点

### 1. Excel 格式保留

使用 `openpyxl` 加载原文件，只追加新 Sheet，不破坏原有格式：

```python
from openpyxl import load_workbook

workbook = load_workbook(file_path)  # 保留格式
ws = workbook.create_sheet("分析结果")  # 新增 Sheet
# 写入数据...
workbook.save(output_path)
```

### 2. 交叉验证逻辑

```python
# 按姓名和日期 Join
for name in attendance['姓名'].unique():
    person_attendance = attendance[attendance['姓名'] == name]
    person_travel = travel[travel['姓名'] == name]
    
    for _, row in person_attendance.iterrows():
        att_date = row['日期']
        att_status = row['当日状态判断']
        
        day_travel = person_travel[
            person_travel['出发日期'].dt.date == att_date.date()
        ]
        
        # 异常 A: 上班 + 有差旅
        if '上班' in att_status and not day_travel.empty:
            anomalies.append({...})
        
        # 异常 B: 出差 + 无差旅
        if '出差' in att_status and day_travel.empty:
            anomalies.append({...})
```

### 3. 项目代码提取

```python
def extract_project_code(project_str: str) -> Tuple[str, str]:
    # "05010013 市场-整星..." → ("05010013", "市场-整星...")
    match = re.match(r'(\d+)\s+(.*)', project_str.strip())
    if match:
        return match.group(1), match.group(2)
    return "", project_str
```

### 4. 前端图表配置

使用 ECharts 配置对象，示例：

```typescript
const pieOption = {
  title: { text: '部门成本分布', left: 'center' },
  tooltip: { trigger: 'item' },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    data: data.map(item => ({
      value: item.total_cost,
      name: item.department
    }))
  }]
}
```

## 性能考虑

1. **大文件处理**: Pandas 使用分块读取
2. **并行分析**: FastAPI 异步支持
3. **前端缓存**: localStorage 缓存分析结果
4. **按需加载**: React 路由懒加载

## 扩展性

### 添加新分析维度

1. 在 `ExcelProcessor` 中添加新方法
2. 在 `/api/analyze` 中调用
3. 在前端 `Dashboard` 中添加新图表

### 支持新 Sheet

1. 修改 `clean_*_data()` 方法
2. 更新数据模型 Schema
3. 调整前端展示逻辑

## 安全性

1. **文件验证**: 仅允许 .xlsx/.xls 格式
2. **大小限制**: 配置最大上传 50MB
3. **CORS**: 配置允许的源
4. **路径安全**: 文件保存到受控目录

## 测试建议

### 后端测试
```bash
pytest backend/tests/
```

### 前端测试
```bash
npm test
```

### 集成测试
使用 Postman 或 curl 测试 API 端点。

---

**维护者**: GalaxySpace AI Team  
**最后更新**: 2026-01-05


