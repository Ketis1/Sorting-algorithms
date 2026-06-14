import { Visualizer, highlightsFromStep } from "./visualizer.js";

const algorithmSelect = document.getElementById("algorithm-select");
const arraySizeInput = document.getElementById("array-size");
const arraySizeValue = document.getElementById("array-size-value");
const speedInput = document.getElementById("speed");
const speedValue = document.getElementById("speed-value");
const shuffleBtn = document.getElementById("shuffle-btn");
const playBtn = document.getElementById("play-btn");
const pauseBtn = document.getElementById("pause-btn");
const stepBtn = document.getElementById("step-btn");
const resetBtn = document.getElementById("reset-btn");
const algorithmDescription = document.getElementById("algorithm-description");
const stepCount = document.getElementById("step-count");
const stepTotal = document.getElementById("step-total");
const compareCount = document.getElementById("compare-count");
const swapCount = document.getElementById("swap-count");
const vizTier = document.getElementById("viz-tier");
const statusMessage = document.getElementById("status-message");
const chart = document.getElementById("chart");

const visualizer = new Visualizer(chart);

const state = {
  algorithms: [],
  currentArray: [],
  steps: [],
  stepIndex: 0,
  playing: false,
  playTimer: null,
  sortResult: null,
};

function shuffleArray(size) {
  const values = Array.from({ length: size }, (_, index) => index + 1);
  for (let i = values.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [values[i], values[j]] = [values[j], values[i]];
  }
  return values;
}

function getSelectedAlgorithm() {
  return state.algorithms.find((algorithm) => algorithm.id === algorithmSelect.value);
}

function setStatus(message = "", isWarning = false) {
  statusMessage.textContent = message;
  statusMessage.style.color = isWarning ? "var(--warning)" : "var(--muted)";
}

function clearElement(element) {
  while (element.firstChild) {
    element.removeChild(element.firstChild);
  }
}

function updateAlgorithmMeta() {
  const algorithm = getSelectedAlgorithm();
  if (!algorithm) {
    return;
  }

  clearElement(algorithmDescription);

  const name = document.createElement("strong");
  name.textContent = algorithm.name;
  algorithmDescription.appendChild(name);
  algorithmDescription.appendChild(document.createElement("br"));

  const description = document.createElement("span");
  description.textContent = algorithm.description || "No description available.";
  algorithmDescription.appendChild(description);

  const complexity = [algorithm.time_complexity, algorithm.space_complexity]
    .filter(Boolean)
    .join(" · ");
  if (complexity) {
    algorithmDescription.appendChild(document.createElement("br"));
    const complexityNode = document.createElement("span");
    complexityNode.textContent = complexity;
    algorithmDescription.appendChild(complexityNode);
  }

  if (algorithm.reason) {
    algorithmDescription.appendChild(document.createElement("br"));
    const reason = document.createElement("em");
    reason.textContent = algorithm.reason;
    algorithmDescription.appendChild(reason);
  }
}

function updateStats() {
  const currentStep = state.stepIndex;
  stepCount.textContent = String(currentStep);
  stepTotal.textContent = String(state.steps.length);
  compareCount.textContent = String(state.sortResult?.stats?.comparisons ?? 0);
  swapCount.textContent = String(state.sortResult?.stats?.swaps ?? 0);
  vizTier.textContent = state.sortResult?.viz_tier ?? getSelectedAlgorithm()?.viz_tier ?? "-";
}

function renderCurrentStep() {
  if (!state.steps.length) {
    visualizer.render(state.currentArray);
    updateStats();
    return;
  }

  const step = state.steps[Math.min(state.stepIndex, state.steps.length - 1)];
  const highlights = highlightsFromStep(step);
  visualizer.render(step.array, highlights);
  updateStats();
}

function stopPlayback() {
  state.playing = false;
  if (state.playTimer) {
    clearTimeout(state.playTimer);
    state.playTimer = null;
  }
  playBtn.disabled = false;
  pauseBtn.disabled = true;
}

async function fetchAlgorithms() {
  const response = await fetch("/api/algorithms");
  if (!response.ok) {
    throw new Error("Failed to load algorithms");
  }
  state.algorithms = await response.json();
  algorithmSelect.replaceChildren();
  for (const algorithm of state.algorithms) {
    const option = document.createElement("option");
    option.value = algorithm.id;
    option.textContent = `${algorithm.name} (${algorithm.viz_tier})`;
    algorithmSelect.appendChild(option);
  }
  updateAlgorithmMeta();
}

async function runSort() {
  stopPlayback();
  setStatus("Running sort...");

  const algorithm = getSelectedAlgorithm();
  if (!algorithm) {
    setStatus("No algorithm selected.", true);
    return;
  }

  const payload = {
    algorithm: algorithm.id,
    array: state.currentArray,
    max_steps: 5000,
  };

  const response = await fetch("/api/sort", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    setStatus(data.detail || "Sort request failed.", true);
    return;
  }

  state.sortResult = data;
  state.steps = data.steps || [];
  state.stepIndex = 0;
  state.currentArray = data.initial;

  const warnings = [...(data.warnings || []), ...(data.messages || [])];
  setStatus(warnings.join(" · "), warnings.length > 0);

  renderCurrentStep();
}

function resetVisualization() {
  stopPlayback();
  state.steps = [];
  state.stepIndex = 0;
  state.sortResult = null;
  setStatus("");
  visualizer.render(state.currentArray);
  updateStats();
}

function play() {
  if (!state.steps.length) {
    runSort().then(() => {
      if (state.steps.length) {
        play();
      }
    });
    return;
  }

  state.playing = true;
  playBtn.disabled = true;
  pauseBtn.disabled = false;

  const tick = () => {
    if (!state.playing) {
      return;
    }

    if (state.stepIndex >= state.steps.length - 1) {
      stopPlayback();
      return;
    }

    state.stepIndex += 1;
    renderCurrentStep();
    state.playTimer = setTimeout(tick, Number(speedInput.value));
  };

  state.playTimer = setTimeout(tick, Number(speedInput.value));
}

function stepForward() {
  if (!state.steps.length) {
    runSort();
    return;
  }
  if (state.stepIndex < state.steps.length - 1) {
    state.stepIndex += 1;
    renderCurrentStep();
  }
}

function shuffle() {
  stopPlayback();
  state.currentArray = shuffleArray(Number(arraySizeInput.value));
  resetVisualization();
}

arraySizeInput.addEventListener("input", () => {
  arraySizeValue.textContent = arraySizeInput.value;
});

speedInput.addEventListener("input", () => {
  speedValue.textContent = speedInput.value;
});

algorithmSelect.addEventListener("change", () => {
  updateAlgorithmMeta();
  resetVisualization();
});

shuffleBtn.addEventListener("click", shuffle);
playBtn.addEventListener("click", play);
pauseBtn.addEventListener("click", stopPlayback);
stepBtn.addEventListener("click", stepForward);
resetBtn.addEventListener("click", resetVisualization);

async function init() {
  try {
    await fetchAlgorithms();
    shuffle();
  } catch (error) {
    setStatus(error.message, true);
  }
}

init();
