---
title: "日志模块封装"
description: ""
author: Pancake
date: 2025-06-09
categories: Tech
tags: Golang
---

## Bearer Token

### JWT 规范

JWT (JSON Web Token) 是一种开放标准 (RFC 7519)，用于在各方之间以 JSON 对象安全地传输信息。它由三部分组成：

- Header - 包含令牌类型和签名算法
- Payload - 包含声明 (claims)，通常是用户信息和其他数据
- Signature - 用于验证消息在传输过程中没有被更改

先了解一下标准的字段，这些字段能被大部分 JWT 库识别和处理：

| 字段名     | 缩写 | 描述                             |
| ---------- | ---- | -------------------------------- |
| Issuer     | iss  | 签发者                           |
| Subject    | sub  | 主题(通常是用户 ID)              |
| Audience   | aud  | 接收方                           |
| Expiration | exp  | 过期时间(Unix 时间戳)            |
| Not Before | nbf  | 在此之前不可用(Unix 时间戳)      |
| Issued At  | iat  | 签发时间(Unix 时间戳)            |
| JWT ID     | jti  | JWT 唯一标识符，用于防止重放攻击 |
