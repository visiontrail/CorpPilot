# 📁 CorpPilot 项目结构

## 完整目录树

```
CostMatrix/
├── README.md                    # 项目主文档
├── QUICKSTART.md               # 快速开始指南
├── ARCHITECTURE.md             # 架构设计文档
├── DEPLOYMENT.md               # 部署指南
├── PROJECT_STRUCTURE.md        # 本文件：项目结构说明
├── start.sh                    # 一键启动脚本
├── .editorconfig              # 编辑器配置
│
├── backend/                    # 后端目录
│   ├── app/                    # 应用代码
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── config.py          # 配置管理
│   │   │
│   │   ├── api/               # API 路由层
│   │   │   ├── __init__.py
│   │   │   └── routes.py      # REST API 端点定义
│   │   │
│   │   ├── models/            # 数据模型层
│   │   │   ├── __init__.py
│   │   │   └── schemas.py     # Pydantic 数据模型
│   │   │
│   │   ├── services/          # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   └── excel_processor.py  # Excel 处理核心
│   │   │
│   │   └── utils/             # 工具函数
│   │       ├── __init__.py
│   │       └── helpers.py     # 辅助函数
│   │
│   ├── requirements.txt       # Python 依赖
│   ├── .gitignore            # Git 忽略配置
│   ├── uploads/              # 上传文件存储（运行时生成）
│   └── venv/                 # Python 虚拟环境（运行时生成）
│
└── frontend/                  # 前端目录
    ├── public/                # 静态资源
    │
    ├── src/                   # 源代码
    │   ├── main.tsx          # React 应用入口
    │   ├── App.tsx           # 根组件
    │   ├── App.css           # 全局样式
    │   ├── index.css         # 基础样式
    │   ├── vite-env.d.ts     # TypeScript 环境声明
    │   │
    │   ├── layouts/          # 布局组件
    │   │   └── MainLayout.tsx  # 主布局（Header + Content + Footer）
    │   │
    │   ├── pages/            # 页面组件
    │   │   ├── Dashboard.tsx  # 数据看板页面
    │   │   └── Upload.tsx     # 文件上传页面
    │   │
    │   ├── services/         # API 服务层
    │   │   └── api.ts        # API 请求封装
    │   │
    │   └── utils/            # 工具函数（可扩展）
    │
    ├── index.html            # HTML 入口
    ├── package.json          # npm 依赖配置
    ├── tsconfig.json         # TypeScript 配置
    ├── tsconfig.node.json    # TypeScript Node 配置
    ├── vite.config.ts        # Vite 构建配置
    ├── .gitignore           # Git 忽略配置
    ├── node_modules/        # npm 依赖（运行时生成）
    └── dist/                # 构建产物（运行时生成）
```

## 文件说明

### 根目录文件

| 文件 | 说明 |
|------|------|
| `README.md` | 项目主文档，包含项目简介、技术栈、快速开始 |
| `QUICKSTART.md` | 5分钟快速上手指南 |
| `ARCHITECTURE.md` | 系统架构设计文档，包含技术选型、模块设计、数据流 |
| `DEPLOYMENT.md` | 生产环境部署指南（Docker、Nginx、性能优化） |
| `PROJECT_STRUCTURE.md` | 本文件，项目结构说明 |
| `start.sh` | 一键启动脚本（自动配置环境、启动服务） |
| `.editorconfig` | 编辑器代码风格配置 |

### 后端核心文件

| 文件 | 职责 | 关键内容 |
|------|------|----------|
| `backend/app/main.py` | 应用入口 | FastAPI app, CORS, 路由注册 |
| `backend/app/config.py` | 配置管理 | 环境变量、上传目录、CORS 白名单 |
| `backend/app/api/routes.py` | API 端点 | `/upload`, `/analyze`, `/export` 等 |
| `backend/app/models/schemas.py` | 数据模型 | Pydantic 模型（验证、序列化） |
| `backend/app/services/excel_processor.py` | 核心业务逻辑 | Excel 读取、分析、回写 |
| `backend/app/utils/helpers.py` | 工具函数 | 格式化、验证、文件操作 |
| `backend/requirements.txt` | 依赖列表 | fastapi, pandas, openpyxl 等 |

### 前端核心文件

| 文件 | 职责 | 关键内容 |
|------|------|----------|
| `frontend/src/main.tsx` | React 入口 | ReactDOM render, ConfigProvider |
| `frontend/src/App.tsx` | 根组件 | React Router, 路由配置 |
| `frontend/src/layouts/MainLayout.tsx` | 主布局 | Header, Menu, Footer |
| `frontend/src/pages/Dashboard.tsx` | 数据看板 | ECharts 图表、统计卡片、表格 |
| `frontend/src/pages/Upload.tsx` | 文件上传 | Dragger 组件、上传逻辑、步骤引导 |
| `frontend/src/services/api.ts` | API 层 | Axios 封装、接口定义 |
| `frontend/vite.config.ts` | 构建配置 | 代理、别名、插件 |
| `frontend/package.json` | 依赖管理 | react, antd, echarts 等 |

## 运行时生成的目录/文件

### 后端
- `backend/venv/`: Python 虚拟环境
- `backend/uploads/`: 上传的 Excel 文件存储
- `backend/__pycache__/`: Python 字节码缓存

### 前端
- `frontend/node_modules/`: npm 依赖包
- `frontend/dist/`: 生产构建产物

## 关键模块依赖关系

```
前端 (React)
  ↓ HTTP/REST API
后端 (FastAPI)
  ├─ routes.py → excel_processor.py
  ├─ excel_processor.py → pandas, openpyxl
  └─ schemas.py ← config.py
```

## 扩展指南

### 添加新 API 端点

1. 在 `backend/app/api/routes.py` 添加路由函数
2. 在 `backend/app/services/` 添加业务逻辑
3. 在 `backend/app/models/schemas.py` 定义数据模型
4. 在 `frontend/src/services/api.ts` 添加前端调用方法

### 添加新页面

1. 在 `frontend/src/pages/` 创建新组件
2. 在 `frontend/src/App.tsx` 添加路由
3. 在 `frontend/src/layouts/MainLayout.tsx` 添加菜单项

### 添加新图表

1. 在 `frontend/src/pages/Dashboard.tsx` 添加 ECharts option 配置
2. 使用 `<ReactECharts option={...} />` 渲染
3. 确保后端返回对应的数据结构

## 代码风格

### Python (后端)
- 遵循 PEP 8
- 使用类型提示
- 函数/类添加 docstring

### TypeScript (前端)
- 使用 ESLint 规则
- 函数式组件 + Hooks
- 明确类型定义

## Git 工作流

```bash
# 开发新功能
git checkout -b feature/new-feature

# 提交代码
git add .
git commit -m "feat: add new feature"

# 推送到远程
git push origin feature/new-feature

# 创建 Pull Request
```

## 环境变量

### 后端 (backend/.env)
```env
APP_NAME=CorpPilot
APP_VERSION=1.0.0
DEBUG=True
ALLOWED_ORIGINS=http://localhost:5173
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=50
```

### 前端
前端通过 Vite 的代理配置连接后端，无需额外环境变量。

## 依赖更新

### 后端
```bash
pip list --outdated
pip install -U package_name
pip freeze > requirements.txt
```

### 前端
```bash
npm outdated
npm update
npm install package@latest
```

---

**维护者**: GalaxySpace AI Team  
**版本**: 1.0.0  
**最后更新**: 2026-01-05


