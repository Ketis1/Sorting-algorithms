import { StageController } from "./visualizer.js";

const algorithmSelect = document.getElementById("algorithm-select");
const arraySizeInput = document.getElementById("array-size");
const arraySizeValue = document.getElementById("array-size-value");
const speedInput = document.getElementById("speed");
const speedValue = document.getElementById("speed-value");
const arrayModeSelect = document.getElementById("array-mode");
const arrayMinInput = document.getElementById("array-min");
const arrayMaxInput = document.getElementById("array-max");
const arrayDuplicatesInput = document.getElementById("array-duplicates");
const shuffleBtn = document.getElementById("shuffle-btn");
const playBtn = document.getElementById("play-btn");
const pauseBtn = document.getElementById("pause-btn");
const stepBtn = document.getElementById("step-btn");
const resetBtn = document.getElementById("reset-btn");
const algorithmDescription = document.getElementById("algorithm-description");
const algorithmExplanation = document.getElementById("algorithm-explanation");
const algorithmSource = document.getElementById("algorithm-source");
const copyCodeBtn = document.getElementById("copy-code-btn");
const stepCount = document.getElementById("step-count");
const stepTotal = document.getElementById("step-total");
const compareCount = document.getElementById("compare-count");
const swapCount = document.getElementById("swap-count");
const vizTier = document.getElementById("viz-tier");
const statusMessage = document.getElementById("status-message");
const stage = document.getElementById("viz-stage");

const visualizer = new StageController(stage);

const MAX_HISTOGRAM_RANGE = 200;
const HISTOGRAM_ALGORITHMS = new Set(["counting_sort", "pigeonhole_sort"]);

const ARRAY_PRESETS = {
  counting_sort: { mode: "range", min: 1, max: 9, duplicates: true },
  pigeonhole_sort: { mode: "range", min: 1, max: 9, duplicates: true },
  radix_sort: { mode: "range", min: 10, max: 99, duplicates: true },
  bucket_sort: { mode: "range", min: 1, max: 20, duplicates: true },
  default: { mode: "unique", min: 1, max: 30, duplicates: false },
};

const state = {
  algorithms: [],
  currentArray: [],
  steps: [],
  stepIndex: 0,
  playing: false,
  playTimer: null,
  sortResult: null,
};

function fisherYates(values) {
  for (let i = values.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [values[i], values[j]] = [values[j], values[i]];
  }
  return values;
}

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function getArrayGenerationOptions() {
  return {
    mode: arrayModeSelect.value,
    size: Number(arraySizeInput.value),
    min: Number(arrayMinInput.value),
    max: Number(arrayMaxInput.value),
    duplicates: arrayDuplicatesInput.checked,
  };
}

function syncArrayControlsUi() {
  const isRange = arrayModeSelect.value === "range";
  document.querySelectorAll(".array-range-controls").forEach((element) => {
    element.hidden = !isRange;
  });
  arrayMinInput.disabled = !isRange;
  arrayMaxInput.disabled = !isRange;
  arrayDuplicatesInput.disabled = !isRange;
}

function applyAlgorithmArrayPreset(algorithmId, { reshuffle = true } = {}) {
  const preset = ARRAY_PRESETS[algorithmId] || ARRAY_PRESETS.default;
  arrayModeSelect.value = preset.mode;
  arrayMinInput.value = String(preset.min);
  arrayMaxInput.value = String(preset.max);
  arrayDuplicatesInput.checked = preset.duplicates;
  syncArrayControlsUi();
  if (reshuffle) {
    shuffle();
  }
}

function buildArray({ mode, size, min, max, duplicates }) {
  if (mode === "unique") {
    return fisherYates(Array.from({ length: size }, (_, index) => index + 1));
  }

  if (!Number.isInteger(min) || !Number.isInteger(max)) {
    throw new Error("Min and max must be integers.");
  }
  if (min > max) {
    throw new Error("Min value cannot be greater than max value.");
  }

  const span = max - min + 1;
  if (!duplicates && span < size) {
    throw new Error(
      `Need at least ${size} distinct values in [${min}, ${max}] (only ${span} available).`,
    );
  }

  if (duplicates) {
    return Array.from({ length: size }, () => randomInt(min, max));
  }

  const pool = Array.from({ length: span }, (_, index) => min + index);
  return fisherYates(pool).slice(0, size);
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

  algorithmExplanation.textContent =
    algorithm.explanation || algorithm.description || "No detailed explanation available.";

  const codeNode = algorithmSource.querySelector("code") || algorithmSource;
  codeNode.textContent = algorithm.source || "# Source unavailable";
  copyCodeBtn.textContent = "Copy";
}

async function copyAlgorithmSource() {
  const algorithm = getSelectedAlgorithm();
  const source = algorithm?.source;
  if (!source) {
    setStatus("No source available to copy.", true);
    return;
  }

  try {
    await navigator.clipboard.writeText(source);
    copyCodeBtn.textContent = "Copied";
    setTimeout(() => {
      copyCodeBtn.textContent = "Copy";
    }, 1500);
  } catch (error) {
    setStatus("Could not copy to clipboard.", true);
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

function isVisualStep(step) {
  return step && step.type !== "access";
}

function nextVisualStepIndex(fromIndex) {
  for (let index = fromIndex + 1; index < state.steps.length; index += 1) {
    if (isVisualStep(state.steps[index])) {
      return index;
    }
  }
  return state.steps.length - 1;
}

function showStep() {
  if (!state.steps.length) {
    visualizer.reset(state.currentArray);
    updateStats();
    return;
  }

  const step = state.steps[Math.min(state.stepIndex, state.steps.length - 1)];
  visualizer.renderStep(step, state.sortResult?.initial ?? state.currentArray);

  if (step?.type === "mark" && step.label) {
    setStatus(step.label);
  }

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
  playBtn.disabled = true;

  const algorithm = getSelectedAlgorithm();
  if (!algorithm) {
    playBtn.disabled = false;
    setStatus("No algorithm selected.", true);
    return;
  }

  const payload = {
    algorithm: algorithm.id,
    array: state.currentArray,
    max_steps: 5000,
  };

  try {
    const response = await fetch("/api/sort", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      const detail = Array.isArray(data.detail)
        ? data.detail.map((item) => item.msg).join(", ")
        : data.detail;
      setStatus(detail || "Sort request failed.", true);
      return;
    }

    state.sortResult = data;
    state.steps = data.steps || [];
    state.stepIndex = 0;
    state.currentArray = data.initial;

    const warnings = [...(data.warnings || []), ...(data.messages || [])];
    setStatus(warnings.join(" · "), warnings.length > 0);

    visualizer.reset(data.initial);
    state.stepIndex = 0;
    // Fast-forward structure snapshots without painting until the first visual step.
    for (let index = 0; index <= 0 && index < state.steps.length; index += 1) {
      const step = state.steps[index];
      if (step.array) {
        visualizer.state.main.values = [...step.array];
      }
      visualizer.applyStepStructures(step);
    }
    showStep();
  } finally {
    playBtn.disabled = false;
  }
}

function resetVisualization() {
  stopPlayback();
  state.steps = [];
  state.stepIndex = 0;
  state.sortResult = null;
  setStatus("");
  visualizer.reset(state.currentArray);
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

    const previousIndex = state.stepIndex;
    state.stepIndex = nextVisualStepIndex(state.stepIndex);
    // Apply skipped non-visual steps' snapshots too.
    for (let index = previousIndex + 1; index <= state.stepIndex; index += 1) {
      const step = state.steps[index];
      if (step.array) {
        visualizer.state.main.values = [...step.array];
      }
      visualizer.applyStepStructures(step);
    }
    visualizer.renderAll(state.steps[state.stepIndex]);
    const step = state.steps[state.stepIndex];
    if (step?.type === "mark" && step.label) {
      setStatus(step.label);
    }
    updateStats();
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
    const previousIndex = state.stepIndex;
    state.stepIndex = nextVisualStepIndex(state.stepIndex);
    for (let index = previousIndex + 1; index <= state.stepIndex; index += 1) {
      const step = state.steps[index];
      if (step.array) {
        visualizer.state.main.values = [...step.array];
      }
      visualizer.applyStepStructures(step);
    }
    visualizer.renderAll(state.steps[state.stepIndex]);
    const step = state.steps[state.stepIndex];
    if (step?.type === "mark" && step.label) {
      setStatus(step.label);
    }
    updateStats();
  }
}

function shuffle() {
  stopPlayback();
  try {
    const options = getArrayGenerationOptions();
    const algorithm = getSelectedAlgorithm();
    if (
      algorithm &&
      HISTOGRAM_ALGORITHMS.has(algorithm.id) &&
      options.mode === "range"
    ) {
      const span = options.max - options.min + 1;
      if (span > MAX_HISTOGRAM_RANGE) {
        throw new Error(
          `Value range ${span} exceeds visualization limit of ${MAX_HISTOGRAM_RANGE} for ${algorithm.name}.`,
        );
      }
    }

    state.currentArray = buildArray(options);
    resetVisualization();
    if (options.mode === "unique") {
      setStatus(`Generated unique values 1…${options.size}`);
    } else {
      const dup = options.duplicates ? "with duplicates" : "unique in range";
      setStatus(`Generated ${options.size} values in [${options.min}, ${options.max}] (${dup})`);
    }
  } catch (error) {
    setStatus(error.message, true);
  }
}

arraySizeInput.addEventListener("input", () => {
  arraySizeValue.textContent = arraySizeInput.value;
  shuffle();
});

speedInput.addEventListener("input", () => {
  speedValue.textContent = speedInput.value;
});

arrayModeSelect.addEventListener("change", () => {
  syncArrayControlsUi();
  shuffle();
});

arrayMinInput.addEventListener("change", shuffle);
arrayMaxInput.addEventListener("change", shuffle);
arrayDuplicatesInput.addEventListener("change", shuffle);

algorithmSelect.addEventListener("change", () => {
  updateAlgorithmMeta();
  applyAlgorithmArrayPreset(algorithmSelect.value, { reshuffle: true });
});

shuffleBtn.addEventListener("click", shuffle);
playBtn.addEventListener("click", play);
pauseBtn.addEventListener("click", stopPlayback);
stepBtn.addEventListener("click", stepForward);
resetBtn.addEventListener("click", resetVisualization);
copyCodeBtn.addEventListener("click", copyAlgorithmSource);

async function init() {
  try {
    await fetchAlgorithms();
    syncArrayControlsUi();
    applyAlgorithmArrayPreset(algorithmSelect.value, { reshuffle: true });
  } catch (error) {
    setStatus(error.message, true);
  }
}

init();
