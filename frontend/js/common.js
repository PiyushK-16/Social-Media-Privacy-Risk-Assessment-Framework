// common.js - tiny helpers shared by all pages. Server data is ALWAYS inserted with
// textContent (never innerHTML), which prevents XSS.
async function api(path, options) {
  const res = await fetch(path, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const e = data.error || {};
    throw new Error((e.message || "Request failed") + (e.details ? " " + e.details.join(" ") : ""));
  }
  return data;
}
function el(tag, props, ...children) {
  const node = document.createElement(tag);
  Object.entries(props || {}).forEach(([k, v]) => {
    if (k === "class") node.className = v; else node.setAttribute(k, v);
  });
  children.flat().forEach(c => node.append(c instanceof Node ? c : document.createTextNode(String(c))));
  return node;
}
function levelBadge(level) { return el("span", { class: "lvl " + level }, level); }
const CAT_LABELS = {
  profile: "Profile", personal_info: "Personal Info", location: "Location", content: "Content",
  connections: "Connections", tagging: "Tagging", account_security: "Account Security",
  third_party: "Third-Party Apps", social_engineering: "Social Engineering", digital_footprint: "Digital Footprint"
};
function colorForScore(s) { return s <= 20 ? "#2e9e5b" : s <= 40 ? "#c9a400" : s <= 70 ? "#e07b00" : "#c62828"; }
