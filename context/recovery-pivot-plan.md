# High-Upside Recovery Plan

## Summary

Stop investing in the current V3 direction. Its completed cached validation is 0.8436, below V2’s logged 0.8755; it has no evidence of approaching 0.98.

V3 also cannot reach test inference as written: it formats a per-country threshold dictionary as a float when creating the progress filename.

The public gap is not a threshold-tuning problem. The current pipeline has an unmeasured candidate-recall ceiling, drops some true pairs at blocking, and overwrites calibrated model scores with uncalibrated generic retrieval scores.

A 0.98–0.999 result within 20 hours is unlikely from this codebase. It becomes plausible only if the data has a strong recoverable structure that is currently unused: deterministic address/name transformations and corroboration between S2 and S3 records for the same S1 entity.

## Key Changes

Preserve the 0.770 V2 submission as the rollback baseline and run all recovery work in an isolated experiment/cache namespace.

Repair the V3 inference blocker, but do not use V3 as the primary bet until it clears the gates below.

Build a diagnostic ledger for every validation false negative and false positive, with five exclusive causes: absent from candidates, rejected by score threshold, lost by one-to-one assignment, rejected by number rule, or changed by reranking.

Measure candidate recall separately for S2/S3 and US/India before training any new model. A missing candidate is unrecoverable; candidate recall must be near the intended score ceiling.

Replace the single semantic top-25 retrieval with a union of compact retrieval paths: multilingual semantic retrieval, character-level lexical retrieval, address-led retrieval, name-led retrieval, and high-confidence S2↔S3 linkage. Deduplicate candidates before scoring.

Add entity-level corroboration: use confident S2/S3 matches as anchors, then use matching S2/S3 variants to resolve aliases with weak individual similarity. Enforce each S2/S3 ID’s one-to-one S1 assignment.

Train a task-specific pair judge on labeled positive pairs plus mined hard negatives from the new candidate union. Do not overwrite supervised probabilities with raw MS MARCO scores. If a cross-encoder is used, fine-tune or calibrate it on this task and blend only after validation.

Tune source- and country-specific decision rules from held-out evidence. For France, choose thresholds from the worse of US→India and India→US transfer tests; France cannot be honestly calibrated from the available labels.

## Acceptance Gates

Candidate recall: report by source and country; do not run full inference if it cannot support the target score.
Matching quality: beat V2’s 0.8755 on the existing split and avoid a material decline on both leave-country-out tests.
Error mix: blocking misses must no longer dominate false negatives; false positives must be explained by a concrete recurring pattern before adding a rule.
Runtime: one complete inference and output-validation pass must fit before the deadline using cached embeddings, candidates, features, and model checkpoints.
Submit only an output that beats 0.770 locally under the stronger validation suite; retain V2 unchanged for rollback.

## Assumptions

The aim is maximum upside, with the 0.770 submission protected.

No external identity data is used.

Existing running work remains untouched; implementation begins only in an isolated experiment after Plan Mode.

The top scores may reflect a discoverable dataset-generation pattern, but no local evidence currently proves that. If the candidate-recall and cross-source diagnostics do not reveal one quickly, a jump from 0.770 to 0.98 is not realistic in the remaining window.