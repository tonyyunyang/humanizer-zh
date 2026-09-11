# 上游与中文适配

本项目独立维护中文版本。Blader Humanizer 是主要上游，说人话提供中文编辑经验，op7418 的 Humanizer-zh 是早期中文参考。引用和致谢不表示这些作者为本项目背书。

## 本次审阅

审阅日期：**2026-09-11**。对应本项目版本：**1.0.0**。

| 来源 | 审阅版本 | 固定提交 | 用途 |
| --- | --- | --- | --- |
| [blader/humanizer](https://github.com/blader/humanizer) | 3.0.0 | [`9862685`](https://github.com/blader/humanizer/tree/9862685f575c65a8247f90369951df1b3416e3d6) | 核心模式、样文匹配、回读流程、文件保护和安装结构 |
| [MrGeDiao/shuorenhua](https://github.com/MrGeDiao/shuorenhua) | 2.4.0 | [`d2d0ce2`](https://github.com/MrGeDiao/shuorenhua/tree/d2d0ce27da295581c3cf87a30ab65deb7d0ddfb8) | 中文语体、信息保真、术语边界、默认终稿和只标问题 |
| [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh) | 早期 24 项整理 | [`91f3d39`](https://github.com/op7418/Humanizer-zh/tree/91f3d394db8419c20d67ebe22a96cf8fee0a404b) | 中文使用入口和早期汉化经验 |

机器可读记录在 [`upstream.lock.json`](../upstream.lock.json)，包括完整提交 SHA 和已审阅文件的 Git blob SHA。提交固定了本次审阅的材料；上游版本号是辅助信息，不替代提交记录。

本次查看时，op7418 仓库未归档，最新提交日期为 2026-01-19。我们不据此替作者宣布弃用或停止维护。Blader 的最新提交日期为 2026-09-06；说人话为 2026-09-02。

## Blader 3.0.0 对照表

本项目保留上游 1–25 的编号，便于比较。每项都经过中文判断；“适配”不表示逐字翻译，也不表示每项都要执行删改。

| 编号 | 上游模式 | 中文处理 |
| --- | --- | --- |
| 1 | Not X but Y | 去掉没有信息的对比；保留真实区别、纠错和限制 |
| 2 | One-line closers and dramatic fragments | 处理金句收尾和碎句表演，保留有用的短句 |
| 3 | Sayings that sound deep | 改写“本质”“底层逻辑”等空泛定调，保留实际原理 |
| 4 | Staged run-up before the point | 去掉预告层，不把教程引导和正常口语一并删除 |
| 5 | Arguing with no one | 处理假想反对者，保留真实异议与取舍 |
| 6 | Forced triads | 检查是否信息重复，不靠删掉第三个真实项目打散结构 |
| 7 | Repeated sentence openings | 调整机械起句，保留有意排比 |
| 8 | Dashes as the universal connector | 处理滥用；不采用无样文时全面禁止破折号的规则 |
| 9 | Stacked qualifiers | 简化重复限定，保留真实不确定性和范围 |
| 10 | Hyphenated pairs everywhere | 仅对中英混排按语法处理；纯中文不适用 |
| 11 | Passive voice and missing subjects | 理顺动作和主体；不为中文省略句编造执行者 |
| 12 | Overused AI words | 改成中文语境的抽象词与黑话判断，不建硬性禁词表 |
| 13 | Inflated significance | 删除没有信息的拔高、空展望；保留计划和限制 |
| 14 | Vague connection or association | 有依据才具体化，不把“参与”改成“负责” |
| 15 | Shallow -ing riders | 对应中文句尾的“体现、彰显、确保”；保留实际因果 |
| 16 | Sales language | 降低无依据的宣传性，保留真实特点和个人喜好 |
| 17 | Borrowed authority | 保留归属，指出必要的来源缺口，防止把无源结论洗成事实 |
| 18 | Avoiding is, are, and has | 还原“是、有、负责”等具体动词，不模糊动作差异 |
| 19 | Bold as decoration | 清理重复标签，保留方便检索和比较的结构 |
| 20 | Decorative headings | 处理装饰和重复标题；中文不套英文标题大小写规则 |
| 21 | Curly quotation marks | 不采用“中文弯引号像 AI”的判断；遵循中文及目标格式习惯 |
| 22 | Chatbot residue | 删除正文外壳，保留真实的礼貌、称呼和邀请 |
| 23 | Knowledge-limit disclaimers and guesses | 清理模型自述与脑补，保留有意义的日期和资料缺口 |
| 24 | A heading repeated in the first sentence | 删除同义重述，保留必要定义和前提 |
| 25 | Writing about the previous version | 现状文档聚焦当前行为，变更类文档保留前后关系 |

## 从说人话吸收什么

- **双向保真。** 检查输入的信息是否保留，再检查输出能否回指输入。数字和修饰对象、主体和责任、条件和完成状态一起保护。
- **语体有区别。** 技术文档、进度同步和个人文章不统一改成口语；按实际语义区分“闭环控制”和进度包装用语。
- **防止抽象信息被脑补。** “提升效率”不自动等于省钱、省时间；“参与”不等于“负责”。
- **默认直接给终稿，按需只标问题。** 用户需要的是可用的改稿；分析和多版本不是默认交付。
- **保留自然中文。** 不靠强塞热梗、安慰、身份夸奖或同义词轮换消除模板感。

我们没有引入说人话的多级档位、scope 矩阵和默认必读的整套参考文件。对这个项目，单文件可用与减少选择负担更重要。用户明确提出的保句数、保段落、保篇幅要求仍然有效。

## 对早期中文版的取舍

保留易安装、直接用中文解释的方向。重新编写示例，避免加入原文不存在的功能、调查、年份和个人经历。不采用固定 50 分自评分、用两项或四项取代三项的机械节奏规则，也不把正式文档强行写成第一人称。

## 与英文版的有意差异

1. 默认输出一版终稿。英文版默认展示初稿、简短审阅和终稿；本项目只在用户需要时解释改动。
2. 正常的中文引号、破折号、省略主语不构成问题；根据具体语境判断。
3. 样文用于匹配风格，不能提供待改稿里不存在的事实；“更有人味”不能成为编造作者经历或情绪的理由。
4. 缺引文不是删掉原文断言的充分理由。涉及未提供来源的数字、预测和结论时保留归属，必要时提示缺口，不默默改成无主语的确定事实。
5. 不以某个日期、词表或语气来断定 AI 作者身份，不承诺通过检测器。

## 后续怎样同步

[`Upstream watch`](../.github/workflows/upstream.yml) 每天尝试检查一次，也可手动运行。只有 `upstream.lock.json` 中指定文件的内容发生变化才创建或更新待审阅 Issue；同样的变化不会反复评论。仅 README 改动可能影响安装说明，因此也列入跟踪。

检测和审阅分开：机器人生成差异线索，维护者决定如何适配。Issue 关闭了但基线没更新，下次仍会重新打开，避免误把“关掉提醒”当成“完成审阅”。所有变化回到已审阅内容时，现有提醒会关闭。

一次同步 PR 应完成：

1. 阅读 Issue 中的固定提交差异，确定哪些变化适合中文。
2. 在本页或新的版本记录中写明采用、改写或跳过的原因。
3. 更新 `SKILL.md`，补一个体现收益的中文案例和一个防止误改的边界案例；不适用的变化只记原因。
4. 按 [`evals/README.md`](../evals/README.md) 回归，运行 `python3 scripts/validate.py` 与 `python3 -m unittest discover -s tests -v`。
5. 审阅完成后，运行 `python3 scripts/check_upstream.py --record <来源 ID> --ref <已审阅的完整 SHA>` 更新该来源的记录，再核对 diff。此命令不会自行判断内容已审阅。
6. 涉及行为变化时更新本项目版本、插件版本、README 和 `CHANGELOG.md`。下一次检查会以合并后的记录为基线。

来源 ID 是 `blader`、`shuorenhua`、`op7418`。`--record` 只写文件 SHA、提交和审阅日期；有新版本号时需同时核对并更新 `version`，补充新增或改名的跟踪路径。

新增语种规则或推翻现有边界时，优先让中文案例解释为什么值得改。不要只为了跟上上游版本号原样搬运。
