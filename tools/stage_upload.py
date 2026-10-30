#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stage only changed public files against origin/main, never the whole local archive."""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import shutil
import subprocess

root = Path(__file__).resolve().parent.parent
raw = subprocess.check_output(['git', 'ls-tree', '-r', '-z', 'origin/main'], cwd=root)
remote = {}
for record in raw.split(b'\0'):
    if record:
        metadata, path = record.split(b'\t', 1)
        remote[path.decode('utf-8')] = metadata.split()[2].decode('ascii')
paths = set(['.gitignore', '.nojekyll', 'README.md', 'LICENSE', '404.html',
             'CydiaIcon.png', 'index.html', 'style.css', 'site.js', 'catalog.json',
             'Packages', 'Packages.gz', 'Packages.bz2', 'Packages.xz', 'Release', 'SHA256SUMS'])
for folder in ['apps', 'archive', 'help', 'icons', 'docs', 'tools']:
    paths.update(str(p.relative_to(root)) for p in (root/folder).rglob('*')
                 if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc' and p.name != '.DS_Store')
catalog = json.loads((root/'catalog.json').read_text())
for app in catalog['apps']:
    for version in app['versions']:
        paths.update(f['path'] for f in version['files'])
changed = []
for name in sorted(paths):
    path = root/name
    data = path.read_bytes()
    blob = hashlib.sha1(b'blob '+str(len(data)).encode('ascii')+b'\0'+data).hexdigest()
    if remote.get(name) != blob:
        if len(data) > 25*1024*1024:
            raise SystemExit('File needs another publishing route: '+name)
        changed.append(name)
if not changed:
    print('No changes against origin/main. Fetch before checking remote updates.')
    raise SystemExit(0)
stage = Path.home()/'Downloads/chanlx86-网站上传'/('更新-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
stage.mkdir(parents=True)
for name in changed:
    target = stage/name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root/name, target)
print(stage)
print(len(changed), 'changed files;', sum((root/p).stat().st_size for p in changed), 'bytes')
print('Upload the CONTENTS of this directory to the repository root. Review hidden files too.')
if len(changed)>100:
    print('More than 100 files: split the upload into smaller batches.')
