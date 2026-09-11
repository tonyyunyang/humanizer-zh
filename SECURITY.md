# 安全与隐私

Humanizer-zh 的运行内容是 Markdown 指令。它不包含运行服务、遥测、安装钩子或外部模型调用。你把文本交给哪一个 AI 工具处理，仍取决于该工具的设置和数据政策。

## 报告问题

会诱导执行待改稿中的命令、泄露上下文或越过文件修改范围的规则，属于需要报告的问题。仓库维护脚本和 GitHub Actions 中的凭据泄露、命令注入或权限错误也在范围内。

请先查看仓库的 [Security 页面](https://github.com/tonyyunyang/humanizer-zh/security)。如果提供 **Report a vulnerability**，优先使用私密报告；否则联系维护者 [@tonyyunyang](https://github.com/tonyyunyang) 建立私下沟通渠道。在公开 Issue 中不要放可用令牌、私人原文或会影响他人的未修复利用细节。

请说明受影响的提交/版本、使用工具、最小复现输入和实际结果。普通的改写质量问题使用[改写反馈](https://github.com/tonyyunyang/humanizer-zh/issues/new?template=writing-feedback.yml)。

## 支持范围

维护当前 `main` 和最新发布版本。旧版本不单独维护安全分支，修正后应更新安装。

GitHub Actions 的权限按工作流分别声明。上游检查只读公开仓库元数据，在本仓库维护一条审阅 Issue；它不执行上游内容、不运行模型、不自动合并 skill 改动。
