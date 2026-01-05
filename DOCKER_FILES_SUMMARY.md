# 🐳 Docker 配置文件汇总

## 📁 文件清单

本次为 **CorpPilot** 项目创建了完整的 Docker 部署配置，以下是所有文件的详细说明：

### 1️⃣ Docker 核心配置文件

#### 📄 `docker-compose.yml`
**位置**: 项目根目录  
**用途**: Docker Compose 编排配置文件  
**核心功能**:
- 定义 `backend` 和 `frontend` 两个服务
- 配置服务间网络通信
- 设置端口映射（8180 → frontend:80）
- Volume 挂载（开发模式后端代码热重载）
- 健康检查配置

**关键配置**:
```yaml
services:
  backend:
    volumes:
      - ./backend:/app  # 代码挂载，支持热重载
  frontend:
    ports:
      - "8180:80"      # 对外服务端口
```

---

#### 📄 `backend/Dockerfile`
**位置**: `backend/` 目录  
**用途**: 后端 Python FastAPI 镜像配置  
**核心功能**:
- 基于 `python:3.9-slim`
- 使用清华源加速 pip 安装
- 配置 uvicorn 热重载
- 暴露端口 8000

**特点**:
- ✅ 开发模式：代码通过 volume 挂载
- ✅ 生产模式：取消注释 `COPY . .` 即可

**命令**:
```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

---

#### 📄 `frontend/Dockerfile`
**位置**: `frontend/` 目录  
**用途**: 前端 React + Nginx 镜像配置  
**核心功能**:
- **Stage 1**: Node 18 构建 React 应用
- **Stage 2**: Nginx Alpine 托管静态文件
- 多阶段构建优化镜像大小（~1GB → ~40MB）

**构建流程**:
```
Node.js 构建 → npm install → npm run build
                                ↓
                         复制 dist 到 Nginx
                                ↓
                         最终镜像: Nginx + 静态文件
```

---

#### 📄 `frontend/nginx.conf`
**位置**: `frontend/` 目录  
**用途**: Nginx 配置文件  
**核心功能**:
- ✅ API 反向代理: `/api` → `backend:8000`
- ✅ SPA 支持: `try_files $uri $uri/ /index.html`
- ✅ 静态资源缓存: 1 年过期时间
- ✅ Gzip 压缩
- ✅ 代理 API 文档: `/docs`, `/redoc`

**关键配置**:
```nginx
# API 反向代理（解决跨域）
location /api {
    proxy_pass http://backend:8000;
}

# React Router 支持（防止刷新 404）
location / {
    try_files $uri $uri/ /index.html;
}
```

---

### 2️⃣ 自动化脚本

#### 📄 `deploy.sh`
**用途**: 🚀 一键部署脚本  
**功能**:
- ✅ 检查 Docker 环境
- 🧹 清理旧容器
- 🔨 构建镜像 (`--no-cache`)
- 🚀 启动所有服务
- 📊 显示服务状态

**使用场景**:
- 首次部署
- 新增依赖
- 完全重新构建

**执行**:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

#### 📄 `restart-dev.sh`
**用途**: 🔄 快速重启脚本  
**功能**:
- 🔍 智能检测依赖文件变更 (requirements.txt, package.json)
- 🔨 仅重新构建前端镜像
- ⚡ 利用 Docker 缓存层，速度极快
- 📝 生成依赖文件 hash 用于检测变更

**使用场景**:
- 修改前端业务代码
- 修改后端业务代码（自动热重载）

**执行**:
```bash
./restart-dev.sh
```

**智能提示**: 如检测到依赖变更，会提示是否需要完整部署

---

#### 📄 `stop.sh`
**用途**: 🛑 停止服务脚本  
**功能**:
- 停止所有容器
- 清理网络
- 可选：清理 Docker 资源

**执行**:
```bash
./stop.sh
```

---

### 3️⃣ 构建优化文件

#### 📄 `backend/.dockerignore`
**用途**: 排除后端不需要的文件，加速构建  
**排除内容**:
- `__pycache__`, `*.pyc`
- `.vscode`, `.idea`
- `*.md`, `.git`
- 测试文件和日志

---

#### 📄 `frontend/.dockerignore`
**用途**: 排除前端不需要的文件，加速构建  
**排除内容**:
- `node_modules` (会在容器内重新安装)
- `dist`, `build`
- `.env*` 文件
- 开发工具配置

---

### 4️⃣ 配置文件

#### 📄 `.env.example`
**用途**: 环境变量模板  
**包含配置**:
- 应用环境 (development/production)
- 调试模式
- CORS 配置
- 数据库连接（可选）
- 文件上传设置
- 日志级别

**使用方法**:
```bash
cp .env.example .env
vim .env  # 修改配置
```

---

### 5️⃣ 文档文件

#### 📄 `DOCKER_DEPLOYMENT.md`
**用途**: 📖 完整部署文档  
**包含内容**:
- 详细架构说明
- 故障排查指南
- 性能优化建议
- 生产环境配置
- 常见问题解答

---

#### 📄 `DOCKER_QUICK_START.md`
**用途**: ⚡ 快速启动指南  
**包含内容**:
- 三步快速部署
- 常用命令速查表
- 开发工作流示例
- 快速故障排查

---

#### 📄 `DOCKER_FILES_SUMMARY.md` (本文件)
**用途**: 📋 文件清单汇总  

---

## 📊 文件结构树

```
CostMatrix/
├── docker-compose.yml              # Docker Compose 编排
├── .env.example                    # 环境变量模板
├── deploy.sh                       # 一键部署脚本
├── restart-dev.sh                  # 快速重启脚本
├── stop.sh                         # 停止服务脚本
│
├── backend/
│   ├── Dockerfile                  # 后端镜像配置
│   ├── .dockerignore               # 后端构建排除
│   ├── requirements.txt            # Python 依赖
│   └── app/                        # FastAPI 代码
│
├── frontend/
│   ├── Dockerfile                  # 前端镜像配置（多阶段）
│   ├── nginx.conf                  # Nginx 配置
│   ├── .dockerignore               # 前端构建排除
│   ├── package.json                # Node 依赖
│   └── src/                        # React 代码
│
└── docs/
    ├── DOCKER_DEPLOYMENT.md        # 完整部署文档
    ├── DOCKER_QUICK_START.md       # 快速启动指南
    └── DOCKER_FILES_SUMMARY.md     # 本文件
```

---

## 🎯 核心设计理念

### 1. 开发体验优化
- ✅ **后端热重载**: Volume 挂载 + uvicorn --reload
- ✅ **快速迭代**: restart-dev.sh 利用 Docker 缓存
- ✅ **智能检测**: 自动识别依赖文件变更

### 2. 生产环境就绪
- ✅ **多阶段构建**: 前端镜像体积优化 90%+
- ✅ **健康检查**: 自动监测服务状态
- ✅ **安全配置**: 环境变量隔离

### 3. 部署简化
- ✅ **一键部署**: 3 个脚本搞定所有操作
- ✅ **自动化**: 环境检查 + 错误提示
- ✅ **跨平台**: Linux/macOS/Windows 兼容

---

## 🚀 快速使用指南

### Step 1: 赋予脚本执行权限
```bash
chmod +x deploy.sh restart-dev.sh stop.sh
```

### Step 2: 一键部署
```bash
./deploy.sh
```

### Step 3: 访问应用
- 🎨 前端: http://localhost:8180
- 🔧 后端: http://localhost:8000
- 📚 文档: http://localhost:8180/docs

---

## 📈 技术亮点

### 1. Nginx 反向代理配置
解决前后端分离的跨域问题：
```nginx
location /api {
    proxy_pass http://backend:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

### 2. React Router History 模式支持
防止刷新页面 404：
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

### 3. Docker 多阶段构建
优化镜像大小：
```dockerfile
# Stage 1: Build
FROM node:18-alpine AS builder
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

**效果**: 
- 构建阶段: ~1GB (Node.js)
- 最终镜像: ~40MB (Nginx)

### 4. Volume 挂载开发模式
后端代码实时生效：
```yaml
volumes:
  - ./backend:/app
```

### 5. 智能依赖检测
`restart-dev.sh` 自动检测 requirements.txt 和 package.json 变更。

---

## 🔧 维护建议

### 定期清理
```bash
# 清理未使用的镜像和容器
docker system prune -a

# 清理 volume
docker volume prune
```

### 更新依赖
```bash
# 1. 修改 requirements.txt 或 package.json
# 2. 重新部署
./deploy.sh
```

### 查看日志
```bash
# 所有日志
docker-compose logs -f

# 特定服务
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## ✅ 质量检查清单

部署前请确认：

- [ ] Docker 和 Docker Compose 已安装
- [ ] 端口 8180 和 8000 未被占用
- [ ] 所有脚本有执行权限 (`chmod +x`)
- [ ] `.env` 文件已配置（可选）
- [ ] 防火墙允许对应端口（生产环境）

---

## 📞 问题反馈

如遇到问题，请按以下顺序排查：

1. **查看日志**: `docker-compose logs -f`
2. **检查状态**: `docker-compose ps`
3. **测试网络**: `docker exec -it corppilot-frontend wget -O- http://backend:8000/`
4. **重新部署**: `./stop.sh && ./deploy.sh`

如问题仍未解决，请查阅：
- 📖 [完整部署文档](DOCKER_DEPLOYMENT.md)
- ⚡ [快速启动指南](DOCKER_QUICK_START.md)

---

## 🎉 部署成功标志

当你看到以下输出时，说明部署成功：

```
==========================================
  🎉 部署完成！
==========================================

📍 访问地址：
   前端界面： http://localhost:8180
   后端 API： http://localhost:8000
   API 文档： http://localhost:8180/docs

📊 服务状态：
NAME                  STATUS    PORTS
corppilot-backend     Up        0.0.0.0:8000->8000/tcp
corppilot-frontend    Up        0.0.0.0:8180->80/tcp
```

**🚀 现在可以开始使用 CorpPilot 了！**

---

**创建时间**: 2026年1月5日  
**项目**: CorpPilot (企业级行政与差旅成本效能分析平台)  
**维护者**: DevOps Team

