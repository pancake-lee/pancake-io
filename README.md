# [个人网站](https://pancake-lee.github.io/pancake-io/)

theme 来自[Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy)

## [commitlint](https://github.com/conventional-changelog/commitlint)

| prefix   | desc       |
| -------- | ---------- |
| build    | 构建相关   |
| chore    | 杂项       |
| ci       | CI/CD 相关 |
| docs     | 文档       |
| feat     | 功能       |
| fix      | 修复       |
| perf     | 性能       |
| refactor | 重构       |
| revert   | 回退       |
| style    | 代码风格   |
| test     | 测试       |
| post     | 发布文章   |

## 本地 Markdown 预览图片加载

### 问题

文章中的图片在 GitHub Pages 上能正常显示，但用 VS Code 内置预览或 Office Viewer 等本地插件打开时无法加载。

### 根因

- 文章放在 `_posts/<子目录>/` 下，图片放在仓库根目录的 `assets/img/` 下。
- 之前图片路径有两种写法：
  - `assets/img/...`（无 `/`）— 本地预览器会把它当成 `_posts/app/assets/img/...`，找不到。
  - `/assets/img/...`（有 `/`）— 本地预览器会当成文件系统根 `/assets/img/...`，也找不到。
- GitHub Pages 上能显示是因为 Chirpy 主题的 `media-url.html` 会自动给路径加上 `baseurl`（`/pancake-io`）。

### 解决

把图片路径统一改成正确的相对路径 `../../assets/img/...`，同时修改主题 `_includes/media-url.html` 让其正确处理 `../` 开头的浏览器相对路径。

**修改点**（`_includes/media-url.html`）：

```liquid
{% unless url contains '..' %}
  ... 原有的 baseurl / CDN / subpath 拼接逻辑 ...
{% endunless %}
```

如果路径包含 `..`，主题会原样保留，不做 baseurl 拼接。浏览器从文章 URL（`/pancake-io/posts/标题/`）相对解析 `../../assets/...` 时，会自动得到 `/pancake-io/assets/...`，和线上一致。

如果不修改主题源码，要么牺牲本地预览体验（只用 `bundle exec jekyll serve`），要么牺牲维护便利性（硬编码完整 URL 或把图片复制到文章同级目录）。

### 后续新增文章的路径规范

- 所有 `_posts/<子目录>/` 下的文章，引用 `assets/img/` 下的图片时，统一使用 `../../assets/img/...` 的相对路径写法。
