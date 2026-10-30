# chanlx86 · 旧 iOS 软件与修复补丁

**[进入软件源](https://chanlx86.github.io/repo/) · [安装说明](https://chanlx86.github.io/repo/help/) · [版本归档](https://chanlx86.github.io/repo/archive/)**

面向旧 iPhone、iPad 的应用、移植构建与兼容补丁。维护作者：**chanlx86**。

## 应用与补丁

| 软件 | 版本 | 系统要求 | 安装 / 下载 |
| --- | --- | --- | --- |
| [J2ME模拟器](https://chanlx86.github.io/repo/apps/j2me/) | build65 | iOS 6+ | [直接安装](https://chanlx86.github.io/repo/apps/j2me/#install) · [IPA](https://chanlx86.github.io/ipa/j2me/build65/j2me.ipa) |
| [存档浏览器](https://chanlx86.github.io/repo/apps/archive-browser/) | 0.9.0 | iOS 9+ | [直接安装](https://chanlx86.github.io/repo/apps/archive-browser/#install) · [IPA](https://chanlx86.github.io/ipa/archive-browser/0.9.0/archive-browser.ipa) · [源码](https://chanlx86.github.io/source/archive-browser/0.9.0/source.zip) |
| [录屏大师](https://chanlx86.github.io/repo/apps/screen-recorder/) | 0.6.1 | iOS 9.x · 32 位 | [Cydia](https://chanlx86.github.io/repo/apps/screen-recorder/#install) · [DEB](https://chanlx86.github.io/repo/deb/local.legacy.screenrecorder_0.6.1-1_iphoneos-arm.deb) · [源码](https://chanlx86.github.io/source/screen-recorder/0.6.1/source.zip) |
| [LocalSend](https://chanlx86.github.io/repo/apps/localsend/) | 0.7.0 | iOS 9+ · ARMv7 | [直接安装](https://chanlx86.github.io/repo/apps/localsend/#install) · [IPA](https://chanlx86.github.io/ipa/localsend/0.7.0/localsend.ipa) · [源码](https://chanlx86.github.io/source/localsend/0.7.0/source.zip) |
| [Troubadour](https://chanlx86.github.io/repo/apps/troubadour/) | 1.6.1 | ARMv7 iOS 5.1+ / ARM64 iOS 7+ | [直接安装](https://chanlx86.github.io/repo/apps/troubadour/#install) · [IPA](https://chanlx86.github.io/ipa/troubadour/1.6.1/troubadour.ipa) · [源码](https://chanlx86.github.io/source/troubadour/1.6.1/source.zip) |
| [维基文库](https://chanlx86.github.io/repo/apps/wikisource/) | 0.2.0 | iOS 9+ | [直接安装](https://chanlx86.github.io/repo/apps/wikisource/#install) · [IPA](https://chanlx86.github.io/ipa/wikisource/0.2.0/wikisource.ipa) · [源码](https://chanlx86.github.io/source/wikisource/0.2.0/source.zip) |
| [Onegram 登录修复](https://chanlx86.github.io/repo/apps/onegram-login-fix/) | 0.2.0 | iOS 9+ | [Cydia](https://chanlx86.github.io/repo/apps/onegram-login-fix/#install) · [DEB](https://chanlx86.github.io/repo/deb/local.onegram.loginfix_0.2.0-1_iphoneos-arm.deb) · [源码](https://chanlx86.github.io/source/onegram-login-fix/0.2.0/source.zip) |
| [Wikipedia 正文兼容](https://chanlx86.github.io/repo/apps/wikipedia-compat/) | 0.1.0 | iOS 9+ | [Cydia](https://chanlx86.github.io/repo/apps/wikipedia-compat/#install) · [DEB](https://chanlx86.github.io/repo/deb/local.wikipedia.mobileview.compat_0.1.0-1_iphoneos-arm.deb) · [源码](https://chanlx86.github.io/source/wikipedia-compat/0.1.0/source.zip) |
| [爱丽丝快跑启动修复](https://chanlx86.github.io/repo/apps/alice-launch-fix/) | 1.0.0 | ARMv7 · rootful 越狱 | [Cydia](https://chanlx86.github.io/repo/apps/alice-launch-fix/#install) · [DEB](https://chanlx86.github.io/repo/deb/local.luoxian.aliceresponseguard_1.0.0-1_iphoneos-arm.deb) · [源码](https://chanlx86.github.io/source/alice-launch-fix/1.0.0/source.zip) |
| [洛克图鉴 · 横屏修复](https://chanlx86.github.io/repo/apps/locke-display/) | 1.0.0 | iOS 6+ · ARMv7 | [Cydia](https://chanlx86.github.io/repo/apps/locke-display/#install) · [DEB](https://chanlx86.github.io/repo/deb/local.lockekingdom.displayfix_1.0.0-1_iphoneos-arm.deb) |

## Cydia 软件源

```text
https://chanlx86.github.io/repo/
```

在已越狱设备的 Safari 打开网站，可点击“添加到 Cydia”。传统 rootful 软件源，支持范围以各软件说明为准。旧根地址仍保留兼容索引，无需同时添加两个源。

## 安装前

- IPA 的“直接安装”通过系统 OTA 入口，需要可用签名或兼容的 AppSync 环境；不代表可以在普通未越狱设备免签安装。
- 补丁需要指定版本的原应用。更新前备份数据，不要混装同一个应用的 IPA 和 DEB 副本。
- 各下载页面提供 SHA-256，历史版本可能仅有源码。

## 来源与反馈

维护和发布为 chanlx86。Troubadour 基于 [Computershik73/Troubadour](https://github.com/Computershik73/Troubadour)，LocalSend 适配版基于 [theanazerka/unlocalsend](https://github.com/theanazerka/unlocalsend)。原作者、第三方贡献及各自许可保留在对应源码与说明中。

[问题反馈](https://github.com/chanlx86/chanlx86.github.io/issues) · [维护文档](docs/maintenance.md)
