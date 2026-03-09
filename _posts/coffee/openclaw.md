- docker pull docker/dockerfile:1.7
- docker pull node:22-bookworm
- 没有一键成功`./docker-setup.sh`
- 手动部署
  - docker build -t openclaw:local -f Dockerfile .
  - docker compose run --rm openclaw-cli onboard
    - 初始化只设置了火山引擎的API-KEY，其他都跳过
  - docker compose up -d openclaw-gateway
  - docker compose run --rm openclaw-cli dashboard --no-open
    - 进入openclaw-gateway容器运行openclaw dashboard --no-open更顺畅
    - 首次登录要用这里的带token的url - 否则概览(dashboard)有如下提示

```txt
unauthorized: too many failed authentication attempts (retry later)
身份验证失败。请使用 openclaw dashboard --no-open 重新复制令牌化 URL，或更新令牌，然后点击连接。
```

遇到这类问题，重启openclaw-gateway容器，然后openclaw dashboard --no-open，直到提示paring

- docker compose run --rm openclaw-cli devices list
- docker compose run --rm openclaw-cli devices approve <requestId>
