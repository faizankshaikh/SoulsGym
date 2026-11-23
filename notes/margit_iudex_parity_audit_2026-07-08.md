# Margit vs Iudex Parity Audit (2026-07-08)

Purpose:

- Document current functional parity between Margit and Iudex env paths.
- Record CE table evidence reviewed for Elden Ring pointer coverage.
- Identify what is implemented now vs intentionally pending.

## Summary

Current parity level is good for baseline reset and one-step interaction checks, but not yet complete for calibrated arena setup and phase transition parity.

## CE table cross-check (ER_TGA.CT)

Reviewed evidence in `ce_tables/ER_TGA.CT`:

- `GameDataMan` and `WorldChrMan` bases are present in table scripts.
- Player core values are present in `WorldChrMan` chains (Health/MaxHP/SP/FP style entries).
- `Last Grace` entry exists as `GameMan + 0xB30`.
- Player animation entries exist in `WorldChrMan` chains (`Current Animation`).

Concrete evidence samples reviewed:

- `Last Grace` via `GameMan` with offset `B30`.
- `Current Animation` via `WorldChrMan` chain rooted at `10EF8`.
- Player `Health` / `MaxHP` entries via `WorldChrMan` chain rooted at `10EF8`.

Implication:

- Existing Soulsgym Elden Ring pointers used by Margit are consistent with CE table structures at the base-chain level.
- No strongly validated new pointer was found in this pass that should replace current addresses immediately.

## Address parity status

Checked against `soulsgym/core/data/eldenring/addresses.yaml`:

Implemented and used:

- Player HP/SP/MP and max values
- Player pose and local pose records
- Player animation
- Lock-on
- Last grace
- Time
- Camera pointers
- Margit HP/MaxHP/Animation/AnimationTime/pose records

Status:

- No address changes applied in this audit pass.
- Existing mappings remain the best validated set for current env behavior.

## Functional parity matrix (Margit vs Iudex style)

1. Reset lifecycle parity:
   - Status: Implemented
   - Notes: Margit reset now follows the base lifecycle pattern with retry/error boundaries.

2. Arena setup fidelity:
   - Status: Partial
   - Notes: Guarded path exists; real coordinate calibration is still pending.

3. Phase handling:
   - Status: Partial
   - Notes: Phase 2 has explicit no-op warning path until calibration is available.

4. Action validity timing:
   - Status: Implemented (baseline)
   - Notes: Action flow is stable for smoke and random-step checks.

5. Lock-on resilience:
   - Status: Implemented (baseline)
   - Notes: Camera reset and lock-on attempts are integrated in reset path.

6. Critical animation handling:
   - Status: Implemented
   - Notes: Empty-list handling and unknown-animation fallback prevent hard failures.

7. HP/SP/MP reset semantics:
   - Status: Implemented
   - Notes: Reset semantics are deterministic and aligned with current training-safe behavior.

## Remaining gaps

- Calibrate real Margit coordinates in `coordinates.yaml`.
- Implement robust phase-2 transition setup rather than no-op warning path.
- Continue incremental animation ID mapping as new IDs appear in live runs.

## Reviewer guidance

For current PR scope, this parity/audit pass supports keeping addresses unchanged and focusing review on:

- profile additions in `scripts/run_envs.py`
- existing reset stability behavior
- explicit documentation of known pending parity gaps
