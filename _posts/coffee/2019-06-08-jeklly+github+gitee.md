---
title: "jeklly+github+gitee做个人博客"
description: " "
author: Pancake
date: 2019-06-08
categories: Coffee
tags: Github
---

# 方案
* github-pages：初衷最希望是在github上用jeklly做个个人博客，慢慢累积自己的文章，但是github有时很慢，所以转到gitee。
* gitee-pages：但是不想放弃github，所以github的pages首页下链接都指向于gitee的pages，可能这样做不太道德？以后可能考虑同时push到两个远程仓库的方案来做同步。
* jekyll-theme：找了一个足够简洁的主题，保留作者链接最页面底部。
* gitalk评论系统：对比了各种评论系统，gitalk应该是比较可行的方案了，将gitalk用于了gitee的评论，但是实际评论是在github的issue。
* 总结：其实github + jeklly + gitalk的方案是我的初衷，但是考虑国内访问方便，于是转移到了gitee，最后没想到绕一下圈还能把gitalk也用在gitee-pages上。

# pages项目
* github-pages：新建仓库 -> Settings -> GitHub Pages
* gitee-pages：新建仓库 -> 服务 -> Gitee Pages

网上随便搜就有教程，不详细说

# jekyll-theme
* [jekyll主题官网](http://jekyllthemes.org/)挑选，教程对应看作者的文档
* github在Settings -> GitHub Pages下有一个Theme Chooser可以选择一个github提供的主题，选择比较少


# gitalk
## 说明
* 搜索jeklly添加评论的方案时，发现了gitalk，一开始不知道是什么，还以为能直接用于gitee的pages，瞎折腾了一下。
* gitalk是用于github的，依赖github账号，依赖github仓库的issue。
* 刚好我是在github和gitee都创建了pages工程仓库的，所以是不是可以利用github-pages + gitalk来做gitee-pages的评论区呢？实践证明是**可行的**。
* 这个方案，评论最终写进的是github的pages项目的issue。
* 这个方案，评论需要登录github账号，也要写入github的issue，所以有些网络状态下会load得慢，或者根本load不出来。但是至少放在gitee上得文章还是能够稳定访问的。

## jeklly工程添加代码
* 一般情况下，jeklly会有./\_layouts/post.html作为文章页面的html模板，在适当的位置加入以下代码，适当的位置需要对html有点了解，知道post的大概布局自行确定放在哪里。

```html
<!-- ························Gitalk评论系统·························· -->
<div id="gitalk-container"></div>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/gitalk@1/dist/gitalk.css">
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

repo：填写github上工程名称，不是url，只需要名称。
owner和admin：填写你github账号的昵称。
clientID和clientSecret见下文

## 注册 GitHub Application
https://github.com/settings/applications/new
其中Homepage URL和Authorization callback URL填写你的pages主页url，如我的是https://pancake-lee.github.io/pancake-pages
注册完成获得Client ID和Client Secret，填写到./\_includes/gitalk.html



