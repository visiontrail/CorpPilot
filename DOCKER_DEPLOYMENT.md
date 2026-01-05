# CorpPilot Docker 部署指南

## 📋 目录结构

```
CostMatrix/
├── docker-compose.yml          # Docker Compose 编排文件
├── deploy.sh                   # 一键部署脚本
├── restart-dev.sh             # 快速重启脚本（开发用）
├── stop.sh                    # 停止服务脚本
├── backend/
│   ├── Dockerfile             # 后端 Docker 镜像
│   ├── requirements.txt       # Python 依赖
│   └── app/                   # FastAPI 应用代码
└── frontend/
    ├── Dockerfile             # 前端 Docker 镜像（多阶段构建）
    ├── nginx.conf             # Nginx 配置文件
    ├── package.json           # Node 依赖
    └── src/                   # React 应用代码
```

## 🚀 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+（或 docker-compose 1.29+）

### 一键部署

```bash
# 赋予执行权限（首次运行）
chmod +x deploy.sh restart-dev.sh stop.sh

# 一键部署
./deploy.sh
```

部署完成后，访问：
- **前端界面**: http://localhost:8180
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8180/docs

## 📦 容器架构

### 服务组成

| 服务 | 容器名 | 端口映射 | 说明 |
|------|--------|----------|------|
| backend | corppilot-backend | 8000:8000 | FastAPI 后端服务 |
| frontend | corppilot-frontend | 8180:80 | React 前端 + Nginx |

### 网络架构

```
                    ┌─────────────────────────┐
                    │   宿主机 (Host)          │
                    │   Port: 8180            │
                    └──────────┬──────────────┘
                               │
                    ┌──────────▼──────────────┐
                    │  Frontend Container     │
                    │  - React App (静态)     │
                    │  - Nginx (Port 80)      │
                    └──────────┬──────────────┘
                               │
                    ┌──────────▼──────────────┐
                    │  /api/* 反向代理         │
                    └──────────┬──────────────┘
                               │
                    ┌──────────▼──────────────┐
                    │  Backend Container      │
                    │  - FastAPI (Port 8000)  │
                    │  - Uvicorn (--reload)   │
                    └─────────────────────────┘
```

## 🔧 开发模式特性

### 后端热重载

后端代码通过 **volume 挂载** 实现热重载：

```yaml
volumes:
  - ./backend:/app  # 本地代码映射到容器
```

**效果**：修改 Python 代码后，无需重启容器，uvicorn 会自动重载。

### 前端开发流程

前端使用 **多阶段构建**，修改代码后需要重新构建：

```bash
# 方法1：快速重启（推荐）
./restart-dev.sh

# 方法2：手动重启前端容器
docker-compose build frontend
docker-compose up -d frontend
```

## 📝 脚本说明

### 1. deploy.sh - 一键部署

**功能**：
- ✅ 检查 Docker 环境
- 🧹 清理旧容器
- 🔨 构建镜像（--no-cache）
- 🚀 启动所有服务
- 📊 显示服务状态

**使用场景**：
- 首次部署
- 新增了 npm/pip 依赖
- 需要完全重新构建

```bash
./deploy.sh
```

### 2. restart-dev.sh - 快速重启

**功能**：
- 🔍 检测依赖文件变更
- 🔨 仅重新构建前端镜像
- 🚀 重启前端服务
- ⚡ 利用 Docker 缓存层，速度快

**使用场景**：
- 修改了前端业务代码
- 修改了后端业务代码（会自动热重载）
- **不适用于**：新增依赖（请用 deploy.sh）

```bash
./restart-dev.sh
```

**智能提示**：
- 如果检测到 `requirements.txt` 或 `package.json` 变更，会提示是否需要完整部署

### 3. stop.sh - 停止服务

**功能**：
- 🛑 停止所有容器
- 🗑️ 清理网络
- 🧹 可选：清理 Docker 资源

```bash
./stop.sh
```

## 🔍 常用命令

### 查看日志

```bash
# 所有服务日志
docker-compose logs -f

# 仅查看后端日志
docker-compose logs -f backend

# 仅查看前端日志
docker-compose logs -f frontend

# 查看最近 100 行
docker-compose logs --tail=100
```

### 进入容器

```bash
# 进入后端容器
docker exec -it corppilot-backend bash

# 进入前端容器
docker exec -it corppilot-frontend sh
```

### 检查服务状态

```bash
# 查看运行中的容器
docker-compose ps

# 查看资源占用
docker stats
```

### 重启单个服务

```bash
# 重启后端
docker-compose restart backend

# 重启前端
docker-compose restart frontend
```

## 🐛 故障排查

### 1. 端口冲突

**问题**：`port 8180 is already in use`

**解决**：
```bash
# 查找占用端口的进程
lsof -i :8180

# 杀死进程
kill -9 <PID>

# 或修改 docker-compose.yml 中的端口
ports:
  - "8181:80"  # 改为其他端口
```

### 2. 后端无法连接

**问题**：前端显示 API 请求失败

**检查**：
```bash
# 1. 检查后端是否运行
docker-compose ps backend

# 2. 查看后端日志
docker-compose logs backend

# 3. 测试后端健康状态
curl http://localhost:8000/

# 4. 进入前端容器测试网络
docker exec -it corppilot-frontend sh
wget -O- http://backend:8000/
```

### 3. 前端 404 错误

**问题**：刷新页面后出现 404

**原因**：Nginx 配置未正确支持 React Router

**检查**：确认 `nginx.conf` 包含：
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

### 4. 镜像构建失败

**问题**：npm install 或 pip install 超时

**解决**：
```bash
# 方案1：使用国内镜像（已配置）
# - Python: 清华源
# - Node: 淘宝镜像

# 方案2：清理缓存重新构建
docker-compose build --no-cache

# 方案3：手动构建查看详细错误
docker build -t test-backend ./backend
docker build -t test-frontend ./frontend
```

### 5. 后端代码修改不生效

**检查**：
```bash
# 1. 确认 volume 挂载正确
docker inspect corppilot-backend | grep -A 5 Mounts

# 2. 确认 uvicorn 使用了 --reload
docker logs corppilot-backend | grep reload

# 3. 手动重启后端
docker-compose restart backend
```

## 📊 性能优化

### 多阶段构建优势

前端 Dockerfile 使用多阶段构建：
- **构建阶段**：Node 18 (约 1GB)
- **运行阶段**：Nginx Alpine (约 40MB)

**效果**：最终镜像体积减少 90%+

### 缓存优化

```dockerfile
# ✅ 正确：先复制依赖文件，利用缓存
COPY package*.json ./
RUN npm install
COPY . .

# ❌ 错误：每次代码变更都重装依赖
COPY . .
RUN npm install
```

## 🚀 生产环境部署

### 修改配置

1. **禁用后端热重载**

编辑 `backend/Dockerfile`:
```dockerfile
# 移除 --reload 参数
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **移除 volume 挂载**

编辑 `docker-compose.yml`:
```yaml
backend:
  # volumes:
  #   - ./backend:/app  # 生产环境注释掉
```

并在 `backend/Dockerfile` 中取消注释：
```dockerfile
COPY . .  # 生产环境启用
```

3. **配置环境变量**

创建 `.env` 文件：
```env
DEBUG=False
ALLOWED_ORIGINS=https://yourdomain.com
DATABASE_URL=postgresql://...
```

更新 `docker-compose.yml`:
```yaml
backend:
  env_file:
    - .env
```

### 安全加固

```yaml
# docker-compose.yml
services:
  backend:
    read_only: true  # 只读文件系统
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
```

## 📖 相关文档

- [Docker 官方文档](https://docs.docker.com/)
- [FastAPI 部署指南](https://fastapi.tiangolo.com/deployment/)
- [Nginx 配置参考](https://nginx.org/en/docs/)
- [React 生产构建](https://react.dev/learn/start-a-new-react-project#building-for-production)

## ❓ 常见问题

**Q: 为什么后端使用 volume 挂载，前端不用？**

A: 
- 后端：Python 是解释型语言，代码修改后 uvicorn 可以直接重载
- 前端：需要编译构建（TypeScript → JavaScript，模块打包），必须重新 build

**Q: 如何修改对外端口？**

A: 编辑 `docker-compose.yml`，修改 frontend 的 ports：
```yaml
ports:
  - "8181:80"  # 8181 改为你想要的端口
```

**Q: 可以同时运行多个实例吗？**

A: 可以，但需要修改容器名和端口避免冲突：
```bash
# 复制项目
cp -r CostMatrix CostMatrix-test
cd CostMatrix-test

# 修改 docker-compose.yml 中的容器名和端口
# 然后部署
./deploy.sh
```

---

**🎉 部署成功后，欢迎访问 http://localhost:8180 开始使用！**

