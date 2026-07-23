const state = {};

const LAYOUT = {
  Q1: {
    height: 650,
    claims: {
      RC1: [5, 20],
      RC10: [5, 178],
      RC3: [5, 336],
      RC6: [5, 494],
      RC2: [70, 20],
      RC4: [70, 274],
      RC5: [70, 494]
    }
  },
  Q2: {
    height: 550,
    claims: {
      RC10: [5, 190],
      RC7: [37, 28],
      RC8: [70, 98],
      RC9: [70, 370]
    }
  },
  Q3: {
    height: 650,
    claims: {
      RC1: [5, 20],
      RC10: [5, 178],
      RC11: [5, 494],
      RC2: [37, 20],
      RC12: [37, 336],
      RC13: [70, 220]
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

function groundById(id) {
  return state.grounds.find(ground => ground.id === id);
}

function renderMetrics() {
  const reach = state.graph.inferential_reachability;
  const items = [
    [state.graph.claims.length, "claims"],
    [reach.claim_dependency_edges, "claim dependencies"],
    [state.graph.arguments.length, "arguments"],
    [state.graph.defeaters.length, "defeaters"],
    [reach.maximum_claim_dependency_depth, "maximum depth"],
    [`${reach.claims_reaching_a_terminal}/${state.graph.claims.length}`, "reach a terminal"]
  ];
  document.getElementById("metrics").innerHTML = items
    .map(([value, label]) => `<span class="metric"><b>${value}</b> ${label}</span>`)
    .join("");

  const incomplete = reach.terminal_claim_ids_without_complete_ground_route;
  document.querySelector("#truth-note span").textContent =
    `No new evidence was added. The reconstruction has ${reach.claim_dependency_edges} ` +
    `claim-to-claim dependencies, depth ${reach.maximum_claim_dependency_depth}, and all ` +
    `${state.graph.claims.length} claims reach a terminal. ${incomplete.join(", ")} ` +
    `remains explicitly incomplete because control-effectiveness evidence is missing.`;
}

function renderAnswer() {
  document.getElementById("synthesis").textContent = state.answer.overall_synthesis;
  const audit = document.getElementById("audit");
  audit.textContent = state.answer._graph_projection?.independent_review_status === "pending"
    ? "Prose audit passed · reconstructed claim mapping awaits independent review"
    : "Independent prose and mapping audit passed";

  const target = document.getElementById("verdicts");
  const template = document.getElementById("verdict-template");
  state.answer.question_verdicts.forEach(item => {
    const node = template.content.firstElementChild.cloneNode(true);
    node.querySelector(".verdict__id").textContent =
      `${item.question_id} · ${item.claim_ids.join(" / ")}`;
    node.querySelector(".status-pill").textContent =
      `${item.evidential_state} / ${item.coverage_state}`;
    node.querySelector(".verdict__line").textContent = item.one_line_verdict;
    node.querySelector(".verdict__support").textContent = item.strongest_support;
    node.querySelector(".verdict__challenge").textContent = item.strongest_challenge;
    node.querySelector(".verdict__more").addEventListener("click", event => {
      node.classList.toggle("open");
      event.currentTarget.textContent = node.classList.contains("open")
        ? "hide detail"
        : "show support and challenge";
    });
    target.appendChild(node);
  });
}

function renderClaimNode(canvas, questionId, claimId, position) {
  const claim = claimById(claimId);
  if (!claim) return;
  const terminal = terminalFor(questionId, claimId);
  const shared = (claim.question_ids || []).filter(id => id !== questionId);
  const node = document.createElement("button");
  node.type = "button";
  node.className = "claim-node";
  node.dataset.claim = claim.id;
  node.dataset.state = evidenceState(claim.id);
  node.style.left = `${position[0]}%`;
  node.style.top = `${position[1]}px`;
  node.innerHTML = `
    <span class="claim-node__meta">
      <b>${esc(claim.id)}</b>
      <span>${esc(evidenceState(claim.id))} · ${esc(coverageState(claim.id))}</span>
    </span>
    <span class="claim-node__text">${esc(claim.proposition)}</span>
    <span class="claim-node__foot">
      ${terminal ? '<span class="terminal-mark">terminal</span>' : ""}
      ${shared.length ? `<span class="shared-mark">shared: ${esc(shared.join(", "))}</span>` : ""}
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
          <div class="question-lane__id">${esc(question.id)}</div>
          <div class="question-lane__question">${esc(question.question)}</div>
          <div class="question-lane__type">${esc(question.type)} contract</div>
        </div>
        <div class="lane-scroll">
          <div class="lane-canvas" style="height:${layout.height}px">
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

function curve(x1, y1, x2, y2) {
  const direction = x2 >= x1 ? 1 : -1;
  const bend = Math.max(35, Math.abs(x2 - x1) * .43);
  return `M ${x1} ${y1} C ${x1 + direction * bend} ${y1}, ` +
    `${x2 - direction * bend} ${y2}, ${x2} ${y2}`;
}

function svgPath(svg, d, className, marker = "") {
  const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute("d", d);
  path.setAttribute("class", className);
  if (marker) path.setAttribute("marker-end", marker);
  svg.appendChild(path);
  return path;
}

function addEdgeLabel(canvas, argument, x, y, questionId) {
  const label = document.createElement("button");
  label.type = "button";
  label.className = "edge-label";
  if (!argument.ground_ids.length && !argument.premise_claim_ids.length) {
    label.classList.add("edge-label--missing");
  }
  label.style.left = `${x}px`;
  label.style.top = `${y}px`;
  const input = argument.ground_ids.length
    ? `${argument.ground_ids.length} grounds`
    : argument.premise_claim_ids.length
      ? `${argument.premise_claim_ids.length} claim premise${argument.premise_claim_ids.length > 1 ? "s" : ""}`
      : "missing evidence";
  label.innerHTML = `${esc(argument.id)} · ${esc(argument.assessment)}
    <small>${esc(input)}</small>`;
  label.addEventListener("click", () => openArgument(argument.id, questionId));
  canvas.appendChild(label);
}

function drawLaneRoutes(lane) {
  const questionId = lane.dataset.question;
  const canvas = lane.querySelector(".lane-canvas");
  const svg = lane.querySelector(".lane-svg");
  canvas.querySelectorAll(".edge-label,.defeater-label").forEach(node => node.remove());
  const canvasRect = canvas.getBoundingClientRect();
  svg.setAttribute("viewBox", `0 0 ${canvasRect.width} ${canvasRect.height}`);
  svg.innerHTML = `
    <defs>
      <marker id="arrow-${questionId}" viewBox="0 0 10 10" refX="9" refY="5"
        markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M0 1 L9 5 L0 9 Z" class="arrow-head"></path>
      </marker>
      <marker id="attack-${questionId}" viewBox="0 0 10 10" refX="9" refY="5"
        markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M1 1 L9 9 M9 1 L1 9" class="attack-head"></path>
      </marker>
    </defs>`;

  const visible = new Set(
    [...lane.querySelectorAll(".claim-node")].map(node => node.dataset.claim)
  );
  const routeGeometry = new Map();

  state.graph.arguments.forEach(argument => {
    if (!visible.has(argument.conclusion_claim_id)) return;
    const targetNode = lane.querySelector(
      `[data-claim="${argument.conclusion_claim_id}"]`
    );
    const target = center(targetNode.getBoundingClientRect(), canvasRect);
    const premises = argument.premise_claim_ids.filter(id => visible.has(id));
    const midpoints = [];

    if (argument.premise_claim_ids.length && !premises.length) return;

    if (premises.length) {
      premises.forEach(premiseId => {
        const premiseNode = lane.querySelector(`[data-claim="${premiseId}"]`);
        const premise = center(premiseNode.getBoundingClientRect(), canvasRect);
        const sameColumn = Math.abs(premise.x - target.x) < 100;
        const x1 = sameColumn ? premise.x : premise.right + 4;
        const y1 = sameColumn ? premise.bottom + 4 : premise.y;
        const x2 = sameColumn ? target.x : target.left - 7;
        const y2 = sameColumn ? target.top - 7 : target.y;
        const d = sameColumn
          ? `M ${x1} ${y1} C ${x1} ${y1 + 42}, ${x2} ${y2 - 42}, ${x2} ${y2}`
          : curve(x1, y1, x2, y2);
        svgPath(svg, d, "route-path", `url(#arrow-${questionId})`);
        midpoints.push({ x: (x1 + x2) / 2, y: (y1 + y2) / 2 });
      });
    } else {
      const x1 = 2;
      const y1 = target.y;
      const x2 = target.left - 7;
      const y2 = target.y;
      const d = curve(x1, y1, x2, y2);
      const missing = !argument.ground_ids.length;
      svgPath(
        svg,
        d,
        missing ? "route-path route-path--missing" : "route-path",
        `url(#arrow-${questionId})`
      );
      midpoints.push({ x: (x1 + x2) / 2, y: y1 });
    }

    const midpoint = {
      x: midpoints.reduce((sum, item) => sum + item.x, 0) / midpoints.length,
      y: midpoints.reduce((sum, item) => sum + item.y, 0) / midpoints.length
    };
    routeGeometry.set(argument.id, midpoint);
    addEdgeLabel(
      canvas,
      argument,
      Math.max(8, midpoint.x - 56),
      midpoint.y - 32,
      questionId
    );
  });

  state.graph.defeaters.forEach(defeater => {
    const targetArgument = argumentById(defeater.target_id);
    if (!targetArgument || !visible.has(targetArgument.conclusion_claim_id)) return;
    const target = routeGeometry.get(defeater.target_id);
    if (!target) return;
    const backingId = (defeater.premise_claim_ids || [])
      .find(id => visible.has(id));

    if (backingId) {
      const backingNode = lane.querySelector(`[data-claim="${backingId}"]`);
      const backing = center(backingNode.getBoundingClientRect(), canvasRect);
      const d = curve(backing.right, backing.y, target.x, target.y);
      svgPath(svg, d, "defeater-path", `url(#attack-${questionId})`);
    } else {
      const d = `M ${target.x} ${target.y + 38} L ${target.x} ${target.y + 5}`;
      svgPath(svg, d, "defeater-path", `url(#attack-${questionId})`);
    }

    const badge = document.createElement("button");
    badge.type = "button";
    badge.className = "defeater-label";
    badge.style.left = `${Math.max(4, target.x - 42)}px`;
    badge.style.top = `${target.y + 38}px`;
    badge.textContent = `${defeater.id} · ${defeater.attack_type}`;
    badge.addEventListener("click", () =>
      openArgument(defeater.target_id, questionId, true)
    );
    canvas.appendChild(badge);
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
    <article class="ghost-question">
      <div class="ghost-question__top">
        <span>${esc(question.id)} · ${esc(question.type)}</span>
        <span>${esc(question.disposition.replaceAll("_", " "))}</span>
      </div>
      <p>${esc(question.question)}</p>
      <small>${esc(question.disposition_reason)}</small>
    </article>`).join("");
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
  return sourceIds
    .map(id => state.assessments[id])
    .find(Boolean);
}

function openClaim(claimId, questionId) {
  const claim = claimById(claimId);
  const sourceAssessment = sourceAssessmentFor(claim);
  const argument = argumentsFor(claimId)[0];
  const terminal = terminalFor(questionId, claimId);
  showDialog(`
    <article class="inspector">
      <div class="inspector__eyebrow">${esc(claimId)} · claim node${terminal ? ` · terminal for ${esc(questionId)}` : ""}</div>
      <h3>${esc(claim.proposition)}</h3>
      ${metricPills([
        [evidenceState(claimId), "evidential state"],
        [coverageState(claimId), "coverage"],
        [claim.modality, "modality"],
        [argument?.assessment || "none", "argument"]
      ])}
      <section class="inspector__section">
        <h4>Role in the graph</h4>
        <p>${esc((claim.roles || []).join(" · "))}</p>
      </section>
      <section class="inspector__section">
        <h4>Why the support route bears on this claim</h4>
        <p>${esc(argument?.warrant_reconstruction || "No argument attempt recorded.")}</p>
      </section>
      <section class="inspector__section">
        <h4>Source assessment</h4>
        <p>${esc(
          sourceAssessment?.comparator?.rationale ||
          sourceAssessment?.verifier?.rationale ||
          "This reconstructed claim has no directly inherited assessment rationale."
        )}</p>
      </section>
      <section class="inspector__section">
        <h4>Reconstruction status</h4>
        <p>${esc(claim.display_assessment?.derivation)}. Independent review:
          <b>${esc(claim.display_assessment?.independent_review_status)}</b>.</p>
      </section>
    </article>`);
}

function openArgument(argumentId, questionId, focusDefeaters = false) {
  const argument = argumentById(argumentId);
  const claim = claimById(argument.conclusion_claim_id);
  const grounds = argument.ground_ids.map(groundById).filter(Boolean);
  const defeaters = defeatersFor(argument.id);
  const premiseClaims = argument.premise_claim_ids.map(claimById).filter(Boolean);
  showDialog(`
    <article class="inspector">
      <div class="inspector__eyebrow">${esc(argument.id)} · argument relation · ${esc(questionId)}</div>
      <h3>${esc(argument.scheme || argument.inference_type)} → ${esc(claim.id)}</h3>
      ${metricPills([
        [argument.assessment, "strength"],
        [argument.strictness, "strictness"],
        [argument.warrant_fidelity, "warrant fidelity"],
        [grounds.length, "grounds"]
      ])}
      ${premiseClaims.length ? `
        <section class="inspector__section">
          <h4>Claim premises</h4>
          <ul>${premiseClaims.map(premise =>
            `<li><b>${esc(premise.id)}</b> — ${esc(premise.proposition)}</li>`
          ).join("")}</ul>
        </section>` : ""}
      <section class="inspector__section">
        <h4>Warrant reconstruction</h4>
        <p>${esc(argument.warrant_reconstruction)}</p>
      </section>
      <section class="inspector__section">
        <h4>${grounds.length ? "Grounds cited by this relation" : "Evidence requirement"}</h4>
        ${grounds.map(ground => `
          <div class="ground">
            <p>${esc(ground.content)}</p>
            ${ground.url ? `<a href="${esc(ground.url)}" target="_blank" rel="noreferrer">${esc(ground.source_title || "open source")} ↗</a>` : ""}
          </div>`).join("") || `
            <p>No direct grounds are attached.</p>
            <ul>${(argument.anticipated_ground_kinds || []).map(item =>
              `<li>${esc(item)}</li>`
            ).join("")}</ul>`}
      </section>
      <section class="inspector__section" ${focusDefeaters ? 'data-focused="true"' : ""}>
        <h4>Defeaters targeting this argument</h4>
        ${defeaters.map(defeater => `
          <div class="defeater">
            <b>${esc(defeater.id)} · ${esc(defeater.attack_type)}</b> · ${esc(defeater.status)}<br>
            ${esc(defeater.content)}
            ${(defeater.premise_claim_ids || []).length
              ? `<br><small>backed by ${esc(defeater.premise_claim_ids.join(", "))}</small>`
              : ""}
          </div>`).join("") || "<p>No defeaters recorded.</p>"}
      </section>
      <section class="inspector__section">
        <h4>Formal status</h4>
        <p>${argument.formal_candidate?.suitable
          ? "Marked as a candidate for formal validation."
          : `Not formalized: ${esc(argument.formal_candidate?.reason || "no reason recorded")}`}</p>
      </section>
    </article>`);
}

function showDialog(content) {
  const dialog = document.getElementById("inspector");
  document.getElementById("dialog-content").innerHTML = content;
  dialog.showModal();
  const focused = dialog.querySelector('[data-focused="true"]');
  if (focused) {
    requestAnimationFrame(() => focused.scrollIntoView({ block: "center" }));
  }
}

async function init() {
  try {
    const response = await fetch("data.json");
    if (!response.ok) throw new Error(`data.json: ${response.status}`);
    Object.assign(state, await response.json());
    renderMetrics();
    renderAnswer();
    renderLanes();
    renderDeferred();
  } catch (error) {
    document.body.innerHTML = `<div class="error"><b>Could not load the run artifact.</b><br>${esc(error.message)}<br><br>Open this page through the local HTTP server, not as a file.</div>`;
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
