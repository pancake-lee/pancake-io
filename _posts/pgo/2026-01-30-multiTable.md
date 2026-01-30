---
title: "PGO-MultiTable"
description: ""
author: Pancake
date: 2026-01-30
categories: PGO
tags: Golang
---

## 多维表格

各家产品上命名不同，如

- 智能表格（Smart Database）
- 维格表（Vika）
- 多维表格（multi-dimensional spreadsheet）
- 很多很多不同叫法

个人比较习惯叫多维表格（multi-dimensional table），

首先是“多维”是最重要的特性，正是以不同的维度去展示数据。

然后 spreadsheet 还算是比较产品向的命名，
而 table 比较技术向，适合开发者，毕竟 mysql 命令是 show tables;

代码中我就缩写一下"MultiTable" = "MTBL"，
相对的本地数据库叫"LocalTable" = "LTBL"。

## 企微智能表格

[code](https://github.com/pancake-lee/pgo/blob/master/pkg/pweixin/wx.go)

最先对接的就是企微的智能表格，大部分开发需要注意的都注释在代码里了。

主要的问题是：

- 不能私有化部署，很多时候我们需要局域网内部署。联系客服应该可以本地部署，至少官网提及私有化的特性，但是功能是否阉割就不知道了。
- API 的调用频率限制比较大，我的测试代码（新建表-创建字段-删除字段-删除现有数据-创建新数据）经常无法一次性跑完测试。
  `get sheet failed: errcode=45009, errmsg=api freq out of limit, hint: [1752203840059500818414065], from ip: 1.2.3.4, more info at https://open.work.weixin.qq.com/devtool/query?e=45009`

还有飞书/钉钉这些平台，应该都差不多的，个人觉得飞书走得比较前一点，但是具体选择还得看公司在用哪个平台，毕竟不太可能说换就换的。

总结：可用，需要试用清楚。

## NocoDB

### 部署

[readme](https://github.com/nocodb/nocodb/blob/develop/markdown/readme/languages/chinese.md)

[docker-compose](https://github.com/nocodb/nocodb/blob/master/docker-compose/2_pg/docker-compose.yml)

根据官方文档，很快就能部署出来。

### 体验

先测试一下基本的功能，确认没有 APITable 那样的限制。
另外 NocoDB 主打可以直接管理自研系统的数据库，测试了一下，确实方便。

不过连接数据库之后，不能在多维表格中增加“额外字段”，
就是不修改数据库的情况下，希望可以增加多维表格的字段，

    比如做一个公式求两个列的和，或者做一个映射把数值枚举值展示成有意义的文本。
    Emm...看了一下好像公式类型也不支持，应该就是主打 DB 的可视化管理，而不是“多维表格”的概念。企微/飞书一类的多维表格中公式/关联/AI 等等都很有用。
    好吧，[官网平台](https://www.nocodb.com/)是有的，不知道源码全不全，如果源码全，然后找到限制代码改一下还好说。

还有还有，怎么没有甘特图呀，官网平台也没有，[插件](https://nocodb.com/docs/product-docs/extensions#extensions-marketplace)也没有，插件平台暂时还没有开放给开发者。

那对我来说缺的有点多，定位不一样，部署好的就用来看看 DB 数据玩玩吧，先溜了，NEXT~

PS: 记一下别人写的[SDK](https://github.com/eduardolat/nocodbgo)，还没用上

## NocoBase

我是搜 NocoDB 的甘特图时发现的，他们名字这么接近，开发团队有什么关系吗？

### 部署

我本地部署后，页面提示我 `Click the "UI Editor" icon in the upper right corner to enter the UI Editor mode`，但是我真的找不到这个按钮。原来吧，我是自己注册的账号，要用管理员账号才能编辑界面。

其实根本原因是我自己没把文档看完，[部署文档](https://docs-cn.nocobase.com/welcome/getting-started/installation/docker-compose)最后一句就是默认账号密码。我硬是排查了好一会儿，通过[环境变量](https://docs-cn.nocobase.com/welcome/getting-started/env)设置初始化账号密码，然后重新初始化了容器。

也可以直接从官网的[LiveDemo](https://demo.nocobase.com/new)体验一下。

### 体验

于是发现，这不是一个“多维表格”这么简单了，这是一个“低代码平台”，相对的更加灵活，也更加复杂了，二者不可兼得。

    首先字段类型是足够丰富的，但是增加一个字段的路径比较长（相对来说）。操作路径大概为：
    设置-数据源-指定数据源-指定数据表-配置字段-增加字段-回到展示页面-编辑 UI-配置字段-设置新增的字段可见。
    比起多维表格中直接修改列头的交互繁琐多了。
    确实用 NocoBase 可以搭建出功能足够丰富的应用，包括多维表格。

我们再来体验一下对接业务数据库的能力

- 首先官方是有[Mysql 插件](https://docs-cn.nocobase.com/handbook/data-source-external-mysql)的，但是要付费.
- 而且本地部署后，插件市场是“敬请期待”。LiveDemo 倒是提供了所有插件的试用，但是我也不可能提供一个公网的数据库啊。
- 又找到一个[开源插件](https://github.com/Nigori999/mysql-connector)，但是 NocoBase 加载后报错：插件兼容性检查失败，你应该修改依赖版本以满足版本要求。

最后还是临时部署了个 mysql 在公网做测试。
确实可以同步业务数据库，在甘特图中拖拽时间启停位置，也能修改数据库的值。
但是表格视图竟然**没有单元格编辑的功能**，自己创建的区块以及 demo 演示的表格都不能编辑，
demo 里是先点击编辑按钮，在弹出的抽屉中交互，才能修改数据。[官方文档](https://www.nocobase.com/cn/tutorials/task-tutorial-data-management-guide#36-%E4%BB%BB%E5%8A%A1%E7%9A%84%E7%BC%96%E8%BE%91%E4%B8%8E%E5%88%A0%E9%99%A4)也是明确了这种编辑交互方式的。

![修改数据]({{ "/assets/img/pages/frontend/NocoBaseEdit.png" | relative_url }})

我想要的是“多维表格”，不能直接编辑单元格实在落差有点大，暂时也先放一边了，NEXT~

### 总结

如果对于管理后台这类型的需求，足够。而对于产品级别的应用，不太够用。

## APITable

最终选型了APITable

### 部署

[APITable](https://github.com/apitable/apitable)

一键部署，在 window 上用 git-bash 执行

`curl https://apitable.github.io/install.sh | bash`

坑 1：

    有时候网络问题导致脚本失败了，好好判断报错信息吧。
    我有梯子，但是还是失败了，还以为是有什么依赖错误，
    排查了一会儿，什么都没改，重新执行一下又好了，就单纯是网络问题。

坑 2：

    all-in-one 部署出来容器内报错，没有深究。
    docker run -d -v ${PWD}/.data:/apitable -p 80:80 --name apitable apitable/all-in-one:latest
    在 window 上用 git-bash 执行，因为cmd没有${PWD}变量

### API

对于开发，以下几个关键的信息需要从WEB页面中获取：

- spaceId 右侧【空间站管理】
- datasheetId/viewId 进入一个表格/视图，点击【API】，curl 示例中有该表格/视图的 id
- token 【个人信息】中的【开发者配置】中创建【API 令牌】

然后我实现了和上面企微智能表格几乎一样的封装，但不完全一致，
也没有抽象成统一的接口，等有实际业务跑通了，代码稳定下来再考虑抽象。

APITable 界面上的 API 面板是挺好的，但是如果能提供一个完整的 swagger（就是 OpenAPI 3.0）我就可以直接生成 SDK 了，可惜。

### 限制和源码

最大问题是官方脚本部署出来后，单表最多 100 行数据？？？

我都把好几个接口以及好几种字段类型都实现完了，想测试个大一点的数据量，才发现有这么个限制。

一看空间管理，用户席位 2 个，存储 1G，文件 5 个，总行数 250 行？加上面单表 100 行限制，这没法用啊。

[官方文档](https://apitable.getoutline.com/s/82e078fc-1a8d-4616-b69d-fcdbb18ef715/doc/configuration-paNhPtzqMN)
查到 SERVER_MAX_RECORD_COUNT 配置，尝试在 `.env`和 `docker-compose.yaml`配置过，不起作用。
而且这个变量默认值是 50000，应该不是对应上述的限制。

在官方文档/网上冲浪/源码阅读中辗转了大半天，最后确定这个问题需要修改源码重新编译[参考 issues](https://github.com/apitable/apitable/issues/1122)

搭建[开发环境](https://apitable.getoutline.com/s/751b142b-866f-4174-a5f1-a2975f85ad41/doc/developer-quick-start-zofpBpXg9A)拉源码下来研究一下，配合AI很快就能找到方法的。

### 封装

基于官方 API，我在 `pkg/papitable` 下封装apitable的api调用：

- **结构化操作**：
  - **Table/Column**：封装了表格创建以及字段的动态增删查。支持将复杂的字段配置简化为结构体操作。
  - **Row**：提供了强类型的行记录操作接口（CRUD），自动处理不同字段类型（如多选、成员、关联）的 JSON 序列化与反序列化。

- **高级功能**：
  - **Attachment**：封装了附件上传流程，处理了上传 Token 获取与文件流传输。
  - **Permission**：集成了成员列表获取与基础权限判断。未完成，需要二开apitable。
  - **Sync**：实现了本地数据与多维表格的双向同步逻辑，支持增量更新，这也是实现“混合开发模式”的核心组件。

> 也正是"Sync"这部分的开发，耗费比较多精力之余，学习了大量相关的知识。
> CDC/Canal/GTID/ETL等等各种技术原理。
> 具体到如何标记一个同步消息是否已经处理过了等等问题。
> 阅读理论知识，到实际自己开发解决问题还是有很大距离的。

- **AI 辅助设计 (`doc4ai`)**：
  - 为了配合 AI 编程，我在 `doc4ai` 目录下维护了一套纯文本的“接口说明书”（如 `row_查询记录.txt`、`tbl_创建表格.txt`）。这些不仅是文档，更是提供给 AI Agent 的 Context，使得 AI 在编写业务逻辑时能准确调用 SDK。
