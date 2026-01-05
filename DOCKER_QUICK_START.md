# 🚀 CorpPilot Docker 快速启动

## 📦 已创建的文件清单

```
✅ docker-compose.yml          Docker 编排配置
✅ backend/Dockerfile          后端镜像配置
✅ backend/.dockerignore       后端构建排除文件
✅ frontend/Dockerfile         前端镜像配置（多阶段构建）
✅ frontend/nginx.conf         Nginx 配置（反向代理 + SPA 支持）
✅ frontend/.dockerignore      前端构建排除文件
✅ deploy.sh                   一键部署脚本
✅ restart-dev.sh              快速重启脚本
✅ stop.sh                     停止服务脚本
```

## ⚡ 三步快速部署

```bash
# Step 1: 赋予执行权限（仅首次需要）
chmod +x deploy.sh restart-dev.sh stop.sh

# Step 2: 一键部署
./deploy.sh

# Step 3: 访问应用
open http://localhost:8180
```

## 🎯 核心特性

### 1️⃣ 开发模式优化
- ✅ **后端热重载**: 修改 Python 代码立即生效（volume 挂载）
- ✅ **快速重启**: `restart-dev.sh` 利用 Docker 缓存，无需重装依赖
- ✅ **健康检查**: 自动监测服务状态

### 2️⃣ Nginx 配置亮点
```nginx
# ✅ API 反向代理（解决跨域）
location /api {
    proxy_pass http://backend:8000;
}

# ✅ React Router 支持（防止刷新 404）
location / {
    try_files $uri $uri/ /index.html;
}

# ✅ 静态资源缓存（提升性能）
location ~* \.(js|css|png|jpg)$ {
    expires 1y;
}
```

### 3️⃣ 多阶段构建
前端镜像从 **~1GB** 优化到 **~40MB**

## 📋 常用操作速查

| 操作 | 命令 | 说明 |
|------|------|------|
| 🚀 首次部署 | `./deploy.sh` | 构建镜像并启动 |
| 🔄 快速重启 | `./restart-dev.sh` | 应用代码变更 |
| 🛑 停止服务 | `./stop.sh` | 停止所有容器 |
| 📊 查看状态 | `docker-compose ps` | 查看运行状态 |
| 📜 查看日志 | `docker-compose logs -f` | 实时日志输出 |
| 🐛 后端日志 | `docker-compose logs -f backend` | 仅后端日志 |
| 🎨 前端日志 | `docker-compose logs -f frontend` | 仅前端日志 |
| 🔧 进入容器 | `docker exec -it corppilot-backend bash` | 后端调试 |
| 🔄 重启后端 | `docker-compose restart backend` | 仅重启后端 |

## 🌐 访问地址

| 服务 | URL | 说明 |
|------|-----|------|
| 🎨 前端界面 | http://localhost:8180 | React 应用 |
| 🔧 后端 API | http://localhost:8000 | FastAPI 接口 |
| 📚 API 文档 | http://localhost:8180/docs | Swagger UI |
| 📖 Redoc 文档 | http://localhost:8180/redoc | ReDoc UI |

## 🔄 开发工作流

### 场景 1: 修改后端代码
```bash
# 1. 编辑 Python 文件
vim backend/app/api/routes.py

# 2. 无需操作！Uvicorn 会自动重载
# 3. 刷新浏览器测试
```

### 场景 2: 修改前端代码
```bash
# 1. 编辑 React 文件
vim frontend/src/App.tsx

# 2. 快速重启前端
./restart-dev.sh

# 3. 刷新浏览器测试（约 10-30 秒）
```

### 场景 3: 新增依赖
```bash
# 1. 修改 requirements.txt 或 package.json
echo "requests==2.31.0" >> backend/requirements.txt

# 2. 完整重新部署
./deploy.sh

# 3. 测试新功能
```

## 🐛 故障排查

### 问题 1: 端口 8180 被占用
```bash
# 查找占用进程
lsof -i :8180

# 方案1: 杀死进程
kill -9 <PID>

# 方案2: 修改端口
# 编辑 docker-compose.yml，将 "8180:80" 改为 "8181:80"
```

### 问题 2: 前端无法访问后端
```bash
# 检查后端是否运行
docker-compose ps backend

# 查看后端日志
docker-compose logs backend

# 测试后端连接
curl http://localhost:8000/
```

### 问题 3: 刷新页面 404
```bash
# 检查 nginx.conf 是否正确
docker exec -it corppilot-frontend cat /etc/nginx/conf.d/default.conf

# 重启前端容器
docker-compose restart frontend
```

### 问题 4: 代码修改不生效
```bash
# 后端：确认 volume 挂载
docker inspect corppilot-backend | grep Mounts

# 前端：重新构建
./restart-dev.sh

# 清除所有缓存重新部署
./stop.sh
./deploy.sh
```

## 📊 性能监控

```bash
# 查看资源占用
docker stats

# 查看镜像大小
docker images | grep corppilot

# 预期大小：
# - backend: ~500MB (Python + 依赖)
# - frontend: ~40MB (Nginx + 静态文件)
```

## 🔐 生产环境部署

### 快速切换到生产模式

1. **编辑 `backend/Dockerfile`**:
```dockerfile
# 移除 --reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **编辑 `docker-compose.yml`**:
```yaml
backend:
  # 注释掉 volume
  # volumes:
  #   - ./backend:/app
  environment:
    - DEBUG=False
```

3. **重新部署**:
```bash
./stop.sh
./deploy.sh
```

## 💡 最佳实践

### ✅ DO (推荐)
- ✅ 开发时使用 `restart-dev.sh` 快速迭代
- ✅ 提交代码前运行完整的 `deploy.sh` 测试
- ✅ 定期运行 `docker system prune` 清理资源
- ✅ 使用 `docker-compose logs` 查看错误信息

### ❌ DON'T (避免)
- ❌ 不要直接修改容器内的文件
- ❌ 不要在生产环境使用 `--reload`
- ❌ 不要提交 `.env` 文件到 Git
- ❌ 不要忽略健康检查失败的警告

## 📚 进阶阅读

- 📖 [完整部署文档](DOCKER_DEPLOYMENT.md)
- 🔧 [项目架构说明](ARCHITECTURE.md)
- 🚀 [快速开始指南](QUICKSTART.md)

---

## 🎉 部署成功示例

```bash
$ ./deploy.sh

==========================================
  CorpPilot Docker 一键部署脚本
==========================================

✅ Docker 环境检查通过

🧹 清理旧容器...

🔨 开始构建 Docker 镜像...
   这可能需要几分钟时间，请耐心等待...

✅ 镜像构建完成

🚀 启动服务...

✅ 服务启动成功！

📊 服务状态：
NAME                  STATUS    PORTS
corppilot-backend     Up        0.0.0.0:8000->8000/tcp
corppilot-frontend    Up        0.0.0.0:8180->80/tcp

==========================================
  🎉 部署完成！
==========================================

📍 访问地址：
   前端界面： http://localhost:8180
   后端 API： http://localhost:8000
   API 文档： http://localhost:8180/docs
```

**🎊 现在可以开始使用了！**

