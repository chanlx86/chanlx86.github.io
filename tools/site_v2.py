#!/usr/bin/env python3
"""Build /repo/, OTA manifests, compact Cydia depictions and legacy redirects."""
import bz2
import copy
import gzip
import hashlib
import html
import io
import json
import lzma
import plistlib
import re
import tarfile
import zipfile
from pathlib import Path
from urllib.parse import quote
import build as release

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = 'https://chanlx86.github.io/'
BASE = ORIGIN + 'repo/'
GITHUB = 'https://github.com/chanlx86/chanlx86.github.io'
AUTHOR = 'chanlx86'
ESC = html.escape
REV = '20261030-nico2'

def put(path, value):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    data = value.encode('utf-8') if isinstance(value, str) else value
    if not p.exists() or p.read_bytes() != data:
        p.write_bytes(data)

def web(path):
    return ORIGIN + quote(path, safe='/')

def url_for(item):
    return web(item['path'])

def package_link(item):
    return 'cydia://package/' + quote(item['control']['Package'], safe='.')

def ar_members(data):
    assert data[:8] == b'!<arch>\n'
    pos = 8
    while pos < len(data):
        header = data[pos:pos+60]
        assert len(header) == 60 and header[-2:] == b'`\n'
        size = int(header[48:58])
        payload = data[pos+60:pos+60+size]
        assert len(payload) == size
        yield header[:16].decode().strip().rstrip('/'), payload
        pos += 60 + size + size % 2

def ar_write(members):
    out = bytearray(b'!<arch>\n')
    for name, data in members:
        header = ('{:<16}{:<12}{:<6}{:<6}{:<8}{:<10}`\n'.format(name+'/', 0, 0, 0, '100644', len(data))).encode()
        assert len(header) == 60
        out.extend(header); out.extend(data)
        if len(data) % 2:
            out.extend(b'\n')
    return bytes(out)

def rebrand_deb(item, app):
    source = ROOT / item['path']
    control = release.fields(release.control_from_deb(source))
    if control.get('Author') == AUTHOR and control.get('Maintainer') == AUTHOR and control.get('Depiction') == BASE+'cydia/'+app['id']+'/':
        return
    original = list(ar_members(source.read_bytes()))
    control['Author'] = AUTHOR
    control['Maintainer'] = AUTHOR
    control['Version'] += '-1'
    control['Homepage'] = BASE
    control['Depiction'] = BASE+'cydia/'+app['id']+'/'
    control['Icon'] = BASE+(app['icon'] if app['icon'].endswith('.png') else 'CydiaIcon.png')
    control_bytes = ('\n'.join(k+': '+v for k, v in control.items())+'\n').encode()
    updated = []
    for name, data in original:
        if name.startswith('control.tar'):
            output = io.BytesIO()
            with tarfile.open(fileobj=io.BytesIO(data), mode='r:*') as old:
                with tarfile.open(fileobj=output, mode='w', format=tarfile.GNU_FORMAT) as new:
                    found = False
                    for member in old:
                        info = copy.copy(member)
                        content = old.extractfile(member).read() if member.isfile() else None
                        if member.name.lstrip('./') == 'control':
                            content = control_bytes; info.size = len(content); found = True
                        new.addfile(info, io.BytesIO(content) if content is not None else None)
                    assert found
            updated.append(('control.tar.gz', gzip.compress(output.getvalue(), mtime=0)))
        else:
            updated.append((name, data))
    data = ar_write(updated)
    path = 'repo/deb/{Package}_{Version}_{Architecture}.deb'.format(**control)
    put(path, data)
    # Code and package scripts are preserved, only the control file is rewritten.
    assert [m for m in original if not m[0].startswith('control.tar')] == [m for m in ar_members(data) if not m[0].startswith('control.tar')]
    item.update(path=path, size=len(data), sha256=release.digest(data), control=control)

def manifest(app, version, item):
    with zipfile.ZipFile(ROOT/item['path']) as z:
        info_name = next(n for n in z.namelist() if n.startswith('Payload/') and n.endswith('.app/Info.plist') and n.count('/') == 2)
        info = plistlib.loads(z.read(info_name))
    entry = {'assets':[{'kind':'software-package','url':url_for(item)}], 'metadata': {
        'bundle-identifier':info['CFBundleIdentifier'], 'bundle-version':str(info['CFBundleVersion']),
        'kind':'software', 'title':app['name']}}
    path = 'repo/manifests/{}/{}.plist'.format(app['id'], version['version'])
    put(path, plistlib.dumps({'items':[entry]}, fmt=plistlib.FMT_XML))
    item['manifest'] = path
    item['install_url'] = 'itms-services://?action=download-manifest&url='+quote(web(path), safe='')

def get_file(app, kind):
    return next((f for f in app['versions'][0]['files'] if f['type'] == kind), None)

def action(app, prefix='', label=None):
    ipa, deb = get_file(app, 'ipa'), get_file(app, 'deb')
    if ipa:
        return '<a class="get-button ota" href="{}" data-help="{}apps/{}/#install">{}</a>'.format(ESC(ipa['install_url']),prefix,app['id'],label or '安装')
    if deb:
        return '<a class="get-button cydia-action" href="{}">{}</a>'.format(package_link(deb),label or 'Cydia')
    return ''

def shell(title, content, prefix='', current='home', compact=False):
    links = ''.join('<a{} href="{}{}">{}</a>'.format(' class="active" aria-current="page"' if current==key else '', prefix, target, text) for key,target,text in [('home','index.html','软件'),('archive','archive/','归档'),('help','help/','说明')])
    body_class = 'compact' if compact else 'website'
    return '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="format-detection" content="telephone=no"><meta name="theme-color" content="#f8f8f8"><title>'''+ESC(title)+''' · chanlx86</title><link rel="icon" type="image/png" href="'''+prefix+'''assets/nico-small.png"><link rel="apple-touch-icon" href="'''+prefix+'''assets/nico-avatar.png"><link rel="stylesheet" href="'''+prefix+'''style.css?v='''+REV+'''"></head><body class="'''+body_class+'''"><header class="topbar"><div class="bar-inner"><a class="brand" href="'''+prefix+'''index.html"><img src="'''+prefix+'''assets/nico-small.png" alt="" width="34" height="34"><strong>chanlx86</strong><span>软件源</span></a><nav aria-label="主导航">'''+links+'''<a href="'''+GITHUB+'''">GitHub ↗</a></nav></div></header><main class="page">'''+content+'''</main><footer class="footer">chanlx86 · 旧 iOS 应用与兼容修复<br><a href="'''+prefix+'''help/#about">关于与来源</a> · <a href="'''+GITHUB+'''/issues">问题反馈</a><p>头像角色：矢泽妮可 / Love Live!，非官方同人主题。各应用与上游项目分别保留其许可。</p></footer><script src="'''+prefix+'''site.js?v='''+REV+'''"></script></body></html>'''

def source_buttons():
    return '<a class="button primary" href="cydia://url/https://cydia.saurik.com/api/share#?source='+BASE+'">添加到 Cydia</a><a class="button plain" href="sileo://source/'+BASE+'">Sileo</a><a class="button plain" href="zbra://sources/add/'+BASE+'">Zebra</a>'

def row(app):
    v = app['versions'][0]
    kind = 'IPA' if get_file(app,'ipa') else 'DEB'
    return '<article class="app-row" data-category="{category}" data-search="{search}"><a class="row-main" href="apps/{id}/"><img class="app-icon" src="{icon}" alt="" width="54" height="54"><span class="row-copy"><strong>{name}</strong><span class="row-sub">{tagline}</span><span class="row-meta">{version} · {os} · {kind}</span></span></a><div class="row-action">{action}</div></article>'.format(category=app['category'],search=ESC(app['name']+' '+app['id']+' '+app['tagline']),id=app['id'],icon=app['icon'],name=ESC(app['name']),tagline=ESC(app['tagline']),version=ESC(v['version']),os=ESC(app['os']),kind=kind,action=action(app))

def download_list(version):
    rows=[]
    for f in sorted(version['files'], key=lambda f:['ipa','deb','source'].index(f['type'])):
        install = '<a class="inline-install ota" href="{}">直接安装</a>'.format(ESC(f['install_url'])) if f.get('install_url') else ''
        rows.append('<li><a href="{}" class="file-link" download><strong>{}</strong><span>{} ↓</span></a>{}<p class="hash">SHA-256 <code>{}</code></p></li>'.format(url_for(f),f['label'],release.size_label(f['size']),install,f['sha256']))
    return '<ul class="downloads">'+''.join(rows)+'</ul>'

def build_pages(apps):
    count_versions=sum(len(a['versions']) for a in apps)
    featured=[next(a for a in apps if a['id']==i) for i in ['j2me','archive-browser','screen-recorder']]
    featured_html=''.join('<a class="feature-item" href="apps/{}/"><img src="{}" alt="" width="38" height="38"><span><strong>{}</strong><small>{}</small></span><b>›</b></a>'.format(a['id'],a['icon'],ESC(a['name']),ESC(a['versions'][0]['version'])) for a in featured)
    groups=''.join('<section class="software-section" data-section="{}"><h2 class="section-label">{}</h2><div class="group app-list">{}</div></section>'.format(cat,title,''.join(row(a) for a in apps if a['category']==cat)) for cat,title in [('apps','应用'),('patches','兼容修复补丁')])
    content='''<section class="profile group"><img class="avatar" src="assets/nico-avatar.png" alt="妮可头像，白色背景" width="90" height="90"><div class="profile-copy"><span class="eyebrow">HELLO, LEGACY iOS</span><h1>chanlx86 软件源<span class="ribbon" aria-hidden="true">♥</span></h1><p>把喜欢的旧设备，继续用下去。</p><span class="profile-meta">应用 · 移植 · 修复补丁</span></div><a class="profile-link" href="help/#about">关于本站 ›</a></section><div class="columns"><div class="main-column"><section class="featured group">'''+featured_html+'''</section><div id="software" class="search-tools"><label class="search"><span class="sr-only">搜索软件</span><input id="search" type="search" placeholder="搜索应用或补丁" autocomplete="off"></label><div class="segments" aria-label="筛选软件"><button class="selected" data-filter="all" aria-pressed="true">全部</button><button data-filter="apps" aria-pressed="false">应用</button><button data-filter="patches" aria-pressed="false">补丁</button></div></div>'''+groups+'''<p id="empty" class="empty" hidden>没有匹配的软件，请试试其他关键词。</p><noscript><p class="small">未启用脚本时仍可浏览和下载全部软件。</p></noscript></div><aside class="side-column"><h2 class="section-label">软件源</h2><section class="group source-box"><div class="source-title"><img src="assets/nico-small.png" alt="" width="42" height="42"><span><strong>chanlx86</strong><small>传统 rootful 越狱</small></span></div><code class="source-url">'''+BASE+'''</code><div class="source-actions">'''+source_buttons()+'''</div><p class="small">DEB 应用与插件可通过 Cydia 安装、更新。</p></section><h2 class="section-label">安装提示</h2><section class="group note-box"><h3>点一下，安装最新版</h3><p>IPA 的“安装”使用系统 OTA 入口，需要设备已有可用签名或兼容的 AppSync 环境。</p><p>没有出现安装提示？可进入详情页下载 IPA，再用 Filza 等兼容工具打开。</p><a href="help/#ipa">查看完整安装说明 ›</a></section><section class="group note-box archive-note"><strong>'''+str(len(apps))+''' 款软件 · '''+str(count_versions)+''' 个版本</strong><p>历史文件与源码按版本保留。</p><a href="archive/">浏览发行归档 ›</a></section></aside></div>'''
    put('repo/index.html',shell('软件源',content))
    for a in apps:
        v=a['versions'][0];p='../../';ipa=get_file(a,'ipa');deb=get_file(a,'deb')
        source='<p>上游项目：<a href="{0}">{0}</a></p>'.format(ESC(a['upstream'])) if a.get('upstream') else ''
        revision='<li><span>源修订</span><strong>'+ESC(deb['control']['Version'])+'</strong></li>' if deb else ''
        install=action(a,p,'直接安装' if ipa else '在 Cydia 中打开')
        fallback='<a class="button plain" href="'+url_for(ipa or deb)+'" download>下载 '+('IPA' if ipa else 'DEB')+'</a>' if ipa or deb else ''
        install_note='通过 HTTPS 清单唤起系统安装；需可用签名或兼容的 AppSync 环境。不能据此在普通未越狱设备上免签安装。' if ipa else '先添加 chanlx86 软件源，再打开此软件包；MobileSubstrate 等依赖请从其可信来源获取。'
        history=''.join('<section class="history-version"><h3>'+ESC(x['version'])+'</h3>'+download_list(x)+'</section>' for x in a['versions'][1:]) or '<p class="small pad">暂无更早的公开版本。</p>'
        content='<div class="back"><a href="../../">‹ 全部软件</a></div><section class="group app-heading"><img src="../../'+a['icon']+'" alt="" width="78" height="78"><div><h1>'+ESC(a['name'])+'</h1><p>'+ESC(a['tagline'])+'</p><span class="small">'+ESC(v['version'])+' · 作者 / 适配维护：'+AUTHOR+'</span></div></section><section class="group install-panel" id="install"><div class="install-buttons">'+install+fallback+'</div><p class="small">'+install_note+'</p>'+('' if ipa else '<a href="../../#software">返回首页添加软件源 ›</a>')+'</section><h2 class="section-label">版本信息</h2><ul class="group info-table"><li><span>版本</span><strong>'+ESC(v['version'])+'</strong></li><li><span>作者 / 维护</span><a href="https://github.com/chanlx86">chanlx86</a></li><li><span>兼容性</span><strong>'+ESC(a['os'])+'</strong></li>'+revision+'</ul><h2 class="section-label">说明</h2><section class="group prose"><p>'+ESC(a['description'])+'</p><ul>'+''.join('<li>'+ESC(n)+'</li>' for n in a['notes'])+'</ul>'+source+'</section><h2 class="section-label" id="download">下载与校验</h2><section class="group">'+download_list(v)+'</section><h2 class="section-label" id="history">历史版本</h2><section class="group history">'+history+'</section>'
        put('repo/apps/'+a['id']+'/index.html',shell(a['name'],content,p))
        depiction='<section class="mini-brand"><img src="../../assets/nico-small.png" alt="" width="36" height="36"><span>chanlx86</span></section><section class="group mini-heading"><img src="../../'+a['icon']+'" alt="" width="48" height="48"><h1>'+ESC(a['name'])+'</h1><p>'+ESC(v['version'])+'</p></section><ul class="group info-table"><li><span>作者</span><strong>chanlx86</strong></li><li><span>兼容性</span><strong>'+ESC(a['os'])+'</strong></li>'+revision+'</ul><section class="group prose"><p>'+ESC(a['description'])+'</p><ul>'+''.join('<li>'+ESC(n)+'</li>' for n in a['notes'])+'</ul></section><p class="mini-link"><a href="../../apps/'+a['id']+'/">完整说明与下载 ›</a></p>'
        put('repo/cydia/'+a['id']+'/index.html',shell(a['name'],depiction,p,compact=True))
    for old in release.APPS:
        if old['id'] not in {a['id'] for a in apps}:
            put('repo/apps/'+old['id']+'/index.html',shell(old['name'],'<section class="group prose"><h1>暂未公开下载</h1><a href="../../">浏览当前软件 ›</a></section>','../../'))
    rows=''.join('<tr><td><a href="../apps/{}/#history">{}</a></td><td>{}</td><td>{}</td></tr>'.format(a['id'],ESC(a['name']),ESC(v['version']),' · '.join('<a href="'+url_for(f)+'">'+f['type'].upper()+'</a>' for f in v['files'])) for a in apps for v in a['versions'])
    put('repo/archive/index.html',shell('版本归档','<h1 class="page-title">版本归档</h1><p class="small">历史版本可能只保留源码，以实际文件为准。</p><section class="group table-wrap"><table><thead><tr><th>软件</th><th>版本</th><th>下载</th></tr></thead><tbody>'+rows+'</tbody></table></section>','../','archive'))
    help_body='''<h1 class="page-title">安装与使用说明</h1><section class="group prose" id="ipa"><h2>IPA 直接安装</h2><ol><li>在 iPhone / iPad 的 Safari 打开软件详情。</li><li>确认系统与设备要求，点击“直接安装”，再按系统提示操作。</li><li>此入口需要可用签名或兼容的 AppSync 越狱环境；OTA 链接本身不会解除系统签名限制。</li><li>没有提示或无法安装时，选择“下载 IPA”，用 Filza、iFile 或兼容的 IPA 安装器打开。</li></ol><p>使用 HTTPS 清单与系统 itms-services 入口。清单、下载链接可访问不等于每台设备都能成功安装。桌面电脑可以下载文件，但不能直接安装 iOS 应用。</p><p>更新前备份存档，保持原 Bundle ID。不要同时混装同一应用的 IPA 与 DEB 副本。</p></section><section class="group prose" id="cydia"><h2>Cydia 软件源</h2><code class="source-url">'''+BASE+'''</code><p>在 Cydia → 软件源 → 编辑 → 添加中输入上面的地址，刷新后搜索软件。</p>'''+source_buttons()+'''<p>本源为传统 rootful 软件源；iOS 与架构范围以软件包及详情说明为准。所需第三方依赖需从其可信来源获取。补丁安装或卸载后，彻底退出目标 App 再打开。</p><p>旧的根地址仍提供兼容索引。新用户请使用 /repo/ 地址，已添加旧地址的用户无需重复添加两个源。</p></section><section class="group prose"><h2>下载与校验</h2><p>下载列表提供 SHA-256。Mac 使用 <code>shasum -a 256 文件名</code>，Windows PowerShell 使用 <code>Get-FileHash 文件名 -Algorithm SHA256</code>。回退前先备份数据，旧版未必能读取新版存档。</p></section><section class="group prose" id="about"><h2>关于本站</h2><p>维护与发布：<a href="https://github.com/chanlx86">chanlx86</a>。网页与 Cydia 元信息统一使用此标识；移植项目的原作者、开放源码许可与第三方贡献仍在对应源码和详情中保留。</p><p>Troubadour 基于 <a href="https://github.com/Computershik73/Troubadour">Computershik73/Troubadour</a>；LocalSend 适配版基于 <a href="https://github.com/theanazerka/unlocalsend">theanazerka/unlocalsend</a>。根目录 MIT 不替代应用各自许可。</p><p>头像采用用户提供的 Love Live! 矢泽妮可插画制作白底版本，角色及原插画权利归其权利人，本页面不是官方产品。未接入广告或访问统计。</p><p>问题反馈请提供版本、设备、系统与复现步骤，不要公开账号、密码或令牌。</p></section>'''
    put('repo/help/index.html',shell('安装说明',help_body,'../','help'))

def build_indexes(apps):
    stanzas=[]
    for a in apps:
        f=get_file(a,'deb')
        if not f:continue
        c=dict(f['control']);b=(ROOT/f['path']).read_bytes()
        c.update(Filename='deb/'+Path(f['path']).name,Size=str(len(b)),MD5sum=release.digest(b,'md5'),SHA1=release.digest(b,'sha1'),SHA256=release.digest(b))
        stanzas.append(c)
    def indexes(prefix,legacy=False):
        entries=[]
        for control in stanzas:
            c=dict(control)
            if legacy:c['Filename']='repo/'+c['Filename']
            entries.append('\n'.join(k+': '+v for k,v in c.items()))
        raw=('\n\n'.join(entries)+'\n\n').encode()
        payloads={'Packages':raw,'Packages.gz':gzip.compress(raw,mtime=0),'Packages.bz2':bz2.compress(raw),'Packages.xz':lzma.compress(raw)}
        rel='Origin: chanlx86\nLabel: chanlx86\nSuite: stable\nVersion: 2.0\nCodename: stable\nArchitectures: iphoneos-arm\nComponents: main\nDescription: Applications and fixes maintained by chanlx86\nIcon: '+BASE+'CydiaIcon.png\n'
        for key,alg in [('MD5Sum','md5'),('SHA1','sha1'),('SHA256','sha256')]:
            rel+=key+':\n'+''.join(' {} {} {}\n'.format(release.digest(b,alg),len(b),name) for name,b in payloads.items())
        for name,b in payloads.items():put(prefix+name,b)
        put(prefix+'Release',rel)
    indexes('repo/');indexes('',True)

def redirect(path,target):
    put(path,'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0;url='+ESC(target)+'"><link rel="canonical" href="'+ESC(target)+'"><title>软件源已迁移 · chanlx86</title></head><body><p>软件源已迁移至 <a href="'+ESC(target)+'">'+ESC(target)+'</a>。</p><script>location.replace('+json.dumps(target)+'+location.search+location.hash);</script></body></html>')

def update_readme(apps):
    lines=['# chanlx86 · 旧 iOS 软件与修复补丁','','**[进入软件源]('+BASE+') · [安装说明]('+BASE+'help/) · [版本归档]('+BASE+'archive/)**','','面向旧 iPhone、iPad 的应用、移植构建与兼容补丁。维护作者：**chanlx86**。','','## 应用与补丁','','| 软件 | 版本 | 系统要求 | 安装 / 下载 |','| --- | --- | --- | --- |']
    for a in apps:
        fs=a['versions'][0]['files'];links=[]
        if get_file(a,'ipa'):links.append('[直接安装]('+BASE+'apps/'+a['id']+'/#install)')
        if get_file(a,'deb'):links.append('[Cydia]('+BASE+'apps/'+a['id']+'/#install)')
        for f in sorted(fs,key=lambda f:['ipa','deb','source'].index(f['type'])):
            links.append('['+{'ipa':'IPA','deb':'DEB','source':'源码'}[f['type']]+']('+url_for(f)+')')
        lines.append('| ['+a['name']+']('+BASE+'apps/'+a['id']+'/) | '+a['versions'][0]['version']+' | '+a['os']+' | '+' · '.join(links)+' |')
    lines+=['','## Cydia 软件源','','```text',BASE,'```','','在已越狱设备的 Safari 打开网站，可点击“添加到 Cydia”。传统 rootful 软件源，支持范围以各软件说明为准。旧根地址仍保留兼容索引，无需同时添加两个源。','','## 安装前','','- IPA 的“直接安装”通过系统 OTA 入口，需要可用签名或兼容的 AppSync 环境；不代表可以在普通未越狱设备免签安装。','- 补丁需要指定版本的原应用。更新前备份数据，不要混装同一个应用的 IPA 和 DEB 副本。','- 各下载页面提供 SHA-256，历史版本可能仅有源码。','','## 来源与反馈','','维护和发布为 chanlx86。Troubadour 基于 [Computershik73/Troubadour](https://github.com/Computershik73/Troubadour)，LocalSend 适配版基于 [theanazerka/unlocalsend](https://github.com/theanazerka/unlocalsend)。原作者、第三方贡献及各自许可保留在对应源码与说明中。','','[问题反馈]('+GITHUB+'/issues) · [维护文档](docs/maintenance.md)']
    put('README.md','\n'.join(lines)+'\n')

def main():
    catalog=json.loads((ROOT/'catalog.json').read_text());apps=catalog['apps']
    for a in apps:
        a['author']=AUTHOR
        for v in a['versions']:
            for f in v['files']:
                if f['type']=='deb':rebrand_deb(f,a)
                if f['type']=='ipa':manifest(a,v,f)
                f['download_url']=url_for(f)
    catalog.update(schema=2,base_url=BASE,asset_origin=ORIGIN)
    put('catalog.json',json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
    put('repo/catalog.json',json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
    build_pages(apps);build_indexes(apps);update_readme(apps)
    for old in release.APPS:redirect('apps/'+old['id']+'/index.html',BASE+'apps/'+old['id']+'/')
    redirect('archive/index.html',BASE+'archive/');redirect('help/index.html',BASE+'help/')
    redirect('index.html',BASE)
    put('repo/404.html',shell('未找到页面','<section class="group prose"><h1>页面未找到</h1><a href="/repo/">返回软件源 ›</a></section>','/repo/'))
    put('404.html',(ROOT/'repo/404.html').read_bytes())
    sums=''.join(f['sha256']+'  '+f['path']+'\n' for a in apps for v in a['versions'] for f in v['files'])
    put('SHA256SUMS',sums);put('repo/SHA256SUMS',sums)
    for a in apps:
        for v in a['versions']:
            for f in v['files']:
                b=(ROOT/f['path']).read_bytes();assert release.digest(b)==f['sha256'];assert len(b)==f['size']
    put('.nojekyll','');put('repo/.nojekyll','')
    print('Built /repo/:',len(apps),'apps; 6 OTA manifests; 5 revised DEBs; legacy source compatibility.')

if __name__=='__main__':main()
