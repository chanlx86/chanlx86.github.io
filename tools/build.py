#!/usr/bin/env python3
"""Build a static, old-Safari-friendly catalogue and a flat Cydia repository.

python3 tools/build.py --import-archive /path/to/Repo
python3 tools/build.py
Only explicitly mapped release artifacts are imported. Original archives stay intact.
"""
import argparse
import bz2
import gzip
import hashlib
import html
import io
import json
import lzma
import re
import shutil
import struct
import subprocess
import tarfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://chanlx86.github.io/'
REPO = 'https://github.com/chanlx86/chanlx86.github.io'
ESC = html.escape

# Public descriptions are written for visitors; local test reports are not published.
APPS = [
 dict(id='j2me', folder='J2ME模拟器', name='J2ME模拟器', category='apps', os='iOS 6+',
      tagline='让功能机时代的 Java 游戏重回掌心。',
      description='导入 JAR，使用方向键、数字键或触屏游玩。支持 MIDP 图像、音频与部分 M3G 3D 游戏，提供布局和帧率显示选项。',
      notes=['不同游戏的接口和性能仍有差异，不能保证所有 JAR 兼容。','本页提供已越狱设备使用的 IPA；JIT 等实验功能的可用性取决于系统与越狱环境。']),
 dict(id='archive-browser', folder='存档浏览器', name='存档浏览器', category='apps', os='iOS 9+',
      tagline='用原生界面，探索 Internet Archive。',
      description='搜索条目、浏览合集与文件，下载公开资源，阅读文档和播放支持的媒体。时光机入口可查看网页历史快照。',
      notes=['媒体格式、网页完整性及网络可达性受旧系统与远端服务限制。','0.9.0 的普通音频预览以 MP3 为主；SWF 可保存，不支持运行 Flash 游戏。'],
      features=['公开档案搜索与下载','PDF / EPUB / 文本阅读','Wayback 快照时间轴']),
 dict(id='screen-recorder', folder='录屏大师', name='录屏大师', category='apps', os='iOS 9.x · 32 位',
      tagline='为老 iPad 留下有画面、有声音的记录。',
      description='系统画面录制、内部音频与可选麦克风。带录制浮标、视频库、多选分享，以及低、中、高码率设置。',
      notes=['需要 rootful 越狱、MobileSubstrate 和 RocketBootstrap。依赖请从各自可信来源安装。','Retina 档面向 iPad 3 / 4；性能与录制效果依设备和应用而异。','标准档最长 30 分钟，Retina 档最长 10 分钟；先短录检查画面和声音。']),
 dict(id='localsend', folder='LocalSend', name='LocalSend', category='apps', os='iOS 9+ · ARMv7',
      tagline='让旧 iPad 也能轻松参与局域网传输。',
      description='基于 unlocalsend 的 iPad 适配版本。中文界面、Retina 显示、照片缩略图、文件导入和系统照片分享扩展。',
      notes=['发送文件浏览器默认从 /var/mobile/Documents 开始；接收文件保存在应用自己的 Documents。','分享扩展准备好文件后，需打开 LocalSend 选择接收设备。','这不是官方 LocalSend 客户端；部分行为与现代客户端不同。'],
      upstream='https://github.com/theanazerka/unlocalsend'),
 dict(id='troubadour', folder='Troubadour', name='Troubadour', category='apps', os='ARMv7 iOS 5.1+ / ARM64 iOS 7+',
      tagline='面向旧 iOS 的 YouTube 客户端。',
      description='基于 Computershik73 的开放源码构建。此处提供 Xcode 7.3.1 的修复构建 1.6.1，处理进入 Shorts 时的回调生命周期闪退。',
      notes=['这是移植修复构建，与上游最新发行版分开维护。','IPA 的容器安装不执行 DEB 安装脚本，部分依赖 root 辅助程序的图标功能可能不同。','保留上游 GPL-3.0 及第三方许可；对应源码包随版本提供。'],
      upstream='https://github.com/Computershik73/Troubadour'),
 dict(id='wikisource', folder='维基文库', name='维基文库', category='apps', os='iOS 9+',
      tagline='在旧设备上，安静地读一本书。',
      description='第三方中文维基文库只读客户端。作品搜索、目录、简繁转换、横排与竖排阅读、收藏和阅读进度。',
      notes=['非维基媒体基金会官方产品。内容与图片许可请查看原站。','缓存用于最近阅读的正文，不代表整部作品已经离线下载。']),
 dict(id='onegram-login-fix', folder='Onegram登录补丁', name='Onegram 登录修复', category='patches', os='iOS 9+',
      tagline='修复登录入口与验证码位数限制。',
      description='针对 Onegram 1.4.2，处理登录界面本地化等待和验证码输入。允许手动输入完整验证码再提交。',
      notes=['需要原应用和 MobileSubstrate。仅针对已适配的客户端版本。','不恢复服务器服务，也不绕过账号验证。']),
 dict(id='wikipedia-compat', folder='维基百科兼容补丁', name='Wikipedia 正文兼容', category='patches', os='iOS 9+',
      tagline='让旧版 Wikipedia 重新显示正文。',
      description='针对 Wikipedia 5.5.1（1164），将已失效的 mobileview 正文请求适配到现有 Parse API。',
      notes=['只作用于 org.wikimedia.wikipedia 的指定版本。','正文以单一节提供，不恢复完整原生章节侧栏；其他旧接口未全面改造。','安装或卸载后，请彻底退出 Wikipedia 再打开。']),
 dict(id='alice-launch-fix', folder='爱丽丝快跑补丁/响应保护补丁', name='爱丽丝快跑启动修复', category='patches', os='ARMv7 · rootful 越狱',
      tagline='保护异常的网络响应，恢复游戏启动。',
      description='针对中文版 RushingAliceCN 2.40，在网络响应抛出异常时保护客户端，避免直接闪退。',
      notes=['实测 iPad 3 / iOS 9.3.6；其他系统和设备需另行验证。','仅提供独立修复补丁，不附带原游戏或内置补丁游戏包。','不能恢复已关闭的在线服务。安装后彻底退出游戏再打开。']),
 dict(id='locke-display', folder='洛克王国图鉴补丁/显示修复', name='洛克图鉴 · 横屏修复', category='patches', os='iOS 6+ · ARMv7',
      tagline='找回被截断的横屏页面。',
      description='恢复洛克王国图鉴 1.2 的窗口和横屏布局，使界面正确适配 iPad。',
      notes=['需要原应用 com.uwingame.roco.ipad.free 1.2 和 MobileSubstrate。','补丁不包含原应用。安装后退出原应用再打开。']),
 dict(id='locke-type', folder='洛克王国图鉴补丁/属性克制修复', name='洛克图鉴 · 属性克制', category='patches', os='iOS 6+ · ARMv7',
      tagline='修正旧战斗模拟中的属性映射。',
      description='依据原应用附带的克制表，校正类型编号与伤害倍率。',
      notes=['仅适用于洛克王国图鉴 1.2 和 rootful 越狱环境。','使用其他战斗补丁前，请阅读该补丁的依赖和功能说明。']),
 dict(id='locke-stats', folder='洛克王国图鉴补丁/种族值修复', name='洛克图鉴 · 种族值与伤害', category='patches', os='iOS 6+ · ARMv7',
      tagline='按同时代数据校对宠物与等级公式。',
      description='采用指定的 4399 旧种族表，调整等级数值、速度出招顺序与普通伤害计算；统一满天赋 31、努力值 0、中性性格。',
      notes=['2.0.1 对未收录的宠物保留原数据；不宣称覆盖页游的全部技能机制。','仅适用于原图鉴 1.2；需 MobileSubstrate。']),
 dict(id='locke-battle', folder='洛克王国图鉴补丁/回合战斗', name='洛克图鉴 · 回合战斗', category='patches', os='iOS 6+ · ARMv7',
      tagline='从胜率模拟，走向可以操作的对战。',
      description='十秒回合、自由选技能、血条与战斗日志，支持 PvE 和本地双人 PvP，并加入控制、持续伤害及能力等级规则。',
      notes=['依赖种族值补丁 ≥ 2.0.1 和横屏补丁 ≥ 1.0.0；本源提供这些依赖。','需要原图鉴 1.2、MobileSubstrate；部分复杂技能效果仍为有限实现。'])
]

def write(path, data):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        data = data.encode('utf-8')
    if not p.exists() or p.read_bytes() != data:
        p.write_bytes(data)

def digest(data, algorithm='sha256'):
    return hashlib.new(algorithm, data).hexdigest()

def control_from_deb(path):
    data = path.read_bytes()
    if data[:8] != b'!<arch>\n':
        raise ValueError('Not a Debian ar archive: ' + str(path))
    pos = 8
    while pos + 60 <= len(data):
        header = data[pos:pos + 60]
        size = int(header[48:58])
        member = data[pos + 60:pos + 60 + size]
        if len(member) != size:
            raise ValueError('Truncated ar archive')
        pos += 60 + size + size % 2
        if header[:16].decode().strip().rstrip('/').startswith('control.tar'):
            with tarfile.open(fileobj=io.BytesIO(member), mode='r:*') as tar:
                item = next(x for x in tar if x.name.lstrip('./') == 'control')
                return tar.extractfile(item).read().decode('utf-8')
    raise ValueError('Missing control')

def fields(text):
    result, key = {}, None
    for line in text.splitlines():
        if line[:1] in (' ', '\t') and key:
            result[key] += '\n' + line
        elif ':' in line:
            key, value = line.split(':', 1)
            result[key] = value.strip()
    return result

def version_key(value):
    # Imported versions are numeric dotted versions or buildNN, not arbitrary Debian versions.
    return tuple(int(x) for x in re.findall(r'\d+', value))

def copy_artifact(source, dest):
    target = ROOT / dest
    target.parent.mkdir(parents=True, exist_ok=True)
    data = source.read_bytes()
    if target.exists() and target.read_bytes() != data:
        raise ValueError('Existing version differs; use a new version: ' + dest)
    if not target.exists():
        shutil.copyfile(source, target)
    return dict(path=dest, size=len(data), sha256=digest(data))

def import_icon(ipa, app_id):
    with zipfile.ZipFile(ipa) as z:
        candidates = []
        for item in z.infolist():
            if item.filename.count('/') != 2 or not item.filename.lower().endswith('.png'):
                continue
            if 'icon' not in Path(item.filename).name.lower() or item.file_size > 4 * 1024 * 1024:
                continue
            b = z.read(item)
            offset = b.find(b'IHDR')
            if offset < 0:
                continue
            width, height = struct.unpack_from('>II', b, offset + 4)
            if width == height and 100 <= width <= 1024:
                candidates.append((abs(width - 152), item.filename, b))
        if candidates:
            b = min(candidates, key=lambda x: x[0])[2]
            dest = 'icons/' + app_id + '.png'
            write(dest, b)
            if b'CgBI' in b[:80]:
                pngcrush = Path('/Volumes/OS X/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/usr/bin/pngcrush')
                if not pngcrush.is_file():
                    raise ValueError('CgBI icon needs Apple pngcrush conversion')
                temp = ROOT / ('icons/' + app_id + '.converted.png')
                subprocess.run([str(pngcrush), '-q', '-revert-iphone-optimizations', str(ROOT / dest), str(temp)], check=True, stdout=subprocess.DEVNULL)
                temp.replace(ROOT / dest)
            return dest
    return 'icons/package.svg'

def import_archive(archive):
    catalog = []
    for app in APPS:
        base = archive / app['folder']
        versions = []
        for directory in sorted(base.iterdir(), key=lambda p: version_key(p.name)):
            if not directory.is_dir() or not re.fullmatch(r'(?:build)?\d+(?:\.\d+)*', directory.name):
                continue
            artifacts = []
            for file in sorted(directory.rglob('*')):
                if not file.is_file():
                    continue
                # Only release artifacts, never loose source snapshots, logs or private records.
                if file.suffix == '.deb' and (file.parent == directory or app['id'] == 'alice-launch-fix'):
                    c = fields(control_from_deb(file))
                    filename = '{Package}_{Version}_{Architecture}.deb'.format(**c)
                    if not re.fullmatch(r'[A-Za-z0-9.+_~-]+\.deb', filename):
                        raise ValueError('Unexpected Debian filename: ' + filename)
                    item = copy_artifact(file, 'deb/' + filename)
                    item.update(type='deb', label='DEB 安装包', control=c)
                    artifacts.append(item)
                elif file.parent == directory and file.suffix == '.ipa':
                    item = copy_artifact(file, 'ipa/{}/{}/{}.ipa'.format(app['id'], directory.name, app['id']))
                    item.update(type='ipa', label='IPA 安装包')
                    artifacts.append(item)
                elif file.parent == directory and file.suffix == '.zip' and '源码' in file.name:
                    item = copy_artifact(file, 'source/{}/{}/source.zip'.format(app['id'], directory.name))
                    item.update(type='source', label='对应源码 ZIP')
                    artifacts.append(item)
            if app['id'] == 'alice-launch-fix':
                # The existing ZIP contains the independent patch and its source, not the game.
                for file in directory.glob('AliceResponseGuard-*.zip'):
                    item = copy_artifact(file, 'source/{}/{}/source.zip'.format(app['id'], directory.name))
                    item.update(type='source', label='补丁与源码 ZIP')
                    artifacts.append(item)
            if artifacts:
                versions.append(dict(version=directory.name, files=artifacts))
        if not versions:
            raise ValueError('No releases for ' + app['id'])
        item = {k: v for k, v in app.items() if k != 'folder'}
        item['versions'] = sorted(versions, key=lambda v: version_key(v['version']), reverse=True)
        item['icon'] = 'icons/package.svg'
        latest = item['versions'][0]
        ipa = next((f for f in latest['files'] if f['type'] == 'ipa'), None)
        if ipa:
            item['icon'] = import_icon(ROOT / ipa['path'], app['id'])
        elif app['id'] == 'screen-recorder':
            # Existing source export already includes the application's normal PNG resources.
            src = archive / '录屏大师/0.4.0/源码快照/LegacyScreenRecorder/Resources/Icon76@2x.png'
            if src.exists():
                item['icon'] = 'icons/screen-recorder.png'
                write(item['icon'], src.read_bytes())
        catalog.append(item)
    write('catalog.json', json.dumps(dict(schema=1, base_url=BASE, apps=catalog), ensure_ascii=False, indent=2) + '\n')
    return catalog

def size_label(size):
    return ('%.1f MB' % (size / 1048576)) if size >= 1048576 else ('%.0f KB' % max(1, size / 1024))

def page(title, body, prefix='', current=''):
    nav = ''.join('<a%s href="%s%s">%s</a>' % (' class="active" aria-current="page"' if current == key else '', prefix, target, label)
                  for key, target, label in [('home','index.html','全部软件'),('archive','archive/index.html','版本归档'),('help','help/index.html','安装指南')])
    return '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="chanlx86 的旧 iOS 应用、移植版本与修复补丁。提供 IPA 下载、历史版本和 Cydia 软件源。">
<title>''' + ESC(title) + ''' · chanlx86</title><link rel="icon" href="''' + prefix + '''icons/package.svg" type="image/svg+xml">
<link rel="stylesheet" href="''' + prefix + '''style.css"></head><body>
<div class="topline"></div><div class="wrap"><header class="header"><a class="brand" href="''' + prefix + '''index.html"><span class="brand-icon">c<span>86</span></span><span class="brand-name">chanlx86<small>旧设备，也有新可能。</small></span></a><nav aria-label="主导航">''' + nav + '''<a href="''' + REPO + '''">GitHub ↗</a></nav></header>
<main>''' + body + '''</main><footer><span>chanlx86 · 为仍在使用的旧设备</span><a href="''' + prefix + '''help/index.html#about">关于与许可</a><a href="''' + REPO + '''">网站源码 ↗</a><p>兼容性以各软件说明为准。此处为个人发行存档，与 Apple 及各上游项目无隶属关系。</p></footer></div><script src="''' + prefix + '''site.js"></script></body></html>'''

def add_source():
    return '<a class="button primary" href="cydia://url/https://cydia.saurik.com/api/share#?source=' + BASE + '">添加到 Cydia</a>'

def app_card(app):
    latest = app['versions'][0]
    kinds = ' / '.join(f.upper() for f in ['ipa','deb'] if any(a['type'] == f for a in latest['files']))
    return '<article class="app-card" data-category="{category}" data-search="{search}"><a class="app-link" href="apps/{id}/"><img class="app-icon" src="{icon}" alt="" width="64" height="64"><span class="app-copy"><strong>{name}</strong><span class="app-version">{version} <span class="format">{kinds}</span></span></span><p>{tagline}</p><span class="compat">{os}</span><span class="card-arrow" aria-hidden="true">↗</span></a></article>'.format(
        category=app['category'], search=ESC(app['name']+' '+app['tagline']+' '+app['id']), id=app['id'], icon=app['icon'], name=ESC(app['name']), version=latest['version'], kinds=kinds, tagline=ESC(app['tagline']), os=ESC(app['os']))

def download_rows(version, prefix):
    rows = []
    for item in sorted(version['files'], key=lambda f: ['ipa','deb','source'].index(f['type'])):
        rows.append('<li><a class="download-link" href="{prefix}{path}" download><b>{label}</b><span>{size} <span aria-hidden="true">↓</span></span></a><div class="checksum">SHA-256 <code>{sha}</code></div></li>'.format(prefix=prefix, path=quote(item['path']), label=item['label'], size=size_label(item['size']), sha=item['sha256']))
    return '<ul class="downloads">' + ''.join(rows) + '</ul>'

def build_site(apps):
    totals = sum(len(a['versions']) for a in apps)
    cards = ''.join(app_card(a) for a in apps)
    body = '''<section class="hero"><div class="eyebrow">LEGACY iOS / 软件与修复</div><h1>旧设备的故事，<br><span>还可以继续。</span></h1><p>这里收藏我为老 iPhone、iPad 开发与适配的软件。<br class="wide-only">找到需要的工具，读一读说明，再给设备一点新用途。</p><div class="hero-links"><a class="button primary" href="#software">浏览软件 <span aria-hidden="true">↓</span></a><a class="text-link" href="help/">第一次安装？</a></div><div class="hero-mark" aria-hidden="true"><span class="chip-label">CHANLX86</span><span class="chip-main">86</span><span class="chip-sub">KEEP IT RUNNING</span></div></section>
<div class="catalog-layout"><section class="catalog-main" id="software"><div class="section-heading"><div><span class="eyebrow">THE COLLECTION</span><h2>应用与补丁 <span>''' + str(len(apps)) + '''</span></h2></div><label class="search"><span class="sr-only">搜索软件</span><input id="search" type="search" placeholder="搜索名称或用途…" autocomplete="off"></label></div><div class="filters" aria-label="筛选软件"><button class="selected" data-filter="all" aria-pressed="true">全部</button><button data-filter="apps" aria-pressed="false">应用</button><button data-filter="patches" aria-pressed="false">修复补丁</button></div><div class="app-grid">''' + cards + '''</div><p id="empty" class="empty" hidden>没有找到匹配的软件。试试其他关键词。</p><noscript><p>无需 JavaScript 也可以浏览和下载；搜索与筛选需要启用脚本。</p></noscript></section>
<aside class="sidebar"><section class="source-card"><span class="eyebrow">CYDIA REPOSITORY</span><h2>把软件源带到设备上</h2><p>在 Cydia 中安装这里提供的 DEB 应用与补丁，并接收后续版本。</p><code class="source-url">''' + BASE + '''</code>''' + add_source() + '''<p class="source-alternatives"><a href="sileo://source/''' + BASE + '''">Sileo</a> · <a href="zbra://sources/add/''' + BASE + '''">Zebra</a></p><p class="small">适用于传统 rootful 越狱。只有 IPA 的应用请从详情页下载。</p><a class="text-link" href="help/#cydia">查看添加方法 →</a></section><section class="aside-note"><span class="note-number">01 / 保留旧版本</span><h3>更新，也留一条退路。</h3><p>当前共归档 ''' + str(totals) + ''' 个版本。每份安装文件提供 SHA-256，历史版本在各软件详情页保留。</p><a href="archive/">打开版本归档 →</a></section><section class="aside-note"><span class="note-number">02 / 面向旧浏览器</span><h3>少一点负担，多一点可用。</h3><p>静态页面，无广告、无外部字体，不依赖现代前端框架。可直接用旧版 Safari 浏览。</p></section></aside></div>'''
    write('index.html', page('软件源与发行存档', body, current='home'))
    for app in apps:
        pre = '../../'
        latest = app['versions'][0]
        upstream = '<p>上游项目：<a href="{0}">{0}</a></p>'.format(ESC(app['upstream'])) if app.get('upstream') else ''
        deb = next((f for f in latest['files'] if f['type'] == 'deb'), None)
        install = ''
        if deb:
            install = '<div class="install-box"><h3>通过 Cydia 安装</h3><p>先添加本源，再搜索此软件。软件包标识：<code>' + ESC(deb['control']['Package']) + '</code></p>' + add_source() + '<p class="small">保留安装包原有依赖；需要的第三方依赖仍需从其可信来源获取。</p></div>'
        else:
            install = '<div class="install-box"><h3>通过 IPA 安装</h3><p>本版本不在 Cydia 的 DEB 列表中。下载 IPA 后，使用设备已有的兼容安装方式。</p><a href="../../help/#ipa">查看 IPA 安装说明 →</a></div>'
        history = ''.join('<section class="version-block"><h3>' + ESC(v['version']) + '</h3>' + download_rows(v, pre) + '</section>' for v in app['versions'][1:])
        if not history:
            history = '<p class="muted">暂无更早的公开版本。</p>'
        body = '<div class="breadcrumbs"><a href="../../">全部软件</a> / ' + ESC(app['name']) + '</div><section class="detail-title"><img class="detail-icon" src="../../' + app['icon'] + '" alt="" width="96" height="96"><div><span class="eyebrow">' + ('应用' if app['category']=='apps' else '修复补丁') + '</span><h1>' + ESC(app['name']) + '</h1><p>' + ESC(app['tagline']) + '</p><span class="badge">' + ESC(latest['version']) + '</span> <span class="badge">' + ESC(app['os']) + '</span></div></section><div class="detail-layout"><div class="detail-main"><section class="panel"><h2>关于这个版本</h2><p>' + ESC(app['description']) + '</p>' + upstream + '<ul class="notes">' + ''.join('<li>' + ESC(n) + '</li>' for n in app['notes']) + '</ul></section><section class="panel" id="download"><div class="section-heading"><h2>下载 <span>' + ESC(latest['version']) + '</span></h2></div>' + download_rows(latest, pre) + '<p class="small">安装包面向已有越狱安装能力的设备。下载完成不等于所有设备都可直接安装。</p></section><section class="panel" id="history"><h2>历史版本</h2>' + history + '</section></div><aside class="detail-side">' + install + '<section class="aside-note"><h3>安装前请留意</h3><p>阅读系统和原应用版本要求。更新前备份需要保留的数据；出现问题时记录版本及崩溃日志。</p><a href="../../help/">安装与常见问题 →</a></section></aside></div>'
        write('apps/' + app['id'] + '/index.html', page(app['name'], body, pre))
    # Previously linked, unselected packages should not keep stale download links.
    for app in APPS:
        if app['id'] not in {a['id'] for a in apps}:
            write('apps/' + app['id'] + '/index.html', page(app['name'], '<section class="page-intro"><span class="eyebrow">发行状态</span><h1>此补丁暂未公开下载。</h1><p>当前可用的软件与版本以首页目录为准。</p><a class="button primary" href="../../">浏览当前软件</a></section>', '../../'))
    archive_rows = ''.join('<tr><td><a href="../apps/{id}/#history">{name}</a></td><td>{version}</td><td>{kinds}</td></tr>'.format(id=a['id'], name=ESC(a['name']), version=ESC(v['version']), kinds=' · '.join('<a href="../' + quote(f['path']) + '">' + f['type'].upper() + '</a>' for f in v['files'])) for a in apps for v in a['versions'])
    write('archive/index.html', page('版本归档', '<div class="page-intro"><span class="eyebrow">RELEASE ARCHIVE</span><h1>每次更新，都有来处。</h1><p>按软件保留公开版本。优先使用各详情页的当前版本，回退前请先备份数据。</p></div><section class="panel table-panel"><table><thead><tr><th>软件</th><th>版本</th><th>文件下载</th></tr></thead><tbody>' + archive_rows + '</tbody></table></section>', '../', 'archive'))
    help_body = '''<div class="page-intro"><span class="eyebrow">GETTING STARTED</span><h1>先读说明，再安装。</h1><p>不同的软件，可能有不同的系统、架构和越狱要求。</p></div><div class="reading"><section class="panel" id="cydia"><h2>01 / 添加 Cydia 软件源</h2><ol><li>在已越狱设备的 Safari 打开本站，点击“添加到 Cydia”。</li><li>或者在 Cydia → 软件源 → 编辑 → 添加，输入 <code>''' + BASE + '''</code>。</li><li>刷新后搜索需要的软件，确认依赖和版本，再安装。</li><li>插件类补丁安装后，彻底退出对应应用再打开；仅在安装提示要求时重新载入桌面。</li></ol>''' + add_source() + '''<p>本源的 DEB 面向传统 rootful 环境，并非现代 rootless 越狱包。Package 内的系统依赖约束不代表所有对应系统都经过实测，仍以详情说明为准。</p><p>本源目前通过 GitHub Pages 的 HTTPS 提供，未发布独立的 GPG 签名。Cydia 可能提示来源未签名。若旧系统遇到 TLS 连接问题，先核对日期和系统证书环境；不要关闭全局证书校验。</p></section><section class="panel" id="ipa"><h2>02 / 下载与安装 IPA</h2><p>IPA 下载不会自动完成安装。本页包主要采用本地 ad hoc／伪签名，适用于已有兼容安装环境的越狱设备，并非 App Store 或 Apple 正式分发包。</p><p>已配置 AppSync 与兼容安装器的设备，可用 Filza 等工具打开下载的 IPA；是否能成功安装还取决于包、系统与安装器版本。没有此环境时，需使用自己合法可用的签名方式。</p><p>IPA 容器安装和 DEB 系统目录安装可能使用不同数据位置。不要为同一个应用同时混装两种副本，也不要未经备份直接卸载旧版。</p></section><section class="panel" id="verify"><h2>03 / 校验与回退</h2><p>每个文件下方提供 SHA-256。Mac 可运行 <code>shasum -a 256 文件名</code>，Windows PowerShell 可运行 <code>Get-FileHash 文件名 -Algorithm SHA256</code>。它用于发现文件损坏，不等同于开发者身份认证。</p><p>保留旧包与存档。旧版程序未必能读取新版数据，不能只安装旧包就保证无损回退。历史文件可以在“版本归档”和软件详情页找到。</p></section><section class="panel" id="about"><h2>04 / 关于与许可</h2><p>这里是 chanlx86 的个人发行存档，收录自研软件、开放源码项目的移植修复构建及独立兼容补丁。应用和补丁的权利、许可及第三方组件以各自源码和包内声明为准。网站根目录的 MIT 许可不替代这些软件各自的许可。</p><p>Troubadour 上游为 <a href="https://github.com/Computershik73/Troubadour">Computershik73/Troubadour</a>；LocalSend 适配版基于 <a href="https://github.com/theanazerka/unlocalsend">theanazerka/unlocalsend</a>。对应源码 ZIP 随相关版本提供。页面层级参考 <a href="https://github.com/Computershik73/repo">Computershik73/repo</a>，页面样式与生成工具独立编写。</p><p>补丁不包含所针对的第三方原应用，不恢复停服内容，也不替代正常账号授权。本站不收集访问者账号，不接入统计或广告脚本。</p><p>问题反馈：<a href="''' + REPO + '''/issues">GitHub Issues</a>。请提供软件版本、设备、系统和复现步骤；不要公开密码、令牌或未经整理的私人日志。</p></section></div>'''
    write('help/index.html', page('安装指南', help_body, '../', 'help'))
    write('404.html', page('页面未找到', '<section class="page-intro"><span class="eyebrow">404</span><h1>这个页面暂时找不到。</h1><p>文件可能已调整位置，请回到软件目录查找。</p><a class="button primary" href="/">返回首页</a></section>', '/'))

def build_apt(apps):
    stanzas = []
    for app in apps:
        for item in app['versions'][0]['files']:
            if item['type'] != 'deb':
                continue
            c = fields(control_from_deb(ROOT / item['path']))
            # Keep real package identities/dependencies. Only repository-specific fields are added.
            b = (ROOT / item['path']).read_bytes()
            c.update(Filename=item['path'], Size=str(len(b)), MD5sum=digest(b, 'md5'), SHA1=digest(b, 'sha1'), SHA256=digest(b), Depiction=BASE+'apps/'+app['id']+'/', Icon=BASE+(app['icon'] if app['icon'].endswith('.png') else 'CydiaIcon.png'))
            stanzas.append('\n'.join(k + ': ' + v for k, v in c.items()))
    packages = ('\n\n'.join(stanzas) + '\n\n').encode('utf-8')
    write('Packages', packages)
    write('Packages.gz', gzip.compress(packages, mtime=0))
    write('Packages.bz2', bz2.compress(packages))
    write('Packages.xz', lzma.compress(packages))
    release = 'Origin: chanlx86\nLabel: chanlx86\nSuite: stable\nVersion: 1.0\nCodename: stable\nArchitectures: iphoneos-arm\nComponents: main\nDescription: Legacy iOS applications and compatibility patches\n'
    for key, alg in [('MD5Sum','md5'),('SHA1','sha1'),('SHA256','sha256')]:
        release += key + ':\n'
        for name in ['Packages','Packages.gz','Packages.bz2','Packages.xz']:
            b = (ROOT / name).read_bytes()
            release += ' {} {} {}\n'.format(digest(b, alg), len(b), name)
    write('Release', release)
    if not (ROOT / 'CydiaIcon.png').exists():
        # Generated elsewhere from the same site vector; use an existing published app icon as fallback.
        icon = next(a['icon'] for a in apps if a['id'] == 'j2me')
        shutil.copyfile(ROOT / icon, ROOT / 'CydiaIcon.png')

def check(apps):
    count, total = 0, 0
    for a in apps:
        for v in a['versions']:
            for f in v['files']:
                b = (ROOT / f['path']).read_bytes()
                assert digest(b) == f['sha256'], f['path']
                assert len(b) == f['size'], f['path']
                assert len(b) < 25 * 1024 * 1024, 'Use a GitHub Release asset for this large file'
                count += 1
                total += len(b)
    write('SHA256SUMS', ''.join(f['sha256']+'  '+f['path']+'\n' for a in apps for v in a['versions'] for f in v['files']))
    print('{} apps / {} versions / {} artifacts / {:.1f} MiB'.format(len(apps), sum(len(a['versions']) for a in apps), count, total/1048576))
    print('Artifact hashes verified. Generated HTML and Cydia indexes.')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import-archive', type=Path)
    args = parser.parse_args()
    if args.import_archive:
        apps = import_archive(args.import_archive.expanduser().resolve())
    else:
        apps = json.loads((ROOT/'catalog.json').read_text())['apps']
    build_site(apps)
    build_apt(apps)
    check(apps)
    write('.nojekyll', '')

if __name__ == '__main__':
    main()
