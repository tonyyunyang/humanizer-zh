# 维护说明

项目维护者：[@tonyyunyang](https://github.com/tonyyunyang)。目标是保留一个完整可用的中文 skill，让更新的来源、理由和验证结果可查。

## 文件分工

| 文件 | 职责 |
| --- | --- |
| `SKILL.md` | 唯一运行指令，复制它即可使用 |
| `.claude-plugin/` | Claude Code 插件与 GitHub marketplace 的元数据 |
| `agents/openai.yaml` | Codex 展示名称与默认提示 |
| `README.md` / `README.en.md` | 使用与安装说明 |
| `upstream.lock.json` / `docs/UPSTREAM.md` | 文件版本基线与中文适配决策 |
| `evals/` | 行为回归样例、原始模型输出和评审记录 |
| `scripts/` / `tests/` / `.github/` | 仓库校验和上游变化提醒，不参与改稿 |

不要增加第二份 `SKILL.md`、默认要求读完所有维护文档，或为了打包引入 npm runtime。改变安装结构时，先在临时目录里验证，避免覆盖自己的已装 skill。

## 首次公开

1. 检查 `LICENSE` 保留原有 Tony Yang 的 MIT 许可，`THIRD_PARTY_NOTICES.md` 保留上游许可。
2. 运行下文检查，按 `evals/README.md` 做并记录行为回归。确认 README 里的示例没有新增事实。
3. 将工作分支合并到 `main` 并推送。Skills CLI 和 marketplace 读取的是远端仓库，只有本地文件时，公开安装命令还无法安装本次版本。
4. 在 Actions 页面确认 **Validate** 成功，手动运行一次 **Upstream watch**。工作流在默认分支后才有定时触发；只会在有变化时创建 Issue。
5. 在仓库 Settings 中确认 Issues 和 Actions 可用，并启用 Private vulnerability reporting。行为准则的私密联系地址如需更换，应使用维护者明确愿意公开的邮箱。
6. 按下面的发布流程创建首个版本。GitHub 的 About 文案与 topics 可按本页建议设置。

建议 About：`持续跟进 Blader Humanizer 的中文写作 skill：去 AI 味，保留事实与作者语气。支持 Claude Code / Codex / Cursor。`

建议 topics：`humanizer`、`humanizer-zh`、`chinese`、`agent-skills`、`claude-code`、`codex`、`writing-tools`。

仓库 marketplace 是自己的分发入口，不表示获得 Claude 或 OpenAI 官方收录。`npx skills add` 从 GitHub 安装，不需要发布 npm 包。Star History 使用公开图表服务；不为图表上传个人访问令牌。

## 日常检查

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
python3 scripts/check_upstream.py
```

前两条离线运行。第三条只读 GitHub，输出有无变化及对比链接，不创建 Issue、不修改基线；需要时可提供 `GITHUB_TOKEN` 减少 API 限流。网络或 API 错误会让检查失败，不会报告成“没有变化”。

已安装 Claude Code 时也运行：

```bash
claude plugin validate .
claude plugin validate .claude-plugin/plugin.json --strict
```

CI 在临时项目中使用固定版本 Skills CLI 安装本地 skill，核对单一发现结果及 Claude Code / Codex 的安装路径。测试过程中不调用模型。升级 CLI 或 Actions 时，更新固定版本并重跑安装检查。

## 上游提醒的边界

`upstream.yml` 仅在 `tonyyunyang/humanizer-zh` 运行，避免 fork 默认给自己的仓库发提醒。fork 维护者如需启用，应修改仓库判断和 `upstream.lock.json`。工作流使用 `contents: read` 与 `issues: write`，不需要 PAT 或付费模型。

每天的 schedule 是检查机会，不是同步时限。GitHub 可能延迟任务，也可能暂停长期不活跃仓库的 schedule；维护者需留意 Actions 失败和计划任务是否仍启用。一次检查只维护一条由机器人创建、带专用标记的 Issue，不反复贴评论。

自动化不会翻译、修订规则、修改审阅基线或发布版本。语言适用性和事实保真需要有人审阅。具体步骤见 [UPSTREAM.md](UPSTREAM.md)。

## 发布

本项目用自己的 `major.minor.patch`，不直接复制 Blader 的版本号。输出合同或安装方式不兼容的变更升 major；新增编辑能力升 minor；规则修正、例子修正和兼容性修复升 patch。纯维护变更可先积累在 Unreleased。

发布前同步：

- `SKILL.md` 的 `metadata.version`。
- `.claude-plugin/plugin.json` 的 `version`（marketplace 从插件读取版本，不重复声明）。
- 两份 README 的当前版本和适配基线。
- `CHANGELOG.md` 中的日期、变更和验证说明；首次发布时去掉“待发布”。

跑检查并确认合并后的 CI 通过，再创建同名 tag（例如 `v1.0.0`）和 GitHub Release。Release 说明已适配的上游提交、中文行为变化、验证方式和已知限制。不要写“全模型通用”“100% 去 AI 味”等未经验证的承诺。

为手动安装提供精简 ZIP。把示例中的 tag 换成本次发布版本，生成后作为 Release 附件上传，保持文件名 `humanizer-zh.zip`，让 README 的下载地址继续有效：

```bash
git archive --format=zip --prefix=humanizer-zh/ --output=humanizer-zh.zip v1.0.0 SKILL.md LICENSE THIRD_PARTY_NOTICES.md agents/openai.yaml
```

检查 ZIP 内的文件与 tag 一致，且包含完整许可；不要加入维护脚本或第二份 skill。

### 同步完成的判断

commit 数不会自动更新版本号，推送 `main` 也不代表完成发版或本机更新。纯维护提交可留在 Unreleased；决定发布累积的编辑改进时，要一并核对：

1. 本地与远端 `main` 一致，skill、插件、README 与 changelog 的版本一致。
2. 正式 tag 指向已通过 CI 的提交，GitHub Latest release 指向本次 tag；保留旧 tag 与旧附件。
3. 从公开 Latest 下载地址重新取得 `humanizer-zh.zip`，逐文件核对 tag 内容与许可，再从公开仓库或附件做临时安装检查。
4. 更新用户实际使用的安装位置，核对安装后的版本与文件内容，并确认宿主确实发现了该 skill。仓库工作树和临时安装成功不能替代这一步；不覆盖用户自定义副本或其他同名来源。

在发布记录中分别说明仓库、release、安装包与实际安装的结果。测试和文风效果也分开报告；若只验证了某个工具或当前机器，不把结论扩展到其他安装。

## 反馈处理

先复现，再判断是事实损坏、语体漂移、未去掉模板感还是安装问题。优先修会改错事实或破坏命令的例子。解释采用或拒绝规则的原因；不要对贡献者的文笔或作者身份下判断。

如果长期无人接手，更新 README 说明维护状态与最后审阅日期。保持真实的状态，比保留“持续更新”口号更重要。
