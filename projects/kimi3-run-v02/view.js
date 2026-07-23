const state = {};

const CARD_WIDTH = 360;
const CARD_HEIGHT = 176;
const COLUMN_STEP = 420;
const ROW_STEP = 205;
const LAYOUT = {};

const esc = value => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;");

function claimById(id) {
  return state.graph.claims.find(claim => claim.id === id);
}

function argumentById(id) {
  return state.graph.arguments.find(argument => argument.id === id);
}

function groundById(id) {
  return state.grounds.find(ground => ground.id === id);
}

function evidenceState(claimId) {
  return claimById(claimId)?.display_assessment?.evidential_state || "unassessed";
}

function acceptanceStatus(claimId) {
  return claimById(claimId)?.display_assessment?.acceptance_status || "not_supported";
}

function coverageState(claimId) {
  return claimById(claimId)?.display_assessment?.coverage_state || "not_assessed";
}

function coverageQuarters(claimId) {
  return claimById(claimId)?.display_assessment
    ?.coverage_display?.harvey_quarters ?? 0;
}

function terminalFor(questionId, claimId) {
  return (state.graph.terminal_claim_ids_by_question?.[questionId] || []).includes(claimId);
}

function argumentsFor(claimId) {
  return state.graph.arguments.filter(argument => argument.conclusion_claim_id === claimId);
}

function defeatersFor(argumentId) {
  return state.graph.defeaters.filter(defeater =>
    defeater.target_type === "argument" && defeater.target_id === argumentId
  );
}

function buildProjection(questionId) {
  const terminals = [
    ...(state.graph.terminal_claim_ids_by_question?.[questionId] || [])
  ];
  const includedClaims = new Set(terminals);
  const includedArguments = new Set();
  const queue = [...terminals];

  while (queue.length) {
    const conclusionId = queue.shift();
    argumentsFor(conclusionId).forEach(argument => {
      includedArguments.add(argument.id);
      const linkedClaims = [
        ...argument.premise_claim_ids,
        ...defeatersFor(argument.id).flatMap(
          defeater => defeater.premise_claim_ids || []
        )
      ];
      linkedClaims.forEach(claimId => {
        if (!includedClaims.has(claimId)) {
          includedClaims.add(claimId);
          queue.push(claimId);
        }
      });
    });
  }

  const edges = [];
  includedArguments.forEach(argumentId => {
    const argument = argumentById(argumentId);
    argument.premise_claim_ids.forEach(source => {
      if (includedClaims.has(source)) {
        edges.push({ source, target: argument.conclusion_claim_id, type: "support" });
      }
    });
    defeatersFor(argumentId).forEach(defeater => {
      (defeater.premise_claim_ids || []).forEach(source => {
        if (includedClaims.has(source)) {
          edges.push({ source, target: argument.conclusion_claim_id, type: "challenge" });
        }
      });
    });
  });

  const outgoing = new Map(
    [...includedClaims].map(claimId => [claimId, []])
  );
  edges.forEach(edge => outgoing.get(edge.source)?.push(edge.target));

  const distance = new Map(terminals.map(claimId => [claimId, 0]));
  let changed = true;
  while (changed) {
    changed = false;
    edges.forEach(edge => {
      if (!distance.has(edge.target)) return;
      const candidate = distance.get(edge.target) + 1;
      if (!distance.has(edge.source) || candidate < distance.get(edge.source)) {
        distance.set(edge.source, candidate);
        changed = true;
      }
    });
  }

  const challengeClaims = new Set(
    edges.filter(edge => edge.type === "challenge").map(edge => edge.source)
  );
  const designations = {};
  includedClaims.forEach(claimId => {
    designations[claimId] = terminals.includes(claimId)
      ? "answer"
      : challengeClaims.has(claimId)
        ? "challenge"
        : "support";
  });

  function terminalAffinity(claimId) {
    const pending = [claimId];
    const seen = new Set();
    const reached = [];
    while (pending.length) {
      const current = pending.shift();
      if (seen.has(current)) continue;
      seen.add(current);
      const terminalIndex = terminals.indexOf(current);
      if (terminalIndex >= 0) reached.push(terminalIndex);
      pending.push(...(outgoing.get(current) || []));
    }
    return Math.min(...reached, terminals.length);
  }

  const columns = new Map();
  includedClaims.forEach(claimId => {
    const column = distance.get(claimId);
    if (column === undefined) {
      throw new Error(`Claim ${claimId} does not reach a terminal for ${questionId}`);
    }
    if (!columns.has(column)) columns.set(column, []);
    columns.get(column).push(claimId);
  });
  columns.forEach(items => items.sort((left, right) => {
    const affinity = terminalAffinity(left) - terminalAffinity(right);
    if (affinity) return affinity;
    const designationOrder = { answer: 0, support: 1, challenge: 2 };
    const designation = designationOrder[designations[left]]
      - designationOrder[designations[right]];
    return designation || left.localeCompare(right, undefined, { numeric: true });
  }));

  const maxRows = Math.max(...[...columns.values()].map(items => items.length));
  const claims = {};
  columns.forEach((items, column) => {
    const slots = items.length === 1
      ? [Math.floor((maxRows - 1) / 2)]
      : items.map((_, index) =>
        Math.round(index * (maxRows - 1) / (items.length - 1))
      );
    items.forEach((claimId, index) => {
      claims[claimId] = [column, slots[index]];
    });
  });
  const maxColumn = Math.max(...columns.keys());
  return {
    claims,
    designations,
    width: 40 + CARD_WIDTH + maxColumn * COLUMN_STEP,
    height: 40 + CARD_HEIGHT + (maxRows - 1) * ROW_STEP
  };
}

function sentenceList(text) {
  const sentences = typeof Intl.Segmenter === "function"
    ? [...new Intl.Segmenter("en", { granularity: "sentence" }).segment(text)]
      .map(item => item.segment.trim())
    : text.split(/(?<=[.!?])\s+/);
  return sentences.filter(Boolean);
}

function readableEvidentialState(value) {
  const labels = {
    supported: "Supported",
    insufficient: "Insufficient evidence",
    contested: "Contested",
    opposed: "Contradicted",
    refuted: "Contradicted",
    unassessed: "Not assessed"
  };
  return labels[value] || value.replaceAll("_", " ");
}

function designationFor(questionId, claimId) {
  return LAYOUT[questionId].designations[claimId];
}

function readableLabel(value) {
  return value.replaceAll("_", " ").replace(/\b\w/g, letter => letter.toUpperCase());
}

function renderEngineStamp() {
  const generated = new Date(state.graph.generated_at);
  const timestamp = new Intl.DateTimeFormat("en-US", {
    timeZone: "America/New_York",
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZoneName: "short"
  }).format(generated);
  document.getElementById("engine-stamp").textContent =
    `Reasoning engine output / ${timestamp}`;
}

function renderAnswer() {
  const target = document.getElementById("synthesis");
  const synthesis = state.answer.overall_synthesis.replace(
    /^Provisional overall assessment:\s*/i,
    ""
  );
  const sentences = sentenceList(synthesis);
  target.innerHTML = `
    <ul>${sentences
      .map(sentence => `<li>${esc(sentence)}</li>`)
      .join("")}</ul>`;
}

function renderClaimNode(canvas, questionId, claimId, gridPosition) {
  const claim = claimById(claimId);
  if (!claim) return;
  const terminal = terminalFor(questionId, claimId);
  const acceptance = acceptanceStatus(claim.id);
  const designation = designationFor(questionId, claim.id);
  const coverage = coverageState(claim.id);
  const quarters = coverageQuarters(claim.id);
  const node = document.createElement("button");
  node.type = "button";
  node.className = `claim-node${terminal ? " claim-node--answer" : ""}`;
  node.dataset.claim = claim.id;
  node.dataset.acceptance = acceptance;
  node.style.left = `${20 + gridPosition[0] * COLUMN_STEP}px`;
  node.style.top = `${20 + gridPosition[1] * ROW_STEP}px`;
  node.innerHTML = `
    <span class="claim-node__designation">${esc(readableLabel(designation))}</span>
    <span class="claim-node__text">${esc(claim.proposition)}</span>
    <span class="claim-node__assessment">
      <span class="assessment-row">
        <i class="valence-icon" data-valence="${esc(acceptance)}"></i>
        <span>${esc(readableLabel(acceptance))}</span>
      </span>
      <span class="assessment-row">
        <i class="coverage-icon" style="--coverage-turn:${quarters / 4}turn"></i>
        <span>${esc(readableLabel(coverage))} coverage</span>
      </span>
    </span>`;
  node.addEventListener("click", () => openClaim(claim.id, questionId));
  canvas.appendChild(node);
}

function renderLanes() {
  const lanes = document.getElementById("lanes");
  lanes.innerHTML = "";

  state.portfolio.questions
    .filter(question => question.disposition === "active")
    .forEach(question => {
      const layout = buildProjection(question.id);
      LAYOUT[question.id] = layout;
      const lane = document.createElement("section");
      lane.className = "question-lane";
      lane.dataset.question = question.id;
      lane.innerHTML = `
        <div class="question-lane__heading">
          <h2>${esc(question.question)}</h2>
        </div>
        <div class="lane-scroll">
          <div class="lane-canvas" style="width:${layout.width}px;min-width:${layout.width}px;height:${layout.height}px">
            <svg class="lane-svg" aria-hidden="true"></svg>
          </div>
        </div>`;
      const canvas = lane.querySelector(".lane-canvas");
      Object.entries(layout.claims).forEach(([claimId, position]) =>
        renderClaimNode(canvas, question.id, claimId, position)
      );
      lanes.appendChild(lane);
    });

  requestAnimationFrame(drawAllRoutes);
}

function center(rect, canvasRect) {
  return {
    left: rect.left - canvasRect.left,
    right: rect.right - canvasRect.left,
    top: rect.top - canvasRect.top,
    bottom: rect.bottom - canvasRect.top,
    x: rect.left - canvasRect.left + rect.width / 2,
    y: rect.top - canvasRect.top + rect.height / 2
  };
}

function orthogonalPath(x1, y1, x2, y2) {
  const elbow = (x1 + x2) / 2;
  return `M ${x1} ${y1} H ${elbow} V ${y2} H ${x2}`;
}

function verticalPath(x1, y1, x2, y2) {
  const elbow = (y1 + y2) / 2;
  return `M ${x1} ${y1} V ${elbow} H ${x2} V ${y2}`;
}

function defeaterPath(backing, target) {
  const flowsLeft = target.x < backing.x;
  const x1 = flowsLeft ? backing.left - 7 : backing.right + 7;
  const channel = flowsLeft ? backing.left - 30 : backing.right + 30;
  return `M ${x1} ${backing.y} H ${channel} V ${target.y} H ${target.x}`;
}

function svgPath(svg, d, className, marker = "") {
  const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute("d", d);
  path.setAttribute("class", className);
  if (marker) path.setAttribute("marker-end", marker);
  svg.appendChild(path);
  return path;
}

function clickableRoute(svg, d, className, marker, title, onClick) {
  const hit = svgPath(svg, d, "route-hit");
  hit.setAttribute("tabindex", "0");
  hit.setAttribute("role", "button");
  hit.setAttribute("aria-label", title);
  const tooltip = document.createElementNS("http://www.w3.org/2000/svg", "title");
  tooltip.textContent = title;
  hit.appendChild(tooltip);
  hit.addEventListener("click", onClick);
  hit.addEventListener("keydown", event => {
    if (event.key === "Enter" || event.key === " ") onClick();
  });
  svgPath(svg, d, className, marker);
}

function drawLaneRoutes(lane) {
  const questionId = lane.dataset.question;
  const canvas = lane.querySelector(".lane-canvas");
  const svg = lane.querySelector(".lane-svg");
  const canvasRect = canvas.getBoundingClientRect();
  svg.setAttribute("viewBox", `0 0 ${canvasRect.width} ${canvasRect.height}`);
  svg.innerHTML = `
    <defs>
      <marker id="arrow-${questionId}" viewBox="0 0 10 10" refX="9" refY="5"
        markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M0 1 L9 5 L0 9 Z" class="arrow-head"></path>
      </marker>
      <marker id="attack-${questionId}" viewBox="0 0 10 10" refX="9" refY="5"
        markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M1 1 L9 9 M9 1 L1 9" class="attack-head"></path>
      </marker>
    </defs>`;

  const visible = new Set(
    [...lane.querySelectorAll(".claim-node")].map(node => node.dataset.claim)
  );
  const routeGeometry = new Map();

  state.graph.arguments.forEach(argument => {
    if (!visible.has(argument.conclusion_claim_id)) return;
    const targetNode = lane.querySelector(`[data-claim="${argument.conclusion_claim_id}"]`);
    const target = center(targetNode.getBoundingClientRect(), canvasRect);
    const premises = argument.premise_claim_ids.filter(id => visible.has(id));
    if (argument.premise_claim_ids.length && !premises.length) return;
    const midpoints = [];

    if (premises.length) {
      premises.forEach(premiseId => {
        const premiseNode = lane.querySelector(`[data-claim="${premiseId}"]`);
        const premise = center(premiseNode.getBoundingClientRect(), canvasRect);
        const sameColumn = Math.abs(premise.x - target.x) < 80;
        const targetBelow = target.y > premise.y;
        const x1 = sameColumn ? premise.x : premise.left - 7;
        const y1 = sameColumn
          ? (targetBelow ? premise.bottom + 5 : premise.top - 5)
          : premise.y;
        const x2 = sameColumn ? target.x : target.right + 7;
        const y2 = sameColumn
          ? (targetBelow ? target.top - 7 : target.bottom + 7)
          : target.y;
        const d = sameColumn
          ? verticalPath(x1, y1, x2, y2)
          : orthogonalPath(x1, y1, x2, y2);
        clickableRoute(
          svg,
          d,
          "route-path",
          `url(#arrow-${questionId})`,
          `Open the reasoning supporting “${claimById(argument.conclusion_claim_id).proposition}”`,
          () => openArgument(argument.id, questionId)
        );
        midpoints.push({ x: (x1 + x2) / 2, y: (y1 + y2) / 2 });
      });
    } else {
      // Grounds are inspected inside the claim. They are not graph nodes, so
      // a line from the canvas edge falsely suggests clipped content.
      midpoints.push({ x: target.right + 9, y: target.y });
    }

    routeGeometry.set(argument.id, {
      x: midpoints.reduce((sum, item) => sum + item.x, 0) / midpoints.length,
      y: midpoints.reduce((sum, item) => sum + item.y, 0) / midpoints.length
    });
  });

  state.graph.defeaters.forEach(defeater => {
    const targetArgument = argumentById(defeater.target_id);
    if (!targetArgument || !visible.has(targetArgument.conclusion_claim_id)) return;
    const target = routeGeometry.get(defeater.target_id);
    if (!target) return;
    const backingIds = (defeater.premise_claim_ids || [])
      .filter(id => visible.has(id));
    backingIds.forEach(backingId => {
      const backingNode = lane.querySelector(`[data-claim="${backingId}"]`);
      const backing = center(backingNode.getBoundingClientRect(), canvasRect);
      const d = defeaterPath(backing, target);
      clickableRoute(
        svg,
        d,
        "defeater-path",
        `url(#attack-${questionId})`,
        `Open challenge: ${defeater.content}`,
        () => openArgument(defeater.target_id, questionId, true)
      );
    });
  });
}

function drawAllRoutes() {
  document.querySelectorAll(".question-lane").forEach(drawLaneRoutes);
}

function renderDeferred() {
  const target = document.getElementById("deferred");
  const questions = state.portfolio.questions.filter(
    question => question.disposition !== "active"
  );
  target.innerHTML = questions.map(question => `
    <p class="ghost-question">${esc(question.question)}</p>`).join("");
}

function metricPills(items) {
  return `<div class="inspector__stats">${items
    .map(([value, label]) =>
      `<span class="metric"><b>${esc(value)}</b> ${esc(label)}</span>`
    )
    .join("")}</div>`;
}

function sourceAssessmentFor(claim) {
  const sourceIds = claim.display_assessment?.source_claim_assessment_ids || [];
  return sourceIds.map(id => state.assessments[id]).find(Boolean);
}

function groundCards(grounds) {
  return grounds.map(ground => `
    <div class="ground">
      <p>${esc(ground.content)}</p>
      ${ground.url
        ? `<a href="${esc(ground.url)}" target="_blank" rel="noreferrer">${esc(ground.source_title || "Open source")} ↗</a>`
        : ""}
    </div>`).join("");
}

function openClaim(claimId, questionId) {
  const claim = claimById(claimId);
  const sourceAssessment = sourceAssessmentFor(claim);
  const argument = argumentsFor(claimId)[0];
  const grounds = (argument?.ground_ids || []).map(groundById).filter(Boolean);
  const terminal = terminalFor(questionId, claimId);
  showDialog(`
    <article class="inspector">
      <div class="inspector__eyebrow">${esc(readableLabel(designationFor(questionId, claimId)))} claim</div>
      <h3>${esc(claim.proposition)}</h3>
      ${metricPills([
        [readableLabel(acceptanceStatus(claimId)), "acceptance"],
        [readableEvidentialState(evidenceState(claimId)), "evidential state"],
        [readableLabel(coverageState(claimId)), "research coverage"]
      ])}
      <section class="inspector__section">
        <h4>Why this follows</h4>
        <p>${esc(argument?.warrant_reconstruction || "No supporting inference was recorded.")}</p>
      </section>
      <section class="inspector__section">
        <h4>Assessment</h4>
        <p>${esc(
          sourceAssessment?.comparator?.rationale ||
          sourceAssessment?.verifier?.rationale ||
          "This reconstructed claim has not yet received an independent assessment."
        )}</p>
      </section>
      ${grounds.length ? `
        <section class="inspector__section">
          <h4>Evidence</h4>
          ${groundCards(grounds)}
        </section>` : ""}
    </article>`);
}

function openArgument(argumentId, questionId, focusDefeaters = false) {
  const argument = argumentById(argumentId);
  const conclusion = claimById(argument.conclusion_claim_id);
  const grounds = argument.ground_ids.map(groundById).filter(Boolean);
  const defeaters = defeatersFor(argument.id);
  const premises = argument.premise_claim_ids.map(claimById).filter(Boolean);
  showDialog(`
    <article class="inspector">
      <div class="inspector__eyebrow">${focusDefeaters ? "Challenge to an inference" : "Support relation"}</div>
      <h3>${esc(conclusion.proposition)}</h3>
      ${metricPills([
        [argument.assessment, "inference strength"],
        [grounds.length || premises.length, grounds.length ? "evidence items" : "supporting claims"]
      ])}
      ${premises.length ? `
        <section class="inspector__section">
          <h4>Supporting claim${premises.length > 1 ? "s" : ""}</h4>
          <ul>${premises.map(premise => `<li>${esc(premise.proposition)}</li>`).join("")}</ul>
        </section>` : ""}
      <section class="inspector__section">
        <h4>Why the support may hold</h4>
        <p>${esc(argument.warrant_reconstruction)}</p>
      </section>
      <section class="inspector__section">
        <h4>${grounds.length ? "Evidence" : "Evidence needed"}</h4>
        ${groundCards(grounds) || `
          <ul>${(argument.anticipated_ground_kinds || [])
            .map(item => `<li>${esc(item)}</li>`).join("")}</ul>`}
      </section>
      <section class="inspector__section" ${focusDefeaters ? 'data-focused="true"' : ""}>
        <h4>Challenges to this inference</h4>
        ${defeaters.map(defeater => `
          <div class="defeater">${esc(defeater.content)}</div>`
        ).join("") || "<p>No challenges were recorded.</p>"}
      </section>
      <section class="inspector__section">
        <h4>Deterministic logic check</h4>
        <p>${argument.formal_candidate?.suitable
          ? "This relation was marked as suitable for solver validation."
          : `Not checked by a formal solver: ${esc(argument.formal_candidate?.reason || "this is not a strict deductive inference.")}`}</p>
      </section>
    </article>`);
}

function showDialog(content) {
  const dialog = document.getElementById("inspector");
  document.getElementById("dialog-content").innerHTML = content;
  dialog.showModal();
  const focused = dialog.querySelector('[data-focused="true"]');
  if (focused) requestAnimationFrame(() => focused.scrollIntoView({ block: "center" }));
}

async function init() {
  try {
    const response = await fetch("data.json");
    if (!response.ok) throw new Error(`data.json: ${response.status}`);
    Object.assign(state, await response.json());
    renderEngineStamp();
    renderAnswer();
    renderLanes();
    renderDeferred();
  } catch (error) {
    document.body.innerHTML = `<div class="error"><b>Could not load the run artifact.</b><br>${esc(error.message)}</div>`;
  }
}

document.getElementById("dialog-close").addEventListener("click", () => {
  document.getElementById("inspector").close();
});
document.getElementById("inspector").addEventListener("click", event => {
  if (event.target === event.currentTarget) event.currentTarget.close();
});
window.addEventListener("resize", () => {
  clearTimeout(window.__resizeTimer);
  window.__resizeTimer = setTimeout(drawAllRoutes, 120);
});

init();
