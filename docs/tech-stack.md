# 技术栈详细方案

## 一、前端技术栈

### 1.1 核心框架选择

#### 方案 A: React 生态（推荐）
```json
{
  "framework": "React 18+",
  "build_tool": "Vite 5+",
  "state_management": "Zustand",
  "routing": "React Router 6+",
  "ui_library": "Ant Design 5+",
  "styling": "Tailwind CSS 3+"
}
```

**优势**:
- 生态成熟，组件丰富
- 性能优秀，开发体验好
- 社区活跃，问题解决快

#### 方案 B: Vue 生态
```json
{
  "framework": "Vue 3+",
  "build_tool": "Vite 5+",
  "state_management": "Pinia",
  "routing": "Vue Router 4+",
  "ui_library": "Element Plus",
  "styling": "Tailwind CSS 3+"
}
```

**优势**:
- 学习曲线平缓
- 文档完善，中文友好
- 性能优秀

### 1.2 前端依赖清单

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "zustand": "^4.4.7",
    "antd": "^5.12.0",
    "axios": "^1.6.2",
    "dayjs": "^1.11.10",
    "lucide-react": "^0.294.0",
    "framer-motion": "^10.16.16"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.8",
    "typescript": "^5.3.3",
    "tailwindcss": "^3.3.6",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "eslint": "^8.55.0",
    "prettier": "^3.1.1"
  }
}
```

### 1.3 前端目录结构

```
src/
├── assets/              # 静态资源
├── components/          # 公共组件
│   ├── Layout/         # 布局组件
│   ├── ConfigPanel/    # 配置面板
│   ├── WorkflowPanel/  # 流程面板
│   └── LogPanel/       # 日志面板
├── pages/              # 页面
│   ├── Home/           # 首页
│   └── Settings/       # 设置页
├── hooks/              # 自定义 Hooks
│   ├── useLLM.ts       # LLM Hook
│   ├── useWeChat.ts    # 微信 Hook
│   └── useWorkflow.ts  # 流程 Hook
├── services/           # API 服务
│   ├── llm.ts          # LLM API
│   ├── wechat.ts       # 微信 API
│   └── search.ts       # 搜索 API
├── stores/             # 状态管理
│   ├── configStore.ts  # 配置状态
│   └── workflowStore.ts # 流程状态
├── types/              # TypeScript 类型
│   └── index.ts
├── utils/              # 工具函数
│   ├── logger.ts       # 日志工具
│   └── validator.ts    # 验证工具
├── App.tsx
└── main.tsx
```

---

## 二、后端技术栈

### 2.1 核心框架选择

#### 方案 A: Node.js + Express（推荐）
```json
{
  "runtime": "Node.js 20+",
  "framework": "Express 4+",
  "language": "TypeScript",
  "orm": "Prisma",
  "validation": "Zod"
}
```

**优势**:
- JavaScript 全栈，开发效率高
- 异步性能优秀
- 生态丰富

#### 方案 B: Node.js + NestJS
```json
{
  "runtime": "Node.js 20+",
  "framework": "NestJS 10+",
  "language": "TypeScript",
  "orm": "TypeORM",
  "validation": "class-validator"
}
```

**优势**:
- 企业级框架，结构清晰
- 依赖注入，易于测试
- TypeScript 原生支持

### 2.2 后端依赖清单

```json
{
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "helmet": "^7.1.0",
    "dotenv": "^16.3.1",
    "axios": "^1.6.2",
    "sharp": "^0.33.1",
    "cheerio": "^1.0.0-rc.12",
    "ioredis": "^5.3.2",
    "prisma": "^5.7.1",
    "zod": "^3.22.4",
    "winston": "^3.11.0",
    "bull": "^4.12.0"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/node": "^20.10.6",
    "typescript": "^5.3.3",
    "ts-node": "^10.9.2",
    "nodemon": "^3.0.2",
    "eslint": "^8.55.0",
    "prettier": "^3.1.1"
  }
}
```

### 2.3 后端目录结构

```
src/
├── config/             # 配置
│   ├── database.ts     # 数据库配置
│   ├── redis.ts        # Redis 配置
│   └── llm.ts          # LLM 配置
├── controllers/        # 控制器
│   ├── workflow.controller.ts
│   ├── config.controller.ts
│   └── wechat.controller.ts
├── services/           # 服务层
│   ├── llm/            # LLM 服务
│   │   ├── deepseek.service.ts
│   │   ├── gemini.service.ts
│   │   └── openai.service.ts
│   ├── search/         # 搜索服务
│   │   ├── ithome.service.ts
│   │   ├── baidu.service.ts
│   │   └── duckduckgo.service.ts
│   ├── image/          # 图片服务
│   │   ├── processor.service.ts
│   │   ├── search.service.ts
│   │   └── generator.service.ts
│   └── wechat/         # 微信服务
│       ├── api.service.ts
│       ├── token.service.ts
│       └── upload.service.ts
├── models/             # 数据模型
│   ├── User.ts
│   ├── Config.ts
│   └── Task.ts
├── repositories/       # 数据访问层
│   ├── user.repository.ts
│   └── task.repository.ts
├── middleware/         # 中间件
│   ├── auth.middleware.ts
│   ├── error.middleware.ts
│   └── logger.middleware.ts
├── utils/              # 工具函数
│   ├── logger.ts
│   ├── validator.ts
│   └── retry.ts
├── queues/             # 队列
│   └── workflow.queue.ts
├── types/              # TypeScript 类型
│   └── index.ts
└── app.ts
```

---

## 三、数据库设计

### 3.1 PostgreSQL 数据库

#### 用户表 (users)
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 配置表 (configs)
```sql
CREATE TABLE configs (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  llm_api_key TEXT NOT NULL,
  llm_base_url VARCHAR(255) NOT NULL,
  llm_model VARCHAR(100) NOT NULL,
  wechat_app_id VARCHAR(50) NOT NULL,
  wechat_app_secret TEXT NOT NULL,
  enable_research BOOLEAN DEFAULT true,
  enable_image_generation BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 任务表 (tasks)
```sql
CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  topic VARCHAR(500) NOT NULL,
  title VARCHAR(200) NOT NULL,
  content TEXT NOT NULL,
  cover_image_url TEXT,
  tech_diagram_url TEXT,
  status VARCHAR(50) DEFAULT 'pending',
  draft_id VARCHAR(100),
  error_message TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 日志表 (logs)
```sql
CREATE TABLE logs (
  id SERIAL PRIMARY KEY,
  task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
  level VARCHAR(20) NOT NULL,
  message TEXT NOT NULL,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 Redis 缓存设计

#### Token 缓存
```typescript
// Key: wechat:token:{appId}
// Value: { token, expireTime }
// TTL: 7200秒
```

#### 热点缓存
```typescript
// Key: hotspots:{source}:{date}
// Value: [热点列表]
// TTL: 3600秒
```

#### 任务状态缓存
```typescript
// Key: task:status:{taskId}
// Value: { status, progress, result }
// TTL: 86400秒
```

---

## 四、API 设计

### 4.1 RESTful API 规范

#### 配置相关
```typescript
// 获取配置
GET /api/config

// 更新配置
PUT /api/config
Body: {
  llmApiKey: string;
  llmBaseUrl: string;
  llmModel: string;
  wechatAppId: string;
  wechatAppSecret: string;
  enableResearch: boolean;
  enableImageGeneration: boolean;
}

// 初始化微信客户端
POST /api/wechat/init
```

#### 工作流相关
```typescript
// 获取热点
GET /api/hotspots?source=ithome&limit=10

// 生成标题
POST /api/generate/titles
Body: {
  topic: string;
  count: number;
}

// 生成正文
POST /api/generate/article
Body: {
  topic: string;
  title: string;
  enableResearch: boolean;
}

// 全自动模式
POST /api/workflow/auto
Body: {
  topic?: string;
  source?: 'manual' | 'ithome' | 'baidu';
  enableResearch: boolean;
  enableImageGeneration: boolean;
}
```

#### 任务相关
```typescript
// 获取任务列表
GET /api/tasks?page=1&limit=20

// 获取任务详情
GET /api/tasks/:id

// 获取任务日志
GET /api/tasks/:id/logs
```

### 4.2 WebSocket 实时通信

```typescript
// 连接
WS /ws

// 消息格式
{
  "type": "log" | "progress" | "complete" | "error",
  "taskId": string,
  "data": {
    "message": string,
    "progress": number,
    "result": any
  }
}
```

---

## 五、部署方案

### 5.1 Docker 配置

#### Dockerfile
```dockerfile
# 前端 Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```dockerfile
# 后端 Dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["node", "dist/app.js"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://user:pass@postgres:5432/wechat_writer
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=wechat_writer
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 5.2 Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api {
        proxy_pass http://backend:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket
    location /ws {
        proxy_pass http://backend:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }
}
```

---

## 六、监控和日志

### 6.1 日志配置

```typescript
// Winston 日志配置
import winston from 'winston';

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}
```

### 6.2 监控指标

```typescript
// Prometheus 指标
import promClient from 'prom-client';

const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code']
});

const taskExecutionTime = new promClient.Histogram({
  name: 'task_execution_duration_seconds',
  help: 'Duration of task execution in seconds',
  labelNames: ['task_type', 'status']
});

const activeTasks = new promClient.Gauge({
  name: 'active_tasks',
  help: 'Number of currently active tasks'
});
```

---

## 七、安全方案

### 7.1 认证和授权

```typescript
// JWT 认证中间件
import jwt from 'jsonwebtoken';

export const authMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const token = req.headers.authorization?.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
};
```

### 7.2 数据加密

```typescript
// AES 加密工具
import crypto from 'crypto';

const algorithm = 'aes-256-cbc';
const secretKey = crypto.scryptSync(process.env.ENCRYPTION_KEY, 'salt', 32);

export const encrypt = (text: string): string => {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(algorithm, secretKey, iv);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return `${iv.toString('hex')}:${encrypted}`;
};

export const decrypt = (encryptedText: string): string => {
  const [ivHex, encrypted] = encryptedText.split(':');
  const iv = Buffer.from(ivHex, 'hex');
  const decipher = crypto.createDecipheriv(algorithm, secretKey, iv);
  let decrypted = decipher.update(encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
};
```

### 7.3 API 限流

```typescript
// Redis 限流中间件
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

export const rateLimitMiddleware = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const key = `rate_limit:${req.ip}`;
  const limit = 100; // 每分钟100次
  const window = 60; // 60秒窗口

  const current = await redis.incr(key);
  if (current === 1) {
    await redis.expire(key, window);
  }

  if (current > limit) {
    return res.status(429).json({ error: 'Too many requests' });
  }

  next();
};
```

---

## 八、测试方案

### 8.1 单元测试

```typescript
// Jest 测试示例
import { DeepSeekService } from '../services/llm/deepseek.service';

describe('DeepSeekService', () => {
  let service: DeepSeekService;

  beforeEach(() => {
    service = new DeepSeekService('test-api-key');
  });

  test('should generate content', async () => {
    const result = await service.generateContent('test prompt');
    expect(result).toBeDefined();
    expect(result.length).toBeGreaterThan(0);
  });

  test('should handle API errors', async () => {
    await expect(
      service.generateContent('')
    ).rejects.toThrow('Invalid prompt');
  });
});
```

### 8.2 集成测试

```typescript
// Supertest 集成测试
import request from 'supertest';
import app from '../app';

describe('Workflow API', () => {
  test('POST /api/workflow/auto should start auto mode', async () => {
    const response = await request(app)
      .post('/api/workflow/auto')
      .send({
        source: 'ithome',
        enableResearch: true,
        enableImageGeneration: true
      })
      .expect(200);

    expect(response.body).toHaveProperty('taskId');
    expect(response.body).toHaveProperty('status');
  });
});
```

---

## 九、性能优化

### 9.1 前端性能优化

```typescript
// 代码分割
const WorkflowPanel = lazy(() => import('./components/WorkflowPanel'));
const LogPanel = lazy(() => import('./components/LogPanel'));

// 图片懒加载
import { lazyload } from 'react-lazyload';

<Image lazyLoad src={imageSrc} alt="description" />
```

### 9.2 后端性能优化

```typescript
// 连接池配置
import { Pool } from 'pg';

const pool = new Pool({
  host: process.env.DB_HOST,
  port: parseInt(process.env.DB_PORT),
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  max: 20, // 最大连接数
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000
});

// 查询优化
const getUsersWithPagination = async (page: number, limit: number) => {
  const offset = (page - 1) * limit;
  const query = `
    SELECT * FROM users
    ORDER BY created_at DESC
    LIMIT $1 OFFSET $2
  `;
  return pool.query(query, [limit, offset]);
};
```

---

## 十、总结

本技术栈方案提供了完整的技术选型和实现细节，包括：

1. **前后端分离架构**: React + Node.js
2. **现代化工具链**: Vite + TypeScript + Tailwind CSS
3. **完善的数据库设计**: PostgreSQL + Redis
4. **RESTful API + WebSocket**: 支持实时通信
5. **容器化部署**: Docker + Docker Compose
6. **监控和日志**: Winston + Prometheus
7. **安全方案**: JWT + AES + Rate Limiting
8. **测试方案**: Jest + Supertest
9. **性能优化**: 代码分割 + 连接池

通过以上技术栈，可以构建一个高性能、高可用、易维护的公众号自动写作助手系统。