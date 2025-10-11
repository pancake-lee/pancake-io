---
title: "Backend Roadmap"
description:
author: Pancake
date: 2018-05-10
categories: Coffee
tags: Cpp Github
---

## Backend Developer

参考[roadmap](https://roadmap.sh/backend)自我审查一下技能点

### Internet

How does the internet work? HTTP? Domain Name? hosting? DNS? Browsers?
这一连串概念问题，我们可以用“从浏览器访问一个网页的整个流程”串联起来：

- 用户在浏览器输入`https://pancake-lee.github.io/pancake-io/`，该 URL 包括
  - http/https 协议
  - 域名 pancake-lee.github.io
  - 路径 /pancake-io/
  - 另外关于 http 的 method，query, header, body 等先不展开
- 进行 DNS 域名解析，查询目标 IP 地址，按以下顺序逐级查询
  - 浏览器缓存，本地缓存（host 配置）
  - 本地 DNS 服务器，如果本地服务器没有该域名记录，则查询根域名服务器
  - 根域名服务器，查询".com", ".cn", ".org"等，返回对应的顶级域名服务器
  - 顶级域名服务器，返回对应的权威服务器
  - 权威服务器，这就是域名注册商的服务器，我们申请域名后，解析规则也是配置在该注册商平台的
  - 向以上 3 个服务器的查询的动作，是由本地 DNS 服务器执行的，查询到 IP 地址后将缓存一段时间
  - 最终将查询到 pancake-lee.github.io 对应的 IP 地址返回给用户设备，最后给到浏览器，他们也会进行缓存
  - 有一个递归查询和迭代查询的区别
    - 首先“根/顶级/权威”这个查询过程可能不只 3 次，尤其是权威服务器可能有更复杂的服务器架构
    - 那么，后续查询的工作由本地 DNS 服务器来执行，则称为递归查询
    - 反之，后续查询的工作由 DNS 客户端（用户设备）自己执行，则称为迭代查询
- 建立 TCP 连接
  - 三次握手，确保数据双向通讯通畅
    - C->S 发送 SYN
    - S->C 回复 SYN-ACK
    - C->S 发送 ACK
  - 我们可以模拟服务端无法访问客户端的情况
    - 拦截所有发出的 SYN-ACK 包（模拟服务端不响应）
    - iptables -A OUTPUT -p tcp --tcp-flags SYN,ACK SYN,ACK -j DROP
    - 恢复规则（测试完成后）
    - iptables -D OUTPUT -p tcp --tcp-flags SYN,ACK SYN,ACK -j DROP
- TCP 数据包封装 IP 头部（源/目的 IP），经路由器转发，路由器由多方提供
  - 内网路由器，家里/公司自己搭建的网络
  - 网络基建设施，路由器由设备商（如华为/锐捷）提供，路由表由网络供应商（如中国移动）维护
- 涉及到链路层/物理层的这里不展开
- 后端处理
  - 收到数据包后，后端可以进而搭建负载均衡，反向代理等等各种后端架构
  - 最终进入代码处理环节
  - 代码将写入状态码/响应头/Body 等数据作为 HTTP 相应，经过 TCP/IP 封装后原路返回
- 原路返回的流程不展开了
- 前端处理收到对应的内容如何展示到页面上
- TCP 连接四次挥手
  - 多出来一次交互，主要是因为需要等待“另一方发送完数据”，是双方都准备好才真正关闭，而不是强行中断。
    - 发送 FIN 表示“我要关闭”/“我准备好了关闭”
    - 回复 ACK 表示“我同意关闭”
  - 先假设由 C 主动关闭
    - C->S 发送 FIN，之后 C 端不应该再发送“数据”
    - S->C 回复 ACK，知道 C 端要关闭了，但是服务端也许还有数据要发送或者正在发送中
    - S->C 发送 FIN，S 端也准备好关闭了
    - C->S 回复 ACK
      - S 端收到这个 ACK，则满足了“自己准备好了关闭，对方也知道了我准备好关闭了”，所以 S 可以关闭了
      - C 端回复这个 ACK，则满足了“自己准备好了关闭，对方也知道了我准备好关闭了”，所以 C 可以关闭了
      - 这里还有一个 TIME_WAIT 状态
        - C 端发出这个 ACK 后，还需要在网络中传递一段时间，所以 C 会等待一会儿，默认 2MSL，通常是 60S
        - 以防这个 ACK 最后丢包，如果这个最后的包丢了，那么 S 端会以为第三步的 FIN 对方没有收到，就会再发送 FIN
        - 正因为这个 TIME_WAIT 状态，如果服务端来主动关闭连接，在建立/关闭连接频繁的情况下，可能会用尽服务器端口
