---
title: "从零搭建 AI 照片助手：一个后端程序员的 Agent 开发学习之路"
description: "记录从 Dify 原型到 Go+Python 双栈再到 LangGraph 路由的完整演进，一个后端程序员学习 AI Agent 开发的技术实践与踩坑记录。"
author: Pancake
date: 2026-06-27
categories: AI-Agent
tags: [AI-Agent, LangGraph, RAG, ChromaDB, Golang, Python, Photo-Agent]
---

2026 年初，我开始做一个个人项目：**用自然语言搜索自己的照片库。**

"猫猫在厕所门口张大嘴巴"，输入这句话，就能找到那张照片。

听起来是一个简单的功能。但作为一个后端程序员，我很快发现，这个项目涉及的技术栈远远超出了我熟悉的 Go + SQL 领域。接下来几个月，它变成了我学习 AI Agent 开发的主战场。

这篇文章不是文档翻译，而是**从学习者的视角**，记录技术栈的四次重大转向、关键踩坑点，以及一个后端程序员进入 AI 领域时最真实的认知转变。

## 起点：一个后端程序员的 AI 知识基线

开始这个项目时，我的 AI 知识大概是这样：

- 会用 OpenAI API 做简单的文本生成
- 知道 RAG 大致是"检索 + 生成"
- 听说过 LangChain 但没写过
- 没碰过向量数据库
- Agent 对我来说就是"让 LLM 调用函数"

这个基线不高，但足够了。剩下的就是在项目中边做边学。

## 第一阶段：Dify 原型 — 图形化编排的甜头

Dify 是一个开源的 LLM 应用平台。它的价值在于：

- **Agent 编排**：拖拽式工作流 + 自带聊天 UI，不需要手写前端
- **知识库 RAG**：内置 Embedding + Weaviate 向量检索
- **模型管理**：统一管理 LLM / Embedding / Rerank 的 API Key
- **可观测性**：每一步思考 → 工具调用 → 结果 → 答案，全链路可见

架构示意：

```
Dify（Docker 部署） → Go Backend（Gin + GORM + SQLite）
     ↑ 智能大脑                        ↑ 业务躯干
  - Agent 编排                      - 照片元数据 CRUD
  - 知识库 RAG                      - 文件管理
  - 聊天 UI                         - VLM 预处理
```

**这个阶段的收获**：理解了 RAG 的完整链路，"描述文本 → Embedding → 向量 → Weaviate → 语义检索"，而不只是概念上的"检索增强生成"。Dify 把每一步都可视化，学习效率比看文档高得多。

但图形化编排也有天花板。当查询需求复杂到"去年用 85mm 镜头在云南拍的猫片"这种级别时，单一的 RAG + API 工具调用就显得力不从心。

PS: 火山引擎 Embedding URL 的 Dify 兼容问题

火山的 Embedding URL 是 `/api/v3/embeddings/multimodal`，但 Dify 的 openai-api-compatible 插件会自动在 base_url 后追加 `/embeddings`。最终 URL 变成 `/embeddings/multimodal/embeddings`，404。

解决方案：Go 后端提供 `/v1/embeddings` 代理，转发到火山真实 URL。**当两个系统的 URL 约定冲突时，加一层代理比改任何一方的配置都便宜。**

## 第二阶段：Go + Python 双栈 — 引入 LangGraph 路由

Dify 阶段跑了几天后，问题浮现：

1. **路由不够精细**：用户查询需要自动判断走 SQL（结构化过滤）还是 RAG（语义检索）还是两者组合。Dify 的图形化编排做条件分支很僵硬
2. **前端不可定制**：照片管理需要上传、VLM 队列、Embedding 状态等定制界面，Dify 只有通用聊天 UI
3. **学习深度受限**：Dify 封装了太多细节，LangChain、LangGraph、ChromaDB 这些核心技术被藏在平台层下面

于是第二次转向：**重新引入 Python AI 服务层，但这次用 LangGraph 做路由编排。**

最终的查询路由是这样设计的：

```
用户输入 "去年用 85mm 在云南拍的猫片"
        ↓
   分类器（LLM）
        ↓
   ┌────┼────┐
   ↓    ↓    ↓
 SQL   RAG  Combined
   ↓    ↓    ↓
   │    │    ├─ SQL: 时间=2025, 镜头=85mm, 地点=云南 → sql_ids
   │    │    ├─ RAG: "猫" 语义检索 → rag_ids
   │    │    └─ 取交集 → 保持 RAG 相似度排序
   ↓    ↓    ↓
   └────┼────┘
        ↓
   LLM 生成回答
```

三条分支的触发规则：

- **SQL 分支**：纯结构化查询 ——"2023 年用 50mm 拍了多少张"
- **RAG 分支**：纯语义描述 ——"有氛围感的海边日落"
- **Combined 分支**：复合条件 ——"逆光的雪山照片"

Combined 分支还带了 5 级降级：

```
SQL 异常 / 过宽(>50) / 为空 / 交集空 / 整体异常 → 纯 RAG
```

**这个阶段最大的认知转变**：从"让 AI 回答一切"到"设计好降级路径"。RAG 不是银弹，SQL 不是银弹，LangGraph 也不是，真正让系统可靠的，是**每一层都有 fallback，且 fallback 的行为是可预期的。**

## 第三阶段：技术栈的"足够好"边界

项目经历过四次架构转向：

```
纯 Python 单栈
  → Go + Python 双栈（复用 Go 工程经验）
    → Go + Dify （降低 Python 工作量）
      → Go + Web + Python 三栈（重新引入 Python 做精细路由）
```

每一次都不是"新技术更好所以换"，而是**"当前方案满足不了新出现的需求"。** 这个原则很重要，如果一开始就上三栈架构，大概率会因为过度设计而死在路上。

几个关键技术决策和它们背后的考量：

### ChromaDB 元数据最小化（Route B 选择）

向量库的 metadata 设计有两种路线：

|            | Route A                         | Route B（✅ 采用）                       |
| ---------- | ------------------------------- | ---------------------------------------- |
| 做法       | ChromaDB 冗余存储所有结构化属性 | ChromaDB 仅存 `photo_id` + `chunk_index` |
| 结构化查询 | Chroma `where` 过滤             | Go SQLite Text-to-SQL                    |
| 优点       | 单库查询                        | 单一数据源，无同步问题                   |
| 缺点       | 数据冗余，同步复杂              | 需要跨服务组合                           |

选择 Route B 的关键原因：**Go SQLite 是唯一数据源。** 不搞 Chroma metadata 和 SQLite 之间的数据同步，向量库只管语义相似度，SQL 只管结构化过滤。组合查询通过 SQL ∩ RAG 取交集实现。

### 属性值动态注入

一个踩坑细节：写 Text-to-SQL 的 System Prompt 时，我硬编码了场景映射值（如 `backlit`、`night`）。但 Go 后端的映射函数实际产出的值是 `backlight`、`dark`，名字对不上，导致 SQL 匹配率为零。

修复方案：新增 `GET /api/v1/photos/attribute-values` API，返回数据库中实际的 distinct 值，Prompt 动态拼接。**不要假设代码和 Prompt 之间的一致性，用 API 强制同步。**

## VLM 预处理：批量生成照片描述

300 张照片需要 VLM 生成描述，每张调用耗时 2-5 秒，总耗时 15-30 分钟。而且 API 按 token 计费，10MB 原图编码成 base64 后体积膨胀，token 消耗惊人。

设计了一个**两阶段流水线**：

```
离线预处理（batch_vlm）
  ├─ 扫描图片目录
  ├─ ImageMagick 压缩（512x512, quality 85）
  ├─ 并发调用 VLM API（3 并发，失败重试）
  ├─ 每 10 张保存一次中间结果（防崩溃丢失）
  └─ 输出 descriptions.json

在线导入（server）
  ├─ 复用压缩图（不重复压缩）
  ├─ 读取 descriptions.json（不重复调 VLM）
  ├─ 解析 EXIF 匹配时间线
  └─ 写入 SQLite
```

**并发安全**：中间保存时先 `Mu.Lock()` 深拷贝 map → 解锁 → Marshal + 原子写入（临时文件 + `os.Rename`）。否则 `json.MarshalIndent` 遍历 map 时，其他 goroutine 写入会触发 `fatal error: concurrent map read and map write`。

## 评估：从单元测试到 AI-as-Judge

传统软件测试的范式是 **"输入确定 → 输出确定 → 断言成立"**。但在 AI 系统中，输出是概率性的，同样的输入可能得到不同的回答。测试从**功能验证**转向了**质量评估**。

Photo Agent 的评估方案是**黄金用例集**：

- 挑选 20 个典型查询作为 ground truth（如"雪山的照片""去年拍的猫"）
- 每次变更后跑一遍，对比 Precision@K / Recall / MRR
- 当前基线：`Precision@10 = 0.93`, `MRR = 1.0`

这个方法论来自一次对 Agent 评估范式的系统学习。核心收获是：

| Agent 评估方式             | 对应测试术语          | 适用场景                 |
| -------------------------- | --------------------- | ------------------------ |
| 人工评估                   | 验收测试 / 探索性测试 | 评估"好不好用"           |
| 代码评估                   | 自动化测试            | 量化指标（准确率、耗时） |
| LLM 评估（LLM-as-a-Judge） | 灰盒测试              | 评估输出质量和一致性     |

对于一个个人项目来说，黄金用例集已经足够形成开发闭环：**改代码 → 跑用例 → 看指标 → 决定合入还是回滚。**

## 架构全景

经过所有迭代后，最终的架构是这样的：

```
Web 前端 (Vue 3 + NaiveUI)
        │
        ├─ 对话 / 聚类 → Python FastAPI
        ├─ 语义检索 (RAG) → ChromaDB
        └─ 结构化查询 → Go Gin API
              │
              └─ LangGraph 路由 (SQL / RAG / Combined)
                    │
                    └─ 5 级降级 → LLM 生成回答
```

三栈各司其职：

| 层            | 技术                                       | 为什么是它                  |
| ------------- | ------------------------------------------ | --------------------------- |
| Go 数据层     | Gin + GORM + SQLite                        | 稳，并发快，后端经验复用    |
| Python 推理层 | FastAPI + LangChain + LangGraph + ChromaDB | AI 生态最丰富，路由控制精细 |
| Web 前端      | Vue 3 + NaiveUI                            | 前后端分离，独立演进        |

**每层可独立替换，不会因为换前端框架就重写推理层。**

## 从这次学习中学到了什么

**技术层面**：RAG 的完整链路、LangGraph 的条件路由、ChromaDB 的向量检索、VLM 的批量预处理、三栈架构的边界设计。

**认知层面**：

1. **从"让 AI 解决一切"到"设计好降级路径"**。AI 系统的不确定性是本质特征，不是 bug。工程能力的体现不在于让 AI 每次都猜对，而在于当 AI 猜错时，系统能优雅地 fallback。

2. **从"看完文档再动手"到"跑起来再说"**。Dify 阶段虽然最终被替换了，但它让我在一天内跑通了完整链路，后续学习 LangGraph 和 ChromaDB 时就有了坐标系，知道每块拼图放在整个架构的哪个位置。

3. **从"技术选型追求最优"到"选择当下最合适的"**。架构转向不是因为"之前的选错了"，而是因为需求在演进。MVP 阶段的过度设计比技术选型失误更致命。

---

> **项目地址**：[github.com/pancake-lee/photo-agent](https://github.com/pancake-lee/photo-agent)（MIT 开源）
>
> **相关阅读**：[PFlow 设计哲学：不是又一个 Agent，而是一张 AI 会话的沙盘指挥图](/pancake-io/posts/pflow-design-philosophy/)
