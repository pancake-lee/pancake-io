---
title: "远程开发环境搭建"
description: ""
author: Pancake
date: 2025-06-30
categories: Coffee
tags: vs-code code-server
---

## 远程开发环境搭建

### code-server

ipad 升级了测试版的 ipados26，又折腾起 ipad 写代码
为了让 ipad 可以写代码，先安装 code-server

```sh
curl -fsSL https://code-server.dev/install.sh | sh

# 修改密码
vim /root/.config/code-server/config.yaml

code-server --bind-addr 0.0.0.0:7050 /root/workspace/pancake-io/
```

ipad 上浏览器访问对应的 ip:7050 即可

但是 code-server 在浏览器上，一些操作不舒服

- 点击登录 github 账号无反应
- 界面上没有 copilot 图标
- 插件需要逐个安装，本来只要登陆就能自动安装的

不想从头搞一遍，也避免后续又重新部署环境时再来 N 遍
所以想要折腾出“统一使用 code-server 作为编辑器后端”的方案

- vs-code -> code-server
- browser -> code-server

### vs-code

vscode 通过 ssh 本身可以使用远程服务器进行开发，
但 vscode 连接后安装在服务器上的"vscode-server"路径为`~/.vscode-server`。
找了挺多资料没有找到关于“vs-code 直接连接 code-server”的相关资料。

突然灵机一动，想到他们“本是同根生”，也许本来就能互相共用。
于是尝试直接建个软连接，让 vs-code 的 Remote-SSH 插件直接把服务端安装到 code-server 的目录。
这个方法初步看是很顺利的:

- ln -s /root/.local/share/code-server/ .vscode-server
- vs-code 通过 Remote-SSH 插件连接，自动安装服务端到.vscode-server
- vs-code 安装插件，可以一件给服务端安装所有插件的

让他们共用同一个安装目录，短期使用还没有发现什么问题，但是可能有还没发现的坑。
如果两者之间长期都能满足以下几点，那么应该是很舒服的。

- 一样的功能，使用，一样的文件，尤其是插件
- 不同的功能，使用，不同的文件名，没有冲突
- 少量不同的功能或配置需要人工修改

然后发现用户数据/配置是不共享的，猜测 vs-code 的用户数据依然存在客户端这边，而 code-server 存在服务端上，
所以在浏览器上访问 code-server 时，还是要登录 github，才能访问到 copilot。
类似这种界面上找不到操作图标的，可以多尝试 ctl+shift+p 然后输入关键字来查询命令。
比如`sign`和`chat`，稍微看看就知道是哪个命令了。
