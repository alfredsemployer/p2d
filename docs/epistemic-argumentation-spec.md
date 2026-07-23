# Epistemic and Argumentation Specification

**Status:** Working foundation, version 0.3  
**Date:** 2026-07-23  
**Scope:** Open-ended research, descriptive synthesis, comparative assessment, bounded interpretation, and specification of preference-conditional decision/advice composition  
**Deferred release modes:** Forecasting, causal estimation, decision/advice execution, and legal adjudication require their specialized contracts and release gates

**Version 0.2 revision:** Adds explicit verdict policies, non-destructive claim correspondence, search coverage and quantitative normalization records, warrant-fidelity assessment, dependence sensitivity, abstention evaluation, and separate structural versus judgment validation.

**Version 0.3 revision:** Adds the artifact–agents–projections system shape, closed-vocabulary contract composition, stable claim fingerprints, explicit signed valence, separate research-coverage and evidence-depth records, source-dependence clustering, native post-evidence graph compilation, challenge and explain sessions, personalization boundaries, trust profiles, and the roadmap sequencing required by stable node identity.

## 1. Purpose

This document defines the intellectual and computational commitments of the p2d reasoning system. Its purpose is not to make model output look rigorous. Its purpose is to make the route from question to answer inspectable, criticizable, and mechanically constrained where possible.

The system must answer five different questions without collapsing them:

1. What exactly are we trying to determine?
2. What propositions would resolve that inquiry?
3. What grounds are available for or against those propositions?
4. What inferences connect those grounds and propositions?
5. What conclusion is warranted after accounting for uncertainty, dependence, objections, and missing information?

The central object is a **shared claim-and-argument graph**. Claims are vertices. Arguments are directed hyperedges from one or more premises or grounds to a conclusion. Sources, citations, questions, assessments, and answer prose belong to associated layers; they are not all forced into the logical graph.

### 1.1 System shape

The product has three ordered architectural levels:

1. **Artifact:** the persistent, typed claim/argument/provenance structure and its invariants. It is shared state, durable across runs, sessions, and users.
2. **Agents:** replaceable model or human passes that populate, inspect, and assess the artifact. Agent choice does not determine artifact identity or schema.
3. **Projections:** replaceable prose answers, graph views, curricula, debates, and other surfaces derived from the artifact. No projection is the artifact itself.

The artifact schema is stabilized before orchestration and interface work; both compile against it. Agents plus visualization without a typed artifact are an explicit anti-goal.

## 2. Normative commitments

These are product invariants, not stylistic preferences.

### 2.1 Distinguish truth from justification

A proposition may be true without having been established by the available argument. An argument may fail without its conclusion being false. A supported conclusion is therefore a claim about the present state of justification, not an assertion of infallibility.

### 2.2 Distinguish premises from inference

The credibility of premises and the quality of the move from premises to conclusion are assessed separately. A valid argument with false premises does not establish its conclusion. True premises joined by a weak inference also do not establish it.

### 2.3 Treat ordinary reasoning as defeasible

Most research arguments are not deductive. They can be reasonable while remaining vulnerable to exceptions, competing explanations, measurement defects, selection effects, or new evidence. The system must represent rebutting and undercutting defeat rather than simulate deductive certainty.

### 2.4 Preserve both conflict and ignorance

“Substantial support exists on both sides” and “almost no useful evidence exists” are different epistemic states. They must never collapse into the same midpoint score.

### 2.5 Count independent evidence paths, not citations

Ten publications repeating one press release are one originating evidence path. Independence is a modeled and auditable relationship, not an assumption derived from URL count.

### 2.6 Make hidden warrants visible

The reconstructed inferential rule connecting grounds to a conclusion is often the most contestable part of an argument. It must be represented explicitly enough to test, criticize, and compare with alternatives, while remaining identifiable as a fallible reconstruction rather than an authoritative foundation.

### 2.7 Match assessment to claim type

Deductive validity, empirical support, causal identification, predictive calibration, interpretive adequacy, and normative acceptability are not interchangeable dimensions. There is no universal “confidence” label.

### 2.8 Preserve the boundary of formal proof

A proof establishes a consequence of a formal specification. It does not by itself establish that the specification faithfully represents the natural-language claim or the world. Formal validity and formalization fidelity are separate assessments.

### 2.9 Permit “unknown”

Insufficient, contested, malformed, and out-of-scope are legitimate results. The system must not turn lack of resolution into falsehood or manufacture precision to avoid abstention.

### 2.10 Make synthesis no stronger than the graph

Every material sentence in the final answer must be traceable to an assessed claim or an explicit unresolved question. Factual context is not exempt from provenance and support merely because it is labeled context. The writer may compress; it may not silently strengthen or introduce a new world-facing assertion.

## 3. The layered model

The system uses six related layers with different semantics.

### 3.1 Inquiry layer

The inquiry layer defines what is being investigated:

- `InitialQuery`
- `AnswerContract`
- `ResearchQuestion`
- `CandidateHypothesis`
- `QuestionDisposition`
- `CoverageRecord`

Questions are not claim nodes. They determine which claims would be answer-relevant and what standards must be met.

### 3.2 Argument layer

The argument layer contains inferentially active objects and explicit claim-identity relations:

- `Claim`
- `ClaimCorrespondence`
- `Argument`
- `Defeater`

Only claims are graph vertices. Arguments and defeaters are relations over claims and grounds. Claim correspondences govern canonical views without destroying the original vertices.

### 3.3 Provenance layer

The provenance layer records where asserted information came from and how it was transformed:

- `Source`
- `SourceSnapshot`
- `Ground`
- `Citation`
- `EvidencePath`
- `ExtractionActivity`
- `NormalizationRecord`

A source is an artifact, not evidence by itself. A citation is a locator and extraction record, not proof of support. A ground becomes evidence for a claim only through an assessed relevance and support relation.

### 3.4 Assessment and policy layer

This layer contains judgments about different targets and the explicit policies used to derive verdicts:

- `ClaimAssessment`
- `ArgumentAssessment`
- `GroundAssessment`
- `SourceAssessment`
- `CitationAssessment`
- `FormalizationAssessment`
- `NormalizationAssessment`
- `WarrantFidelityAssessment`
- `IndependenceAssessment`
- `VerdictPolicy`

Assessments retain their producer, method, inputs, time, and dissent. Policies retain their version, configuration, applicability, and validation record. Neither is baked irreversibly into the underlying objects.

### 3.5 Synthesis layer

The synthesis layer communicates what the inquiry established:

- `QuestionVerdict`
- `AnswerBundle`
- `AnswerSentence`
- `UnresolvedIssue`
- `InquiryFrontier`

An open-ended answer may contain multiple terminal claims. It need not be distorted into one proposition.

### 3.6 Interaction, learning, and user-policy records

Durable interaction records attach to versioned artifact objects without becoming claim vertices:

- `ChallengeSession`;
- `DeepeningJob`;
- `ExplainSession`;
- `LearnerModel`;
- `TrustProfile`;
- personalization-training and adapter provenance.

These records may trigger new inquiry, alter a user-specific projection, or supply candidate grounds. They never directly write world-facing verdicts or mutate the shared graph’s truth conditions.

### 3.7 Deterministic graph projection

A visual graph is compiled from the artifact under a versioned
`ProjectionContract`; it is not hand-curated independently of the graph.

- Active research questions appear as section headings, never as graph cards.
- Every claim in the terminal dependency closure appears as a card.
- A claim is an `answer` card exactly when it is terminal for that question.
- A claim is a `challenge` card when it is a premise of a defeater targeting an
  included argument.
- Every other included claim is a `support` card.
- Precedence is `answer` → `challenge` → `support` when a claim has more than
  one structural role in the same question projection.
- Arguments are solid directed relations; defeaters are dashed directed
  relations. Every visible relation begins at a visible claim card.
- Grounds, sources, citations, warrants, and arguments are available through
  inspection but are not cards.
- Columns are assigned by answer-first graph distance from a terminal claim;
  row ordering is stable and deterministic.

The card assessment has two visually separate axes:

1. **Signed direction:** every assessed claim carries an explicit credence-like
   score `p ∈ [0,1]` and signed valence `v = 2p − 1`. The card displays
   `supported` when `v ≥ 0` and `unsupported` when `v < 0`; exact zero is
   reserved for exact equipoise. This value must be produced and aggregated
   explicitly. It may not be inferred from `insufficient`, coverage, argument
   failure, or a UI label. Until calibrated against resolved cases, it is
   labeled `uncalibrated` and must not be described as an empirical probability.
2. **Evidence depth:** a separate, versioned summary of the depth of the
   supporting record, displayed on a five-segment or equivalent bounded scale.
   It is not belief, truth, or research completeness.

Research coverage remains a third, inspectable field on the artifact. Its
Harvey mapping records search breadth and stopping conditions only. It is not
substituted for evidence depth or signed valence.

The underlying four-way evidential state (`supported`, `refuted`, `contested`,
`insufficient`) is preserved in the artifact and inspection view. A projection
must not rename it “confidence.” A probability or graded confidence display is
permitted only when the artifact contains a separately validated calibrated
credence.

## 4. Inquiry objects

### 4.1 `InitialQuery`

The user’s unmodified wording, timestamp, and conversational context. It must remain preserved even after later operationalization.

### 4.2 `AnswerContract`

The answer contract makes the interpretation of the query explicit:

- referent and entity resolution;
- time or “as of” boundary;
- geographic or institutional scope;
- comparison class;
- dimensions to cover;
- excluded meanings;
- requested level of detail;
- applicable proof or decision standard;
- modes that are unsupported or deferred.

Material ambiguity produces competing candidate contracts or a clarification request. It must not be resolved invisibly.

#### 4.2.1 Contract library and composition

The planner performs **generative composition over a closed vocabulary**. The contract library initially contains:

- empirical;
- quantitative;
- forecast;
- interpretive;
- decision/advice.

Each versioned contract fixes its admissible evidence, verification method, verdict vocabulary, calibration class, deterministic stage spine, and deliverable template. The planner may compose contracts but may not invent a new contract at runtime.

Typing occurs at the subquestion level because ordinary queries are hybrids. For example, a decision may combine measured facts, forecasts, constraints, and preferences. Generative fan-out is confined to declared slots such as question portfolios, hypotheses, defeaters, and degeneracy allocation.

Recomposition keeps contract seams visible. An established fact, a calibrated forecast, and a preference-conditional recommendation remain differently warranted parts of one answer; they must not be blended into one generic confidence statement.

Interpretive and decision/advice contracts are specified by this version. Decision/advice execution remains release-gated until preference handling, forecast inputs, and recommendation-specific evaluation meet their declared floors.

### 4.3 `ResearchQuestion`

A research question is a bounded issue that can receive a recognizable answer. Required fields:

- stable ID;
- natural-language question;
- question type;
- scope and timeframe;
- why it matters to the original query;
- admissible answer form;
- resolution criteria;
- priority dimensions;
- answerability estimate;
- framing provenance;
- disposition and disposition reasons.

Recommended question types:

- proposition assessment;
- comparative assessment;
- descriptive magnitude;
- explanatory or abductive;
- causal;
- predictive;
- interpretive;
- normative;
- decision.

The type routes the question to an assessment contract. Causal, predictive, normative, and decision questions must not pass through a generic descriptive pipeline.

### 4.4 Question portfolio

Open-ended queries first produce a **question portfolio**, not an immediate answer graph. A broad discovery pass proposes candidate questions and competing hypotheses. This material is provisional: discovery sources help construct the inquiry but do not automatically become verified evidence.

Questions are ranked on visible dimensions:

- relevance to the initial query;
- expected user importance;
- explanatory leverage;
- capacity to change the overall interpretation;
- answerability with available methods and evidence;
- novelty or surprise;
- coverage diversity;
- estimated cost of responsible resolution.

The system should not hide these dimensions behind one unexplained score. A weighted score may be used for ordering only if the weights are visible and sensitivity-tested.

Question dispositions are:

- `active`;
- `deferred`;
- `covered_by_other_question`;
- `out_of_contract`;
- `requires_specialized_pipeline`;
- `currently_unanswerable`.

“Ghost” is a presentation treatment for non-active questions, not an epistemic dismissal. Every non-active question retains its provenance and disposition reasons and may be promoted later.

### 4.5 Candidate hypotheses

Hypotheses are proposed answers that organize inquiry. They are not yet established claims. Each hypothesis records:

- the candidate answer;
- discriminating observations;
- conceivable falsifiers;
- important alternatives;
- necessary auxiliary premises;
- confounders or rival explanations;
- generation provenance.

Abductive hypothesis generation and evidential justification are separate stages. Model originality in proposing a hypothesis must never count as support for it.

## 5. Claims

### 5.1 Definition

A `Claim` is a proposition that is:

1. inferentially active;
2. independently contestable;
3. sufficiently precise to assess; and
4. relevant to resolving at least one research question.

A claim is not simply any declarative sentence found in a source. Many truth-apt statements remain grounds because promoting all of them would obscure the inferential structure.

### 5.2 Required claim content

Every claim must record:

- stable ID and version;
- canonical proposition;
- polarity;
- modality;
- conditions and exceptions;
- temporal scope;
- geographic or population scope;
- comparison class, where applicable;
- operationalization or truth conditions;
- claim type;
- roles in particular arguments;
- research questions served.

Claims may additionally record:

- `magnitude`;
- `units`;
- `interval`;
- `weight`;
- `quantity_provenance`: `measured`, `converted`, `bridged`, `elicited`, or `model_estimate`.

Whenever `magnitude`, `interval`, or `weight` is present,
`quantity_provenance` is required. Units are required for dimensional
quantities. User-facing precision must be justified by the provenance,
normalization fidelity, and relevant calibration class; computation-internal
precision does not license unearned decimal places in prose.

Claims may also carry a `structured_reading` with subject, predicate, object or complement, semantic roles, or another domain-specific parse when it materially improves verification. These fields are optional. They must not be populated merely to satisfy a linguistic template.

Roles such as `premise`, `intermediate_conclusion`, `hinge`, `counterclaim`, and `terminal_claim` are contextual roles, not distinct node kinds.

### 5.3 Claim types

At minimum:

- empirical observation;
- quantitative;
- comparative;
- classificatory or definitional;
- conditional;
- statistical;
- causal;
- predictive;
- explanatory;
- interpretive;
- normative;
- mathematical;
- logical.
- preference;
- constraint.

These types determine permissible assessment dimensions and verification methods.

#### 5.3.1 Preference and constraint claims

Preference and constraint claims are ordinary inferentially active claims whose truth-maker is normally a holder’s avowal or an applicable constraint record rather than external empirical evidence.

They record:

- holder;
- elicitation provenance;
- scope;
- stability estimate;
- optional weight;
- consistency and update history.

Verification uses elicitation and consistency checking, including revealed inconsistency between stated weights and choices. A holder’s preference is not refuted by unrelated world evidence; it is defeasible by the holder’s update, scope correction, or demonstrated inconsistency.

Advice is ordinary practical inference over a graph containing empirical claims, forecasts, constraints, and explicit preference claims. No recommendation may conceal a value premise.

### 5.4 Atomicity

“Atomic” means atomic at the **decision-relevant verification grain**, not grammatically tiny.

A claim should normally be split when:

- different conjuncts can receive different verdicts;
- different conjuncts require different evidence or methods;
- the scope, comparator, or timeframe changes within the sentence;
- a falsifier can defeat one part without affecting the other;
- one part is reused independently elsewhere;
- one part is load-bearing while another is decorative.

A claim should not be split when the pieces have no independent inferential role and would always be assessed together.

The anti-conflation test asks:

1. Can the strongest supporting case and strongest opposing case both address the same reading?
2. Could reasonable assessors agree with one component and reject another?
3. Does the statement hide multiple predicates, populations, timeframes, or comparators?

If support and opposition succeed on different readings, the result is `malformed_conflated`; the claim is split and reassessed.

### 5.5 Promotion rule

A proposition-like ground is promoted to a claim node when at least one is true:

- it is used by multiple arguments;
- it is independently disputed;
- it requires a distinct verification method;
- changing it could change a terminal verdict;
- it is a synthesized conclusion;
- its uncertainty materially differs from the containing ground;
- a user is likely to want to inspect it directly.

Otherwise it remains a ground in the provenance layer.

### 5.6 Claim identity and correspondence

Claim identity is an assessed relation, not a string-matching side effect. A `ClaimCorrespondence` records a proposed relation between two versioned claims:

- `equivalent`;
- `entails`;
- `entailed_by`;
- `overlapping_scope`;
- `same_topic_distinct_proposition`;
- `unrelated`;
- `unresolved`.

It also records the producer, method, rationale, scope mapping, assessment reliability, and confirmation status. Correspondence operates over claim IDs, never raw claim text.

No semantic merge occurs silently. A candidate equivalence must be confirmed by a separate review pass or a human under the active policy. Even after confirmation, the original claim objects and their incident provenance are preserved. Analytics may use a canonical equivalence group or canonical view, but destructive vertex merging is prohibited.

An entailment correspondence does not itself create a valid inference. It proposes a strict argument whose scope and validity must be checked independently. An overlap relation keeps both claims and routes them to the atomicity and re-scoping audit.

Unconfirmed correspondence blocks any analytic operation that would require treating the claims as one object. It does not block analyses that keep them distinct. The matching system must favor conservative non-merging because a false merge can misdirect defeaters and double-count support without visible failure.

## 6. Grounds, sources, and evidence

### 6.1 `Source`

A source is an identifiable artifact: paper, dataset, filing, benchmark report, news article, interview, database response, web page, or direct observation record.

Required provenance includes author or responsible agent, publisher, publication time, retrieval time, immutable snapshot or content hash where possible, version, and derivation relations. Provenance should be compatible in spirit with W3C PROV’s distinction among entities, activities, and agents.

### 6.2 `Ground`

A ground is a bounded observation, measurement, quotation, or reported result extracted from a source. It contains proposition-like content but does not automatically occupy the argument graph.

Examples:

- “Evaluator E reports model M scored 57 on suite S under harness H.”
- “The published API price was $X per million output tokens on date D.”
- “The authors report a randomized comparison with sample size N.”

The ground must preserve qualifiers, units, population, procedure, and original context. An extraction that removes a material qualifier is defective even if the quoted words are accurate.

### 6.3 `Citation`

A citation connects a source snapshot to a ground and records:

- exact locator;
- quoted or structured extraction;
- extractor and method;
- transformation steps;
- whether the source directly states the ground;
- whether the extraction was independently checked;
- known ambiguities or omissions.

Citation accuracy and evidential relevance are separate assessments.

### 6.4 Evidence is a role

“Evidence” is not a primitive node kind. A ground functions as evidence only relative to:

- a target claim;
- an argument or reconstructed evidential warrant;
- a direction (`supports`, `opposes`, or `neutral`);
- an assessed degree of relevance and probative force.

The same ground may support one claim, oppose another, and be irrelevant to a third.

### 6.5 Source and ground assessment

Source quality is claim-relative, not a universal prestige score. Relevant dimensions include:

- authenticity and integrity;
- proximity to the event or measurement;
- domain competence;
- methodological transparency;
- risk of bias or strategic interest;
- representativeness;
- measurement validity and reliability;
- recency;
- directness to the target claim;
- precision;
- consistency with independent sources;
- publication or selection effects.

For empirical bodies of evidence, risk of bias, inconsistency, indirectness, imprecision, and dissemination bias should be explicit dimensions rather than hidden deductions from a single quality label.

### 6.6 `EvidencePath`

An evidence path traces a ground to its originating observation, dataset, experiment, press release, or witness. Two grounds are not independent merely because they have different authors or URLs.

Dependence may arise from:

- the same originating dataset;
- syndication or quotation;
- shared experimental apparatus;
- overlapping samples;
- common funding or analysis;
- the same benchmark harness;
- the same model-generated summary;
- one source relying on another.

Independence is graded and documented. Unknown dependence must remain unknown; it must not default to independence.

### 6.7 `CoverageRecord`

Coverage is evidence about the search process, not evidence for the target claim. Each active research question has a `CoverageRecord`, with nested records for its load-bearing claims and arguments where practical.

The record includes:

- search directions attempted: support, opposition, alternatives, and undercutters;
- exact queries and query-generation provenance;
- databases, indexes, domains, and other source universes searched;
- language, date, geography, and document-type limits;
- sources opened and originating evidence paths found by direction;
- inaccessible or excluded material;
- search iterations and whether later iterations changed the graph;
- coverage blind spots;
- stopping reason: `redundancy`, `adequate_for_policy`, `no_longer_changing`, `resource_limit`, or `irreducible`;
- assessment of coverage reliability.

Raw source count is descriptive but not a sufficiency criterion. A single executed opposition query cannot by itself establish adequate coverage. The active `VerdictPolicy`, question type, load-bearing structure, and observed saturation determine the required search behavior.

Coverage status is a separate axis:

- `adequate`;
- `limited`;
- `not_assessed`.

Thus “the evidence found is insufficient” and “the search was insufficient” remain distinct. A user-facing label such as `insufficient_coverage` may summarize a combination, but it must not replace the two underlying states.

Opposition-seeking is normally required before an empirical, comparative, explanatory, or interpretive claim can receive a terminal `supported` or `refuted` verdict. The policy may exempt targets such as exact arithmetic or a fully checked deductive proof, and the exemption must be recorded.

### 6.8 `NormalizationRecord`

Every cross-estimate quantitative comparison requires a `NormalizationRecord` before it may support an argument. The record includes:

- target quantity and canonical metric;
- comparator and reference population;
- canonical unit, currency, price date, denominator, and timeframe as applicable;
- source estimate and source conditions;
- transformation and code or formula;
- assumptions;
- treatment of uncertainty and missing values;
- commensurability tier: `direct`, `converted`, `bridged`, or `incommensurable`;
- normalization provenance;
- fidelity assessment.

Normalization is a miniature formalization: a mathematically correct conversion can still be semantically unfaithful if populations, harnesses, denominators, or measurement constructs differ.

Where useful, a quantitative assessment separately records:

- `valence`: direction of difference;
- `magnitude`: size and uncertainty of difference;
- `valence_confidence`;
- `magnitude_confidence`.

These are assessment facets by default, not mandatory graph vertices. They become separate claims only when they have independent inferential roles or require materially different verification.

Quantity is native to every claim type, not confined to a quantitative
contract. Internal quantification may be as precise as the computation
requires, but user-facing precision is gated by quantity provenance,
normalization fidelity, and the applicable calibration class. Valence and
magnitude assessments remain separate: confidence in the direction of an
effect does not imply equal confidence in its size.

## 7. Arguments

### 7.1 Definition

An `Argument` is a directed hyperedge that attempts to establish one conclusion from one or more premises and/or grounds under a reconstructed inferential bridge.

Required fields:

- stable ID and version;
- premise claim IDs;
- ground IDs;
- exactly one conclusion claim ID;
- inference type;
- argumentation scheme, if applicable;
- warrant reconstruction;
- backing, if any;
- strict or defeasible status;
- explicit assumptions;
- exceptions and applicability conditions;
- anticipated critical questions;
- proof standard, where applicable;
- provenance of construction;
- assessment records.

An argument is not a tile or proposition. It is inferential activity.

### 7.2 Inference types

At minimum:

- deductive;
- mathematical or computational;
- statistical;
- enumerative inductive;
- analogical;
- abductive or inference to best explanation;
- causal;
- classificatory;
- argument from authority or expert testimony;
- argument from sign or indicator;
- practical or means-end;
- interpretive;
- defeasible judgment.

Each type has different success conditions. Calling an argument “inductive” is not enough; its warrant and failure modes must be inspectable.

### 7.3 Warrant reconstruction and backing

The `warrant_reconstruction` is a contestable reconstruction of why the premises or grounds bear on the conclusion. It may reveal a real inferential rule, but it may also be a post-hoc rationalization. It therefore receives a separate fidelity assessment:

- `faithful`;
- `plausible_reconstruction`;
- `confabulated`;
- `vacuous`;
- `unresolved`.

Backing supplies support for the reconstructed bridge or its applicability.

Example:

- Ground: K3 ranks near the top on several broad independent evaluations.
- Claim: K3 is frontier-adjacent on the evaluated task distribution.
- Warrant reconstruction: Broad, valid, independently administered evaluations are informative about relative performance on the tasks they sample.
- Backing: Validation of the benchmark, breadth of sampled tasks, reproducibility, and comparator parity.

The reconstruction also exposes limitations: benchmark performance may not generalize beyond its sampled distribution.

A `confabulated` or `vacuous` reconstruction cannot strengthen the argument. Unless the instantiated scheme itself supplies a transparent and adequate bridge, failure to recover a faithful warrant leaves the inference weak or unresolved; the system must not silently assess the grounds as though their relevance were self-evident.

Warrant reconstructions normally remain one level deep. When a warrant or its applicability is disputed, reused, or load-bearing, it may be promoted to a claim and supported by another argument under the ordinary promotion rule. Value-of-information and answer relevance stop the regress; the system does not prohibit deeper justification by fiat.

### 7.4 Argument schemes and critical questions

Recurring non-deductive patterns should instantiate named schemes with scheme-specific critical questions. Examples:

- expert testimony: expertise, domain fit, source reliability, consistency with peers;
- causal explanation: temporal order, mechanism, confounding, alternatives, intervention evidence;
- analogy: relevant similarities, relevant differences, counteranalogues;
- classification: definition, observed properties, boundary cases;
- sign or indicator: sensitivity, specificity, base rate, alternative causes;
- practical reasoning: goal, feasibility, side effects, alternatives, value conflicts.

Critical questions attach at two levels:

- scheme-level questions test the general inferential pattern;
- instance-level questions test the reconstructed warrant, its scope, and its applicability here.

They generate candidate defeaters and missing premises. They are not a checklist whose completion mechanically proves the argument, and a disputed warrant reconstruction does not orphan scheme-level defeaters.

### 7.5 Strict and defeasible arguments

A strict argument purports that the conclusion must follow if its premises are true. Its validity may be formally checked when the formalization is adequate.

A defeasible argument purports that the premises give a reason for the conclusion, subject to exceptions and competing considerations. It is assessed for:

- applicability of the scheme;
- relevance;
- strength;
- completeness;
- surviving defeaters;
- comparative strength against alternatives.

The system must not label a defeasible argument “valid” without qualification.

## 8. Defeaters, objections, and conflict

### 8.1 Defeater types

A `Defeater` targets a particular component:

- **rebutter:** supports a claim incompatible with the conclusion;
- **underminer:** challenges the acceptability of a premise or ground;
- **undercutter:** attacks the connection between premises and conclusion without asserting the opposite conclusion;
- **exception:** asserts that a warrant’s exclusion condition obtains;
- **alternative explanation:** explains the grounds without the target conclusion;
- **priority challenge:** disputes which argument should prevail when both are acceptable.

These distinctions matter. Evidence that a benchmark is contaminated undercuts an inference from benchmark score to capability; it does not directly establish that the model lacks capability.

### 8.2 Conflicts are relations

Conflict is not a graph node. It is a typed relation targeting a claim, argument, premise use, ground, citation, or assessment.

### 8.3 Argument acceptability is a derived policy result

Version 0.3 includes an experimental deterministic grounded-policy evaluation:
a qualifying argument is accepted only when no supported, claim-backed
defeater is active; unresolved defeaters yield `undecided`. This is a
dialectical policy result, not a truth verdict or probability.

The result is non-release until structural benchmarks demonstrate attack-target
and attack-type accuracy above a declared floor. The structured argument remains
the primary explanatory object. Later Dung-style or other abstract semantics
must remain derived, versioned analyses and preserve multiple coherent
extensions rather than silently collapsing them.

## 9. Assessment semantics

### 9.1 No generic confidence

At least four quantities must remain distinct:

1. **Claim credence:** estimated probability that a suitably probabilistic claim is true.
2. **Evidence or ground quality:** quality of the information used.
3. **Argument strength:** how strongly accepted premises support the conclusion.
4. **Assessment reliability:** confidence that the assessment would survive competent review.

Only the first is a probability about the world. The fourth is a probability about the assessment process. The middle two are structured evaluations unless a domain-specific quantitative model justifies conversion.

### 9.2 `VerdictPolicy`

Every derived claim or question verdict references a versioned, named `VerdictPolicy`. The policy makes operational semantics explicit:

- which ground-assessment dimensions must clear which floors;
- the minimum argument assessment for a qualifying route;
- how unresolved defeaters affect a route;
- how support and opposition routes produce evidential states;
- dependence clustering and sensitivity treatment;
- coverage requirements and permitted exemptions;
- question-type and claim-type rules;
- proof standard;
- stopping conditions;
- treatment of dissent and assessment reliability.

Changing the policy version invalidates cached derived verdicts produced under it. It does not invalidate source records, grounds, arguments, or target assessments; those may be recomposed under the new policy.

Policies are configuration subject to validation and ablation, not hidden model instructions. They may vary by question type and stakes, but the policy used for a run must be visible.

### 9.3 Claim evidence state

Before any scalar probability is introduced, the system records two partially independent axes:

- strength of support;
- strength of opposition.

Under the active policy, a route qualifies as support or opposition only when:

- its grounds clear the required claim-type-specific assessment floors;
- its connecting argument clears the required strength or validity floor;
- no unresolved defeater blocks that route under the policy; and
- applicable coverage and normalization gates are satisfied.

This yields four important states:

| Support | Opposition | State |
|---|---|---|
| qualifying route exists | no qualifying route | supported |
| no qualifying route | qualifying route exists | refuted |
| qualifying route exists | qualifying route exists | contested |
| no qualifying route | no qualifying route | insufficient |

`malformed`, `not_assessable`, and `out_of_scope` remain separate states.

This is an evidential status, not a four-valued metaphysical truth claim. It prevents conflict from being confused with ignorance.

Evidential state and coverage state remain orthogonal. `insufficient` with `adequate` coverage means a responsible search found too little probative evidence. `insufficient` with `limited` or `not_assessed` coverage means the inquiry itself is incomplete.

### 9.4 Claim assessment

A claim assessment records:

- target claim and version;
- assessment dimension;
- verdict;
- support and opposition summaries;
- evidence paths used;
- applicable proof standard;
- assessment method;
- producer and model or human provenance;
- unresolved defeaters;
- sensitivity to assumptions;
- coverage status;
- explicit credence-like score and signed valence used for forced direction;
- calibration state (`calibrated`, `uncalibrated`, or `legacy_migration`);
- calibrated probability language only when defensible against the applicable
  outcome class;
- assessment reliability;
- dissenting assessments.

### 9.5 Argument assessment

Strict arguments:

- `valid`;
- `invalid`;
- `unresolved`;
- `formalization_disputed`.

Defeasible arguments:

- `strong`;
- `moderate`;
- `weak`;
- `defeated`;
- `contested`;
- `unresolved`;
- `inapplicable_scheme`.

The record must say why, identify critical questions considered, and distinguish a missing premise from an unacceptable premise.

### 9.6 Proof standards

The standard required to accept a claim depends on the inquiry. Supported-for-summary, scientific establishment, safety assurance, legal liability, and high-stakes action require different standards.

The system records:

- standard of proof;
- why that standard applies.

Default descriptive research should use explicit qualitative standards until calibration justifies numeric thresholds. Thresholds must not be invented because the schema has a numeric field.

Formal burdens of production, persuasion, and burden-shifting are deferred until the system supports a genuinely adversarial dialogue mode, such as legal adjudication or safety assurance with identifiable parties.

### 9.7 Bayesian use

Bayesian updating is appropriate when:

- propositions and alternatives are sufficiently specified;
- priors are explicit or sensitivity-tested;
- likelihoods or likelihood ratios can be defended;
- evidence dependence is modeled;
- the numeric output is decision-relevant.

It is not a universal glue for arbitrary model judgments. Multiplying uncalibrated model “confidence” values creates false precision.

When Bayesian quantities are used, the record must preserve:

- prior and its basis;
- likelihood model;
- conditional-independence assumptions;
- posterior;
- sensitivity to disputed inputs.

### 9.8 Calibration

Probabilistic claims and assessment-reliability forecasts should be logged against later outcomes and scored with proper scoring rules. Calibration datasets must be separated by question and claim type; a model calibrated on short-horizon factual questions is not thereby calibrated on geopolitical interpretation.

Calibration reporting must include decisiveness as well as correctness: whether the system abstained when later-resolved cases and competent reviewers indicate that the available evidence was sufficient. Accuracy, unjustified-certainty rate, and excessive-abstention rate are reported together.

## 10. Propagation and recomposition

### 10.1 Route semantics

An argument establishes a **support route**. If the route fails, the conclusion may still be true or supported by another route.

Therefore:

- false premise → this argument does not establish its conclusion;
- invalid inference → this argument does not establish its conclusion;
- unresolved premise → this route is unresolved;
- refuted conclusion → requires direct opposing grounds or a sound argument for an incompatible claim;
- valid argument + supported premises → derived support, not a new independent evidence path.

### 10.2 Multiple arguments

Independent convergent arguments may strengthen a conclusion. Linked premises within one argument must not be treated as independent votes. Alternative arguments must preserve whether they are:

- jointly necessary;
- independently sufficient;
- cumulative but non-sufficient;
- competing explanations;
- redundant derivations from the same evidence.

### 10.3 Dependence before aggregation

Evidence and arguments are clustered by originating path before aggregation. Within a dependent cluster, repeated agreement does not accumulate as though independent. Disagreement within a cluster increases ambiguity and triggers provenance review.

No universal propagation equation is authorized for every argument type. Mechanical combination is permitted only when its semantics are declared—for example, Boolean entailment, arithmetic computation, a validated statistical model, or a specified Bayesian network.

When dependence is materially uncertain, the system computes verdict sensitivity under multiple defensible clusterings, including optimistic and pessimistic cases where appropriate. “Everything independent” and “everything dependent” may be shown as outer bounds, but they must not be presented as the only possibilities when both are implausible.

If the verdict is stable across defensible dependence models, report the stable result. If it changes, report a dependence-sensitive result such as `supported_under_model_A / insufficient_under_model_B`, identify the disputed lineage, and apply the active policy’s rule for any required headline verdict. Unknown dependence must not silently become either full independence or full dependence.

### 10.4 Load-bearing analysis

A claim or argument is load-bearing when changing its assessment can materially change a question verdict or answer-bundle conclusion.

Load-bearingness is measured by interventions over the graph:

1. perturb or reverse the target assessment;
2. recompute reachable conclusions under the declared semantics;
3. record which terminal verdicts change and by how much.

Centrality is not load-bearingness. A frequently connected contextual claim may be non-decisive; a sparsely connected hinge may determine the result.

### 10.5 Tenuity

Tenuity is multi-dimensional. It may result from:

- weak or indirect grounds;
- disputed extraction;
- low source quality;
- dependence on one evidence origin;
- weak inferential warrant;
- unresolved undercutter;
- missing alternative;
- high sensitivity to an assumption;
- mismatch between claim breadth and evidence scope;
- semantic uncertainty in the formalization.

The interface may summarize tenuity, but it must expose the dimensions that caused it.

## 11. Formalization and proof

### 11.1 Formalization record

A formalization must include:

- source natural-language claim or argument;
- target formal language;
- symbol table and ontology;
- formal premises;
- formal conclusion;
- domain and quantifier choices;
- omitted context;
- explicit assumptions;
- translator provenance;
- independent semantic review;
- formalization-fidelity verdict.

### 11.2 Two independent questions

Every formal check answers:

1. Does the conclusion follow in the formal system?
2. Does the formal system faithfully represent the intended natural-language argument?

The theorem prover answers only the first. The second requires semantic validation and may remain disputed.

### 11.3 Formalization levels

- `exact_for_stated_scope`;
- `partial`;
- `approximate`;
- `candidate_unvalidated`;
- `unsuitable`.

Only `exact_for_stated_scope` permits a proof result to be described without an immediate formalization caveat.

### 11.4 Formal proof output

The output records:

- solver or prover;
- version;
- proof artifact or checkable certificate;
- axioms and libraries;
- satisfiability of premises;
- countermodel, if found;
- resource limits;
- formalization-fidelity assessment.

Inconsistent premises must not yield a user-facing “proof” through vacuous entailment without a prominent inconsistency result.

### 11.5 Normalization fidelity

Normalization receives the same two-part treatment as formalization:

1. Was the conversion or transformation executed correctly?
2. Does the transformed estimate preserve the meaning needed for the proposed comparison?

A successful unit conversion answers only the first. Differences in construct, population, denominator, experimental harness, censoring, price date, or measurement procedure may make the estimates merely bridged or incommensurable. Every comparison argument that uses transformed estimates carries both the computation artifact and the normalization-fidelity assessment.

## 12. Degeneracy, independence, and adversarial review

Redundancy means repeating similar procedures. Degeneracy means using structurally different procedures that can reach or challenge the same result. The system should prefer useful degeneracy around high-impact failure points.

Candidate independent passes include:

- multiple blind inquiry framers;
- independent claim decompositions;
- source retrieval with different search strategies;
- verifier and falsifier roles;
- scheme-specific critical-question generation;
- completeness adversary;
- formal and informal validity checks;
- independent natural-language-to-formal-logic translations;
- human review for high-stakes or semantically unstable steps.

Independence metadata includes:

- model family and provider;
- prompt and context lineage;
- retrieved-source overlap;
- tool and dataset overlap;
- temporal ordering and whether one pass saw another;
- common code or adjudicator.

Model votes are evidence about judgment stability, not evidence that a world-facing claim is true. Agreement among dependent model passes must be discounted. Dissent is preserved, not averaged away.

Degeneracy should be allocated by expected value:

- load-bearingness;
- uncertainty;
- failure severity;
- current disagreement;
- tractability of verification;
- expected information gain.

## 13. End-to-end pipeline

### Stage 0: contract

Resolve the referent, scope, timeframe, comparison class, supported mode, and answer conditions. Select only versioned contracts from the closed library and record why each applies.

### Stage 1: discovery and question portfolio

Run broad, blind reconnaissance. Generate candidate research questions, hypotheses, live disagreements, and potential failure frames. Type each subquestion and compose an inquiry plan from the selected contracts. Preserve minority framings. Treat discovery as agenda construction, not verified support.

### Stage 2: portfolio selection

Deduplicate questions without erasing meaningful distinctions. Rank on visible criteria. Select active questions; retain all others with dispositions. Any proposed equivalence among questions or claims remains provenance-preserving and reviewable.

### Stage 3: hypothesis and argument construction

For each active question, propose answer hypotheses, discriminating tests, rival hypotheses, necessary premises, and candidate argument schemes. Merge these into one shared claim-and-argument graph.

### Stage 4: structural audit

Mechanically and adversarially test:

- atomicity;
- claim correspondence and false-merge risk;
- scope consistency;
- missing premises;
- circularity;
- unsupported or confabulated warrant reconstructions;
- false dilemmas;
- question coverage;
- normalization requirements;
- invalid topology;
- premature causal or predictive routing.

### Stage 5: evidence acquisition

Prioritize load-bearing and resolvable claims. Fetch sources once, snapshot them, extract bounded grounds, and construct provenance paths. Search explicitly for support, opposition, alternatives, and undercutters. Maintain `CoverageRecord` entries throughout retrieval rather than reconstructing diligence afterward.

### Stage 6: target assessment

Assess citations, grounds, claims, arguments, warrant reconstructions, correspondence proposals, coverage, and normalization under their own dimensions. Run verifier, falsifier, and comparator passes where useful. Split conflated claims and repeat.

### Stage 7: native graph compilation

Compile the completed post-evidence claim, argument, defeater, provenance, and
assessment records into the durable reasoning artifact. This is the graph used
for verdicts, prose, and visualization. A later Kimi-specific or UI-specific
reconstruction is prohibited. Every defeater has a visible claim premise;
every claim has stable identity, explicit signed valence, coverage, evidence
depth, and source-dependence records.

### Stage 8: formal and computational checks

Use arithmetic, code, SAT/SMT, theorem proving, statistical analysis, or causal identification only on suitable targets. Assess formalization fidelity separately.

### Stage 9: recomposition and sensitivity

Compute supported routes under the declared `VerdictPolicy`. Cluster dependence before combining, test defensible alternative dependence models, and identify load-bearing claims, unresolved defeaters, and answer sensitivity.

### Stage 10: question verdicts

Produce one concise verdict for each active question with:

- conclusion;
- status;
- verdict-policy version;
- coverage status;
- strongest support route;
- strongest challenge;
- load-bearing dependencies;
- unresolved issues;
- scope and date.

### Stage 11: answer bundle

Produce:

- terminal claim IDs;
- synthesis text;
- dimensions covered;
- scope and exclusions;
- unresolved questions;
- deferred questions;
- adjacent inquiry frontier;
- “as of” date.

### Stage 12: entailment audit of prose

Map each material answer sentence to graph claims. Flag unsupported strengthening, scope drift, missing qualifiers, and prose that converts “not established” into “false.”

A sentence is material when it makes an external-world assertion that could change a reasonable reader’s understanding of the answer, its justification, its scope, its uncertainty, or a resulting decision. Quantified statements are always material. Novel qualitative assertions are material even when no existing claim happens to match them. A `context` label does not exempt a factual statement from provenance and support requirements.

## 14. Validation contracts

The system distinguishes deterministic invariants from assessed judgment gates. They have different failure modes and must be monitored separately.

### 14.1 Structural invariants

These are machine-checkable and enforced at write time:

1. Every object has a stable ID, version, creator, and timestamp.
2. Questions, sources, citations, assessments, and policies are not claim nodes.
3. Every argument has at least one premise claim or ground and exactly one conclusion claim.
4. Support, defeat, correspondence, and provenance relations bind stable object IDs, never free claim-text strings.
5. An argument cannot conclude its own premise without an explicitly flagged circular structure.
6. Every argument declares an inference type, warrant reconstruction, and strictness.
7. Every defeater declares its target and attack type.
8. Every ground has at least one source snapshot and citation locator.
9. A source cannot directly establish a claim; the path must include a ground and argument or assessed evidential relation.
10. Every assessment names its target version, dimension, method, producer, and inputs.
11. Original claims survive canonical grouping; confirmed equivalence creates a non-destructive canonical view.
12. An unconfirmed claim correspondence cannot authorize analytics that treat the claims as one vertex.
13. Every active research question has resolution criteria and at least one terminal claim or an explicit unanswerable result.
14. Every non-active question has a disposition reason and remains recoverable.
15. Every derived claim or question verdict references a `VerdictPolicy` version.
16. Changing a policy version invalidates derived-verdict caches keyed to the earlier version, but not their underlying records.
17. Every formal proof carries a formalization-fidelity assessment.
18. Every cross-estimate quantitative comparison carries a `NormalizationRecord` and normalization-fidelity assessment.
19. Every causal claim records an estimand, causal assumptions, and identification status before causal language may appear in the answer.
20. Every probabilistic forecast records a horizon, event definition, base rate or prior, update model, and calibration class.
21. Every displayed claim has a stable `claim_uid`, explicit signed valence,
    calibration state, separate coverage record, and separate evidence-depth
    record.
22. Every visual card maps to exactly one claim; arguments, defeaters, grounds,
    sources, and questions cannot become cards.
23. Every visible challenge relation originates in a claim premise and targets
    an argument.

### 14.2 Deterministic reasoning guards

These are process rules that code can enforce once the relevant assessments exist:

1. Premise truth assessments are hidden from pure validity adjudication.
2. A failed support route does not generate a refutation of its conclusion.
3. Derived support is never counted as an independent evidence path from its premises.
4. Independence without sufficient provenance is represented as `unknown`.
5. A conflated claim cannot receive a terminal verdict until split or explicitly re-scoped.
6. An entailment correspondence creates at most a candidate argument until validity is established.
7. A `confabulated` or `vacuous` warrant reconstruction cannot increase argument strength.
8. Evidential state and coverage state remain separate fields.
9. A terminal empirical, comparative, explanatory, or interpretive verdict cannot bypass the active policy’s opposition-search requirement or recorded exemption.
10. Displayed direction is derived only from signed valence; neither
    `insufficient` nor coverage can determine it.
11. Assessments sharing an independence group are clustered before numeric
    aggregation and cannot gain independent weight through repetition.

### 14.3 Judgment gates

These depend on assessed semantic judgments and therefore carry producer provenance, assessment reliability, dissent, and benchmark performance:

1. Whether grounds clear the policy’s quality, directness, and relevance floors.
2. Whether an argument’s reconstructed warrant is faithful and the instantiated scheme applies.
3. Whether coverage is adequate for the claim’s type, stakes, and load-bearing role.
4. Whether two claims are equivalent, overlapping, or connected by entailment.
5. Whether evidence paths are materially dependent.
6. Whether a natural-language formalization or quantitative normalization is faithful.
7. Whether a final-answer sentence is material and entailed by its mapped claims.
8. Whether final prose has broader scope, stronger modality, or higher precision than its support.

Judgment gates must not be described as “machine-checked” merely because a model emitted structured JSON. Their benchmark accuracy and failure distributions are part of the result’s provenance.

### 14.4 Interaction, trust, and personalization invariants

These roadmap invariants extend the structural and reasoning guards above. They
do not relax them.

**A-1 — Explicit preference dependence.** Every conclusion downstream of a preference claim is conditional on that preference and surfaces it. No recommendation depends on an unstated value.

**A-2 — Governed challenge input.** Human and model challenges enter as grounds, arguments, or defeaters with provenance and are untrusted until assessed through the normal pipeline. Challengers never write verdicts directly.

**A-3 — Simplify, never strengthen.** Tutor and explanatory prose remains bound by the prose-entailment audit. Pedagogical fluency may not round tenuity upward.

**A-4 — Tenuity is part of mastery.** Every curriculum discloses the target’s material uncertainties, defeaters, and strength of support. Understanding a claim includes understanding how firmly to hold it.

**A-5 — Selection-bound spatial explanation.** Explanations generated from a selected region or path are entailment-bound to the induced subgraph and any explicitly retrieved adjoining records. A spatial gesture does not authorize unsupported synthesis.

**A-6 — Outcome-based personalization reward.** Personalization uses mastery and transfer outcomes such as successful explain-back, warrant transfer, and improving challenge quality. Engagement and agreement are prohibited reward signals.

**A-7 — Personalization above verification.** A personal adapter may affect only presentation, tutoring, and writing. It cannot alter collection, graph content, assessments, verdicts, or policy. Personalized prose is audited by a non-personalized evaluator.

**A-8 — Trust is a projection.** A `TrustProfile` affects aggregation and derived verdict projections only. It never controls collection or deletes, hides, or mutates graph records.

**A-9 — Trust fragility disclosure.** Every trust-conditioned verdict is labeled `trust_robust` or `trust_fragile` using perturbation and load-bearing analysis. A fragile verdict identifies the trust parameters that change it.

**A-10 — Property-based trust.** Trust assignments are justified through source properties such as method, track record, independence, and conflicts—not agreement with conclusions. The system detects and discloses when observed weighting is better predicted by conclusion agreement than by the stated properties.

## 15. Worked patterns

### 15.1 Benchmark ground used without unnecessary node creation

**Research question:** How close is K3 to the proprietary frontier on evaluated tasks?

**Ground G1:** Independent evaluator E reports K3 scored 57 under suite S and harness H on date D.  
**Ground G2:** Under the same evaluation, models A, B, and C scored within a specified range.  
**Claim C1:** K3 is frontier-adjacent on the task distribution sampled by S under H as of D.

**Argument A1**

- Grounds: G1, G2
- Conclusion: C1
- Type: comparative statistical induction
- Warrant reconstruction: Under a sufficiently valid, broad, and comparator-consistent evaluation, nearby aggregate performance is evidence of frontier adjacency on the sampled distribution.
- Warrant fidelity: plausible reconstruction, pending validation of breadth and comparator parity.
- Critical questions: Is S broad and valid? Were harnesses comparable? Are scores stable? Was there contamination? Does the conclusion stay within the sampled task distribution?

G1 and G2 need not become graph nodes unless they are reused, disputed, or load-bearing independently. C1 is a node because it is the synthesized proposition used in later arguments.

### 15.2 Undercutting is not rebutting

**Claim C1:** K3 is frontier-adjacent on the evaluated task distribution.

**Defeater D1:** The evaluation used materially different scaffolding for K3 and its comparators.

D1 undercuts A1’s reconstructed warrant as applied to this evaluation. It weakens the inference from reported scores to comparative capability. It does not directly prove `not C1`.

### 15.3 Cheap tokens do not entail cheap tasks

**Ground G3:** K3’s listed output-token price is below comparator models.  
**Claim C2:** K3 has a lower listed output-token price than the selected comparators.  
**Claim C3:** K3 has a lower total cost per successful task than the selected comparators.

Before even establishing C2, a `NormalizationRecord` must align input versus output prices, currencies and dates, caching assumptions, batch discounts, and the selected comparator tier. This can establish the valence and magnitude of a token-price difference while recording their different uncertainties.

An argument from C2 directly to C3 remains weak because token price and cost per successful task are different constructs. A second normalization model would need token consumption, retries, latency, success rate, tool costs, and engineering overhead. These bridge quantities become claims only if they are independently contested or load-bearing. Failure of the argument yields “lower task cost is not established,” not “K3 has higher task cost.”

### 15.4 Conflict versus ignorance

For claim C4:

- two independent, methodologically strong studies support C4;
- two independent, methodologically strong studies oppose C4.

Status: `contested`.

For claim C5:

- no direct study exists;
- available commentary traces to one speculative source.

Status: `insufficient`.

A scalar midpoint would obscure the difference and is prohibited as the sole representation.

Coverage remains separate. If the C5 search was broad and saturated, its coverage state may be `adequate`; if only one database was checked, it is `limited`. Both cases have the same evidential state but imply different next actions.

### 15.5 Formal consequence with disputed formalization

Natural-language claim: “If all materially comparable evaluations place K3 near the top, K3 is near-frontier.”

A propositional formalization may prove:

`(E1 and E2 and E3) -> F`

That proof shows only that `F` follows from the encoded rule and premises. Whether “materially comparable,” “near the top,” and “near-frontier” were faithfully encoded remains a separate formalization assessment. The user-facing result must report both.

## 16. Evaluation program

The architecture itself must be tested.

### 16.1 Structural benchmarks

Curate expert-annotated cases for:

- compound-claim splitting;
- claim-correspondence classification;
- canonical-group precision and recall;
- premise/conclusion identification;
- argument reconstruction;
- warrant recovery;
- warrant-fidelity assessment;
- rebutter versus undercutter classification;
- attack-target and attack-type extraction;
- missing-premise detection;
- source-dependence clustering;
- normalization construction and fidelity;
- coverage-status assessment;
- question-to-claim coverage;
- prose-to-graph entailment.

False merges are generally more dangerous than conservative splits. Claim matching therefore uses an asymmetric gating metric in which false merges carry substantially greater cost than missed merges. Abstract extension semantics remain disabled until attack-target and attack-type performance clear a separately declared floor.

### 16.2 Epistemic benchmarks

Measure:

- claim-verdict accuracy where later ground truth exists;
- calibration by claim type and horizon;
- recovery of known defeaters;
- resistance to citation laundering;
- preservation of “unknown” under thin evidence;
- excessive abstention when evidence was sufficient;
- discrimination between insufficient evidence and insufficient search coverage;
- sensitivity accuracy: whether identified hinges actually move conclusions;
- dependence sensitivity: whether conditional verdicts identify the actual disputed lineage;
- stability under paraphrase and irrelevant-source injection;
- rate of unsupported final-answer statements.

Unknown preservation and excessive abstention are reported as a tradeoff pair. A release must not advertise one without the other.

### 16.3 Comparative ablations

Compare:

- single-pass answer;
- multi-model voting without structure;
- structured graph without adversarial passes;
- full system;
- alternative `VerdictPolicy` versions;
- full system with coverage gates removed;
- full system with independence clustering removed;
- full system with normalization-fidelity assessment removed;
- full system with formalization-fidelity assessment removed.

The system earns complexity only if components catch measurable failure modes.

### 16.4 Human review

Expert review should score distinct dimensions rather than holistic impressiveness:

- inquiry completeness;
- claim precision;
- evidential fidelity;
- inference quality;
- defeater coverage;
- uncertainty honesty;
- answer entailment;
- usability.

## 17. Consequences for the current implementation

The existing typed graph is a valuable prototype, but its ontology should change before more interface work:

1. Replace generic `NodeKind` objects with claim-only graph vertices.
2. Replace inference nodes and premise/conclusion edges with `Argument` hyperedges.
3. Move question nodes into the inquiry layer.
4. Move evidence, measurements, sources, and citations into the provenance layer.
5. Replace conflict nodes with typed defeater relations.
6. Preserve definitions, criteria, variables, actions, and preferences as context records unless they become inferentially active claims.
7. Replace the single graph root assumption with per-question terminal claim sets and an `AnswerBundle`.
8. Replace generic truth propagation with inference-type-specific route semantics.
9. Preserve the existing separation between truth assessment and validity assessment.
10. Add non-destructive `ClaimCorrespondence` and canonical views before multi-pass graph analytics.
11. Add `CoverageRecord`, `NormalizationRecord`, and versioned `VerdictPolicy` objects before derived verdicts.
12. Treat warrant text as an assessed reconstruction rather than an authoritative rule.
13. Split deterministic validation from model-produced judgment gates.
14. Retain degeneracy, formal-check artifacts, provenance, and honest “unknown” behavior while measuring excessive abstention explicitly.
15. Stabilize conservative cross-run claim identity before interaction history or personalization is attached to nodes.
16. Implement the closed contract library and subquestion-level plan composition before enabling decision/advice execution.

This should be a schema migration, not a visual masking exercise.

## 18. Interaction, learning, trust, and personalization roadmap

This section records product and schema commitments, not claims that the
features are implemented or release-ready. Each feature remains subject to the
validation contracts and sequencing below.

### 18.1 Node verbs: inspect, contest, learn

Every claim projection eventually supports three user actions:

- **inspect:** view proposition, grounds, arguments, defeaters, provenance, assessments, sensitivity, and dissent;
- **contest:** challenge a claim, ground, argument, warrant, or assessment through a governed session;
- **learn:** traverse and test understanding of the existing subgraph.

These are projections over the same durable artifact. They do not create a
separate conversational truth store.

### 18.2 Challenge sessions

A `ChallengeSession` records:

- target object and version;
- challenger identity and human/model provenance;
- typed moves and transcript;
- outcome: `defeater_added`, `argument_added`, `deepening_triggered`, or `challenge_failed`;
- artifact records proposed or created;
- assessment and review status.

The transcript is preserved regardless of outcome. A failed challenge is
evidence about robustness, not permission to inflate the target’s claim
credence. Each target may expose `survived_challenges`, with the count,
independence, quality, and scope of those challenges available to assessment
reliability rather than collapsed into a vanity score.

A `DeepeningJob` is a budgeted research pass scoped to a challenged subgraph.
Its outputs enter through the ordinary source, ground, argument, and assessment
path; a debate concession is never treated as evidence.

Challenges are permitted wherever the target is contestable and actively
invited where evidential state is `insufficient` or `contested`, tenuity is
high, or a trust-sensitive hinge is load-bearing. Authentic user dissent is a
valuable independent adversarial path and a signal for allocating further
degeneracy.

### 18.3 Explain sessions and learner models

An `ExplainSession` is a pedagogical walk of an existing subgraph, not newly
authored doctrine. It records the target, route, moves, transfer probe, outcome,
mastery signal, and prose-audit result.

The learning projection uses:

- a support route as the explanation skeleton, with the warrant as the central object taught;
- upstream claims as prerequisites;
- defeaters as misconceptions and limits;
- structural analogues as intuition pumps;
- load-bearingness as an emphasis allocator.

The default loop is predict-first → route → self-explanation → transfer probe.
Challenge and explanation are the same Socratic structure with the burden
reversed.

A per-user `LearnerModel` records demonstrated understanding of versioned nodes
and warrants, prerequisite relationships, transfer outcomes, and uncertainty.
It does not record assent as mastery. Curriculum generation must satisfy A-3
and A-4.

### 18.4 Spatial query layer

Drawing on the graph is a typed query language. A selection denotes an induced
subgraph:

| Gesture | Query semantics |
|---|---|
| Lasso a cluster | What does this region establish, and what is its weakest member? |
| Trace a path | Walk through this support or defeat route. |
| Circle empty space between clusters | What premise, bridge, or research is missing here? |
| Sketch an edge between nodes | Propose an argument for construction, validation, or refutation. |

An empty-space or proposed-edge gesture may create a candidate argument or
`DeepeningJob`, never a verdict. A proposed edge must pass the same warrant,
reference, circularity, and assessment gates as any other argument.

The primary reading surface remains prose with drill-down. The canvas is an
inspection and query surface, not a required entry point.

### 18.5 Personalization layer

Explain sessions, challenge sessions, and answer interactions can become
outcome-labeled training data. A per-user adapter may be trained for the
**lens**—pacing, vocabulary, structure, hedging, example choice, tutoring, and
writing—but never for assessment.

The preferred long-term mechanism is a LoRA-class adapter because style is a
distribution rather than a single instruction and because mastery-labeled
interaction histories cannot be represented adequately by an ever-growing
prompt. This is a roadmap hypothesis subject to ablation, not an assumption
that tuning must outperform retrieval or prompting.

Cold start uses named, inspectable style presets. Batch retraining is
sufficient; no current requirement implies online gradient updates.
Personalization evaluation uses held-out contested nodes and transfer probes
to test for flattery, agreement seeking, omitted qualifiers, and epistemic
drift.

### 18.6 Trust profiles

A `TrustProfile` is named, versioned, inspectable, and parallel to
`VerdictPolicy`. Every affected verdict records both versions. A profile
contains:

- source-property dimensions and weights;
- justifications;
- calibration evidence where available;
- creator, scope, and update history;
- declared deviations from the published default;
- permitted perturbation range for robustness analysis.

Trust-conditioned verdicts must not ship unless profiles are versioned and
inspectable, collection remains profile-independent, fragility is disclosed,
and trust is justified by source properties rather than desired conclusions.

Trust multiplies or otherwise modifies assessed source contribution under
declared aggregation semantics; it never replaces claim-relative source
assessment. A down-weighted rigorous study remains methodologically rigorous,
and a trusted weak study remains weak.

Distrusted sources are still collected, snapshotted, linked, and displayed,
with their altered contribution visible. Divergent user conclusions become a
diff over trust parameters applied to one artifact, not different underlying
graphs.

Defaults are an editorial commitment and must be published with their rationale
and empirical track record where checkable. Deviations from empirically
calibrated defaults are displayed, not silently blocked. Trust-fragile verdicts
are priority challenge targets.

### 18.7 Node identity and roadmap order

Challenges, curricula, learner models, survived-challenge histories, and
trust-sensitivity labels accumulate on nodes across runs and sessions. These
features therefore depend on stable, conservative claim identity.

Required implementation order:

1. stabilize claim schemas, versioning, correspondence, and non-destructive canonical views;
2. validate claim matching with an asymmetric penalty for false merges;
3. stabilize Argument, Defeater, Ground, assessment, and policy contracts;
4. implement deterministic contract spines and subquestion-level composition;
5. add governed challenge and deepening records;
6. add explain sessions and learner models;
7. add spatial queries over induced subgraphs;
8. add trust projections and fragility analysis;
9. add lens-only personalization after non-personalized entailment auditing is reliable.

No interaction feature may be used to compensate for unresolved artifact
identity.

## 19. Open design questions

The following remain intentionally unresolved:

- Which initial catalogue of argumentation schemes is small enough to validate well?
- How should qualitative argument strength be calibrated across domains?
- How should every displayed claim receive a signed epistemic valence in
  `[-1, 1]`, with `0` reserved for exact equipoise, without disguising an
  uncalibrated model judgment as probability? The pipeline must produce and
  aggregate this value explicitly; the projection must not derive it from
  `insufficient`, coverage, or proof-standard acceptance.
- Which `VerdictPolicy` families should be tested first, and what evidence would justify a default?
- When should a ground be automatically promoted to a claim versus proposed for review?
- How should dependence be graded when source lineage is incomplete?
- What coverage evidence is sufficient for each question and claim type?
- What deterministic, domain-sensitive rubric should map evidence depth to a
  five-segment display without conflating source count, independence, quality,
  coverage, or confidence? Until validated, the interface should show the
  existing qualitative coverage label and must not invent a segment score.
- Which proof standards apply by default to ordinary research synthesis?
- How should an answer contract be confirmed without making interaction burdensome?
- What is the minimum expert-labelled benchmark needed before automated propagation influences user-facing conclusions?
- What attack-extraction performance would justify enabling abstract argumentation semantics?
- Is the five-contract library sufficient, or should interpretive “take” split into commentary, steelman, and adjudication contracts?
- What rate limits and provenance requirements are appropriate for adversarial challenge sessions?
- Does demonstrated learner mastery transfer across materially different trust profiles?
- Which held-out probes best detect a personalized lens drifting toward flattery or agreement?
- When trust profiles diverge, which projection should be the default shared or public view?
- Which personalization mechanism—preset, retrieval, prompting, or adapter—wins on mastery without epistemic drift?

These are research questions for the product, not implementation details to settle by convenience.

## 20. Intellectual lineage

This specification is a selective synthesis, not an assertion that one historical theory supplies the whole architecture.

- Stephen Toulmin, *The Uses of Argument* (1958): practical anatomy of claim, data, warrant, backing, qualifier, and rebuttal.
- John L. Pollock, “Defeasible Reasoning” (1987): rebutting and undercutting defeat.
- Phan Minh Dung, “On the Acceptability of Arguments and Its Fundamental Role in Nonmonotonic Reasoning, Logic Programming and N-Person Games” (1995): abstract argumentation frameworks and extension semantics.
- Douglas Walton, Christopher Reed, and Fabrizio Macagno, *Argumentation Schemes* (2008): presumptive schemes paired with critical questions.
- Sanjay Modgil and Henry Prakken, “The ASPIC+ Framework for Structured Argumentation: A Tutorial” (2014): structured arguments, attacks, preferences, and rationality postulates.
- Thomas F. Gordon, Henry Prakken, and Douglas Walton, “The Carneades Model of Argument and Burden of Proof” (2007): argument graphs, burdens, and proof standards.
- Nuel Belnap and J. Michael Dunn’s four-valued tradition: keeping inconsistency distinct from absence of information. This specification borrows the distinction for evidential status without treating those statuses as literal truth values.
- Judea Pearl’s work on Bayesian networks and causal models: explicit dependence assumptions, graphical separation, causal identification, interventions, and counterfactuals.
- Peter Lipton, *Inference to the Best Explanation*: contrastive explanation and the relationship between explanatory inference and Bayesian confirmation.
- Jaakko Hintikka’s interrogative model of inquiry: inquiry as a question-guided process in which answers enlarge the premise set.
- Pragma-dialectical argumentation theory: staged critical discussion, explicit starting points, and resolution under rules of reasonable criticism.
- John Lawrence and Chris Reed’s argument-mining survey: the empirical difficulty of recovering argument structure from natural language and the need to benchmark extraction rather than assume it.
- Automated fact-checking and claim-matching research: evidence that claim selection, matching, retrieval, and verification are distinct error-producing stages.
- W3C PROV: provenance as entities, activities, agents, and derivation relations.
- GRADE: explicit assessment of risk of bias, inconsistency, indirectness, imprecision, and publication bias in bodies of empirical evidence.

The two-axis support/opposition representation is not an adoption of Dempster–Shafer theory and does not authorize Dempster’s combination rule. It borrows the more general insight that conflict and absence of information must remain distinct. Any future evidence-combination rule requires its own semantics and adversarial evaluation.

### Reference links

- Dung: https://doi.org/10.1016/0004-3702(94)00041-X
- Pollock: https://doi.org/10.1207/s15516709cog1104_4
- ASPIC+: https://doi.org/10.1080/19462166.2013.869766
- Carneades: https://doi.org/10.1016/j.artint.2007.04.010
- Argumentation Schemes: https://doi.org/10.1017/CBO9780511802034
- Lawrence and Reed, “Argument Mining: A Survey”: https://doi.org/10.1162/coli_a_00364
- Thorne and Vlachos, “Automated Fact Checking”: https://aclanthology.org/C18-1283/
- Pearl, *Causality*: https://bayes.cs.ucla.edu/BOOK-2K/
- Pearl, Glymour, and Jewell, *Causal Inference in Statistics: A Primer*: https://bayes.cs.ucla.edu/PRIMER/
- W3C PROV overview: https://www.w3.org/TR/prov-overview/
- W3C PROV-O: https://www.w3.org/TR/prov-o/
- GRADE handbook: https://gdt.gradepro.org/app/handbook/handbook.html
- NIST definition of formal verification: https://xlinux.nist.gov/dads/HTML/formalverf.html

---

The product succeeds when a skeptical reader can identify exactly what is claimed, why it is believed, which inference carries the weight, what could defeat it, where the information originated, and how the answer would change if a hinge failed.
