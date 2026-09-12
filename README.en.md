# Humanizer-zh

[简体中文](README.md) · [Install](#install) · [Upstream record](docs/UPSTREAM.md)

A Chinese writing skill that removes formulaic phrasing while preserving the writer's facts, intent, and voice.

This independently maintained adaptation follows [Blader Humanizer](https://github.com/blader/humanizer), draws on the Chinese editing practice in [说人话](https://github.com/MrGeDiao/shuorenhua), and acknowledges [op7418's earlier Chinese edition](https://github.com/op7418/Humanizer-zh).

The complete editing workflow lives in one [`SKILL.md`](SKILL.md). No runtime service, project API key, or npm package is required. Use it with your existing AI agent.

## Install

Run in your terminal:

```bash
npx skills add tonyyunyang/humanizer-zh --global
```

Select your agents when prompted. Omit `--global` for a project installation. [`skills`](https://github.com/vercel-labs/skills) is an installer maintained by Vercel; its current CLI requires Node.js 22.20.0 or newer.

For Claude Code 2.1.142 or newer, use the same plugin route as Blader's project:

```text
/plugin marketplace add tonyyunyang/humanizer-zh
/plugin install humanizer-zh@humanizer-zh
```

The marketplace is served by this GitHub repository. It does not imply a listing or endorsement in an official curated marketplace.

For a manual installation, download the [minimal ZIP](https://github.com/tonyyunyang/humanizer-zh/releases/latest/download/humanizer-zh.zip) and place its `humanizer-zh` folder under `~/.claude/skills/` for Claude Code or `~/.agents/skills/` for Codex. It contains the skill, licenses, and optional Codex display metadata. See the [Chinese README](README.md#安装) for updates and removal. Back up and remove another skill with the same name before switching editions.

## Use

```text
Use humanizer-zh to edit this Chinese text. Keep the facts and my voice:

[your text]
```

Invoke `/humanizer-zh` as a manually installed plain Claude skill, `/humanizer-zh:humanizer-zh` as a Claude plugin, or `$humanizer-zh` in Codex CLI / IDE. Skills CLI installations may be discovered as a skill or plugin depending on the Claude Code version; use the name shown in its command list. You can supply a writing sample, request annotations only, or ask it to edit prose in a file.

By default, it returns one finished rewrite. It preserves technical terms, uncertainty, attribution, quotations, and protected file content. It keeps normal Chinese quotation marks and purposeful punctuation. It does not invent personal experiences or identify whether an author used AI.

## Maintenance

The latest release, **1.0.0**, adapts **Blader Humanizer 3.0.0**, reviewed on **2026-09-11**. Our version number tracks this Chinese edition independently. The `main` branch includes subsequent unreleased improvements for Chinese, mixed-language text, and issue/PR descriptions; the minimal ZIP contains the released version.

The [improvement record](docs/RSI.md) links the research and recorded rounds of actual outputs. The current skill is the approved baseline for further RSI. The local scheduled improvement task has been deleted; further iterations are started on demand.

The repository includes a daily [upstream watcher](.github/workflows/upstream.yml). It checks selected files in the three source repositories and creates or updates a review issue only when their contents change. Maintainers review language applicability and examples before updating the skill; the watcher does not translate or merge automatically.

See the [pinned source record and adaptation map](docs/UPSTREAM.md), [changelog](CHANGELOG.md), and [maintenance guide](docs/MAINTAINING.md). "Adapted" always refers to a reviewed commit, not an unreviewed upstream head.

## Contribute

Real examples are welcome, especially edits that lose a condition, change a fact, flatten the writer's voice, or leave awkward Chinese. Remove personal information before sharing.

[Contributing](CONTRIBUTING.md) · [Code of conduct](CODE_OF_CONDUCT.md) · [Security](SECURITY.md)

## License

[MIT](LICENSE). Upstream copyright notices and license texts are retained in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Thanks to Siqi Chen, MrGeDiao, and 歸藏 for their public work.
