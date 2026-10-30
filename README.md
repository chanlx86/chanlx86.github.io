# chanlx86 · 旧 iOS 软件源与发行存档

网站与 Cydia 源：**https://chanlx86.github.io/**

静态中文目录，针对旧版 Safari 保留基础兼容。包含应用／补丁筛选、搜索、软件说明、IPA／DEB／对应源码下载、历史版本、SHA-256 与安装指南。无需 Node 或前端框架。

## 目录

```text
index.html                 首页
apps/<软件标识>/index.html   软件介绍、当前下载与历史版本
archive/index.html         全部版本索引
help/index.html            安装、校验、许可说明
ipa/<标识>/<版本>/           IPA 安装包
debs/                      DEB 原包，保留真实 Package ID 与版本
source/<标识>/<版本>/        对应版本的源码 ZIP
icons/                     应用图标与通用图标
catalog.json               可公开的版本、文件和校验信息
Packages{,.gz,.bz2,.xz}     Cydia 软件索引（各包的当前版本）
Release                    软件源属性与索引哈希
SHA256SUMS                 全部发行文件的校验清单
tools/build.py             导入、页面与 Cydia 索引生成器
```

## 更新

使用 Python 3.9+。在此仓库目录执行：

```sh
python3 tools/build.py --import-archive "$HOME/Downloads/Repo"
```

生成器只导入映射的发行目录中的 IPA、DEB 与源码 ZIP，不修改原归档。测试录像、散装源码快照、设备核验 JSON、整理记录、个人路径说明和已知问题包不自动发布；爱丽丝快跑只发布独立补丁，不发布游戏 IPA。若同一路径内容变化，生成器会停止，避免偷偷覆盖已经发行的版本。

新增已有软件版本：先在原 Repo 中建新版本目录、放入发行包，再运行上面的命令。支持数字版本 `0.9.0` 或 `build65`。新增一种软件：先在 `tools/build.py` 的 `APPS` 加名称、原归档相对目录、说明和适用条件，再导入。导入阶段在 Mac 完成；若遇到苹果优化 PNG，需有 Xcode 的 pngcrush 转回普通 PNG。

只重建现有目录、不访问原归档：

```sh
python3 tools/build.py
```

提交前运行生成器校验全部发行文件。不要修改已经发行的 DEB 再沿用原版本号。`Package`、`Version`、`Architecture`、依赖均从包内读取；网页写上某个系统版本不等于扩大了包的兼容性。

## 预览

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

浏览器打开 http://127.0.0.1:8765/ 。按 Ctrl+C 停止。

## 发布到 GitHub Pages

仓库是 `chanlx86/chanlx86.github.io`，网站位于根目录。Pages 的发布源保持 `main` 分支、`/ (root)`；上传到根目录，不要再套一个 Repo 或 chanlx86.github.io 文件夹。

日常可使用 Safari 的 GitHub 网页：`Add file → Upload files`。把更新的目录与索引一起上传，再填写提交说明、提交。网页单文件上限 25 MiB、每批最多 100 个文件，当前发行文件均低于单文件上限；大量文件可分批。Safari 选文件窗口不便选择整个目录时，打开 Finder 后将目录直接拖到网页上传区域。不能把整个网站 ZIP 当作网页：GitHub Pages 不会自动解压。

本次实测一次提交全部约 104 MiB 的文件被网页拒绝，未入库。首次发布改为两批：先只上传 `ipa`（22 文件，约 69 MiB），再上传其余网站内容、`debs` 和 `source`（91 文件，约 35 MiB）。可运行 `python3 tools/stage_upload.py` 在下载目录生成两个对应批次；即使拖入后列表正常，也要等待提交成功并核对仓库文件，不能只看上传完成。

Git 命令方式需先独立配置 GitHub 身份认证，Safari 登录不会自动让终端 Git 登录：

```sh
git add .
git diff --cached --stat
git commit -m "Update software archive"
git push origin main
```

根目录 `.nojekyll` 保持存在，按静态文件直接发布。提交后查看仓库 Actions 的 Pages 构建结果，再核验线上 `Release`、`Packages.gz` 和实际下载链接。

## 来源与许可

网站样式和生成工具为独立编写；应用、补丁、上游及第三方组件分别遵循其自带许可。根目录 MIT 不替代发行软件许可。Troubadour 的对应源码随 IPA 提供，并保留上游 GPL-3.0；LocalSend 适配版提供对应源码与上游来源。没有复制参考仓库的页面源码或冒用其身份。

参考：[Computershik73 软件源的层级](https://github.com/Computershik73/repo)、[GitHub 网页上传](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)、[大文件限制](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)、[Pages 限制](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)。未来包较大或版本较多时，宜将大型发行文件转到 GitHub Releases；Git LFS 不适合作为 Pages 下载文件的直接替代。
