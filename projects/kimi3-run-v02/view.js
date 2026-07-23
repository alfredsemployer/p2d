const state = {};

const COLUMN_X = [20, 440, 860];
const ROW_Y = [20, 205, 390, 575, 760];
const LAYOUT = {
  Q1: {
    width: 820,
    height: 930,
    claims: {
      RC2: [0, 0],
      RC4: [0, 2],
      RC5: [0, 4],
      RC1: [1, 0],
      RC10: [1, 1],
      RC3: [1, 2],
      RC6: [1, 3]
    }
  },
  Q2: {
    width: 820,
    height: 565,
    claims: {
      RC7: [0, 0],
      RC8: [0, 1],
      RC9: [0, 2],
      RC10: [1, 1]
    }
  },
  Q3: {
    width: 1240,
    height: 750,
    claims: {
      RC13: [0, 1],
      RC2: [1, 0],
      RC12: [1, 2],
      RC1: [2, 0],
      RC10: [2, 1],
      RC11: [2, 3]
    }
  }
};

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

function coverageState(claimId) {
  return claimById(claimId)?.display_assessment?.coverage_state || "not assessed";
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

function sentenceList(text) {
  const sentences = typeof Intl.Segmenter === "function"
    ? [...new Intl.Segmenter("en", { granularity: "sentence" }).segment(text)]
      .map(item => item.segment.trim())
    : text.split(/(?<=[.!?])\s+/);
  return sentences.filter(Boolean);
}

function readableState(value) {
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

function directionFor(questionId, claimId) {
  if (terminalFor(questionId, claimId)) return "Answer";
  const visible = new Set(Object.keys(LAYOUT[questionId].claims));
  const challenges = state.graph.defeaters.some(defeater =>
    (defeater.premise_claim_ids || []).includes(claimId) &&
    visible.has(argumentById(defeater.target_id)?.conclusion_claim_id)
  );
  return challenges ? "Challenges" : "Supports";
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
  const stateName = evidenceState(claim.id);
  const node = document.createElement("button");
  node.type = "button";
  node.className = `claim-node${terminal ? " claim-node--answer" : ""}`;
  node.dataset.claim = claim.id;
  node.dataset.state = stateName;
  node.style.left = `${COLUMN_X[gridPosition[0]]}px`;
  node.style.top = `${ROW_Y[gridPosition[1]]}px`;
  node.innerHTML = `
    <span class="claim-node__text">${esc(claim.proposition)}</span>
    <span class="claim-node__assessment">
      <span class="claim-node__direction">${esc(directionFor(questionId, claim.id))}</span>
      <span class="claim-node__state">${esc(readableState(stateName))}</span>
      <span class="claim-node__coverage">${esc(coverageState(claim.id))} evidence</span>
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
      const layout = LAYOUT[question.id];
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
    const backingId = (defeater.premise_claim_ids || []).find(id => visible.has(id));
    let d;

    if (backingId) {
      const backingNode = lane.querySelector(`[data-claim="${backingId}"]`);
      const backing = center(backingNode.getBoundingClientRect(), canvasRect);
      const x1 = target.x < backing.x ? backing.left - 7 : backing.right + 7;
      d = orthogonalPath(x1, backing.y, target.x, target.y);
    } else {
      d = orthogonalPath(target.x + 42, target.y, target.x, target.y);
    }

    clickableRoute(
      svg,
      d,
      "defeater-path",
      `url(#attack-${questionId})`,
      `Open challenge: ${defeater.content}`,
      () => openArgument(defeater.target_id, questionId, true)
    );
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
      <div class="inspector__eyebrow">${terminal ? "Answer claim" : `${directionFor(questionId, claimId)} the answer`}</div>
      <h3>${esc(claim.proposition)}</h3>
      ${metricPills([
        [readableState(evidenceState(claimId)), "assessment"],
        [`${coverageState(claimId)} evidence`, "coverage"]
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
