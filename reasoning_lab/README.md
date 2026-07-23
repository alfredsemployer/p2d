# p2d reasoning lab

This directory contains the reproducible experimental pipeline built against
version 0.3 of the epistemic and argumentation specification.

It has four deliberately separate parts:

- a budget-enforced OpenRouter client and Kimi K3 pipeline rerun;
- deterministic and model-assisted evaluation harnesses;
- Z3-backed propositional and SMT validation with explicit formalization
  fidelity metadata.
- a deterministic artifact compiler that separates signed claim valence,
  evidence depth, research coverage, source dependence, defeasible
  acceptability, and visual projection.

Credentials are read from `OPENROUTER_API_KEY` or an explicit external key
file. They are never written to a run artifact. Every API call is written to a
cost ledger using the cost returned by OpenRouter. The runner refuses new work
when its conservative reservation would cross the configured budget.

Example:

```bash
python -m p2d_reasoning_lab.cli pipeline \
  --question "What is the significance of Kimi K3?" \
  --budget 3.00 \
  --key-file /path/outside/repository/to/key
```

The default pipeline is intentionally bounded: three discovery framers, one
portfolio merge, three active research questions, six to ten research-target
claims, two web-search lanes per claim, adversarial claim adjudication, native
post-evidence graph compilation, and a final answer-bundle audit.

The compiled `reasoning_artifact.json` is the single source for verdicts and
visualization. Claims are vertices; arguments and defeaters are relations;
grounds and sources remain provenance records. Every claim has a stable
fingerprint, explicit signed valence, calibration state, evidence-depth record,
coverage record, and source-dependence analysis. Visual card designations are
derived only from graph topology.

The run is fail-visible. Deterministic validation rejects graphs with missing
claims, missing argument attempts, invalid references, dependency cycles, or
active questions without terminal claims. Post-evidence completion represents
support as Argument hyperedges and attacks on those inferences as Defeater
relations:

```bash
python -m p2d_reasoning_lab.cli complete \
  --run-dir /path/to/run --budget 3.00 --key-file /external/key
python -m p2d_reasoning_lab.cli repair-completion \
  --run-dir /path/to/run --budget 3.00 --key-file /external/key
python -m p2d_reasoning_lab.cli revise-answer \
  --run-dir /path/to/run --budget 3.00 --key-file /external/key
```

Evaluation can be repeated with independent model families while sharing the
same append-only cost ledger:

```bash
python -m p2d_reasoning_lab.cli evals \
  --run-dir /path/to/run --eval-model google/gemini-2.5-pro \
  --output-subdir evals-independent-gemini \
  --budget 3.00 --key-file /external/key
```

Formal validation supports a restricted propositional syntax and arbitrary
SMT-LIB2 satisfiability checks:

```bash
python -m p2d_reasoning_lab.cli formal entail \
  --premise 'implies(P, Q)' --premise P --conclusion Q
python -m p2d_reasoning_lab.cli formal smt2 assertions.smt2
```

Z3 results establish consequences of the supplied formalization only.
Formalization fidelity remains a separate field, and unsuitable empirical or
defeasible arguments are explicitly left unformalized.

Legacy runs can be upgraded only with explicit signed-valence decisions. The
migration refuses to infer direction from a legacy `insufficient` or coverage
label:

```bash
python -m p2d_reasoning_lab.cli migrate-v03 \
  --run-dir runs/20260723-kimi-k3-v02 \
  --valence-decisions evals/kimi_v02_valence_migration.json
```
