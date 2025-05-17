---
title: "jeklly+github+gitee做个人博客"
description: " "
author: Pancake
date: 2019-06-08
categories: Coffee
tags: Github
---

## 方案

- github-pages：初衷最希望是在 github 上用 jeklly 做个个人博客，慢慢累积自己的文章，但是 github 有时很慢，所以转到 gitee。
- gitee-pages：但是不想放弃 github，所以 github 的 pages 首页下链接都指向于 gitee 的 pages，可能这样做不太道德？以后可能考虑同时 push 到两个远程仓库的方案来做同步。
- jekyll-theme：找了一个足够简洁的主题，保留作者链接最页面底部。
- gitalk 评论系统：对比了各种评论系统，gitalk 应该是比较可行的方案了，将 gitalk 用于了 gitee 的评论，但是实际评论是在 github 的 issue。
- 总结：其实 github + jeklly + gitalk 的方案是我的初衷，但是考虑国内访问方便，于是转移到了 gitee，最后没想到绕一下圈还能把 gitalk 也用在 gitee-pages 上。

## pages 项目

- github-pages：新建仓库 -> Settings -> GitHub Pages
- gitee-pages：新建仓库 -> 服务 -> Gitee Pages

网上随便搜就有教程，不详细说

## jekyll-theme

- [jekyll 主题官网](https://jekyllthemes.org/)挑选，教程对应看作者的文档
- github 在 Settings -> GitHub Pages 下有一个 Theme Chooser 可以选择一个 github 提供的主题，选择比较少

## gitalk

## 说明

- 搜索 jeklly 添加评论的方案时，发现了 gitalk，一开始不知道是什么，还以为能直接用于 gitee 的 pages，瞎折腾了一下。
- gitalk 是用于 github 的，依赖 github 账号，依赖 github 仓库的 issue。
- 刚好我是在 github 和 gitee 都创建了 pages 工程仓库的，所以是不是可以利用 github-pages + gitalk 来做 gitee-pages 的评论区呢？实践证明是**可行的**。
- 这个方案，评论最终写进的是 github 的 pages 项目的 issue。
- 这个方案，评论需要登录 github 账号，也要写入 github 的 issue，所以有些网络状态下会 load 得慢，或者根本 load 不出来。但是至少放在 gitee 上得文章还是能够稳定访问的。

## jeklly 工程添加代码

- 一般情况下，jeklly 会有./\_layouts/post.html 作为文章页面的 html 模板，在适当的位置加入以下代码，适当的位置需要对 html 有点了解，知道 post 的大概布局自行确定放在哪里。

```html
<!-- ························Gitalk评论系统·························· -->
<div id="gitalk-container"></div>
<link
  rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/gitalk@1/dist/gitalk.css"
/>
<script src="https://cdn.jsdelivr.net/npm/gitalk@1/dist/gitalk.min.js"></script>
<script>
  var gitalk = new Gitalk ({
  id: location.pathname, // Ensure uniqueness and length less than 50
  clientID: 'your clientID',
  clientSecret: ''your clientSecret'',
  repo: 'your github repo name',
  owner: 'your github name',
  admin: 'your github name',
  distractionFreeMode: false // Facebook-like distraction free mode
  })
  gitalk.render('gitalk-container')
</script>
```

repo：填写 github 上工程名称，不是 url，只需要名称。
owner 和 admin：填写你 github 账号的昵称。
clientID 和 clientSecret 见下文

## 注册 GitHub Application

[GitHub](https://github.com/settings/applications/new)
其中 Homepage URL 和 Authorization callback URL 填写你的 pages 主页 url，
如我的是`https://pancake-lee.github.io/pancake-pages`
注册完成获得 Client ID 和 Client Secret，填写到./\_includes/gitalk.html
