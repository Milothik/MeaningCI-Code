# Decision after the first code experiment

Do not ship the fixed MeaningCI code probe battery as a CI correctness gate. In the held-out set it correctly classifies 9/24, against 21/24 for direct Jev and 24/24 for conventional execution CI. It abstains on 13 and falsely flags 2 preserving changes. Requiring all tested behaviors to be reliable protects against false PASS but collapses useful coverage. Broad predicates lose exact numerical/string-output differences. These are design findings, not evidence that every possible semantic-probe approach fails.

Keep execution tests as the primary check. Direct Jev can be investigated as supplementary change triage, but it misses defects and abstains; its 21/24 on small public algorithms is not a production guarantee. Do not claim probe cost savings: batches share context and overhead, and no standalone per-method billing was collected.

A follow-up should generate concrete, reviewed behavioral scenarios from source specifications without gold outcomes; compare against a general-purpose code-review LLM, source-grounded test generation and existing tests. Use independently chosen real project revisions, negative controls that include genuine refactors, cluster by project, and evaluate mutations/side effects/contracts—not just output truthiness. Register the new protocol before evaluation. Do not retrofit questions to these held-out defects.

This repository delivers the prototype, the complete negative first experiment, reproducible measurements and the evidence needed to challenge the architecture. No automatic repair, deployment service or enterprise equivalence certification is claimed.
