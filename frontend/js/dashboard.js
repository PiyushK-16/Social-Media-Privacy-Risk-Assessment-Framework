// dashboard.js - aggregate charts built from the SYNTHETIC dataset (+ live counts).
(async function () {
  const $ = id => document.getElementById(id);
  const s = await api("/api/dashboard/stats");
  $("source").textContent = `Data source: ${s.data_source}. ${s.dataset_size} fictional profiles.`;
  $("cScore").textContent = s.average_score;
  const top = Object.entries(s.level_distribution).sort((a, b) => b[1] - a[1])[0][0];
  $("cLevel").replaceChildren(levelBadge(top));
  $("cHigh").textContent = s.high_risk_categories.length;
  $("cRecs").textContent = s.recommendation_count;
  $("cControls").textContent = s.average_controls_enabled_percent + "%";
  $("cLive").textContent = s.live.total_assessments;
  $("disc").textContent = s.disclaimer;

  const cats = s.average_category_scores;
  new Chart($("ch1"), { type: "bar", data: { labels: cats.map(c => CAT_LABELS[c.key]), datasets: [{ label: "Avg risk", data: cats.map(c => c.score), backgroundColor: cats.map(c => colorForScore(c.score)) }] },
    options: { indexAxis: "y", maintainAspectRatio: false, scales: { x: { min: 0, max: 100 } }, plugins: { legend: { display: false } } } });
  const lv = s.level_distribution;
  new Chart($("ch2"), { type: "doughnut", data: { labels: Object.keys(lv), datasets: [{ data: Object.values(lv), backgroundColor: ["#2e9e5b", "#c9a400", "#e07b00", "#c62828"] }] }, options: { maintainAspectRatio: false } });
  new Chart($("ch3"), { type: "bar", data: { labels: s.top_weaknesses.map(w => w.finding_type), datasets: [{ label: "% of profiles", data: s.top_weaknesses.map(w => w.percent), backgroundColor: "#2f5fd0" }] },
    options: { indexAxis: "y", maintainAspectRatio: false, plugins: { legend: { display: false } } } });
  new Chart($("ch4"), { type: "bar", data: { labels: s.account_controls.map(c => c.feature), datasets: [{ label: "% enabled", data: s.account_controls.map(c => c.percent_enabled), backgroundColor: "#2e9e5b" }] },
    options: { maintainAspectRatio: false, scales: { y: { min: 0, max: 100 } }, plugins: { legend: { display: false } } } });
  const fp = s.digital_footprint_distribution;
  new Chart($("ch5"), { type: "bar", data: { labels: Object.keys(fp), datasets: [{ label: "Profiles", data: Object.values(fp), backgroundColor: ["#2e9e5b", "#c9a400", "#e07b00", "#c62828"] }] },
    options: { maintainAspectRatio: false, plugins: { legend: { display: false } } } });
  const imp = s.improvement_comparison;
  new Chart($("ch6"), { type: "bar", data: { labels: ["Current", "After IMMEDIATE fixes", "After IMMEDIATE + IMPORTANT"], datasets: [{ label: "Avg score", data: [imp.current, imp.after_immediate_fixes, imp.after_immediate_and_important_fixes], backgroundColor: ["#c62828", "#e07b00", "#2e9e5b"] }] },
    options: { maintainAspectRatio: false, scales: { y: { min: 0, max: 100 } }, plugins: { legend: { display: false } } } });
})().catch(e => { document.getElementById("source").textContent = "Could not load dashboard: " + e.message; });
