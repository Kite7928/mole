# 开发 SOP（AI 公众号助手项目）

本文档用于统一本项目的日常开发流程，目标是：**稳定迭代、快速定位问题、保证功能可用**。

## 1. 适用范围

- 后端：`backend`（FastAPI + SQLAlchemy）
- 前端：`frontend`（Next.js + TypeScript）
- 日志与可观测：`ops/logging`、`backend/logs`、`logs`

## 2. 开发前准备

### 2.1 环境要求

- Python `3.10+`
- Node.js `18+`（建议与团队统一版本）
- npm（随 Node 安装）
- 可选：Docker（用于 Loki/Grafana 日志系统）

### 2.2 安装依赖

后端：

```bash
cd backend
py -m pip install -r requirements.txt
```

前端：

```bash
cd frontend
npm install
```

## 3. 启动流程（本地开发）

### 3.1 一键启动（推荐）

项目根目录执行：

```bash
start-simple.bat
```

默认地址：

- 前端：`http://localhost:3000`
- 后端：`http://localhost:8000`
- API 文档：`http://localhost:8000/docs`

### 3.2 手动启动（可选）

后端：

```bash
cd backend
py -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

前端：

```bash
cd frontend
npm run dev
```

## 4. 日常开发标准流程

### Step 1：明确需求与影响面

- 明确是功能开发、缺陷修复还是体验优化。
- 列出涉及模块（API、页面、服务层、数据表、日志）。
- 先确认是否有兼容逻辑（例如旧接口/旧调用链）。

### Step 2：先看日志再改代码

- 后端主日志：`backend/logs/app.log`
- 历史根日志：`logs/app.log`
- 重点检索：`trace_id`、`stage`、`ERROR`、微信 `errcode`

### Step 3：小步修改，优先根因

- 优先修根因，不做临时掩盖。
- 避免一次改太多文件，按功能链路最小闭环改。
- 接口返回尽量结构化（`error/message/trace_id/stage`）。

### Step 4：本地验证（必须）

后端最小验证：

```bash
cd backend
pytest tests/test_api.py::TestWeChatAPI::test_publish_to_wechat -q
```

前端类型检查：

```bash
cd frontend
npm run type-check
```

如涉及微信发布：

- 验证封面图是否上传成功。
- 验证正文图片重写统计（`replaced/total`）。
- 记录一次可复现的 `trace_id`。

### Step 5：输出变更说明

- 改了什么（文件 + 目的）
- 为什么这么改（根因）
- 如何验证（命令 + 结果）
- 已知风险与后续建议

## 5. 故障排查 SOP（重点）

### 5.1 微信发布成功但图片未带过去

1. 确认调用入口（`/api/wechat/publish-draft/{id}` 或多平台入口）。
2. 在日志检索同一次 `trace_id`。
3. 查看图片重写统计：`total/replaced/failed/skipped`。
4. 逐条看失败原因：路径解析、文件不存在、`data:` 跳过、微信 `uploadimg` 报错。

### 5.2 微信 access_token 失败（40164）

1. 使用诊断接口：`GET /api/wechat/diagnose`
2. 检查返回 `detected_ip` 是否在公众号后台白名单。
3. 本地网络 IP 变化时，优先用固定出口 IP 环境。

### 5.3 前端偶发报错难复现

1. 查询后端日志中的 `[CLIENT-ERROR]`。
2. 按 `source=window.error / window.unhandledrejection / fetchAPI` 分组。
3. 结合 `page_url + stack + context` 定位页面与触发路径。

## 6. 可观测与告警（当前状态）

- 日志系统：`Loki + Alloy + Grafana`
- 启动命令：

```bash
docker compose -f ops/logging/docker-compose.logging.yml up -d
```

- 文档：`docs/guide/Grafana-Loki-日志管理接入指南.md`

后续可接入飞书告警（建议规则）：

- 5 分钟内 `ERROR` 数超阈值
- 微信发布失败率超阈值
- `CLIENT-ERROR` 突增

## 7. 发布前检查清单（Checklist）

- [ ] 需求范围与实现一致，无多余改动
- [ ] 关键链路已人工走通（至少 1 次）
- [ ] 后端测试通过
- [ ] 前端类型检查通过
- [ ] 关键错误路径有可读日志（含 `trace_id`）
- [ ] 文档已更新（若新增能力/配置）

## 8. 分支与提交建议

- 分支命名：`feature/*`、`fix/*`、`chore/*`
- 提交信息建议：`类型: 模块 + 变更摘要`
  - 示例：`fix: wechat publish chain image rewrite consistency`

---

维护原则：**先可观测，再修复；先根因，再优化；先验证，再交付。**

