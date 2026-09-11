# 参与 Humanizer-zh

谢谢你愿意一起维护。你不需要会写代码：一段改坏的中文、一处失真的对照，往往比多加几十个“禁词”更有帮助。

## 先选最直接的方式

- **改稿丢了事实、变得生硬或不像自己：** 用[改写反馈](https://github.com/tonyyunyang/humanizer-zh/issues/new?template=writing-feedback.yml)，附原文、要求、实际输出和问题所在。
- **安装失败：** 用[安装问题](https://github.com/tonyyunyang/humanizer-zh/issues/new?template=installation.yml)，注明系统、工具版本、安装方式与报错。
- **发现上游变化：** 先看看已有的同步 Issue；如果没有，附上具体提交或 diff，说明哪些经验适合中文。
- **小修正：** 错别字、坏链接和明显表述错误可以直接发 PR。

请移除姓名、公司内部信息、访问令牌和未获授权的原文。样本必须是你能公开分享的；引用第三方内容时附来源和许可。

## 什么样的规则值得加入

先说明现有规则在哪个具体例子上失效。新规则应改变编辑判断，并有清楚的保留边界。至少附一个应该改的例子和一个不应该改的反例。

我们优先接受：

- 保护事实、责任、条件和技术语义的修正。
- 有实际中文例子支持的句式与段落规则。
- 能简化使用或减少加载内容的调整。
- 有审阅记录的上游适配。

不把单个常用词列入硬性黑名单，不用词频、固定句数或自评分证明“已经去掉 AI 味”。未经验证的模型效果不要写成保证。增加依赖、安装器或运行服务前，先说明单文件为什么不能满足需求。

## 本地修改

```bash
git clone https://github.com/tonyyunyang/humanizer-zh.git
cd humanizer-zh
git switch -c improve-chinese-example
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

维护脚本使用 Python 3.10+ 标准库，安装 skill 不需要 Python。`SKILL.md` 是唯一的运行入口；不用在多个目录复制同一份 skill。

改行为时，按 [`evals/README.md`](evals/README.md) 做对应场景回归并说明工具、模型和结果。自动检查只能验证包结构、文件关系和维护脚本，不能证明文笔好坏。文档小修不用跑模型。

如果本机有 Claude Code，可额外运行 `claude plugin validate .` 验证 marketplace，再运行 `claude plugin validate .claude-plugin/plugin.json --strict` 验证插件。CI 会用固定版本的 Skills CLI 在临时项目中验证可发现性与安装路径。

## 提交 PR

用一两句话说明具体问题和修改后的行为，附上原文/改后对照、不能误改的边界和实际做过的验证。关联相关 Issue。上游适配按 [`docs/UPSTREAM.md`](docs/UPSTREAM.md) 补审阅记录。

不需要签 CLA；你的贡献按本项目 [MIT License](LICENSE) 提供。保留上游版权说明。维护者可能会合并重复规则、收窄适用范围或要求更有区分度的例子。

版本号和发布由维护者统一整理。欢迎用中文或英文讨论，请遵守[行为准则](CODE_OF_CONDUCT.md)。
