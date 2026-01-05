# 🏗️ CorpPilot 后端 API 架构说明

## 项目文件结构

```
CostMatrix/
│
├── 📋 核心 API 文件
│   ├── main.py                  # FastAPI 主入口（推荐使用）
│   ├── data_loader.py           # 数据加载和清洗模块
│   ├── analysis_service.py      # 核心分析逻辑
│   ├── export_service.py        # Excel 导出服务
│   └── config.py                # 全局配置文件
│
├── 📦 配置文件
│   ├── requirements.txt         # Python 依赖清单
│   ├── .gitignore              # Git 忽略规则
│   └── run.sh                  # 启动脚本
│
├── 📖 文档
│   ├── README.md               # 完整项目文档
│   ├── QUICKSTART.md           # 快速启动指南
│   └── API_STRUCTURE.md        # 本文件
│
├── 🧪 测试工具
│   └── test_api.py             # API 自动化测试脚本
│
└── 📂 其他目录
    ├── backend/                # （备用）后端模块化结构
    └── frontend/               # 前端代码（React）
```

---

## 核心模块说明

### 1. main.py - API 主入口

**职责**: FastAPI 应用入口，定义所有路由和中间件

**端点列表**:
- `GET /` - API 信息
- `GET /health` - 健康检查
- `POST /api/analyze` - 数据分析
- `POST /api/export` - Excel 导出
- `POST /api/preview` - 数据预览

**技术要点**:
- CORS 中间件配置
- 文件上传处理
- 异常捕获与响应
- 临时文件管理

---

### 2. data_loader.py - 数据加载器

**职责**: 从 Excel 读取数据并进行预处理

**核心类**: `DataLoader`

**关键方法**:
- `load_all_sheets()` - 加载所有 Sheet
- `_clean_attendance_data()` - 清洗考勤数据
- `_clean_travel_data()` - 清洗差旅数据
- `_clean_amount()` - 清洗金额字段
- `_extract_project_code()` - 提取项目代码

**数据清洗规则**:
1. 去除 `授信金额` 中的 `¥`, `,` 符号
2. 统一日期格式为 `datetime` 对象
3. 提取 `项目` 字段中的项目代码（空格前的数字）
4. 填充缺失值为 "未知"

---

### 3. analysis_service.py - 分析引擎

**职责**: 实现核心业务逻辑和数据分析算法

**核心类**: `TravelAnalyzer`

**关键方法**:

#### 3.1 项目成本归集
```python
aggregate_project_cost() -> pd.DataFrame
```
- 提取项目代码
- 聚合机票、酒店、火车票成本
- 按总成本降序排序

#### 3.2 交叉验证
```python
cross_check_anomalies() -> List[Dict]
```
**异常类型1: Conflict**
- 逻辑: 考勤显示 "上班"，但同日有异地差旅消费
- 风险: 虚假报销或打卡异常

**异常类型2: NoExpense**
- 逻辑: 考勤显示 "出差"，但前后3天无差旅消费
- 风险: 考勤录入错误或私人出行

#### 3.3 预订行为分析
```python
analyze_booking_behavior() -> Dict
```
- 统计紧急预订（提前 ≤2 天）比例
- 计算平均提前预订天数

#### 3.4 部门指标计算
```python
calculate_department_metrics() -> pd.DataFrame
```
- 部门总成本
- 部门总工时
- 人员数量
- 饱和度 = 总工时 / (人数 × 标准工时) × 100%

#### 3.5 生成 Dashboard 数据
```python
generate_dashboard_data() -> Dict
```
整合所有分析结果，生成前端所需的 JSON 数据。

---

### 4. export_service.py - Excel 导出

**职责**: 使用 openpyxl 在原 Excel 中追加分析结果 Sheet

**核心类**: `ExcelExporter`

**关键方法**:
- `load_workbook()` - 加载原 Excel 工作簿
- `add_dashboard_sheet()` - 添加 Dashboard_Data Sheet
- `add_anomaly_sheet()` - 添加 Anomaly_Log Sheet
- `save_to_bytes()` - 保存到内存字节流
- `export_with_analysis()` - 导出完整文件

**样式配置**:
- 标题: 蓝色背景 + 白色粗体字
- 表头: 浅蓝色背景 + 粗体字
- 异常标记: Conflict 红色，NoExpense 黄色
- 自动列宽调整
- 首行冻结

**⚠️ 重要**: 
- **必须**使用 `openpyxl.load_workbook()` 加载原文件
- **禁止**使用 `pandas.to_excel()` 直接覆盖
- 原因: 保留原文件样式和排版

---

### 5. config.py - 配置管理

**职责**: 集中管理全局配置参数

**配置项**:
- API 基本信息（标题、版本）
- 服务器配置（主机、端口）
- CORS 跨域设置
- 文件上传限制
- Sheet 名称映射
- 分析参数（标准工时、紧急预订阈值）
- 数据清洗规则
- Excel 导出样式

---

## 数据流程图

```
┌─────────────┐
│ 上传 Excel  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  DataLoader     │ ← 加载 4 个 Sheet
│  数据清洗       │ ← 清洗金额、日期、项目代码
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ TravelAnalyzer  │ ← 项目成本归集
│  核心分析       │ ← 交叉验证异常
│                 │ ← 预订行为分析
│                 │ ← 部门指标计算
└──────┬──────────┘
       │
       ├─────────────────┬─────────────────┐
       ▼                 ▼                 ▼
┌──────────┐    ┌─────────────┐   ┌──────────────┐
│ JSON API │    │ ExcelExporter│   │  前端展示    │
│ /analyze │    │  追加 Sheet  │   │  Dashboard   │
└──────────┘    └─────────────┘   └──────────────┘
                      │
                      ▼
               ┌──────────────┐
               │ 下载带分析    │
               │  结果的文件   │
               └──────────────┘
```

---

## API 调用流程

### 1. 分析流程 (`/api/analyze`)

```python
1. 接收上传文件
   ↓
2. 保存到临时文件
   ↓
3. DataLoader.load_all_sheets()  # 加载 4 个 Sheet
   ↓
4. TravelAnalyzer.generate_dashboard_data()  # 执行分析
   ↓
5. 返回 JSON 响应
   ↓
6. 清理临时文件
```

### 2. 导出流程 (`/api/export`)

```python
1. 接收上传文件
   ↓
2. 保存到临时文件
   ↓
3. DataLoader.load_all_sheets()
   ↓
4. TravelAnalyzer.generate_dashboard_data()
   ↓
5. ExcelExporter.export_with_analysis()
   ├─ add_dashboard_sheet()  # 添加汇总 Sheet
   └─ add_anomaly_sheet()    # 添加异常 Sheet
   ↓
6. 返回文件流
   ↓
7. 清理临时文件
```

---

## 关键业务算法

### 1. 项目代码提取算法

```python
输入: "05010013 市场-整星交付项目"
处理: 使用正则表达式 r'^(\d+)' 提取空格前的数字
输出: "05010013"
```

### 2. 异常检测算法

**Conflict 检测**:
```python
FOR EACH 考勤记录 WHERE 状态 = "上班":
    IF 同日存在差旅消费记录:
        标记为 Conflict 异常
```

**NoExpense 检测**:
```python
FOR EACH 考勤记录 WHERE 状态 = "出差":
    IF 前后3天内无差旅消费记录:
        标记为 NoExpense 异常
```

### 3. 饱和度计算算法

```python
标准工时 = 8小时/天 × 22天/月 = 176小时
部门人数 = DISTINCT COUNT(姓名) WHERE 一级部门 = X
部门总工时 = SUM(工时) WHERE 一级部门 = X
饱和度 = 部门总工时 / (部门人数 × 标准工时) × 100%
```

---

## 错误处理机制

### 1. 文件验证
- 检查文件扩展名是否为 `.xlsx`
- 检查文件大小是否超过限制（50MB）

### 2. 数据验证
- 检查必需 Sheet 是否存在
- 检查必需列是否存在
- 处理空值和异常值

### 3. 异常捕获
```python
try:
    # 业务逻辑
except Exception as e:
    traceback.format_exc()  # 记录详细错误
    raise HTTPException(status_code=500, detail=str(e))
finally:
    # 清理临时文件
```

---

## 性能优化建议

### 当前实现
- 使用 Pandas 向量化操作
- 一次性加载所有数据到内存
- 适用于中小型数据集（< 10MB）

### 大数据优化方案
如果数据量很大（> 100MB），可以考虑：

1. **分块读取**
```python
chunk_size = 10000
for chunk in pd.read_excel(file, chunksize=chunk_size):
    # 处理每个 chunk
```

2. **并行处理**
```python
from multiprocessing import Pool
with Pool(4) as pool:
    results = pool.map(process_func, data_chunks)
```

3. **数据库存储**
- 将 Excel 数据导入 SQLite/PostgreSQL
- 使用 SQL 进行聚合查询

---

## 安全考虑

1. **文件安全**
   - 限制文件类型和大小
   - 临时文件自动清理
   - 使用 `tempfile.NamedTemporaryFile`

2. **跨域安全**
   - 生产环境限制 CORS 域名
   - 配置 `allow_origins=["https://your-domain.com"]`

3. **数据隐私**
   - 不持久化上传文件
   - 不记录敏感业务数据
   - 建议部署时启用 HTTPS

---

## 扩展建议

### 1. 添加认证
```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/analyze")
async def analyze(
    file: UploadFile,
    token: str = Depends(security)
):
    # 验证 token
```

### 2. 添加缓存
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def analyze_cached(file_hash: str):
    # 缓存分析结果
```

### 3. 添加日志
```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### 4. 添加监控
```python
from prometheus_client import Counter

request_count = Counter('api_requests_total', 'Total API requests')

@app.post("/api/analyze")
async def analyze(...):
    request_count.inc()
    # ...
```

---

## 总结

本项目采用**模块化设计**，核心逻辑清晰分离：

- 📥 **数据加载**: `data_loader.py`
- 🧠 **分析引擎**: `analysis_service.py`
- 📤 **导出服务**: `export_service.py`
- 🌐 **API 入口**: `main.py`
- ⚙️ **配置管理**: `config.py`

优点：
✅ 代码易于理解和维护
✅ 模块独立，便于测试
✅ 扩展性强，便于添加新功能
✅ 遵循单一职责原则

使用时请参考 [QUICKSTART.md](QUICKSTART.md) 快速上手！


