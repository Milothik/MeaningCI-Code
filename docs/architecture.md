# Architecture review before implementation

MeaningCI's existing provider, vector comparison and content-addressed evidence design are reusable concepts. Its policy parser, ternary rule semantics and automatic probe generator are not suitable for Python. This project is a separate small repository, preserving the completed text experiment.

## Debt and improvements

- Code equivalence is undecidable in general; PASS must mean only no detected change on the tested observations. Execution tests are the primary baseline, not a competitor to dismiss.
- The full redundant text battery lost to direct questions. Start with a small deterministic input-only behavioral battery; measure direct code-pair judgment on the same model and cases.
- QuixBugs is a public, small algorithm benchmark, not production repositories. Its known bugs can be in model training data. Do not generalize findings to enterprise refactoring.
- Separate `dataset` (input-only probe construction), `execution` (bounded subprocesses), `providers` (native Jev responses), `evaluation` (gold access only after prediction), and `analysis` (paired cluster intervals and exact McNemar).
- Record all 40 upstream program names. The initial adapter covers all 31 with JSON inputs. Nine graph-object programs need an explicit graph serializer and remain excluded for that structural reason, never because of method performance.
- Generate presentation and alpha-renaming controls mechanically. Validate them by AST checks and the full official input suite; keep failures visible.
- Deterministic split by program prevents related controls leaking across splits. Freeze protocol and thresholds before held-out inference. Do not optimize on the test set.
- Local execution is for pinned reviewed public benchmark code, not an arbitrary-code security sandbox. Timeouts contain hangs; they do not contain malicious code. A future upload service requires OS/container isolation, limits and no credentials/network.
- Model uncertainty, missing measurements and execution timeouts are explicit. No synthetic substitute for failed Jev requests.
- Shared batched Jev collection has shared cost/latency. Do not attribute the entire batch separately to each method or call replay wall time inference time.

## Interface

A pair contains code A, code B and deterministic observations derived only from input fixtures. The collection request asks separate A/B behavioral predicates plus one direct pair judgment. Both see the same pair context; this is not an independent source-free code checksum experiment. Evaluator-only JSON contains labels, upstream expected outputs and measured outcomes. Providers never receive that file.

No automatic probe generation from gold outputs, failed tests or corrected-versus-buggy differences. An evaluator-only ORACLE diagnostic reports whether the selected inputs and predicates could detect a real difference even with perfect code understanding.

