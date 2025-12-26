---
title: "TreeWorld-基于树表的前端玩具项目"
description: ""
author: Pancake
date: 2025-07-08
categories: Tech
tags: frontend
---

## 初衷与中断

初衷是要做一个相对通用的页面，来给我自己的后端玩具做交互入口的。

那么就想到了以树表为基本交互方式，则表格中有一列可以展开/收缩子节点。

对于没有怎么接触过前端的我来说，这个工程已经走了有一小段距离了，包含了以下的功能：

- 树形表格展示，支持层级数据结构
- 可调整列宽，支持列拖拽排序
- 数据分表格展示和抽屉详情展示两部分
- 支持搜索/排序功能
- Dark 主题支持
- 数据来源可以自定义实现，支持按层级加载树结构
- 调用后端 API 接口（任务列表、修改、删除等）
- 数据持久化：展开状态和列宽的 localStorage 持久化
- 支持任务排序（prevID 机制）
- 任务创建：支持 Enter/Tab 快捷键，并且选中新任务
- 任务删除：支持 Del 快捷键，二次确认 Del/Esc，选中删除位置最近任务
- 任务移动：支持拖拽行移动任务位置
- 单元格编辑：F2 键或双击进入编辑状态，Esc 键退出编辑状态，修改详情里的值调用后端接口
- 方向键导航：支持上下左右键在树表中选中单元格，递归处理展开节点的情况
- 空格键：展开/折叠被选中单元格对应的树节点，没有子节点的行不展示展开按钮
- F3 键：打开/收起抽屉
- 页面上方展示快捷键说明
- 拖拽目标位置效果提示
- 添加空列作为选中点击位置，支持指定列为展开列
- 优化展示细节和操作后选中逻辑
- 选择列功能

基本上都是 AI 编程，包括上面功能点也是 AI 总结的。

然后刷到一些“多维表格”的咨询，包括各家平台的，包括开源的，
于是就开始搭建[APITable](https://github.com/apitable/apitable)来玩了。

总的来说，那么这个前端玩具就又中断了。

简单总结两句方便日后回忆，也不知道日后还会不会续命了...

## 前端知识框架

- Electron 跨平台桌面应用框架
  - 打包 Web 应用成桌面应用
- React: UI 库
  - Next.js 基于 React 的服务端渲染(SSR)框架
- nodejs
  - npm
    - 开发依赖（devDependencies）
      - 仅开发阶段需要，如构建工具、测试库、代码格式化工具等
      - webpack, eslint, jest, electron-builder
      - npm install package-name --save-dev
    - 生产依赖（dependencies）
  - npx 用于临时安装并运行包，而不需要全局安装
  - pnpm 替代 npm 命令，速度快，磁盘占用少
  - nvm 管理 node 的版本，nvm list 列出当前安装的版本
- MouseEvent
  - screenX/screenY 鼠标相对于整个屏幕的坐标
  - clientX/clientY 鼠标相对于浏览器视口的坐标
  - x/y clientX/clientY 的别名
  - pageX/pageY 鼠标相对于整个文档的坐标
  - offsetX/offsetY 鼠标相对于事件目标元素的坐标
  - movementX/movementY 相对于上一次 mousemove 事件的位移
- Electron 跨平台桌面应用框架
  - 打包 Web 应用成桌面应用
- React: UI 库
  - Next.js 基于 React 的服务端渲染(SSR)框架
- nodejs
  - npm
    - 开发依赖（devDependencies）
      - 仅开发阶段需要，如构建工具、测试库、代码格式化工具等
      - webpack, eslint, jest, electron-builder
      - npm install package-name --save-dev
    - 生产依赖（dependencies）
    - npx 用于临时安装并运行包，而不需要全局安装
    - pnpm 替代 npm 命令，速度快，磁盘占用少
- MouseEvent
  - screenX/screenY 鼠标相对于整个屏幕的坐标
  - clientX/clientY 鼠标相对于浏览器视口的坐标
  - x/y clientX/clientY 的别名
  - pageX/pageY 鼠标相对于整个文档的坐标
  - offsetX/offsetY 鼠标相对于事件目标元素的坐标
  - movementX/movementY 相对于上一次 mousemove 事件的位移
