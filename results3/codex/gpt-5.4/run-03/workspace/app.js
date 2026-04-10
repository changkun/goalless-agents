const STORAGE_KEY = "decision-journal-entries";

const initialEntries = [
  {
    id: crypto.randomUUID(),
    title: "Move status updates to weekly batches",
    context: "Daily syncs were expensive and repeated the same information.",
    choice: "Replace daily updates with one weekly written digest.",
    alternatives: ["Keep daily meetings", "Cut updates entirely"],
    confidence: 7,
    reviewDate: "2026-04-20",
    createdAt: "2026-04-09T00:00:00.000Z",
    outcome: "pending",
  },
];

const form = document.querySelector("#decision-form");
const titleInput = document.querySelector("#title");
const contextInput = document.querySelector("#context");
const choiceInput = document.querySelector("#choice");
const alternativesInput = document.querySelector("#alternatives");
const confidenceInput = document.querySelector("#confidence");
const confidenceValue = document.querySelector("#confidence-value");
const reviewDateInput = document.querySelector("#reviewDate");
const statusFilter = document.querySelector("#status-filter");
const entryList = document.querySelector("#entry-list");
const emptyState = document.querySelector("#empty-state");
const template = document.querySelector("#entry-template");

const statTotal = document.querySelector("#stat-total");
const statOpen = document.querySelector("#stat-open");
const statReviewed = document.querySelector("#stat-reviewed");
const statConfidence = document.querySelector("#stat-confidence");

let entries = loadEntries();

confidenceInput.addEventListener("input", () => {
  confidenceValue.textContent = `${confidenceInput.value} / 10`;
});

form.addEventListener("submit", (event) => {
  event.preventDefault();

  const entry = {
    id: crypto.randomUUID(),
    title: titleInput.value.trim(),
    context: contextInput.value.trim(),
    choice: choiceInput.value.trim(),
    alternatives: parseAlternatives(alternativesInput.value),
    confidence: Number(confidenceInput.value),
    reviewDate: reviewDateInput.value || "",
    createdAt: new Date().toISOString(),
    outcome: "pending",
  };

  entries = [entry, ...entries];
  persistEntries();
  form.reset();
  confidenceInput.value = "6";
  confidenceValue.textContent = "6 / 10";
  render();
});

statusFilter.addEventListener("change", render);

entryList.addEventListener("change", (event) => {
  const target = event.target;

  if (!(target instanceof HTMLSelectElement) || !target.matches(".outcome-select")) {
    return;
  }

  const id = target.closest(".entry-card")?.dataset.id;
  entries = entries.map((entry) =>
    entry.id === id ? { ...entry, outcome: target.value } : entry,
  );
  persistEntries();
  render();
});

entryList.addEventListener("click", (event) => {
  const target = event.target;

  if (!(target instanceof HTMLButtonElement) || !target.matches(".delete-button")) {
    return;
  }

  const id = target.closest(".entry-card")?.dataset.id;
  entries = entries.filter((entry) => entry.id !== id);
  persistEntries();
  render();
});

render();

function loadEntries() {
  const raw = localStorage.getItem(STORAGE_KEY);

  if (!raw) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(initialEntries));
    return initialEntries;
  }

  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : initialEntries;
  } catch {
    return initialEntries;
  }
}

function persistEntries() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
}

function parseAlternatives(value) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function render() {
  const visibleEntries = filterEntries(entries, statusFilter.value);
  entryList.innerHTML = "";

  for (const entry of visibleEntries) {
    const node = template.content.firstElementChild.cloneNode(true);
    node.dataset.id = entry.id;
    node.querySelector(".entry-title").textContent = entry.title;
    node.querySelector(".entry-meta").textContent = buildMeta(entry);
    node.querySelector(".entry-badge").textContent = outcomeLabel(entry.outcome);
    node.querySelector(".entry-context").textContent = entry.context;
    node.querySelector(".entry-choice").textContent = entry.choice;
    node.querySelector(".entry-alternatives").textContent =
      entry.alternatives.length > 0 ? entry.alternatives.join(", ") : "No alternatives recorded.";
    node.querySelector(".outcome-select").value = entry.outcome;
    entryList.appendChild(node);
  }

  emptyState.hidden = visibleEntries.length !== 0;
  updateStats(entries);
}

function filterEntries(allEntries, filter) {
  switch (filter) {
    case "open":
      return allEntries.filter((entry) => entry.outcome === "pending");
    case "reviewed":
      return allEntries.filter((entry) => entry.outcome !== "pending");
    case "wins":
      return allEntries.filter((entry) => entry.outcome === "positive");
    default:
      return allEntries;
  }
}

function updateStats(allEntries) {
  const reviewedCount = allEntries.filter((entry) => entry.outcome !== "pending").length;
  const openCount = allEntries.length - reviewedCount;
  const avgConfidence =
    allEntries.length === 0
      ? 0
      : allEntries.reduce((sum, entry) => sum + Number(entry.confidence), 0) / allEntries.length;

  statTotal.textContent = String(allEntries.length);
  statOpen.textContent = String(openCount);
  statReviewed.textContent = String(reviewedCount);
  statConfidence.textContent = avgConfidence.toFixed(1);
}

function buildMeta(entry) {
  const created = new Date(entry.createdAt).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  const review = entry.reviewDate
    ? `Review ${new Date(entry.reviewDate).toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
      })}`
    : "No review date";

  return `${created} • Confidence ${entry.confidence}/10 • ${review}`;
}

function outcomeLabel(outcome) {
  switch (outcome) {
    case "positive":
      return "Positive";
    case "mixed":
      return "Mixed";
    case "negative":
      return "Negative";
    default:
      return "Pending";
  }
}
