# 网站维护说明

本文供维护者使用。访客入口见根目录 README 与 https://chanlx86.github.io/repo/ 。

## 当前生成器与路径

`tools/build.py` 为入口，`tools/site_v2.py` 生成 iOS 9 风格界面、OTA 清单、Cydia 精简详情和源索引。网站页面、样式、头像、清单与新版 DEB 位于 `repo/`；根首页及旧详情页仅跳转到新入口。根 Cydia 索引保留兼容，Filename 指向 `repo/deb/`，不要把两套索引的相对路径直接混用。

现有 IPA 和源码 ZIP 保留原下载地址，避免重复上传大文件或破坏旧链接。`catalog.json` 中的文件路径始终相对仓库根目录；`download_url` 为实际绝对 HTTPS 下载地址。

5 个 DEB 的源元信息统一为 Author / Maintainer = chanlx86。首次迁移时增加 Debian `-1` 修订号，control 以外的安装载荷和脚本保持原样。再次生成不重复递增；修改程序时仍需使用真实的新版本号。上游来源与原有许可不可删除。

OTA 从 IPA 内的 Info.plist 读取真实 Bundle ID 与 CFBundleVersion，不能用网页版本字符串猜测。协议入口本身不解除签名限制，需要兼容的签名／AppSync 环境。发布前检查清单、IPA 的 HTTPS 可达性；未经过目标设备实际安装时不得宣称真机安装已通过。

## 发布目录

- `ipa/<标识>/<版本>/`：已选择公开的 IPA。
- `repo/deb/`：当前源修订的 DEB。根 `deb/` 是迁移前的旧下载文件。
- `source/<标识>/<版本>/`：对应源码。
- `catalog.json`：当前公开文件的版本、大小、SHA-256 与说明。
- `repo/apps/`、`repo/archive/`、`repo/help/`：访客页面；`repo/cydia/` 为精简插件详情。
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

`.nojekyll` 保持在根目录。Pages 发布源仍为 main / root，不能因为网址迁到 /repo/ 就把 Pages 的发布目录也改成 /repo/。网站文件自然映射为 URL 子目录。发布后核验 `/repo/`、真实下载、两套 Packages 与 Release，以及 OTA 清单，不能只看构建图标。

上传前运行 `git fetch origin main`，然后 `python3 tools/stage_upload.py`。该工具只暂存 catalog 声明的发行包和网站变更；不要使用早期“01／02”整包上传目录，以免重新发布已排除的历史安装包。

## 本地预览

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

浏览器访问 http://127.0.0.1:8765/ ，结束按 Ctrl+C。页面不依赖 Node 或外部字体；核心布局保留对旧 Safari 的兼容，JavaScript 只增强搜索和筛选。

## 来源

[GitHub 上传说明](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)、[大文件限制](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)、[Pages 限制](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)。
