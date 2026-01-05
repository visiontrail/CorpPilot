# CorpPilot 前端快速开始指南

## 🎯 立即体验（无需后端）

前端已成功启动在 **http://localhost:5173** ！

### 方式1：使用演示模式（推荐）

1. **打开浏览器访问**：
   ```
   http://localhost:5173/demo
   ```

2. **点击按钮**："加载模拟数据并查看"

3. **查看效果**：自动跳转到数据看板，展示完整功能

### 方式2：在控制台加载数据

1. 打开浏览器访问：`http://localhost:5173`
2. 按 F12 打开开发者工具
3. 在 Console 中执行：
   ```javascript
   localStorage.setItem('dashboard_data', JSON.stringify({
     summary: { total_cost: 1250000, avg_work_hours: 9.5, anomaly_count: 42 },
     department_stats: [
       { dept: "研发部", cost: 450000, avg_hours: 10.2, headcount: 50 },
       { dept: "市场部", cost: 280000, avg_hours: 9.1, headcount: 25 }
     ],
     project_top10: [
       { code: "0501", name: "灵犀卫星", cost: 300000 },
       { code: "0502", name: "星链计划", cost: 280000 }
     ],
     anomalies: [
       { date: "2025-08-01", name: "张三", dept: "行政部", type: "Conflict", detail: "考勤在岗但有酒店入住" }
     ]
   }))
   location.reload()
   ```

## 🔌 与后端联调

### 步骤1：安装后端依赖

```bash
cd /Users/guoliang/Desktop/workspace/code/GalaxySpace/GalaxySpaceAI/CostMatrix
pip3 install -r requirements.txt
```

### 步骤2：启动后端服务

```bash
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 步骤3：测试完整流程

1. 访问 http://localhost:5173/upload
2. 上传包含考勤和差旅数据的 Excel 文件
3. 系统自动分析并跳转到数据看板
4. 查看可视化结果和异常记录

## 📊 页面功能说明

### 1. 数据看板 (/)
- 📈 总成本、平均工时、异常数量统计
- 🥧 部门成本分布饼图
- 📊 项目成本排名 Top 10
- ⏰ 部门平均工时对比
- 🎯 部门人数与成本关系分析
- 📋 详细数据表格（支持排序、搜索）
- 💾 导出分析结果

### 2. 文件上传 (/upload)
- 📤 拖拽或点击上传 Excel 文件
- 🔍 自动文件验证（格式、大小）
- 📊 实时上传进度
- ⚡ 自动触发数据分析
- ✅ 分析结果预览

### 3. 演示模式 (/demo)
- 🚀 一键加载测试数据
- 💡 无需后端即可体验
- 🎮 适合演示和培训

## 🎨 界面预览

### 核心指标卡片
```
┌─────────────┬─────────────┬─────────────┐
│   总成本    │   平均工时   │  异常记录   │
│ ¥1,250,000  │  9.5 小时   │   42 条    │
└─────────────┴─────────────┴─────────────┘
```

### 数据可视化
- 部门成本分布 - 环形饼图
- 项目成本排名 - 横向柱状图
- 部门工时对比 - 纵向柱状图
- 人数成本关系 - 散点图

## 🛠️ 开发命令

```bash
# 进入前端目录
cd frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint
```

## 📝 Excel 文件格式要求

### 必需的 Sheet：
1. **状态明细** - 考勤数据
   - 列：姓名、日期、状态、工作时长等

2. **机票** - 机票预订记录
   - 列：姓名、日期、价格、项目代码等

3. **酒店** - 酒店预订记录
   - 列：姓名、入住日期、价格等

4. **火车票** - 火车票预订记录
   - 列：姓名、日期、价格等

### 可选的 Sheet：
- **差旅汇总** - 汇总统计数据

## 🌐 API 端点

### 上传文件
```
POST /api/upload
Content-Type: multipart/form-data
```

### 分析数据
```
POST /api/analyze?file_path=xxx.xlsx
Response: AnalysisResult
```

### 导出结果
```
POST /api/export?file_path=xxx.xlsx
Response: Excel Blob
```

### 健康检查
```
GET /api/health
```

## 🔥 技术栈

- **React 18** - UI 框架
- **TypeScript** - 类型安全
- **Ant Design 5** - UI 组件库
- **ECharts 5** - 数据可视化
- **Vite** - 快速构建工具
- **React Router 6** - 路由管理
- **Axios** - HTTP 请求

## 💡 使用技巧

1. **快速测试**：使用演示模式无需准备数据
2. **数据持久化**：刷新页面不会丢失数据（localStorage）
3. **响应式设计**：支持手机、平板、桌面端
4. **键盘快捷键**：表格支持方向键导航
5. **导出功能**：需要后端服务支持

## ❓ 常见问题

### Q: 为什么看不到数据？
**A**: 先访问 `/demo` 加载模拟数据，或上传 Excel 文件

### Q: 上传文件后没反应？
**A**: 检查后端服务是否启动（http://localhost:8000）

### Q: 图表显示异常？
**A**: 清除浏览器缓存，刷新页面

### Q: 如何清除数据？
**A**: 访问 `/demo` 页面，点击"清除所有数据"按钮

## 📞 获取帮助

- 查看详细文档：`frontend/USAGE.md`
- 实现总结：`frontend/IMPLEMENTATION_SUMMARY.md`
- API 文档：`API_STRUCTURE.md`

---

**当前状态**：✅ 前端服务器已启动并运行
**访问地址**：http://localhost:5173
**演示地址**：http://localhost:5173/demo

**开始探索吧！** 🚀


