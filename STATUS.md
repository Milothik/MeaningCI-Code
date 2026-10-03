# Status

Architecture reviewed; standalone code experiment created without altering the text experiment.

1. Dataset/harness complete: 31 JSON-compatible upstream programs, 93 pairs, all nine graph exclusions recorded. Ten core tests pass; 945 unique executions measured with bounded subprocesses.
2. Baselines/analysis complete: syntax controls, budgeted/full tests, conventional timeout-failing CI, native Jev parser, explicit abstention, program-cluster bootstrap and paired McNemar.
3. Development/validation collection complete: 69 verified native Jev 1.13.0 captures. One test capture used for UI contract validation is retained and disclosed. JSD threshold selected on all 24 validation pairs: 0.03 bits; confidence gate fixed at 0.65. Threshold selection saved before remaining test requests.
4. Validation is adverse: MeaningCI JSD has 18 abstentions and correctly classifies only 4/24; direct Jev 22/24. Input-only predicates have limited behavioral coverage. No questions or model settings will be tuned on the held-out set.
5. Held-out collection/analysis complete: 93 verified native requests, 2,325 decisions, no missing or substituted model measurements. Reserved test: MeaningCI JSD 9/24 (13 abstentions, 2 false positives); direct Jev 21/24; conventional CI tests 24/24. Frozen validation threshold remains 0.03 bits. Negative architecture finding preserved.
6. Reproduction/audit complete: 13 tests pass; saved-execution + native-capture replay reproduces summary exactly. Mechanically generated controls show no observed behavioral differences on completed fixtures. Slow reference cases and all timeouts remain recorded.
7. Report/figures complete: reports/benchmark_report.md, heldout_accuracy.svg, paired_intervals.svg. Exact program-level sign-flip analysis added alongside paired McNemar and cluster bootstrap; results remain exploratory.
8. GitHub: private Milothik/MeaningCI-Code created; uploading final source and artifacts. No claim of production readiness or commercial advantage.
