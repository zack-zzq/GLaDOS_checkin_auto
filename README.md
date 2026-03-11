# GLaDOS 自动签到

Docker 容器化部署的 GLaDOS 自动签到工具，支持多账号、Gotify 消息推送、自定义域名。

## 功能

- ✅ 每日自动签到，可自定义签到时间
- ✅ 支持多账号（Cookie 用 `&` 分隔）
- ✅ 支持 Gotify 消息推送，自定义标题格式
- ✅ 支持自定义 GLaDOS 域名（域名变更时无需改代码）
- ✅ Docker / Docker Compose 一键部署
- ✅ GitHub Actions 自动构建多架构镜像（amd64 / arm64）

## 快速开始

### 1. 创建配置文件

```bash
cp .env.example .env
```

编辑 `.env`，至少填写 `GLADOS_COOKIE`：

```env
GLADOS_COOKIE=your_cookie_here
```

### 2. 使用 Docker Compose 部署

```bash
docker compose up -d
```

查看日志：

```bash
docker compose logs -f
```

## 环境变量

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `GLADOS_COOKIE` | ✅ | - | GLaDOS Cookie，多账号用 `&` 分隔 |
| `GLADOS_DOMAIN` | ❌ | `glados.one` | GLaDOS 域名（不含 `https://`） |
| `CHECKIN_TIME` | ❌ | `09:00` | 每日签到时间（HH:MM，24 小时制） |
| `TZ` | ❌ | `Asia/Shanghai` | 容器时区 |
| `GOTIFY_URL` | ❌ | - | Gotify 服务地址 |
| `GOTIFY_TOKEN` | ❌ | - | Gotify 应用 Token |
| `GOTIFY_PRIORITY` | ❌ | `5` | 消息优先级（1-10） |
| `GOTIFY_TITLE_FORMAT` | ❌ | `GLaDOS签到 - {status}` | 标题格式，`{status}` 替换为 成功/失败 |

## 获取 Cookie

1. 浏览器登录 GLaDOS
2. 打开开发者工具（F12）→ Network
3. 访问签到页面，找到任意请求的 `Cookie` 请求头
4. 复制完整的 Cookie 值

## 本地开发

```bash
# 安装依赖
uv sync

# 运行
uv run python -m glados_checkin.main
```

## Docker 镜像

预构建镜像推送至 GitHub Container Registry：

```
ghcr.io/zack-zzq/glados_checkin_auto:latest
```

### 手动构建

```bash
docker build -t glados-checkin .
docker run --env-file .env glados-checkin
```

## GitHub Actions

仓库已配置自动构建工作流，在推送 `v*` 标签时自动构建并推送 Docker 镜像到 GHCR：

```bash
git tag v1.0.0
git push origin v1.0.0
```

## 致谢

基于 [lukesyy/glados_automation](https://github.com/lukesyy/glados_automation) 重构。
