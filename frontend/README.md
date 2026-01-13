# CostMatrix Frontend

React + Vite + Ant Design Pro 前端应用。

## 技术栈

- **React 18**: UI 框架
- **Vite**: 构建工具
- **TypeScript**: 类型安全
- **Ant Design**: UI 组件库
- **ECharts**: 数据可视化
- **Axios**: HTTP 客户端

## 快速开始

### 安装依赖

```bash
npm install
# 或
yarn install
```

### 开发模式

```bash
npm run dev
```

访问: http://localhost:5173

### 生产构建

```bash
npm run build
```

构建产物在 `dist/` 目录。

## 项目结构

```
src/
├── main.tsx              # 入口文件
├── App.tsx               # 根组件
├── layouts/              # 布局
│   └── MainLayout.tsx
├── pages/                # 页面
│   ├── Dashboard.tsx
│   └── Upload.tsx
└── services/             # API 服务
    └── api.ts
```

## 核心功能

### 1. 文件上传

```typescript
import { Upload } from 'antd'
import { uploadFile } from '@/services/api'

const handleUpload = async (file: File) => {
  const result = await uploadFile(file)
  console.log(result.data.file_path)
}
```

### 2. 数据可视化

```typescript
import ReactECharts from 'echarts-for-react'

const option = {
  title: { text: '成本分布' },
  series: [{
    type: 'pie',
    data: departmentCosts
  }]
}

<ReactECharts option={option} />
```

### 3. API 调用

```typescript
import { analyzeExcel } from '@/services/api'

const data = await analyzeExcel(filePath)
console.log(data.overview)
```

## 环境配置

### Vite 代理配置

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

## 组件说明

### MainLayout

主布局组件，包含 Header、Menu、Footer。

**Props**: 无

**Usage**:
```tsx
<MainLayout>
  <YourPage />
</MainLayout>
```

### Dashboard

数据看板页面，展示所有分析结果。

**Features**:
- 统计卡片（总成本、项目数、部门数、异常数）
- 部门成本饼图
- 项目成本柱状图
- 差旅类型堆叠图
- 异常记录表格

### Upload

文件上传页面，支持拖拽上传。

**Features**:
- 文件类型验证
- 上传进度显示
- 自动触发分析
- 步骤引导

## 样式定制

### 主题配置

```tsx
import { ConfigProvider } from 'antd'

<ConfigProvider theme={{
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 6,
  }
}}>
  <App />
</ConfigProvider>
```

### 自定义样式

```css
/* App.css */
.chart-card {
  margin-bottom: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
```

## 路由配置

```tsx
import { Routes, Route } from 'react-router-dom'

<Routes>
  <Route path="/" element={<MainLayout />}>
    <Route index element={<Dashboard />} />
    <Route path="upload" element={<Upload />} />
  </Route>
</Routes>
```

## 状态管理

使用 localStorage 缓存 Dashboard 数据：

```typescript
// 保存
localStorage.setItem('dashboard_data', JSON.stringify(data))

// 读取
const data = JSON.parse(localStorage.getItem('dashboard_data'))
```

## 部署

### Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /var/www/costmatrix/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

### Docker

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
```

## 优化建议

1. **代码分割**: 使用 React.lazy() 懒加载路由
2. **缓存策略**: 配置 Service Worker
3. **CDN 加速**: 静态资源使用 CDN
4. **Gzip 压缩**: Nginx 启用 Gzip

## License

MIT


