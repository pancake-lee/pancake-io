---
title: "OpenClaw"
description:
author: Pancake
date: 2026-03-27
categories: Tech
tags:
---

## 本地 AI 部署笔记

### OpenClaw

- 预拉取镜像：

  ```bash
  docker pull docker/dockerfile:1.7
  docker pull node:22-bookworm
  ```

- 一键脚本 `./docker-setup.sh` 未能成功
- 改为手动部署：

  ```bash
  docker build -t openclaw:local -f Dockerfile .

  docker compose run --rm openclaw-cli onboard
  # 在 `onboard` 初始化时只设置了“火山引擎”的 API-KEY，其他选项均跳过。

  docker compose up -d openclaw-gateway
  ```

- token验证：`openclaw dashboard --no-open`
  - （推荐）进入 `openclaw-gateway` 容器内运行 `openclaw dashboard --no-open`
  - （也可）使用 `docker compose run --rm openclaw-cli dashboard --no-open`
  - 首次登录要使用带 token 的 URL，否则报错
  - 多次验证token或paring失败时，重启 `openclaw-gateway` 容器，然后重复 `openclaw dashboard --no-open`，直到提示 pairing。
    - 失败信息：`unauthorized: too many failed authentication attempts (retry later) 身份验证失败。请使用 openclaw dashboard --no-open 重新复制令牌化 URL，或更新令牌，然后点击连接。

- paring：网页提示要配对时，进入容器执行下面命令，授权指定机器访问管理网页
  - openclaw devices list
  - openclaw devices approve <requestId>

### ollama 跑本地模型

直接安装桌面应用程序，然后看GPU内存，选择合适大小的模型
可以直接跑起openclaw，不用自己部署

#### docker 部署 ollama

**放弃**，没必要折腾docker跑模型，ollama提供多个平台的应用

确认docker能调用到GPU

- 主机
  - `nvidia-smi`
- docker
  - `docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi`
- ollama容器
  - `docker logs ollama | grep -i "gpu\|cuda\|loaded to GPU"`
- 模型
  - `docker ps -a --filter name=ollama --format 'table {{.Names}}\t{{.Status}}' && docker exec ollama ollama ps`
    **放弃**，没必要折腾docker跑模型，ollama提供多个平台的应用
    折腾了很久，docker运行的ollama都只是用cpu跑模型
    [官方](https://docs.ollama.com/docker)说明了直接运行只是CPU ONLY
    而Nvidia GPU那套东西在文档中似乎又不包含win的指引，不折腾了

- docker pull ollama/ollama
- ollama pull deepseek-r1:1.5b
  - docker exec -it ollama ollama pull deepseek-r1:1.5b
  - 更换模型后需要重构容器
  - docker compose up -d --force-recreate ollama

## 脱敏总结与通用建议

下面是对上面操作日志的脱敏总结，保留可复用的运维经验与注意事项，不包含账号、密码或私钥等敏感信息。

- 部署策略：如果官方 Docker 方案不符合运营或安全策略，可以在受控宿主机（例如 Rocky Linux 9）上使用常规模式部署，按企业运维流程管理容器与服务。
- 文件挂载：尽量将宿主数据目录以只读方式挂载到运行服务的容器中，降低容器被入侵后对宿主数据的写入风险。例如：

```bash
# 概念示例：将主机配置目录挂载为只读
docker run --rm -v /host/config:/app/config:ro ...
```

- 启动与配对：高层流程包含初始化(onboard)、启动 gateway 服务、通过 dashboard 进行 pairing。若遇到 token/配对失败，先重启 gateway，再重试 pairing，避免短时间内重复失败导致限流/锁定。
- 中文路径与空格问题：在某些交互场景下，中文与数字间会被错误插入空格，导致路径无法识别。建议使用 ASCII 路径或对路径加引号并在脚本中严格处理转义。
- GPU 检查：确认宿主和容器都能看到 GPU，例如使用 `nvidia-smi`，并根据官方文档为容器启用 GPU 支持。

## 安全与合规建议

- 永远不要将明文密钥、密码、token 或私钥提交到代码仓库。如果历史提交中已经泄露敏感信息，应使用历史重写工具（如 `git filter-repo`）进行清理，并在操作前备份仓库。
- 将凭据存放在专用的机密管理系统（如 Vault、CI 的 secret 管理或企业密码库）并在运行时注入，避免写入脚本或日志。
- 在仓库中添加或更新 `.gitignore`，屏蔽本地配置文件和敏感文件。对于需要保留的调试日志，应在移交前清理敏感内容。

## 后续动作建议

- 将包含敏感信息的原始操作日志移出公共仓库，存放在受控的私有位置；在仓库中仅保留脱敏后的总结性文档。
- 如果你愿意，我可以：
  - 帮你把特定文件脱敏（你指出哪些段落需要模糊化或删除）；
  - 提供一份清理历史提交的操作清单（如何使用 `git filter-repo` 或类似工具），并帮你生成 `.gitignore` 建议条目。
