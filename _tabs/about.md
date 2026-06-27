---
# the default layout is 'page'
icon: fas fa-info-circle
order: 4
---

## 👋 关于我

我是 **Pancake Lee**，一名后端程序员。

关注 **AI Agent 开发**、**后端工程实践**与**结构化思维**——喜欢把复杂问题拆解清楚，也喜欢把思考过程写成文字。

当前在 Go / Python 技术栈上构建项目，同时对 AI Agent 保持着持续学习和实践。

---

## 🛠 项目

### [PFlow](https://github.com/pancake-lee/pflow) — 多 Agent 会话注意力管理

不是又一个 AI Agent，而是一张 **AI 会话的沙盘指挥图**。只做调度，不做对话。

- **技术栈**：Go + Vue 3 + NaiveUI，Go embed 单二进制部署
- **核心能力**：Claude Code + Hermes 监控、主线/支线策略 + 提醒分数算法 + 注意力遮罩、Web 终端一键 attach、~20 个静态场景建议引擎
- **许可证**：MIT

### [Photo Agent](https://github.com/pancake-lee/photo-agent) — AI 个人照片资产管理

用自然语言搜索你的照片库。

- **技术栈**：Go (Gin + GORM + SQLite) 数据层 + Python (FastAPI + LangChain + LangGraph + ChromaDB) 推理层 + Vue 3 前端
- **核心能力**：LangGraph 三分支自动路由（SQL / RAG / Combined）、HDBSCAN + UMAP 无监督聚类 + LLM 主题命名、Text-to-SQL 动态属性注入、5 级降级混合查询
- **评估指标**：Precision@10 = 0.93, MRR = 1.0（黄金用例集）
- **许可证**：MIT

### [PFilter](https://github.com/pancake-lee/pfilter) — Nikon 滤镜批量工具

从 Microsoft Power Automate RPA 原型到 Nikon SDK 集成，最终落地为 MFC 桌面应用。解决 Nikon 相机用户批量导出多种云创色彩方案照片的需求。

- 📄 博客：[调研篇](/pancake-io/posts/pfilter-1/) · [技术篇](/pancake-io/posts/pfilter-2/)

### [PHotKey](https://github.com/pancake-lee/photkey) — CapsLock 改造效率工具

将闲置的 CapsLock 键改造为效率快捷键。状态机驱动设计，11 套预置配置。

- 📄 博客：[PHotKey 介绍](/pancake-io/posts/photkey/)

### 换课工具

教师换课辅助工具：解析 Excel 课表 → 计算换课候选列表 → GUI 图形界面操作。Go + Fyne 实现，CLI/GUI 分离架构。

- 📄 博客：[换课工具](/pancake-io/posts/course-swap/)

---

## 📖 关于本博客

这里记录了我的技术探索和思考过程，按五个分类组织：

- **[Projects](/pancake-io/categories/projects/)** — 项目展示与复盘
- **[AI & Agent](/pancake-io/categories/ai-agent/)** — AI/Agent 开发学习记录
- **[Backend](/pancake-io/categories/backend/)** — 后端工程实践（Go 微服务 + DDIA 笔记）
- **[Tech Notes](/pancake-io/categories/tech-notes/)** — 技术笔记与踩坑记录
- **[Thinking](/pancake-io/categories/thinking/)** — 深度思考与学习方法

---

## 📬 联系方式

- **GitHub**：[pancake-lee](https://github.com/pancake-lee)
- **Email**：[pancake-lee@outlook.com](mailto:pancake-lee@outlook.com)

---

> "It's just a pancake."
