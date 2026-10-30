#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create two small-enough batches for GitHub's web upload UI."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parent.parent
stage = Path.home() / 'Downloads/chanlx86-网站上传'
stage.mkdir(exist_ok=True)
binaries = ['ipa']
pages = [p.name for p in root.iterdir() if p.name not in ['.git'] + binaries]
for name, entries in [('01-先上传发行文件', binaries), ('02-再上传网站页面', pages)]:
    dest = stage / name
    dest.mkdir(exist_ok=True)
    for entry in entries:
        source, target = root / entry, dest / entry
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
        else:
            shutil.copyfile(source, target)
    print(name, sum(1 for p in dest.rglob('*') if p.is_file()), 'files')
text = '''# Safari 发布说明

网站：https://chanlx86.github.io/
仓库：https://github.com/chanlx86/chanlx86.github.io

1. 仓库根目录点 Add file → Upload files。
2. 在 Finder 打开“01-先上传发行文件”，仅选择里面的 ipa 目录，拖到网页上传区域。等待全部完成，再点 Commit changes。此批约 69 MiB。
3. 再打开 Upload files。将“02-再上传网站页面”里面的内容（含 debs、source）拖到仓库根目录上传，提交。此批约 35 MiB、91 个文件。实测网页一次提交约 104 MiB 被拒绝，因此按此批次上传。
4. Finder 按 Command+Shift+. 显示隐藏文件；第二批的 .nojekyll 和 .gitignore 也应上传。本上传副本不含 .git。
5. Settings → Pages 保持 main 分支、/ (root)。Actions 构建成功后，检查线上首页、详情和实际下载。

上传的是两个批次文件夹里面的内容，不是外层文件夹本身。网站 ZIP 不会自动解压，不能只传一个 ZIP。

原 Downloads/Repo 保留不变；开发工程位于 ~/Documents/chanlx86.github.io，其 README.md 介绍后续更新。测试录像、设备核验和整理备份不放到网站。
'''
(stage / '上传说明.md').write_text(text, encoding='utf-8')
print(stage)
