# 网站维护说明

本文供维护者使用。访客入口见根目录 README 与 https://chanlx86.github.io/ 。

## 发布目录

- `ipa/<标识>/<版本>/`：已选择公开的 IPA。
- `deb/`：已选择公开的 DEB，保持原 Package ID、版本和内容。
- `source/<标识>/<版本>/`：对应源码。
- `catalog.json`：当前公开文件的版本、大小、SHA-256 与说明。
- `apps/`、`archive/`、`help/`：自动生成的访客页面。
- `Packages`、压缩索引、`Release`：只索引当前实际公开的 DEB。

## 先选择文件，再生成目录

当前目录已经按维护者在 GitHub 上筛选的包修正。不要直接把全部本地历史包重新上传。下载目录的原始 Repo 是完整归档，不等于全部公开发行。

只更新现有公开目录时：

```sh
python3 tools/build.py
```

从完整归档重新导入，会重新发现映射目录中的所有版本：

```sh
python3 tools/build.py --import-archive "$HOME/Downloads/Repo"
```

此命令只用于有意重新挑选发行包时。运行后必须按发布范围修订 `catalog.json`，移除不准备公开的文件记录，再重新生成。新增同一个软件版本时也可以只新增对应的 catalog 记录；字段沿用已有格式。每条文件记录的路径、字节大小和 SHA-256 必须对应实际文件。

已发行版本不原地改包；新内容使用新版本号。不要把测试录像、设备日志、核验 JSON、账号数据或整理备份加进公开目录。源码 ZIP 也应先检查是否意外包含私人配置。

## 上传与 Pages

Safari 登录 GitHub 不等于终端 Git 已登录。网页方式在仓库根目录使用 Add file → Upload files，按较小批次上传需要更新的文件和目录，不再套外层文件夹。GitHub Pages 不会替你解压一个网站 ZIP。

网页单文件最多 25 MiB，每批最多 100 文件；本次一次提交约 104 MiB 曾被拒绝。后续网页更新宜控制为少量变更。上传和提交是两步，必须看到提交已进入 main。更大的发行文件可改用 GitHub Releases，并显式调整下载路径。

`.nojekyll` 保持在根目录。现有 Pages 发布源应为 main / root；查看 Actions 的 Pages 构建结果。修改后核验首页、真实下载、`Packages.gz`、`Release`，不能只看构建图标。

## 本地预览

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

浏览器访问 http://127.0.0.1:8765/ ，结束按 Ctrl+C。页面不依赖 Node 或外部字体；核心布局保留对旧 Safari 的兼容，JavaScript 只增强搜索和筛选。

## 来源

[GitHub 上传说明](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)、[大文件限制](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)、[Pages 限制](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)。
