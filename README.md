# CorpPilot - 企业差旅分析平台（后端 API）

## 📝 项目简介

CorpPilot 是一个基于 FastAPI + Pandas + OpenPyXL 的企业差旅分析平台后端服务。
核心功能包括：

- 📊 **数据分析**: 读取 Excel (.xlsx) 进行差旅成本分析
- 🔍 **异常检测**: 交叉验证考勤与差旅记录，识别异常情况
- 📈 **可视化支持**: 生成 Dashboard 所需的 JSON 数据
- 📤 **Excel 导出**: 在原文件中追加分析结果 Sheet（保留原样式）

---

## 🏗️ 项目结构

```
CostMatrix/
├── main.py                  # FastAPI 主入口
├── data_loader.py           # 数据加载和清洗模块
├── analysis_service.py      # 核心分析逻辑
├── export_service.py        # Excel 导出服务
├── requirements.txt         # Python 依赖
├── .gitignore              # Git 忽略文件
└── README.md               # 项目说明
```

---

## 🚀 快速开始

### 1. 环境准备

确保已安装 Python 3.8+：

```bash
python --version
```

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖包
pip install -r requirements.txt
```

### 3. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动。

访问 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📡 API 端点

### 1. 健康检查

**GET** `/health`

检查服务运行状态。

**响应示例：**
```json
{
  "status": "healthy",
  "service": "CorpPilot API"
}
```

---

### 2. 数据分析

**POST** `/api/analyze`

上传 Excel 文件，返回分析结果 JSON。

**请求：**
- Content-Type: `multipart/form-data`
- Body: `file` (Excel 文件)

**响应示例：**
```json
{
  "success": true,
  "data": {
    "kpi": {
      "total_cost": 1234567.89,
      "total_orders": 856,
      "anomaly_count": 23,
      "over_standard_count": 45,
      "urgent_booking_ratio": 12.5
    },
    "department_metrics": [
      {
        "一级部门": "研发部",
        "总成本": 456789.12,
        "总工时": 3520.0,
        "人员数量": 20,
        "饱和度": 95.8
      }
    ],
    "top_projects": [
      {
        "项目代码": "05010013",
        "总成本": 123456.78,
        "机票成本": 80000.00,
        "酒店成本": 30000.00,
        "火车票成本": 13456.78,
        "订单数量": 45
      }
    ],
    "anomalies": [
      {
        "Type": "Conflict",
        "姓名": "张三",
        "日期": "2024-01-15",
        "考勤状态": "上班",
        "差旅类型": "机票",
        "差旅金额": 1500.0,
        "一级部门": "研发部",
        "描述": "考勤显示上班但同日有异地差旅消费"
      }
    ],
    "booking_behavior": {
      "total_orders": 856,
      "urgent_orders": 107,
      "urgent_ratio": 12.5,
      "avg_advance_days": 8.5
    },
    "generated_at": "2024-01-20 10:30:45"
  },
  "message": "分析完成"
}
```

---

### 3. 导出分析结果

**POST** `/api/export`

上传 Excel 文件，返回包含分析结果的新 Excel 文件。

**请求：**
- Content-Type: `multipart/form-data`
- Body: `file` (Excel 文件)

**响应：**
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- 文件名: `{原文件名}_分析结果.xlsx`

**新增 Sheet：**
1. **Dashboard_Data**: 包含 KPI、项目 Top 10、部门指标
2. **Anomaly_Log**: 异常记录明细

---

### 4. 数据预览（调试用）

**POST** `/api/preview`

预览 Excel 文件的数据结构。

**请求：**
- Content-Type: `multipart/form-data`
- Body: `file` (Excel 文件)

**响应示例：**
```json
{
  "success": true,
  "data": {
    "attendance": {
      "columns": ["日期", "姓名", "一级部门", "当日状态判断", "工时"],
      "row_count": 1200,
      "sample_data": [...]
    },
    "flight": {
      "columns": ["授信金额", "项目", "预订人姓名", "差旅人员姓名", "出发日期"],
      "row_count": 450,
      "sample_data": [...]
    }
  },
  "message": "数据预览加载成功"
}
```

---

## 📋 数据字典

### 输入 Excel 文件要求

文件必须包含以下 Sheet：

#### 1. **状态明细**（考勤数据）
| 字段名 | 类型 | 说明 |
|--------|------|------|
| 日期 | datetime | 考勤日期 |
| 姓名 | string | 员工姓名 |
| 一级部门 | string | 所属一级部门 |
| 当日状态判断 | string | 上班/出差/休假 |
| 工时 | float | 当日工作时长 |

#### 2. **机票**（差旅数据）
| 字段名 | 类型 | 说明 |
|--------|------|------|
| 授信金额 | string/float | 订单金额（如 "¥1,234.56"） |
| 项目 | string | 项目信息（如 "05010013 市场-整星..."） |
| 预订人姓名 | string | 预订人 |
| 差旅人员姓名 | string | 实际差旅人员 |
| 出发日期 | datetime | 出发日期 |
| 提前预定天数 | int | 提前几天预定 |
| 是否超标 | string | 是/否 |
| 一级部门 | string | 所属部门 |

#### 3. **酒店**（差旅数据）
| 字段名 | 类型 | 说明 |
|--------|------|------|
| 授信金额 | string/float | 订单金额 |
| 项目 | string | 项目信息 |
| 预订人姓名 | string | 预订人 |
| 差旅人员姓名 | string | 实际差旅人员 |
| 入住日期 | datetime | 入住日期 |
| 提前预定天数 | int | 提前几天预定 |
| 是否超标 | string | 是/否 |
| 一级部门 | string | 所属部门 |

#### 4. **火车票**（差旅数据）
结构同 "机票" Sheet。

---

## 🔧 核心业务逻辑

### 1. 项目成本归集
- 从 `项目` 字段提取项目代码（空格前的数字）
- 聚合机票、酒店、火车票的 `授信金额`
- 按总成本降序排序，返回 Top 10

### 2. 交叉验证（异常检测）

#### 类型1: Conflict
- **逻辑**: 考勤显示 "上班"，但同日有异地差旅消费
- **风险**: 可能存在虚假报销或打卡异常

#### 类型2: NoExpense
- **逻辑**: 考勤显示 "出差"，但前后3天无任何差旅消费
- **风险**: 可能存在考勤录入错误或私人出行

### 3. 预订行为分析
- 统计 `提前预定天数 <= 2` 的订单比例
- 计算平均提前预定天数

### 4. 部门指标
- 部门总成本
- 部门总工时
- 人员数量
- 饱和度 = 总工时 / (人数 × 标准工时) × 100%

---

## 🛠️ 技术栈

- **Web 框架**: FastAPI 0.108.0
- **数据处理**: Pandas 2.1.4
- **Excel 操作**: OpenPyXL 3.1.2
- **异步服务器**: Uvicorn 0.25.0

---

## 📦 依赖说明

| 包名 | 版本 | 用途 |
|------|------|------|
| fastapi | 0.108.0 | Web 框架 |
| uvicorn | 0.25.0 | ASGI 服务器 |
| pandas | 2.1.4 | 数据分析 |
| openpyxl | 3.1.2 | Excel 读写 |
| python-multipart | 0.0.6 | 文件上传支持 |
| pydantic | 2.5.3 | 数据验证 |
| python-dateutil | 2.8.2 | 日期处理 |

---

## 🧪 测试指南

### 使用 cURL 测试

```bash
# 1. 健康检查
curl http://localhost:8000/health

# 2. 分析数据
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@your_data.xlsx" \
  -o analysis_result.json

# 3. 导出文件
curl -X POST http://localhost:8000/api/export \
  -F "file=@your_data.xlsx" \
  -o result.xlsx
```

### 使用 Python Requests

```python
import requests

# 分析数据
with open('your_data.xlsx', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/analyze',
        files={'file': f}
    )
    data = response.json()
    print(data)

# 导出文件
with open('your_data.xlsx', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/export',
        files={'file': f}
    )
    with open('output.xlsx', 'wb') as out:
        out.write(response.content)
```

---

## ⚠️ 注意事项

### Excel 导出特别说明

本项目**必须使用 `openpyxl`** 来处理 Excel 导出，**禁止**使用 `pandas.to_excel()` 直接覆盖文件，原因：

1. ❌ `to_excel()` 会丢失原文件的样式、排版、公式
2. ✅ `openpyxl` 可以在原 Workbook 对象中追加 Sheet，保留所有原有格式

**正确做法：**
```python
# ✅ 正确
workbook = openpyxl.load_workbook(file_path)
new_sheet = workbook.create_sheet("Dashboard_Data")
# ... 写入数据 ...
workbook.save(output_path)

# ❌ 错误
df.to_excel(file_path, sheet_name="Dashboard_Data")  # 会覆盖原文件
```

---

## 🔒 数据安全

- 所有上传的文件仅保存在临时目录，处理完成后自动删除
- 不存储任何企业敏感数据
- 生产环境建议：
  - 配置 HTTPS
  - 限制 CORS 允许的域名
  - 添加身份认证中间件

---

## 📞 常见问题

### Q1: 服务启动失败？
**A**: 检查端口 8000 是否被占用：
```bash
lsof -i :8000
```

### Q2: Excel 文件解析失败？
**A**: 确保文件包含所有必需的 Sheet（状态明细、机票、酒店、火车票）

### Q3: 如何部署到生产环境？
**A**: 使用 Gunicorn + Uvicorn Workers：
```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

## 📝 开发日志

- **v1.0.0** (2024-01): 初始版本
  - 实现数据加载、分析、导出功能
  - 支持项目成本归集、异常检测、预订行为分析
  - 完整的 API 文档和测试用例

---

## 📄 License

本项目为企业内部工具，版权归银河航天所有。

---

## 👨‍💻 作者

GalaxySpace AI Team

如有问题请联系开发团队。
