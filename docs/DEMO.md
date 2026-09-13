# 三个实际改写例子

这些是 2026-09-13 为产品演示自拟的场景，使用 Humanizer-zh v1.1.0、Codex CLI 0.153.4、gpt-6-astra（high），每个场景在独立文本会话里运行一次。模型只收到 skill、用户要求和输入，没有收到预期答案；输出逐字保存。

固定 skill 提交：`72b23e9658400f36fead85f2e51ea8ea61804517`。运行文件 SHA-256：`9c1be9fc3985c3e04422cd6f9808405ccf3fbdf541af72417008660908f2554c`。结构化记录见 [cases.json](../assets/demo/cases.json)，执行方法对应 [run_evals.py](../scripts/run_evals.py)。

The video is a designed presentation of saved CLI input and output, with edited pacing. It is not a separate product interface or a real-time performance demonstration. English explanations are editorial translations, not additional skill outputs.

[演示视频](../assets/demo/humanizer-zh.mp4) · [GIF](../assets/demo/before-after.gif) · [静态对照](../assets/demo/comparison.png)

## 产品更新：保留使用范围

要求：用 humanizer-zh 润色这段产品更新说明，保留事实与使用范围。只给最终成稿。

原文：

> 这不仅仅是一次功能更新，更是我们对用户体验的持续深耕。现在，上传失败时可以点击「重试」。该功能目前只在网页版开放，手机端尚未支持。

实际输出：

> 现在，上传失败时可以点击「重试」。该功能目前只在网页版开放，手机端尚未支持。

删除了开头的空泛评价，保留上传失败时可重试、仅网页版开放、手机端尚未支持。

## 技术说明：保留数字和未完成事项

要求：用 humanizer-zh 润色这段技术更新，保留全部数字、指标、条件和未完成事项。只给最终成稿。

原文：

> 在测试环境中，我们针对 60 个请求的验证结果表明，缓存命中时的 p95 延迟由 420ms 降到了 260ms。这一成果充分体现了此次优化的显著价值。需要指出的是，缓存未命中的情况尚未验证。

实际输出：

> 在测试环境中，我们验证了 60 个请求，结果显示：缓存命中时的 p95 延迟由 420ms 降到了 260ms。缓存未命中的情况尚未验证。

保留测试环境、60 个请求、p95、420ms、260ms、缓存命中条件和缓存未命中尚未验证。数字属于演示样文，不是本工具的性能数据。

## 作者语气：本来就自然可以不改

要求：用 humanizer-zh 看看这段中文需不需要润色，保留作者的语气。只给最终成稿。

原文：

> 我本来只想修个小问题，结果一下午都搭进去了。明天再说吧。

实际输出：

> 我本来只想修个小问题，结果一下午都搭进去了。明天再说吧。

本次输出与输入逐字相同，没有为制造改动而替换原有语气。

## 如何理解这些结果

这是三个选定的说明性例子，由制作会话核对事实和表达，没有独立外部编辑盲评，也不是代表性样本。其他模型、上下文或重复运行可能得到不同输出。没有据此计算普遍提升率、与其他工具的胜率或检测器结果。

本轮另将公开仓库与 v1.1.0 精简 ZIP 安装到临时 Codex 和 Claude Code 项目，逐字核对运行文件与许可。安装通过与模型改写质量是两件事；上述行为演示只使用了 gpt-6-astra。正式精简 ZIP 的四个文件不包含视频、GIF 或这些维护材料。

实际应用时仍应对照原文检查数字、范围、完成状态和作者语气。更广的维护记录见 [行为回归](../evals/README.md)。
