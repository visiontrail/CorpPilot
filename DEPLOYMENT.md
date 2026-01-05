# CorpPilot 部署指南

## 环境要求

### 后端
- Python 3.8+
- pip (Python 包管理器)

### 前端
- Node.js 16+
- npm 或 yarn

## 本地开发部署

### 方式一：一键启动（推荐）

```bash
# 给启动脚本添加执行权限
chmod +x start.sh

# 运行启动脚本
./start.sh
```

### 方式二：手动启动

#### 1. 启动后端

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（首次运行）
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --port 8000
```

后端服务将在 `http://localhost:8000` 启动。

#### 2. 启动前端

```bash
# 打开新终端，进入前端目录
cd frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 `http://localhost:5173` 启动。

## 生产环境部署

### 后端部署

#### 使用 Gunicorn + Nginx

1. **安装 Gunicorn**

```bash
pip install gunicorn
```

2. **启动 Gunicorn**

```bash
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

3. **配置 Nginx**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

### 前端部署

1. **构建生产版本**

```bash
cd frontend
npm run build
```

构建产物将在 `dist` 目录中。

2. **部署到静态服务器**

将 `dist` 目录的内容部署到 Nginx、Apache 或其他静态文件服务器。

### Docker 部署

#### 后端 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 前端 Dockerfile

```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/uploads:/app/uploads
    environment:
      - DEBUG=False

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

## 数据持久化

上传的文件默认存储在 `backend/uploads` 目录中。生产环境建议：

1. **使用对象存储服务**（如 AWS S3、阿里云 OSS）
2. **配置独立的文件存储卷**
3. **定期备份上传文件**

## 性能优化

### 后端优化

1. **启用多进程**

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. **配置缓存**（Redis）

3. **数据库优化**（如需持久化存储）

### 前端优化

1. **启用 CDN** 加速静态资源
2. **Gzip 压缩**
3. **按需加载**路由组件

## 监控和日志

### 后端日志

配置日志记录到文件或日志服务：

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 前端错误监控

集成 Sentry 或其他前端监控服务。

## 安全建议

1. **启用 HTTPS**
2. **配置 CORS** 白名单
3. **文件上传限制**（大小、类型）
4. **API 认证**（JWT Token）
5. **定期更新依赖**

## 故障排查

### 后端无法启动

- 检查 Python 版本
- 检查依赖是否安装完整
- 查看错误日志

### 前端无法连接后端

- 检查 CORS 配置
- 检查 API 代理配置
- 查看浏览器控制台错误

### 文件上传失败

- 检查上传目录权限
- 检查文件大小限制
- 检查磁盘空间

## 技术支持

如有问题，请联系：
- Email: support@galaxyspace.ai
- GitHub Issues: [项目仓库地址]


