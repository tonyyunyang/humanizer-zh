# Writing useful issues and pull request descriptions

Issues and pull request descriptions should help someone understand a problem, make a decision, or review a change with an appropriate amount of effort. Clear language matters, but the selection and ordering of information matter just as much. A fluent description can still be difficult to use if the actual problem, proposed behavior, or evidence is buried under background and repeated summaries.

Current guidance supports concrete, focused descriptions with enough context for their readers. It also supports substantial explanations when the reasoning, implementation constraints, or consequences warrant them. There is no well-supported universal word limit, and the available research does not establish that contemporary AI-written descriptions are generally worse than human-written descriptions.[^1][^2][^11][^12]

## The reader's task

An issue can report a defect, propose an improvement, or organize a decision. A PR asks readers to assess a particular change. Their useful content follows from those purposes; sharing a platform does not make their information requirements identical. Project contribution guidelines and supplied templates establish additional local requirements.[^7][^14]

| Reader's immediate task | Information that usually helps | Information that should remain conditional |
| --- | --- | --- |
| Understand or reproduce an observed problem | Specific symptom, triggering circumstances, expected and actual behavior, relevant environment, reproducibility and evidence | Root-cause analysis, a proposed fix, or a minimal reproducer that the reporter has not established |
| Discuss an improvement | Existing difficulty, a concrete use case, desired outcome, known constraints and a decision to make | A settled implementation, delivery date, universal demand or quantified benefit |
| Review a change | Problem addressed, resulting behavior, relevant reasoning, actual validation and consequences | A walkthrough of every changed file, an extensive background section or a generic risk checklist |
| Evaluate a consequential design | Motivation, alternatives, compatibility, migration, limitations and unresolved questions | Artificial brevity that removes the reasons needed to choose between approaches |

This table is a synthesis for editing, not a form that every description must fill. A small correction may need a short paragraph. A proposal can need several sections. A request to correct wording within an existing section does not authorize replacing the author's structure.

## Issues: make observations usable

Mozilla's bug-writing guidance emphasizes a distinctive summary, precise reproduction steps, expected and observed results, and the separation of observations from speculation. It also asks reporters to distinguish reliable reproduction from intermittent behavior. Its browser-specific diagnostics and approximate English title length should not become general Chinese editing rules.[^3]

The VS Code project similarly asks for version and platform details, reproduction steps, and relevant evidence. Screenshots can illustrate the behavior, but cannot replace copyable code or the steps needed to reproduce it. It encourages one problem or feature request per issue; this is a useful way to keep a report focused, subject to the project's actual workflow.[^4]

An earlier empirical study provides a reason to care about these details. Bettenburg and colleagues surveyed developers and reporters from Apache, Eclipse and Mozilla, obtaining 466 responses. Developers valued reproduction steps, stack traces and test cases, while reporters often found those difficult to provide. This supports preserving useful diagnostic evidence and identifying gaps. It does not justify inventing evidence or requiring every reporter to diagnose the implementation.[^10]

For an editor, the practical work is to bring the observed problem into view and make the supplied evidence easy to follow. A chronological account can be reorganized if chronology is incidental. A sequence in which the failure depends on what happened first must remain a sequence. A suspected regression must remain suspected unless the material establishes it.

### Feature requests and open questions

Feature requests need the use case and desired outcome. They should not be forced into a bug-report form when no malfunction is being alleged. Django's guidance asks for a clear explanation of the missing feature, a minimal use case and, where useful, example code. It also has its own route for discussing significant proposals before implementation; that routing policy is specific to Django.[^5]

Editing can clarify what decision is being requested without pretending that a solution has been approved. “Could we expose this option?” and “This implements the approved option” have different meanings. Likewise, an issue that asks maintainers which behavior is intended should retain that uncertainty instead of becoming a confident bug accusation.

If essential information is absent, a short note about the gap can help. The absence of a version number is not evidence of any particular version. Missing test information is not evidence that tests were never run. A polished report should remain explicit about the limits of its material.

## PRs: explain the change and its reasoning

GitHub recommends titles and descriptions that communicate the problem, approach and result. It also recognizes the value of directing attention to important files, a useful review order, or the particular feedback wanted. Its advice to keep PRs small concerns the scope of the change; it is not a numerical limit on the description.[^1]

Google treats a change description as a durable record for reviewers and future maintainers. A focused opening should identify the change; the body should retain the context and reasoning that cannot be recovered from the code alone. Relevant shortcomings and supporting links belong there too, with enough local explanation to survive an inaccessible link. Descriptions should be updated when the change evolves.[^2]

These principles support a simple editing sequence: establish the problem and resulting behavior, explain decisions that matter, then make validation and consequential limitations easy to find. This is an information priority, not a mandatory set of headings. The reader may already understand much of the implementation from the diff, while still needing to know why this approach was chosen.

GitLab's contribution guidance illustrates how context can require more detail. Its MR descriptions should provide the setup needed to examine the change; its UI workflow requires before-and-after visuals. Such requirements can justify extra material. They do not imply that every PR needs screenshots, feature-flag instructions or a new checklist.[^6]

### Validation and implementation history

Validation should describe evidence actually available: the check, its result and any material limit. A unit-test result does not establish end-to-end behavior. A benchmark on one workload does not establish a general performance gain. Linux's patch guidance explicitly asks optimization claims to include supporting measurements and non-obvious costs.[^8]

Development history needs editorial judgment. Exploratory attempts that have no bearing on the final change can obscure it. An alternative rejected because it breaks an important constraint can explain the final design and should remain. The description must also remain consistent with the final scope: a partial fix should not be rewritten as a complete resolution of its linked issue.

File names and code references have a similar boundary. A list that merely repeats each diff entry may add little. A short explanation of where to begin reviewing a complicated change can be valuable. The relevant question is what the reference helps the reviewer understand.

## Length, structure and necessary detail

Long explanations are appropriate when the reader needs them. The Rust RFC template explicitly allows lengthy motivation and asks for detailed design, drawbacks, alternatives and unresolved questions. An RFC is a design proposal, so its requirements should not be copied into every routine issue or implementation PR. It provides a clear counterexample to the idea that substantial prose is inherently wrong in a contribution workflow.[^9]

Linux also asks for a self-contained problem statement, impact, technical explanation and justification. At the same time, it treats an expanding description as a possible indication that a patch combines too much work. This is a prompt to inspect the scope and reasoning, not proof that deleting explanatory paragraphs improves the patch.[^8]

A useful editing judgment is whether a passage helps a reader identify, reproduce, evaluate or revisit the work. Background that establishes a compatibility constraint earns its space. Repeating that a routine fix demonstrates a commitment to quality usually adds little. A closing paragraph can be necessary when it states a pending decision; it need not repeat the description's opening.

Headings, lists and templates can reduce search effort. They become cumbersome when they create multiple places to restate the same point or imply that an empty section must be filled with something plausible. GitHub provides templates precisely so projects can ask for the information they need. Preserving a required template is compatible with removing generic filler inside it.[^7]

A practical size rule for the skill is proportionality: use the amount of explanation needed for this particular review or decision. A brief entry should still be understandable. A substantial entry should expose its main point early and give readers a clear way through the supporting detail.

## Evidence about AI-generated descriptions

The concern about essay-like AI output is a reasonable hypothesis about particular descriptions. It should be tested through their usefulness: repetition, unsupported claims, misplaced emphasis and missing evidence can all be inspected. Attributing a description to AI from its style is a separate claim that this skill does not make.

Pirouzkhah, Wurzel Gonçalves and Bacchelli's 2026 study examined about 80,000 PRs from 156 projects and surveyed 64 developers. It found that different description elements mattered in different contexts, with purpose and code explanations valued by developers and specific feedback requests associated with review outcomes. However, the repository sample comes from a 2019 GHTorrent release. It cannot measure today's AI authoring practices. The authors also report limitations from automated element classification, selection and residual confounding; their findings do not establish an optimal length or a causal effect of adding a particular section.[^11]

Xiao and colleagues' 2024 study examined 18,256 PRs containing Copilot-generated descriptions. It reported favorable review and merge outcomes in that early-adopter setting, while documenting developers' additions, deletions, refinements and replacements. Authors often supplied intent, testing information and other context beyond the generated text. The study used a quasi-experimental design with controls, but acknowledges remaining confounders and limited generalizability. It offers counterevidence to a blanket assumption that AI assistance necessarily degrades PR descriptions.[^12]

GitHub's current application card also identifies the possibility of plausible but inaccurate PR text and calls for verification. For humanizer-zh, this reinforces a concrete constraint: polishing language must not create a root cause, a successful test, a compatibility guarantee or an implementation claim that the source does not support.[^13]

The defensible target is useful, accountable communication. Whether an author used AI does not determine whether a paragraph's rationale is necessary, whether a reproduction is complete, or whether a claim is true.

## Original editing examples

The following examples are synthetic. Each rewrite uses only the information in its source. They illustrate judgments, not unique correct answers or evaluation results.

### A routine PR

**Source**

> 本次 PR 围绕分页体验进行了系统性优化，为列表浏览提供更加稳健的支撑。此前收到空列表后仍会请求下一页，现在收到空列表就停止分页。`pagination.test.ts` 已通过，集成测试还没跑。总体而言，这次改动为后续持续提升用户体验奠定了基础。

**Possible rewrite**

> 收到空列表后停止分页，修复此前仍会请求下一页的问题。
>
> `pagination.test.ts` 已通过，集成测试还没跑。

The result preserves the behavior change and actual validation while removing claims that add no further information. It does not need a separate background, implementation, impact and conclusion section to repeat the same fact.

**Boundary:** if a longer PR explains why stopping here preserves a pagination contract or how the change affects existing clients, those details can be necessary. This example does not authorize deleting them.

### An intermittent issue

**Source**

> 为了共同促进软件质量的持续提升，我想反馈一个值得重视的问题。我在 `2.3.0` 的 macOS 版本中，断网后点“保存”，遇到过一直转圈的情况；我预期会显示失败提示。重新联网后再试没有出现，但我还没找到稳定复现的步骤，不确定是不是网络切换造成的。希望这能为产品稳定性建设提供参考。

**Possible rewrite**

> 在 `2.3.0` 的 macOS 版本中，断网后点“保存”时遇到过一直转圈的情况，预期应显示失败提示。
>
> 重新联网后再试没有出现。目前还没有稳定的复现步骤，也不确定是否由网络切换造成。

The report is easier to use while retaining its limits. It does not turn one observation into a reliably reproduced defect or a confirmed diagnosis.

**Boundary:** a feature proposal about offline saving needs its use case and intended behavior. It should not acquire invented reproduction steps simply because it is submitted as an issue.

### A decision that needs its reasoning

**Source**

> 这里暂时保留双写。旧客户端还在读取 `legacy_name`，而新客户端只读取 `display_name`，直接停掉旧字段的写入会让旧客户端拿到过期值。等旧客户端退出后再讨论删除；目前还没有退出日期。请重点看同一次更新里两个字段是否可能出现不一致。

This can remain substantially intact. It provides a compatibility reason, a dependency, an unresolved date and a specific review question. Reducing it to “Keep dual writes for compatibility” would remove information needed to assess the decision.

## Implications for humanizer-zh

The existing purpose-based editing approach can support this work through a small conditional addition. Issues and PRs need guidance about the information that supports their readers' decisions, alongside the existing language, precision and voice protections.

The addition should cover two judgments: make reported problems or proposed improvements actionable, and make submitted changes reviewable. It should bring the concrete subject into the title or opening, preserve meaningful evidence and reasoning, use the project's required form, and scale detail to the task. It should explicitly distinguish unprovided evidence from negative results.

It should avoid a new universal voice, a fixed word count, mandatory sections, exhaustive file-by-file summaries and a checklist of claims to manufacture. It should also preserve the current editing boundary: creating or polishing a description does not authorize running its sample commands, changing the implementation or publishing the text.

Behavioral evaluation should include concise fixes, detailed proposals, incomplete observations, supplied templates, changes with important validation limits, tightly scoped wording requests and unrelated expressive writing. Success requires usable information, fidelity and appropriate emphasis. Shorter output alone is insufficient evidence of improvement.

## Sources

The rolling guides below were checked on 12 September 2026. Their project-specific tooling, submission rules and English syntax conventions are not universal requirements for Chinese editing.

[^1]: GitHub. [Helping others review your changes](https://docs.github.com/en/pull-requests/concepts/helping-others-review-your-changes). Rolling documentation. Context, focused scope, reviewer guidance and review of generated summaries.

[^2]: Google Engineering Practices. [Writing good CL descriptions](https://google.github.io/eng-practices/review/developer/cl-descriptions.html). Rolling guidance. Opening, durable rationale, sufficient context and updating the description as the change evolves. CL conventions inform PR editing but are not identical to all PR workflows.

[^3]: Mozilla. [Bug Writing Guidelines](https://bugzilla.mozilla.org/page.cgi?id=bug-writing.html). Rolling project guidance, including some legacy browser-specific material. Summary, reproduction, observed versus expected behavior, and uncertainty.

[^4]: Microsoft / VS Code. [Submitting Bugs and Suggestions](https://github.com/microsoft/vscode/wiki/Submitting-Bugs-and-Suggestions). Wiki revision displayed as 23 June 2025. Focused reports, copyable evidence and reproduction information.

[^5]: Django. [Reporting bugs and requesting features](https://docs.djangoproject.com/en/dev/internals/contributing/bugs-and-features/). Development documentation. Distinct needs for bug reports, feature use cases and project-specific proposal routing.

[^6]: GitLab. [Merge requests workflow](https://docs.gitlab.com/development/contributing/merge_request_workflow/). Rolling contribution guidance, particularly description of changes and UI requirements. Local requirements illustrate why a universal minimal format would be inappropriate.

[^7]: GitHub. [About issue and pull request templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/about-issue-and-pull-request-templates). Rolling documentation. Templates and forms express repository-specific information requirements.

[^8]: Linux Kernel Documentation. [Submitting patches: the essential guide to getting your code into the kernel](https://docs.kernel.org/process/submitting-patches.html), “Describe your changes.” Rolling guidance. Problem, impact, evidence, trade-offs and a self-contained explanation. Email-patch and commit formatting rules remain project-specific.

[^9]: Rust project. [RFC template](https://github.com/rust-lang/rfcs/blob/master/0000-template.md). Current master version. Motivation, design, drawbacks, alternatives and unresolved questions; evidence that substantial explanations can be necessary in a proposal workflow.

[^10]: Nicolas Bettenburg, Sascha Just, Adrian Schröter, Cathrin Weiss, Rahul Premraj and Thomas Zimmermann. [What Makes a Good Bug Report?](https://thomas-zimmermann.com/publications/files/bettenburg-tr-2008.pdf), technical report, revision 1.1, 12 March 2008. Author-hosted full report; survey and sample description support the limited claims used here. Historical evidence from three projects, not a current AI-writing study.

[^11]: Shirin Pirouzkhah, Pavlína Wurzel Gonçalves and Alberto Bacchelli. [The Value of Effective Pull Request Description](https://arxiv.org/html/2602.14611v1), arXiv v1, 16 February 2026; MSR 2026, DOI [10.1145/3793302.3793368](https://doi.org/10.1145/3793302.3793368). Methods, findings and threats to validity. Repository data originates in the 2019 GHTorrent release; findings are not a measurement of present-day AI use.

[^12]: Tao Xiao, Hideaki Hata, Christoph Treude and Kenichi Matsumoto. [Generative AI for Pull Request Descriptions: Adoption, Impact, and Developer Interventions](https://arxiv.org/html/2402.08967v1), arXiv v1, 14 February 2024; related publication DOI [10.1145/3643773](https://doi.org/10.1145/3643773). Early Copilot adoption, observed editorial interventions and validity limits. Its outcome estimates should not be generalized to all current tools or projects.

[^13]: GitHub. [Application card: GitHub Copilot inline suggestions](https://docs.github.com/en/copilot/responsible-use/inline-suggestions), sections on PR text completion and limitations. Rolling product documentation. Used for the specific limitation concerning inaccurate generated PR text, not product availability or model-performance comparisons.

[^14]: GitHub. [Communicating on GitHub](https://docs.github.com/en/get-started/using-github/communicating-on-github). Rolling documentation. Distinguishes issue, PR and discussion purposes without implying that an editor should relocate an existing task.
