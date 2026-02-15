# Grafana Loki 日志管理接入指南

本项目已接入一套开源日志管理方案：`Loki + Alloy + Grafana`。

- `Loki`：日志存储与查询
- `Alloy`：日志采集（从本地日志文件推送到 Loki）
- `Grafana`：日志可视化与检索

> 为什么不用 Promtail？
>
> `Promtail` 已进入 LTS，并计划在 `2026-03-02` EOL（官方建议迁移到 Alloy）。

## 1. 文件位置

- 编排文件：`ops/logging/docker-compose.logging.yml`
- Loki 配置：`ops/logging/loki/config.yaml`
- Alloy 配置：`ops/logging/alloy/config.alloy`
- Grafana 数据源：`ops/logging/grafana/provisioning/datasources/loki.yml`

## 2. 启动日志系统

先准备环境变量（首次必做）：

```bash
copy ops/logging/.env.example .env
```

并将 `.env` 中的 `GRAFANA_ADMIN_PASSWORD` 修改为高强度密码。

在项目根目录执行：

```bash
docker compose -f ops/logging/docker-compose.logging.yml up -d
```

查看容器状态：

```bash
docker compose -f ops/logging/docker-compose.logging.yml ps
```

停止：

```bash
docker compose -f ops/logging/docker-compose.logging.yml down
```

## 3. 访问地址

- Grafana：`http://localhost:3001`
  - 用户名：`GRAFANA_ADMIN_USER`（默认 `admin`）
  - 密码：`GRAFANA_ADMIN_PASSWORD`（必填）
- Loki 健康检查：`http://localhost:3100/ready`

> 安全说明：`docker-compose.logging.yml` 默认仅绑定本机回环地址（`127.0.0.1`），避免被局域网直接访问。

## 4. 当前采集范围

Alloy 默认采集以下日志：

- `backend/logs/*.log`
- `logs/*.log`

此外，前端浏览器运行时错误会通过后端接口统一写入后端日志（从而被 Loki 采集）：

- `POST /api/observability/client-errors`
- 来源包括：`window.error`、`window.unhandledrejection`、`fetchAPI` 非 2xx 请求

并自动打标签：

- `project=gzh`
- `env=local`
- `service=backend` 或 `service=app`
- `job=gzh-backend` 或 `job=gzh-root`

## 5. Grafana 查询示例

在 Grafana 的 Explore 页面选择 Loki，输入：

```logql
{project="gzh"}
```

仅看后端日志：

```logql
{project="gzh",service="backend"}
```

按微信发布追踪 ID 查询：

```logql
{project="gzh",service="backend"} |= "wxpub-"
```

按图片重写关键字查询：

```logql
{project="gzh",service="backend"} |= "正文图片"
```

按前端上报错误查询：

```logql
{project="gzh",service="backend"} |= "[CLIENT-ERROR]"
```

按前端请求失败查询：

```logql
{project="gzh",service="backend"} |= "source=fetchAPI"
```

## 6. 常见问题

### 6.1 Grafana 打不开

- 检查 `3001` 端口是否被占用。
- 执行 `docker compose -f ops/logging/docker-compose.logging.yml logs grafana` 查看报错。

### 6.2 看不到日志

- 确认后端确实写入日志文件（例如 `backend/logs/app.log`）。
- 执行 `docker compose -f ops/logging/docker-compose.logging.yml logs alloy` 检查采集状态。
- 执行 `docker compose -f ops/logging/docker-compose.logging.yml logs loki` 检查接收状态。

### 6.3 想扩展采集目录

修改 `ops/logging/alloy/config.alloy` 中 `local.file_match` 的 `path_targets`，然后重启：

```bash
docker compose -f ops/logging/docker-compose.logging.yml restart alloy
```
