"use strict";

const KIND_ICON = {
  cpu: "🧠", gpu: "🎮", disk: "💽", board: "🔌", battery: "🔋", other: "📟",
};

let timer = null;
let intervalMs = 2000;
let paused = false;

function fmtTemp(c) {
  return c == null ? "--" : c.toFixed(1);
}

// Position 0→100% sur une plage 30°C → seuil critique.
function gaugePercent(reading) {
  if (reading.celsius == null) return 0;
  const min = 30;
  const max = reading.critical || reading.warning || 90;
  const pct = ((reading.celsius - min) / (max - min)) * 100;
  return Math.max(3, Math.min(100, pct));
}

function statusColor(status) {
  return getComputedStyle(document.documentElement)
    .getPropertyValue("--" + status).trim() || "#888";
}

function renderCard(group) {
  const hot = group.hottest;
  const card = document.createElement("section");
  card.className = "card status-" + group.status;

  const icon = KIND_ICON[group.kind] || KIND_ICON.other;
  const pct = hot ? gaugePercent(hot) : 0;

  card.innerHTML = `
    <div class="card-head">
      <span class="card-title">${icon} ${escapeHtml(group.name)}</span>
      <span class="card-kind">${escapeHtml(group.kind)}</span>
    </div>
    <div class="big-temp">${fmtTemp(hot && hot.celsius)}<span class="unit">°C</span></div>
    <div class="gauge"><span style="width:${pct}%;background:${statusColor(group.status)}"></span></div>
    <ul class="readings">
      ${group.readings.map(r => `
        <li>
          <span><span class="dot status-${r.status}"></span>${escapeHtml(r.label)}</span>
          <b>${fmtTemp(r.celsius)} °C</b>
        </li>`).join("")}
    </ul>`;
  return card;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"]/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

function render(snap) {
  const src = document.getElementById("source");
  const overall = document.getElementById("overall");
  const updated = document.getElementById("updated");

  src.textContent = "source: " + snap.source;
  overall.textContent = "état: " + snap.overall_status;
  overall.className = "pill status-" + snap.overall_status;
  updated.textContent = "màj: " + new Date(snap.timestamp * 1000).toLocaleTimeString();

  const grid = document.getElementById("grid");
  grid.innerHTML = "";
  snap.groups.forEach(g => grid.appendChild(renderCard(g)));
}

async function tick() {
  if (paused) return;
  try {
    const res = await fetch("/api/snapshot", { cache: "no-store" });
    if (!res.ok) throw new Error("HTTP " + res.status);
    render(await res.json());
  } catch (e) {
    document.getElementById("grid").innerHTML =
      `<div class="error">Erreur de lecture : ${escapeHtml(e.message)}</div>`;
  }
}

function schedule() {
  if (timer) clearInterval(timer);
  timer = setInterval(tick, intervalMs);
}

document.getElementById("interval").addEventListener("change", e => {
  intervalMs = parseInt(e.target.value, 10);
  schedule();
});

document.getElementById("pause").addEventListener("click", e => {
  paused = !paused;
  e.target.textContent = paused ? "▶ Reprendre" : "⏸ Pause";
  if (!paused) tick();
});

tick();
schedule();
