# Acceptance-criteria audit: r5-holdout-02

## Scope and conclusion

This audit uses only the `r5-holdout-02` entry in `/tmp/humanizer-zh-r5-holdout.json`: its request, supplied material, expectations, and rationale. No generated answer, reviewer result, repository, skill, or other task was consulted. The original case files were not modified.

The case has a sound core: produce two useful review replies from the current implementation and actual test state. Several expectations nevertheless mix required answers with optional implementation detail. In particular, the reply need not enumerate every fallback branch, explain repeated reads of an unchanged bad value, or reproduce every test count. Conversely, the full-suite status is a direct review question and must not be treated as optional.

## What the request actually requires

The deliverable is two numbered Chinese replies suitable for the two reviewers, retaining technical identifiers when used. Their necessary information is:

1. Explain the parse-failure behavior and disposition of the saved value: the current read falls back to defaults without deleting, replacing, or broadly clearing stored data. Answer whether normal configuration and additional fields are preserved, consistently with the current merge behavior.
2. State that this change does not add `schema version` or `migration`, without promising a migration schedule. Respond to the test gate: the full suite is not all green and has an unresolved snapshot failure. Do not turn the font hypothesis into a confirmed explanation or imply the gate is already satisfied.

The source packet supports those answers. It does not require a branch-by-branch code walkthrough, a list of all covered tests, a new implementation proposal, or a commitment to merge or undertake separately scoped work.

## Audit of the original expectations

| Criterion | Required core | Optional or excessive element |
| --- | --- | --- |
| 1. Two numbered, usable Chinese replies | Valid as written. Each reply must answer its corresponding review, rather than merely provide unrelated technical facts. | It should allow multiple natural phrasings and ordinary brief context. |
| 2. All fallback branches and current implementation | Parse-failure fallback and use of the current implementation are required. Claiming deletion or replacement of the saved value would materially misanswer the first reviewer. | Requiring explicit descriptions of a missing key and every non-object result exceeds the question. Those branches are background. A reply can omit them, and the detail that the default object is copied, without losing the requested answer. Any branches it chooses to discuss must be described accurately. |
| 3. No clearing/writing; bad value remains and is read again | The first reviewer directly asks how the old value is handled. Saying the read does not clear storage or delete/overwrite `panel:prefs` answers that concern. An equivalent concise statement such as read-only fallback can cover these facts together. | An additional explanation that subsequent reads encounter the same bad value is a valid consequence, but optional completeness. It is not a separate required disclosure once the unchanged saved value is clear. |
| 4. Merge behavior and lack of field validation | The reply must answer preservation of normal configuration and additional fields truthfully. The existing configuration takes precedence over defaults, and unknown fields are retained in the returned object. A contradictory claim would be material. | Do not require the wording “ordinary object,” a literal spread-expression explanation, or an explicit disclaimer about field validation when no broad validation claim is made. A functional explanation that defaults fill gaps while existing and unknown fields are retained is sufficient. Claims of comprehensive field validation remain unsupported. |
| 5. No migration and no invented future work | No `schema version` or `migration` is included. A promised version, deadline, or scheduled migration would contradict the author's explicit limit. | The blanket ban on “other future actions not in the material” is too broad. A modest conditional response to the review gate—waiting for the outstanding failure to be resolved before treating the suite as green—is grounded in the review. It should not fail merely because that exact future-facing sentence was not supplied. Substantial new commitments, dates, or scope are different. |
| 6. Test counts, introduced by “if reporting tests” | The full-suite status must be answered. It is not optional: the reviewer explicitly asks about the all-green gate. Claiming all green, or substituting focused-test success for the full-suite answer, would be material. | Reporting the focused run and reproducing every numeric count are optional. A clear statement that the full suite still has an unresolved snapshot failure is sufficient. If counts or focused results are included, they must remain accurate and clearly distinguished. |
| 7. Snapshot identity and unresolved cause | The unresolved current failure must not be presented as fixed, explained, or proven unrelated. The font explanation is only a guess. | The exact full test label, the detailed review history, and the font hypothesis itself need not all appear. Naming the failing test is useful, but an otherwise clear answer that the full suite has an unresolved snapshot failure is not a material failure merely for omitting its full label. |
| 8. Technical identifiers and unsupported artifacts | No invented commits, links, or deployment records. Concrete identifiers used in the replies should remain as supplied. | “Preserve their meaning” is weaker than the user's request to keep technical identifiers unchanged. Tighten this to identifier fidelity when used, without requiring every identifier from the packet to appear. Ordinary Chinese explanation and omission of an unnecessary identifier are not renaming it. |

## Missing or under-specified necessary checks

- **Explicitly require an answer to the full-suite question.** Criterion 6 currently begins conditionally. The combination of the review and the requested reply makes an affirmative disclosure that the suite is not all green necessary. Merely avoiding a false success claim is not enough if the reply sidesteps the question.
- **Apply exact preservation to identifiers that the answer uses.** The request is stronger than preserving technical meaning alone. This should not become an identifier-coverage checklist.
- **Assess substantive coverage across the replies.** A response that answers only the storage-clearing concern but omits normal/additional-field preservation, or answers only migration but omits the test gate, fails to answer the corresponding review. This is implicit in criterion 1 but worth making explicit.

No extra requirement is justified to explain every supplied code branch, state a root cause, propose a fix for the snapshot test, promise a new schedule, or narrate the earlier abandoned design.

## Material failure versus optional completeness

Material failures include describing the abandoned storage-writing implementation as current; failing to answer what happens to the saved value; misrepresenting preservation of existing/additional fields; claiming or scheduling a migration against the supplied limits; evading the full-suite question; implying the unresolved suite is green; or treating the font guess as confirmed. Failure to produce the requested two numbered Chinese replies, or altering a technical identifier that is actually used, also violates the deliverable.

Optional completeness includes enumerating missing-key and non-object branches, explaining repeated reads of the retained bad value, discussing fresh default-object copies, listing focused-test coverage, repeating every test count, giving the complete failing-test label, or proactively stating the lack of field-level validation. These details can improve an answer when relevant, but their absence alone should not make a substantively correct reply fail. If included, their factual accuracy still matters.

This audit concerns criterion validity only. It makes no judgment about any generated answer and recommends no change to the editing skill.
