# Receipt template rules: worker_error kickbacks

Lifted by yokoten wo-20261107-0d6d863c from gregore corrective action wo-20261106-d09715ba, where the worker_error kickback rate fell from 0.01 to 0.00 over the next 10 orders. Applies to every receipt and production order. Review-by: 90 days after this action verifies.

## Why

Eight kickbacks in gregore were classed `worker_error` — the receipt was clear and the worker still did not do it. Every one of the eight is a **mechanical** failure, not a judgement failure. Read together they fall into exactly three shapes, and none of the three is caught by the tripwire today.

The tripwire (`cortex/src/work-orders/tripwire.ts`) checks `scope_out`, `test_lock` and `interface`. All three ask *"did the worker touch something it should not have?"* None asks *"did the worker touch the thing it was told to?"* A PR that changes nothing, or changes the wrong file, passes all three checks clean.

| Order | What happened | Shape | Rule |
|---|---|---|---|
| wo-20261016-c752ef03 | PR #496 contained 0 files; the T0 action classes and template cache were never built. | empty | W1 |
| wo-20261030-1ee74dfe | PR only added an audit report; ENF-04 enforcement and the routing ladder changes were not implemented. | empty | W1 |
| wo-20261030-b5ac5baf | Spec stored as `david/DREAM_RIG.md`; the order required `david/DREAM_RIG.html`. | wrong path | W2 |
| wo-20261015-d47dc487 | Rule written to `areas/free-credits.md`; the order required `david/WORKING_AGREEMENTS.md`. | wrong path | W2 |
| wo-20261025-3c09ad7e | `cortex/src/effector-tools.ts` was not changed, so the timeout fix never landed. | absent | W3 |
| wo-20261030-b5ac5baf | Header references (artifact URL, three brain.db entries, four order ids) missing from the file. | absent | W3 |
| wo-20261012-529d670b | Unrelated `freeModel` default change; `pool.ts` not in scope. | scope drift | W3 |
| wo-20261014-939f32c8 | Turned tool use off instead of capping results; removed `step` from the pool entry; `LANE_FAILED_TEXT` not implemented. | scope drift | W3 |

## Rules

**W1. A receipt that requires a change names the files it requires changed.** `required_paths` lists every path the order must modify. It is not `scope.in` (what may be touched); it is what must be touched. An order whose work is entirely additive or entirely a document names the file it creates.

**W2. A required path is written exactly, including the extension.** `david/DREAM_RIG.html` and `david/DREAM_RIG.md` are different paths. If the order names a file, that file is the deliverable; a near-miss is a miss. When the location is genuinely open, the receipt says so explicitly rather than naming a path it does not mean.

**W3. The receipt states the artifact, not the activity.** "Implement ENF-04 enforcement" is an activity; "`cortex/src/native/routing/tagger.ts` exports `tagTurn` and `ring-evaluator.ts` calls it" is an artifact. A receipt whose body can be satisfied by a report about the work is not a receipt. Where the deliverable is a set of references or values inside a file, the receipt lists them.

**W4. A PR that changes no file is never a delivery.** Zero files, or a diff confined to a report, audit or summary document, fails the order regardless of what the body says. This is the single most common worker_error shape and it is detectable without reading the diff.

## Enforcement

W1–W4 are checkable from the PR file list alone, which is what the tripwire already receives. The check is: every path in `required_paths` appears in the PR's changed files, and the PR is not empty.

**That check does not exist yet.** `tripwire.ts` has no `required_paths` handling, and adding it is cortex code — outside this action's `scope.in` (receipt templates). Until it lands, these rules bind the receipt author, not the machine. A separate order is required to enforce them; without it this document has the same status as R1–R5: correct, and unread by anything that gates a PR.

## Check

The action closes only when the project's worker_error kickback rate over the next 10 orders falls below baseline. A rule that never prevents a kickback is pruned at review-by.

## Related

`docs/receipts/RECEIPT_TEMPLATE_RULES.md` covers the `environment` class (R1–R5). The two documents are complementary: R1–R5 govern what the receipt *declares* so a reviewer is not misled; W1–W4 govern what the receipt *requires* so a worker cannot deliver nothing.
