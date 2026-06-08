const state = {
  players: [],
  selectedPlayerId: null,
};

const $ = (selector) => document.querySelector(selector);

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}

function formatNumber(value, digits = 0) {
  return Number(value).toLocaleString(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  });
}

function formatDate(value) {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

function renderSummary(reports, workflows) {
  const avg = state.players.reduce((total, player) => total + player.readiness_score, 0) / state.players.length;
  $("#playerCount").textContent = state.players.length;
  $("#avgReadiness").textContent = formatNumber(avg);
  $("#highPriority").textContent = workflows.filter((task) => task.priority === "High" && task.status !== "Done").length;
  $("#reportCount").textContent = reports.length;
  $("#lastUpdated").textContent = `Updated ${new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}`;
}

function renderPlayers() {
  const list = $("#playerList");
  list.innerHTML = "";

  state.players.forEach((player) => {
    const button = document.createElement("button");
    button.className = `player-card ${player.id === state.selectedPlayerId ? "active" : ""}`;
    button.type = "button";
    button.innerHTML = `
      <span>
        <strong>${player.name}</strong>
        <span class="meta">${player.position} · ${player.level} · Rank ${player.org_rank}</span>
      </span>
      <span class="badge">${player.readiness_score}</span>
    `;
    button.addEventListener("click", () => selectPlayer(player.id));
    list.appendChild(button);
  });

  const select = $("#workflowPlayer");
  select.innerHTML = state.players
    .map((player) => `<option value="${player.id}">${player.name}</option>`)
    .join("");
}

async function selectPlayer(playerId) {
  state.selectedPlayerId = playerId;
  renderPlayers();

  const detail = await api(`/api/players/${playerId}`);
  const latest = detail.metrics[0];
  $("#playerDetail").innerHTML = `
    <div class="section-title">
      <div>
        <h2>${detail.player.name}</h2>
        <span>${detail.player.position} · ${detail.player.level} · ${detail.player.status}</span>
      </div>
      <span class="badge">Org Rank ${detail.player.org_rank}</span>
    </div>

    <div class="status-line">
      <span class="badge">Bats ${detail.player.bats}</span>
      <span class="badge">Throws ${detail.player.throws}</span>
      <span class="badge">Age ${detail.player.age}</span>
      <span class="badge">Collected ${formatDate(latest.collected_at)}</span>
    </div>

    <div class="detail-grid">
      <div><span>OPS</span><strong>${formatNumber(latest.ops, 3)}</strong></div>
      <div><span>wOBA</span><strong>${formatNumber(latest.woba, 3)}</strong></div>
      <div><span>Sprint Speed</span><strong>${formatNumber(latest.sprint_speed, 1)}</strong></div>
      <div><span>Throw Velo</span><strong>${formatNumber(latest.throwing_velocity, 1)}</strong></div>
    </div>

    <h3>Performance Trend</h3>
    <div class="trend-list">
      ${detail.metrics
        .map((metric) => `
          <div class="trend-row">
            <span>${formatDate(metric.collected_at)}</span>
            <div class="bar"><span style="width: ${metric.readiness_score}%"></span></div>
            <strong>${metric.readiness_score}</strong>
          </div>
        `)
        .join("")}
    </div>
  `;
}

function renderReports(reports) {
  $("#reportList").innerHTML = reports
    .map((report) => `
      <article class="report-card">
        <h3>${report.title}</h3>
        <p>${report.summary}</p>
        <small>${report.player} · ${report.author} · ${formatDate(report.created_at)}</small>
      </article>
    `)
    .join("");
}

function renderWorkflows(workflows) {
  $("#workflowList").innerHTML = workflows
    .map((task) => `
      <article class="workflow-card">
        <div>
          <strong>${task.title}</strong>
          <div class="meta">${task.player} · ${task.owner} · due ${formatDate(task.due_date)}</div>
        </div>
        <span class="badge priority-${task.priority.toLowerCase()}">${task.priority}</span>
      </article>
    `)
    .join("");
}

async function renderRecommendations() {
  const { recommendations } = await api("/api/recommendations", { method: "POST", body: "{}" });
  $("#recommendations").innerHTML = recommendations
    .map((item) => `
      <article class="recommendation-card">
        <div class="section-title">
          <h3>${item.player}</h3>
          <span class="badge">${item.confidence}%</span>
        </div>
        <strong>${item.action}</strong>
        <p class="meta">${item.rationale}</p>
      </article>
    `)
    .join("");
}

async function loadDashboard() {
  const [{ players }, { reports }, { workflows }] = await Promise.all([
    api("/api/players"),
    api("/api/reports"),
    api("/api/workflows"),
  ]);

  state.players = players;
  state.selectedPlayerId = state.selectedPlayerId || players[0]?.id;
  renderSummary(reports, workflows);
  renderPlayers();
  renderReports(reports);
  renderWorkflows(workflows);

  if (state.selectedPlayerId) {
    await selectPlayer(state.selectedPlayerId);
  }
}

$("#refreshButton").addEventListener("click", loadDashboard);
$("#recommendButton").addEventListener("click", renderRecommendations);

$("#workflowForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  await api("/api/workflows", {
    method: "POST",
    body: JSON.stringify({
      playerId: $("#workflowPlayer").value,
      title: $("#workflowTitle").value,
      owner: $("#workflowOwner").value,
      priority: $("#workflowPriority").value,
      dueDate: $("#workflowDueDate").value,
    }),
  });
  event.target.reset();
  await loadDashboard();
});

$("#workflowDueDate").valueAsDate = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
loadDashboard().then(renderRecommendations);
