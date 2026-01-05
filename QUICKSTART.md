# 🚀 快速启动指南

## 一键启动

### macOS/Linux

```bash
# 1. 安装依赖（首次运行）
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 启动服务
./run.sh
# 或
python main.py
```

### Windows

```cmd
# 1. 安装依赖（首次运行）
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. 启动服务
python main.py
```

---

## 访问 API

服务启动后访问：

- **Swagger 文档**: http://localhost:8000/docs
- **ReDoc 文档**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

---

## 快速测试

使用提供的测试脚本：

```bash
python test_api.py your_data.xlsx
```

测试脚本会自动执行：
1. ✅ 健康检查
2. ✅ 数据预览
3. ✅ 数据分析
4. ✅ Excel 导出

---

## 使用示例

### 1. 在浏览器中测试

访问 http://localhost:8000/docs，使用 Swagger UI 上传文件并测试。

### 2. 使用 cURL

```bash
# 分析数据
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@your_data.xlsx" \
  | jq .

# 导出文件
curl -X POST http://localhost:8000/api/export \
  -F "file=@your_data.xlsx" \
  -o result.xlsx
```

### 3. 使用 Python

```python
import requests

# 分析数据
with open('your_data.xlsx', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/analyze',
        files={'file': f}
    )
    result = response.json()
    print(f"总成本: ¥{result['data']['kpi']['total_cost']:,.2f}")
```

---

## 准备测试数据

你的 Excel 文件需要包含以下 Sheet：

1. **状态明细** - 考勤数据
   - 必须字段: `日期`, `姓名`, `一级部门`, `当日状态判断`, `工时`

2. **机票** - 机票订单
   - 必须字段: `授信金额`, `项目`, `差旅人员姓名`, `出发日期`, `提前预定天数`

3. **酒店** - 酒店订单
   - 必须字段: `授信金额`, `项目`, `差旅人员姓名`, `入住日期`, `提前预定天数`

4. **火车票** - 火车票订单
   - 必须字段: `授信金额`, `项目`, `差旅人员姓名`, `出发日期`, `提前预定天数`

---

## 预期输出

### 分析结果 JSON

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
    "department_metrics": [...],
    "top_projects": [...],
    "anomalies": [...]
  }
}
```

### 导出 Excel 文件

原文件 + 2 个新 Sheet：
- **Dashboard_Data** - KPI 汇总、项目成本、部门指标
- **Anomaly_Log** - 异常记录明细

---

## 常见问题

### Q: 端口 8000 被占用？

```bash
# 修改 main.py 中的端口
uvicorn.run("main:app", host="0.0.0.0", port=8001)
```

### Q: 文件上传失败？

检查文件大小是否超过 50MB，检查 Sheet 名称是否正确。

### Q: 分析结果为空？

使用 `/api/preview` 接口预览数据结构，确认字段名称匹配。

---

## 下一步

- 查看完整文档: [README.md](README.md)
- 集成前端: 参考 API 文档
- 部署生产环境: 使用 Gunicorn + Nginx

---

**祝你使用愉快！** 🎉
