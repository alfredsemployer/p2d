const state = {};

const esc = value => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;");

function evidenceState(claimId) {
  return state.assessments[claimId]?.derived_verdict?.evidential_state || "unassessed";
}

function coverageState(claimId) {
  return state.assessments[claimId]?.derived_verdict?.coverage_state || "not assessed";
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
  const terminals = Object.values(state.graph.terminal_claim_ids_by_question || {})
    .reduce((sum, ids) => sum + ids.length, 0);
  const formal = state.graph.arguments.filter(argument => argument.formal_candidate?.suitable).length;
  const items = [
    [`${state.portfolio.questions.filter(q => q.disposition === "active").length}`, "active questions"],
    [state.graph.claims.length, "claims"],
    [state.graph.arguments.length, "arguments"],
    [state.graph.defeaters.length, "defeaters"],
    [terminals, "terminal assignments"],
    [formal, "strict formalizations"]
  ];
  document.getElementById("metrics").innerHTML = items
    .map(([value, label]) => `<span class="metric"><b>${value}</b> ${label}</span>`)
    .join("");
}

function renderAnswer() {
  document.getElementById("synthesis").textContent = state.answer.overall_synthesis;
  const audit = document.getElementById("audit");
  audit.textContent = state.audit.pass
    ? "Independent prose audit passed · 0 fidelity issues"
    : `Independent prose audit found ${state.audit.issues?.length || 0} issues`;

  const target = document.getElementById("verdicts");
  const template = document.getElementById("verdict-template");
  state.answer.question_verdicts.forEach(item => {
    const node = template.content.firstElementChild.cloneNode(true);
    node.querySelector(".verdict__id").textContent = `${item.question_id} verdict`;
    node.querySelector(".status-pill").textContent = `${item.evidential_state} / ${item.coverage_state}`;
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

function claimPosition(index, total, terminal) {
  const mobile = window.innerWidth < 900;
  const left = terminal ? (mobile ? 39 : 70) : (mobile ? 39 : 42);
  const top = 18 + index * (mobile ? 152 : 132);
  return { left, top };
}

function renderLanes() {
  const lanes = document.getElementById("lanes");
  lanes.innerHTML = "";

  state.portfolio.questions
    .filter(question => question.disposition === "active")
    .forEach(question => {
      const claims = state.graph.claims.filter(claim =>
        (claim.question_ids || []).includes(question.id)
      );
      const ordered = [...claims].sort((a, b) =>
        Number(terminalFor(question.id, a.id)) - Number(terminalFor(question.id, b.id))
      );

      const lane = document.createElement("section");
      lane.className = "question-lane";
      lane.dataset.question = question.id;
      lane.innerHTML = `
        <div class="question-lane__heading">
          <div class="question-lane__id">${esc(question.id)}</div>
          <div class="question-lane__question">${esc(question.question)}</div>
          <div class="question-lane__type">${esc(question.type)} contract</div>
        </div>
        <div class="lane-canvas">
          <svg class="lane-svg" aria-hidden="true"></svg>
        </div>`;

      const canvas = lane.querySelector(".lane-canvas");
      canvas.style.height = `${Math.max(175, 34 + ordered.length * (window.innerWidth < 900 ? 152 : 132))}px`;

      ordered.forEach((claim, index) => {
        const terminal = terminalFor(question.id, claim.id);
        const position = claimPosition(index, ordered.length, terminal);
        const shared = (claim.question_ids || []).filter(id => id !== question.id);
        const node = document.createElement("button");
        node.type = "button";
        node.className = "claim-node";
        node.dataset.claim = claim.id;
        node.dataset.state = evidenceState(claim.id);
        node.style.left = `${position.left}%`;
        node.style.top = `${position.top}px`;
        node.innerHTML = `
          <span class="claim-node__meta">
            <b>${esc(claim.id)}</b>
            <span>${esc(evidenceState(claim.id))} · ${esc(coverageState(claim.id))}</span>
          </span>
          <span class="claim-node__text">${esc(claim.proposition)}</span>
          <span class="claim-node__foot">
            ${terminal ? '<span class="terminal-mark">terminal</span>' : ""}
            ${shared.length ? `<span class="shared-mark">also ${esc(shared.join(", "))}</span>` : ""}
          </span>`;
        node.addEventListener("click", () => openClaim(claim.id, question.id));
        canvas.appendChild(node);

        const argument = argumentsFor(claim.id)[0];
        if (!argument) return;
        const label = document.createElement("button");
        label.type = "button";
        label.className = "route-label";
        label.dataset.argument = argument.id;
        label.style.left = "1.2%";
        label.style.top = `${position.top + 33}px`;
        label.innerHTML = `${esc(argument.id)} · ${esc(argument.scheme || argument.inference_type)}
          <small>${argument.ground_ids.length} grounds · ${esc(argument.assessment)}</small>`;
        label.addEventListener("click", () => openArgument(argument.id, question.id));
        canvas.appendChild(label);

        const defeaters = defeatersFor(argument.id);
        if (defeaters.length) {
          const badge = document.createElement("button");
          badge.type = "button";
          badge.className = "defeater-label";
          badge.style.left = terminal ? "50%" : "31%";
          badge.style.top = `${position.top + 75}px`;
          badge.textContent = `${defeaters.length} defeater${defeaters.length === 1 ? "" : "s"}`;
          badge.addEventListener("click", () => openArgument(argument.id, question.id, true));
          canvas.appendChild(badge);
        }
      });

      lanes.appendChild(lane);
    });

  requestAnimationFrame(drawAllRoutes);
}

function drawAllRoutes() {
  document.querySelectorAll(".question-lane").forEach(lane => {
    const canvas = lane.querySelector(".lane-canvas");
    const svg = lane.querySelector(".lane-svg");
    const canvasRect = canvas.getBoundingClientRect();
    svg.setAttribute("viewBox", `0 0 ${canvasRect.width} ${canvasRect.height}`);
    svg.innerHTML = `
      <defs>
        <marker id="arrow-${lane.dataset.question}" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 9 5 L 0 9 z" fill="#3e6579"></path>
        </marker>
      </defs>`;

    lane.querySelectorAll(".route-label").forEach(label => {
      const argument = state.graph.arguments.find(item => item.id === label.dataset.argument);
      const node = lane.querySelector(`[data-claim="${argument.conclusion_claim_id}"]`);
      if (!node) return;
      const labelRect = label.getBoundingClientRect();
      const nodeRect = node.getBoundingClientRect();
      const x1 = labelRect.right - canvasRect.left + 8;
      const y1 = labelRect.top - canvasRect.top + labelRect.height / 2;
      const x2 = nodeRect.left - canvasRect.left - 7;
      const y2 = nodeRect.top - canvasRect.top + nodeRect.height / 2;
      const bend = Math.max(30, (x2 - x1) * .48);
      const d = `M ${x1} ${y1} C ${x1 + bend} ${y1}, ${x2 - bend} ${y2}, ${x2} ${y2}`;
      const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
      const hit = document.createElementNS("http://www.w3.org/2000/svg", "path");
      hit.setAttribute("d", d);
      hit.setAttribute("class", "route-hit");
      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", d);
      path.setAttribute("class", "route-path");
      path.setAttribute("marker-end", `url(#arrow-${lane.dataset.question})`);
      group.append(hit, path);
      svg.appendChild(group);
    });
  });
}

function renderDeferred() {
  const target = document.getElementById("deferred");
  const questions = state.portfolio.questions.filter(question => question.disposition !== "active");
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
    .map(([value, label]) => `<span class="metric"><b>${esc(value)}</b> ${esc(label)}</span>`)
    .join("")}</div>`;
}

function openClaim(claimId, questionId) {
  const claim = state.graph.claims.find(item => item.id === claimId);
  const assessment = state.assessments[claimId];
  const argument = argumentsFor(claimId)[0];
  const support = assessment?.verifier;
  const challenge = assessment?.falsifier;
  const terminal = terminalFor(questionId, claimId);
  showDialog(`
    <article class="inspector">
      <div class="inspector__eyebrow">${esc(claimId)} · claim node${terminal ? " · terminal for " + esc(questionId) : ""}</div>
      <h3>${esc(claim.proposition)}</h3>
      ${metricPills([
        [evidenceState(claimId), "evidential state"],
        [coverageState(claimId), "coverage"],
        [claim.modality, "modality"],
        [argument?.assessment || "none", "argument"]
      ])}
      <section class="inspector__section">
        <h4>Why the support route bears on this claim</h4>
        <p>${esc(argument?.warrant_reconstruction || "No argument attempt recorded.")}</p>
      </section>
      <section class="inspector__section">
        <h4>Assessment</h4>
        <p>${esc(assessment?.comparator?.rationale || support?.rationale || "No assessment recorded.")}</p>
      </section>
      <section class="inspector__section">
        <h4>Conditions</h4>
        <ul>${(claim.conditions || []).map(item => `<li>${esc(item)}</li>`).join("")}</ul>
      </section>
      <section class="inspector__section">
        <h4>What could falsify or overturn it</h4>
        <ul>${(claim.conceivable_falsifiers || []).map(item => `<li>${esc(item)}</li>`).join("")}</ul>
      </section>
      <section class="inspector__section">
        <h4>Strongest recorded challenge</h4>
        <p>${esc(challenge?.rationale || "No challenge rationale recorded.")}</p>
      </section>
    </article>`);
}

function openArgument(argumentId, questionId, focusDefeaters = false) {
  const argument = state.graph.arguments.find(item => item.id === argumentId);
  const claim = state.graph.claims.find(item => item.id === argument.conclusion_claim_id);
  const grounds = argument.ground_ids.map(groundById).filter(Boolean);
  const defeaters = defeatersFor(argument.id);
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
      <section class="inspector__section">
        <h4>Warrant reconstruction</h4>
        <p>${esc(argument.warrant_reconstruction)}</p>
      </section>
      <section class="inspector__section">
        <h4>Grounds cited by this relation</h4>
        ${grounds.map(ground => `
          <div class="ground">
            <p>${esc(ground.content)}</p>
            ${ground.url ? `<a href="${esc(ground.url)}" target="_blank" rel="noreferrer">${esc(ground.source_title || "open source")} ↗</a>` : ""}
          </div>`).join("") || "<p>No grounds recorded.</p>"}
      </section>
      <section class="inspector__section" ${focusDefeaters ? 'data-focused="true"' : ""}>
        <h4>Defeaters targeting this argument</h4>
        ${defeaters.map(defeater => `
          <div class="defeater">
            <b>${esc(defeater.attack_type)}</b> · ${esc(defeater.status)}<br>
            ${esc(defeater.content)}
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
  if (focused) requestAnimationFrame(() => focused.scrollIntoView({ block: "center" }));
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
  window.__resizeTimer = setTimeout(renderLanes, 120);
});

init();
