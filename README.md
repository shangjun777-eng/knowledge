# 芯片知识库

面向数字芯片设计与验证工程师的公开知识库，覆盖总线/接口协议、IP 模块、验证方法学和设计实现。

站点形态是 **博客 + 评论**：文章按分类、标签、系列组织，读者可以在文章下讨论。

## 技术栈

- [Hugo Extended](https://gohugo.io/) + [Stack 主题](https://stack.cai.im/) v4
- [Pagefind](https://pagefind.app/) 中文全文搜索
- [giscus](https://giscus.app/) 评论（GitHub Discussions，零后端）
- [Mermaid](https://mermaid.js.org/) 框图 / 状态机、[WaveDrom](https://wavedrom.com/) 数字时序图
- [KaTeX](https://katex.org/) 数学公式
- Cloudflare Pages 自动构建部署

## 本地开发

前置条件：Hugo Extended、Node.js 22+、Git。

```bash
# 安装 Hugo Extended（Windows）
winget install -e --id Hugo.Hugo.Extended

# 本机已下载的 Hugo 在：
#   C:\Users\jun_s\AppData\Local\hugo-0.169.0\bin
# 如果 `hugo version` 找不到命令，可临时把该目录加入 PATH：
#   PowerShell: $env:Path = 'C:\Users\jun_s\AppData\Local\hugo-0.169.0\bin;' + $env:Path
# 或把该目录加入 Windows 用户环境变量 Path。

# 安装依赖
npm install

# 启动本地预览（不包含 Pagefind 搜索索引）
npm run dev
# http://localhost:1313/

# 完整构建并预览（包含搜索）
npm run build
npm run preview
```

> `hugo server` 不会运行 Pagefind 索引。验证搜索必须使用 `npm run build && npm run preview`。

## 写一篇新文章

```bash
hugo new content posts/my-topic/index.md
```

文章使用 page bundle，图片放在同目录的 `images/` 下。

front matter 约定：

```toml
+++
title = "文章标题"
date = 2026-11-03
draft = false
slug = "my-topic"            # 发布后不要改，评论按 pathname 关联
description = "一句话摘要"
categories = ["总线与接口"]
tags = ["pcie", "tlp"]
series = ["pcie-from-scratch"]
series_title = "PCIe 从零开始"
series_order = 10
math = false                 # 需要公式时设为 true
toc = true
comments = true
keywords = []
+++
```

文章结构见 `archetypes/posts.md`：TL;DR、背景、架构、时序、设计要点、验证要点、常见坑、参考规范、相关文章。

## 目录说明

```text
content/posts/          所有知识文章（page bundle）
content/knowledge-map/  知识地图
content/learning-paths/ 学习路线
content/search/         Pagefind 搜索页
archetypes/posts.md     新文章模板
layouts/                主题覆盖：WaveDrom、Mermaid、KaTeX、搜索页、系列导航
static/vendor/          本地化的 Mermaid / WaveDrom / KaTeX 资源
themes/                 Stack 主题（git submodule）
```

## 部署

### GitHub Pages（项目站）

仓库以 public 项目站方式部署时，站点地址形如 `https://<用户名>.github.io/<仓库名>/`。

1. 创建 public 仓库（例如 `knowledge`）。
2. 仓库 Settings → Pages → Source 选择 **GitHub Actions**。
3. 推送 `main` 分支，`.github/workflows/deploy.yml` 会自动完成：
   - 安装 Hugo Extended 0.169.0 和 Node 22
   - `npm ci`
   - `hugo --gc --minify --baseURL <Pages URL>/`
   - 生成 Pagefind 中文索引
   - 上传 `public/` 到 Pages
4. 在 Actions 或 Pages 页面查看首次部署结果。

项目站使用 `/knowledge/` 子路径：文章内部链接已用 Hugo `relref`，搜索页已给 Pagefind UI 设置 `bundlePath`，不需要手动改链接。`hugo.toml` 的 `baseURL` 只用于本地/根路径构建，GitHub Actions 会通过 `--baseURL` 覆盖为实际的 Pages 地址。

### Cloudflare Pages（可选）

推送到 GitHub 后，在 Cloudflare Pages 连接仓库并配置：

| 配置项 | 值 |
| --- | --- |
| Build command | `git submodule update --init --recursive && npm ci && npm run build` |
| Build output directory | `public` |
| `HUGO_VERSION` | `0.169.0` |
| `NODE_VERSION` | `22.23.4` |
| `HUGO_ENVIRONMENT` | `production` |
| `TZ` | `Asia/Shanghai` |

`HUGO_VERSION` 需要同时设置在 Production 和 Preview 环境。

## 待替换的占位符

- `hugo.toml` 中的 `baseURL`：本地/根路径构建用，当前为 `https://knowledge.pages.dev/`；GitHub Pages 项目站由 workflow 覆盖，改用 Cloudflare Pages 或自定义域名时再改。
- `hugo.toml` 中的 giscus 配置：`repo`、`repoID`、`categoryID`
- `hugo.toml` 中的 `params.author`
- `assets/img/avatar.png`、`assets/img/favicon.png`（可替换为个人头像和站点图标）

评论默认关闭（`[params.comments] enabled = false`）。按 `hugo.toml` 里的 giscus 注释完成仓库、Discussions 和 `giscus.app` 配置后，把 `enabled` 改为 `true` 即可。

## 内容规范

- 分类固定 5 个：总线与接口、IP 与微架构、验证方法学、设计与实现、工具与环境。
- 标签用英文小写，3～8 个，避免堆砌。
- 系列用英文 slug + 中文标题，`series_order` 以 10 递增。
- 发布后不要修改 `slug`，否则已有关联的评论会丢失。
