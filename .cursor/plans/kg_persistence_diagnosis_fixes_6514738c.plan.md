---
name: KG Persistence Diagnosis Fixes
overview: Diagnose KG write failures and empty properties, then harden mappers/validators so malformed artifacts cannot be persisted silently.
todos:
  - id: ssm-validate-semantic-fields
    content: Add a sequential two-layer pre-insert validation chain in story_state_manager_subgraph (semantic gates + strict schema validation) with explicit failure reporting
    status: pending
  - id: mapper-preserve-properties
    content: Update brain_persistence_mapper to preserve non-nested artifact data into properties or reject with explicit errors
    status: pending
  - id: tests-regression-coverage
    content: Add regression tests for blank edge endpoints, flat node artifacts, and unsupported edge types
    status: pending
  - id: verify-e2e-kg-quality
    content: Run targeted + E2E tests and confirm persisted KG docs no longer have empty properties or blank endpoints
    status: pending
isProject: false
---

# Harden KG Persistence Pipeline

## Confirmed Failure Sources
- `tests/test_e2e_full_stack.py` intentionally points E2E to `novelwriter_test_kg` (autouse fixture sets `MONGODB_DB_NAME`).
- `src/story_state_manager_subgraph.py` normalizes node/edge records without validating required semantic fields:
  - `_normalize_add_node()` accepts missing/empty `properties` and still emits write payload.
  - `_normalize_add_edge()` accepts empty `from_node` / `to_node`, allowing blank endpoint edges.
- `src/brain_persistence_mapper.py` also drops non-nested fields by coercing `properties` via `_ensure_dict(record.get("properties"))`; when workers emit flat records, persisted `properties` becomes `{}`.
- `src/kg_models.py` rejects unsupported edge types (`MEMBER_OF`), which explains the observed partial batch failures and retries in E2E logs.

## Implementation Plan
- Keep `story_state_manager` as the existing subgraph, and add a **sequential two-layer pre-insert validation chain** in `src/story_state_manager_subgraph.py`:
  - `collect_and_normalize_payload` -> `validate_required_shape` -> `validate_semantics` -> `validate_strict_type_schema` -> `filter_or_fail_invalid_records`.
  - **Layer 1 (semantic gates):** reject empty node `properties`, reject blank edge endpoints, reject unsupported edge types.
  - **Layer 2 (strict schema):** validate each record against runtime type-specific schemas (Pydantic-backed contracts aligned to `kg_models` and expected worker payload contracts), not only prompt text.
  - Add explicit `records_failed` reasons for `invalid_properties`, `missing_endpoints`, `invalid_edge_type`, and `schema_validation_failed`; only valid records continue to contradiction checks and writes.
- Harden `src/brain_persistence_mapper.py` normalization:
  - For node adds, synthesize `properties` from record residual keys when nested `properties` is absent.
  - For edges, keep strict endpoint requirement and normalize aliases (`from_node`/`from`, `to_node`/`to`); optionally map safe relationship aliases.
- Add/adjust tests in `tests/test_story_state_manager.py` and `tests/test_brain_persistence_mapper.py`:
  - Assert invalid edge records cannot persist (`from`/`to` blank).
  - Assert flat node payloads are either normalized into non-empty `properties` or rejected deterministically.
  - Assert unsupported edge types are reported as failed records, not silently mutated.
  - Assert strict per-type schema validation failures are surfaced as `schema_validation_failed` with deterministic record-level errors.
- Re-run targeted tests first, then E2E to verify:
  - No blank endpoint edges.
  - No empty `{}` `properties` from non-empty source artifacts.
  - Reduced SSM failure retries and worker-history churn.