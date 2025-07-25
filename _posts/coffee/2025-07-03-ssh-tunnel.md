---
title: "通过 SSH 隧道远程访问局域网的主机"
description:
author: Pancake
date: 2025-07-03
categories: Coffee
tags: ssh
---

## 远程访问

手上有多台设备，想要稳定在一个环境里工作。

在 PC 安装了新的东西，假设就是升级了 golang 版本，
然后笔记本又要处理一次，挺麻烦的。

不同设备性能不同，总是希望能用最好的硬件，
笔记本/ipad 只需要文本编辑，把计算的活交给性能最好的 PC。

于是就在利用云主机做 SSH 隧道访问家里 PC，
排除媒体文件（图片/音视频等大文件传输），
个人使用，买个最便宜的云主机是够用的。

但是建议有需要时才临时开启，
比如先远程桌面控制，来打开 SSH 隧道，
像我是搭建了 code-server，用的还是 root，
一旦暴露了，那 code-server 里就用终端可以做任何事了。

## 公网服务器

`vim /etc/ssh/sshd_config`

增加或修改: `GatewayPorts yes`

## 机器 A

### 开启

假设公网 IP 为`192.168.3.4`

`ssh -fNTR 0.0.0.0:1111:localhost:22 root@192.168.3.4`

需要输入**公网服务器**的密码

如果不是想 ssh 到机器 A，可以更换端口（上面实例的 22），来暴露其他服务。

### 关闭

`ps -ef|grep "ssh -fNTR"`

找到对应的 pid，假设是 1234

`kill 1234`

## 机器 B

`ssh -p 1111 root@192.168.3.4`

需要输入**机器 A**的密码（注意**不是**公网服务器的）

## 安全性

为了提高安全性，建议配置密钥登录，而不是密码登录

ssh 客户端生成密钥：`ssh-keygen -t rsa -C "your@email.com"`

把 ssh 客户端创建的公钥`.pub`文件内容贴到下面文件

ssh 服务端创建/修改文件：`vim ~/.ssh/authorized_keys`
