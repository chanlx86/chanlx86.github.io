# /repo/ 界面与头像处理记录

2026-10-30：依用户要求，参考 https://ios6.wangdashuaihenshuai.work 的分组列表、应用详情与 OTA 安装入口，自行编写偏 iOS 9 的扁平界面。白色分组、灰色底、细分隔线、分段筛选，少量粉红色取自妮可蝴蝶结。没有复制参考站的代码、图片、软件包或证书配置。

Cydia 使用专门的精简详情页，不加载首页的大块装饰；首页也可通过 `?view=cydia` 检查精简模式。核心页面不依赖现代 JS 框架；脚本只增强筛选及桌面端安装提示。

头像使用内置 image_gen / imagegen 技能，编辑用户提供的 `kindpng_2892819.png`；原图不修改。输出为纯白不透明方形，保留人物、红眼、黑色双马尾、红蝴蝶结、表情与画风，头像突出头部和上半身，不加文字、边框、圆形遮罩或阴影。生成图经 sips 输出 256 px 和 64 px 网页资源。

最终资产：`repo/assets/nico-avatar.png`、`repo/assets/nico-small.png`、`repo/CydiaIcon.png`；根 `CydiaIcon.png` 供旧源兼容使用。角色与原插画的权利归其权利人，网页已注明非官方主题。

最终提示词：

> Use case: identity-preserve. Edit target: the attached PNG illustration of Nico Yazawa from Love Live. Create ONE square website and Cydia repository avatar on a solid pure white (#FFFFFF), fully opaque background. Preserve the exact original anime character artwork, red eyes, black twin-tail hair, red ribbons, expression and drawing style; do not redesign, repaint into another style or add new details. Frame the existing head and upper shoulders prominently, leaving the entire red ribbons and top of the head visible with a small white margin. Use a natural square crop of the original illustration. No text, no border, no circle mask, no rounded corners, no shadow, no other elements. Goal: a clean white-background square avatar using this exact illustration.

OTA 协议及 HTTPS／签名条件参考 [Apple 部署文档](https://support.apple.com/en-gb/guide/deployment/depce7cefc4d/1/web/1.0)。安装入口不表示签名豁免；未添加证书描述文件或修改设备信任设置。
