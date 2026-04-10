const goals = [
  {
    title: "Ship an onboarding path that ends in a visible win",
    theme: "Product",
    summary: "Turn a blank first-run into a guided flow that proves the core value in under two minutes.",
    why: "Empty or confusing starts hide the product's upside and flatten retention before users reach value.",
    slice: "Build a 3-step starter checklist, persist completion locally, and end with a celebratory success state.",
    risk: "If the checklist is generic, it becomes ceremony. The first step needs to touch the actual product loop.",
    impact: 5,
    speed: 4,
    novelty: 2
  },
  {
    title: "Add a comparison mode that exposes before-and-after change",
    theme: "UX",
    summary: "Make improvement legible by showing baseline and enhanced states side by side.",
    why: "Users trust tools faster when the delta is obvious instead of implied through labels or claims.",
    slice: "Create a split-view card with toggleable sample data and one high-signal metric beneath it.",
    risk: "Comparison views can overfit to demo data. Keep the first version honest and narrowly scoped.",
    impact: 4,
    speed: 3,
    novelty: 4
  },
  {
    title: "Create a local insight dashboard with recent activity patterns",
    theme: "Analytics",
    summary: "Surface trend lines and hotspots so the project starts informing decisions instead of just recording actions.",
    why: "Teams improvise badly when they cannot see momentum, drop-offs, or the shape of recent usage.",
    slice: "Add a dashboard with three cards: volume, streak, and most-used area over the last seven sessions.",
    risk: "Instrumentation debt piles up fast. Start with a compact event schema and avoid vanity charts.",
    impact: 5,
    speed: 2,
    novelty: 3
  },
  {
    title: "Package the project as an install-free static demo",
    theme: "Delivery",
    summary: "Remove setup friction so anyone can open the repo and experience the idea immediately.",
    why: "Distribution bottlenecks kill feedback loops; easy sharing creates faster iteration pressure.",
    slice: "Consolidate the first demo into static assets with one commandless launch path and sample content.",
    risk: "A static demo can diverge from the eventual architecture. Keep it as a proving ground, not a fork.",
    impact: 4,
    speed: 5,
    novelty: 2
  },
  {
    title: "Introduce a playful mode that turns utility into habit",
    theme: "Engagement",
    summary: "Add a light reward loop so repeat use feels earned rather than purely transactional.",
    why: "A small layer of delight can increase return frequency when the core tool is already competent.",
    slice: "Add streaks, rotating prompts, and one lightweight unlock tied to meaningful usage milestones.",
    risk: "Gamification becomes noise if it is detached from useful behavior. Reward progress, not clicks.",
    impact: 3,
    speed: 3,
    novelty: 5
  }
];

const themeSelect = document.querySelector("#theme");
const impactInput = document.querySelector("#impact");
const speedInput = document.querySelector("#speed");
const noveltyInput = document.querySelector("#novelty");
const generateButton = document.querySelector("#generate");
const goalList = document.querySelector("#goal-list");

const output = {
  score: document.querySelector("#goal-score"),
  theme: document.querySelector("#goal-theme"),
  title: document.querySelector("#goal-title"),
  summary: document.querySelector("#goal-summary"),
  why: document.querySelector("#goal-why"),
  slice: document.querySelector("#goal-slice"),
  risk: document.querySelector("#goal-risk")
};

const themes = ["All", ...new Set(goals.map((goal) => goal.theme))];

function buildThemes() {
  themeSelect.innerHTML = themes
    .map((theme) => `<option value="${theme}">${theme}</option>`)
    .join("");
}

function scoreGoal(goal) {
  return (
    goal.impact * Number(impactInput.value) +
    goal.speed * Number(speedInput.value) +
    goal.novelty * Number(noveltyInput.value)
  );
}

function filteredGoals() {
  const selectedTheme = themeSelect.value;
  return goals
    .filter((goal) => selectedTheme === "All" || goal.theme === selectedTheme)
    .map((goal) => ({ ...goal, score: scoreGoal(goal) }))
    .sort((a, b) => b.score - a.score);
}

function renderCards(activeTitle) {
  const ranked = filteredGoals();
  goalList.innerHTML = ranked
    .map(
      (goal) => `
        <article class="goal-card ${goal.title === activeTitle ? "active" : ""}">
          <div class="goal-meta">
            <strong>${goal.theme}</strong>
            <span>${goal.score} pts</span>
          </div>
          <h3>${goal.title}</h3>
          <p>${goal.summary}</p>
        </article>
      `
    )
    .join("");
}

function renderGoal(goal) {
  output.score.textContent = `Score ${goal.score}`;
  output.theme.textContent = goal.theme;
  output.title.textContent = goal.title;
  output.summary.textContent = goal.summary;
  output.why.textContent = goal.why;
  output.slice.textContent = goal.slice;
  output.risk.textContent = goal.risk;
  renderCards(goal.title);
}

function pickGoal() {
  const ranked = filteredGoals();
  const bestScore = ranked[0]?.score ?? 0;
  const finalists = ranked.filter((goal) => goal.score === bestScore);
  const chosen = finalists[Math.floor(Math.random() * finalists.length)];
  if (chosen) {
    renderGoal(chosen);
  }
}

[themeSelect, impactInput, speedInput, noveltyInput].forEach((input) => {
  input.addEventListener("input", pickGoal);
});

generateButton.addEventListener("click", pickGoal);

buildThemes();
pickGoal();
