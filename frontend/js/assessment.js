// assessment.js - renders the questionnaire, submits answers, shows results + simulator.
(async function () {
  const answers = {};            // answers live ONLY in browser memory
  let questions = [], lastResult = null;
  const $ = id => document.getElementById(id);

  const data = await api("/api/questionnaire");
  questions = data.questions;
  const box = $("questions");
  data.categories.forEach(cat => {
    const card = el("div", { class: "card" }, el("h2", {}, `Category ${cat.letter}: ${cat.label}`), el("p", { class: "small muted" }, cat.description));
    questions.filter(q => q.category === cat.key).forEach(q => {
      const opts = el("div", { class: "opts" });
      q.options.forEach(o => {
        const input = el("input", { type: "radio", name: q.id, value: o.value });
        input.addEventListener("change", () => { answers[q.id] = o.value; updateProgress(); });
        opts.append(el("label", {}, input, o.label));
      });
      card.append(el("div", { class: "q" }, el("p", {}, `${q.id}. ${q.text}`), opts));
    });
    box.append(card);
  });

  function updateProgress() {
    const done = Object.keys(answers).length;
    $("progressText").textContent = `${done} / ${questions.length} answered`;
    $("progressBar").style.width = (100 * done / questions.length) + "%";
    $("submitBtn").disabled = done < questions.length;
  }
  updateProgress();

  $("submitBtn").addEventListener("click", async () => {
    $("formError").textContent = "";
    try {
      lastResult = await api("/api/assessment", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ responses: answers }) });
      showResults(lastResult);
    } catch (e) { $("formError").textContent = e.message; }
  });

  function showResults(r) {
    $("quiz").classList.add("hidden"); $("results").classList.remove("hidden"); window.scrollTo(0, 0);
    $("rScore").textContent = r.overall_score + "/100";
    $("rLevel").replaceChildren(levelBadge(r.risk_level));
    $("rControls").textContent = `${r.controls.enabled}/${r.controls.total}`;
    $("rFindings").textContent = r.findings.length;
    const labels = Object.keys(r.category_scores).map(k => CAT_LABELS[k]);
    const values = Object.values(r.category_scores);
    new Chart($("radar"), { type: "radar", data: { labels, datasets: [{ label: "Risk (higher = worse)", data: values, backgroundColor: "rgba(198,40,40,.2)", borderColor: "#c62828" }] },
      options: { maintainAspectRatio: false, scales: { r: { min: 0, max: 100 } } } });
    new Chart($("bars"), { type: "bar", data: { labels, datasets: [{ label: "Risk score", data: values, backgroundColor: values.map(colorForScore) }] },
      options: { indexAxis: "y", maintainAspectRatio: false, scales: { x: { min: 0, max: 100 } }, plugins: { legend: { display: false } } } });

    const fl = $("findingsList"); fl.replaceChildren();
    if (!r.findings.length) fl.append(el("p", {}, "No weaknesses detected from your answers. Keep reviewing settings regularly."));
    r.findings.slice(0, 10).forEach((f, i) => fl.append(el("div", { class: "f" }, el("span", { class: "tag" }, f.severity), el("div", {}, `${i + 1}. ${f.description}`, el("div", { class: "small muted" }, f.category_label)))));

    const rl = $("recList"); rl.replaceChildren();
    r.recommendations.forEach(x => rl.append(el("div", { class: "f" }, el("span", { class: "tag" }, x.priority), el("div", {}, x.recommendation))));

    const sc = $("simChecks"); sc.replaceChildren();
    r.findings.forEach(f => {
      const cb = el("input", { type: "checkbox", value: f.question_id });
      sc.append(el("label", {}, cb, ` Fix: ${f.description}`));
    });
    $("assessId").textContent = "Assessment ID: " + r.assessment_id + " (keep it to reopen your report)";
    $("disclaimer").textContent = r.disclaimer;
    $("reportLink").href = `/api/assessment/${r.assessment_id}/report`;
    $("reportDl").href = `/api/assessment/${r.assessment_id}/report?download=1`;
  }

  $("simBtn").addEventListener("click", async () => {
    const changes = [...document.querySelectorAll("#simChecks input:checked")].map(c => c.value);
    const out = $("simOut"); out.replaceChildren();
    if (!changes.length) { out.append(el("p", { class: "muted" }, "Tick at least one finding first.")); return; }
    try {
      const s = await api("/api/assessment/simulate-improvement", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ responses: answers, changes }) });
      out.append(el("div", { class: "grid g4" },
        el("div", { class: "card stat" }, el("div", { class: "l" }, "Current"), el("div", { class: "v" }, s.current.overall_score + "/100"), levelBadge(s.current.risk_level)),
        el("div", { class: "card stat" }, el("div", { class: "l" }, "Simulated"), el("div", { class: "v" }, s.simulated.overall_score + "/100"), levelBadge(s.simulated.risk_level)),
        el("div", { class: "card stat" }, el("div", { class: "l" }, "Risk reduction"), el("div", { class: "v" }, s.risk_reduction + " points"))),
        el("p", { class: "small muted" }, s.disclaimer));
    } catch (e) { out.append(el("p", {}, e.message)); }
  });

  $("delBtn").addEventListener("click", async () => {
    if (!lastResult || !confirm("Delete this assessment from the server?")) return;
    try {
      await api(`/api/assessment/${lastResult.assessment_id}`, { method: "DELETE", headers: { "X-Delete-Token": lastResult.delete_token } });
      $("assessId").textContent = "Your stored assessment has been deleted.";
      $("reportLink").classList.add("hidden"); $("reportDl").classList.add("hidden");
    } catch (e) { alert(e.message); }
  });
})();
