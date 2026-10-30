# chanlx86 · 旧 iOS 软件与修复补丁

为仍在使用的 iPhone、iPad 提供应用、移植构建和兼容修复。

**[浏览软件下载站](https://chanlx86.github.io/) · [安装指南](https://chanlx86.github.io/help/) · [版本归档](https://chanlx86.github.io/archive/)**

## 应用下载

| 应用 | 版本 | 系统要求 | 下载 |
| --- | --- | --- | --- |
| [J2ME模拟器](https://chanlx86.github.io/apps/j2me/) | build65 | iOS 6+ | [IPA](https://chanlx86.github.io/ipa/j2me/build65/j2me.ipa) |
| [存档浏览器](https://chanlx86.github.io/apps/archive-browser/) | 0.9.0 | iOS 9+ | [IPA](https://chanlx86.github.io/ipa/archive-browser/0.9.0/archive-browser.ipa) · [源码](https://chanlx86.github.io/source/archive-browser/0.9.0/source.zip) |
| [录屏大师](https://chanlx86.github.io/apps/screen-recorder/) | 0.6.1 | iOS 9.x · 32 位 | [DEB](https://chanlx86.github.io/deb/local.legacy.screenrecorder_0.6.1_iphoneos-arm.deb) · [源码](https://chanlx86.github.io/source/screen-recorder/0.6.1/source.zip) |
| [LocalSend](https://chanlx86.github.io/apps/localsend/) | 0.7.0 | iOS 9+ · ARMv7 | [IPA](https://chanlx86.github.io/ipa/localsend/0.7.0/localsend.ipa) · [源码](https://chanlx86.github.io/source/localsend/0.7.0/source.zip) |
| [Troubadour](https://chanlx86.github.io/apps/troubadour/) | 1.6.1 | ARMv7 iOS 5.1+ / ARM64 iOS 7+ | [IPA](https://chanlx86.github.io/ipa/troubadour/1.6.1/troubadour.ipa) · [源码](https://chanlx86.github.io/source/troubadour/1.6.1/source.zip) |
| [维基文库](https://chanlx86.github.io/apps/wikisource/) | 0.2.0 | iOS 9+ | [IPA](https://chanlx86.github.io/ipa/wikisource/0.2.0/wikisource.ipa) · [源码](https://chanlx86.github.io/source/wikisource/0.2.0/source.zip) |

## 兼容修复补丁

补丁需要相应原应用和越狱环境；安装后请彻底退出目标应用再打开。

| 补丁 | 版本 | 适用对象 | 下载 |
| --- | --- | --- | --- |
| [Onegram 登录修复](https://chanlx86.github.io/apps/onegram-login-fix/) | 0.2.0 | Onegram 1.4.2 / iOS 9 | [DEB](https://chanlx86.github.io/deb/local.onegram.loginfix_0.2.0_iphoneos-arm.deb) · [源码](https://chanlx86.github.io/source/onegram-login-fix/0.2.0/source.zip) |
| [Wikipedia 正文兼容](https://chanlx86.github.io/apps/wikipedia-compat/) | 0.1.0 | Wikipedia 5.5.1（1164）/ iOS 9 | [DEB](https://chanlx86.github.io/deb/local.wikipedia.mobileview.compat_0.1.0_iphoneos-arm.deb) · [源码](https://chanlx86.github.io/source/wikipedia-compat/0.1.0/source.zip) |
| [爱丽丝快跑启动修复](https://chanlx86.github.io/apps/alice-launch-fix/) | 1.0.0 | 中文版爱丽丝快跑 2.40 / ARMv7 | [DEB](https://chanlx86.github.io/deb/local.luoxian.aliceresponseguard_1.0.0_iphoneos-arm.deb) · [源码](https://chanlx86.github.io/source/alice-launch-fix/1.0.0/source.zip) |
| [洛克图鉴 · 横屏修复](https://chanlx86.github.io/apps/locke-display/) | 1.0.0 | 洛克王国图鉴 1.2 / iPad | [DEB](https://chanlx86.github.io/deb/local.lockekingdom.displayfix_1.0.0_iphoneos-arm.deb) |

## Cydia 软件源

在 Cydia → 软件源 → 编辑 → 添加中输入：

```text
https://chanlx86.github.io/
```

也可以用设备的 Safari 打开[网站首页](https://chanlx86.github.io/)，点击“添加到 Cydia”。源中提供本页列出的 DEB；仅有 IPA 的应用需单独下载安装。此源面向传统 **rootful** 越狱，不是 rootless 软件源。

## 安装前请留意

- 先查看应用详情中的系统、架构和版本限制；目前主要在 iPad 3 / iOS 9.3.6 上验证，不能保证所有旧设备都兼容。
- IPA 主要采用本地 ad hoc／伪签名，需要兼容的越狱安装环境或自行使用可用的签名方式；下载并不等于可以在未越狱设备上直接安装。
- 更新前备份存档。不要把同一应用的 IPA 和 DEB 副本混装；系统依赖请从其可信来源获取。
- 各详情页提供 SHA-256；也可查看 [SHA256SUMS](SHA256SUMS)。历史版本可能仅保留源码，以归档页面实际文件为准。

## 项目来源与反馈

Troubadour 基于 [Computershik73/Troubadour](https://github.com/Computershik73/Troubadour)，此处的 1.6.1 为 Xcode 7 修复构建；LocalSend 适配版基于 [theanazerka/unlocalsend](https://github.com/theanazerka/unlocalsend)。对应源码随相关版本提供。各软件及第三方组件遵循各自许可，网站的 MIT 许可不替代应用许可。

遇到问题可提交 [Issue](https://github.com/chanlx86/chanlx86.github.io/issues)，注明版本、设备、系统和复现步骤，不要公开账号、密码或令牌。

[维护文档](docs/maintenance.md)
