const COLORS = {
  default: "bar",
  compare: "bar compare",
  swap: "bar swap",
  set: "bar set",
  mark: "bar mark",
  access: "bar access",
};

export class Visualizer {
  constructor(container, { showLabels = false } = {}) {
    this.container = container;
    this.bars = [];
    this.maxValue = 1;
    this.showLabels = showLabels;
  }

  render(array, highlights = {}, { labels = null } = {}) {
    const values = Array.isArray(array) ? array : [];
    const { compare = [], swap = [], set = [], mark = [], access = [] } = highlights;
    this.maxValue = Math.max(...values.map((value) => Number(value) || 0), 1);

    if (this.bars.length !== values.length) {
      this.container.replaceChildren();
      this.bars = values.map((value, index) => {
        const bar = document.createElement("div");
        bar.className = COLORS.default;
        bar.title = String(value);
        if (this.showLabels || labels) {
          const label = document.createElement("span");
          label.className = "bar-label";
          label.textContent = labels ? String(labels[index] ?? index) : String(value);
          bar.appendChild(label);
        }
        this.container.appendChild(bar);
        return bar;
      });
    }

    values.forEach((value, index) => {
      const bar = this.bars[index];
      const height = Math.max((Number(value) / this.maxValue) * 100, values.length ? 4 : 0);
      bar.style.height = `${height}%`;
      bar.title = String(value);
      const labelNode = bar.querySelector(".bar-label");
      if (labelNode) {
        labelNode.textContent = labels ? String(labels[index] ?? index) : String(value);
      }

      let className = COLORS.default;
      if (swap.includes(index)) {
        className = COLORS.swap;
      } else if (set.includes(index)) {
        className = COLORS.set;
      } else if (compare.includes(index)) {
        className = COLORS.compare;
      } else if (mark.includes(index)) {
        className = COLORS.mark;
      } else if (access.includes(index)) {
        className = COLORS.access;
      }
      bar.className = className;
    });
  }
}

export function highlightsFromStep(step) {
  const indices = step.indices || [];
  switch (step.type) {
    case "compare":
      return { compare: indices };
    case "swap":
      return { swap: indices };
    case "set":
      return { set: indices };
    case "access":
      return { access: indices };
    case "mark":
      return { mark: indices };
    default:
      return {};
  }
}

function emptyHighlights() {
  return { compare: [], swap: [], set: [], mark: [], access: [] };
}

export class StageController {
  constructor(stage) {
    this.stage = stage;
    this.state = {
      main: { kind: "array", label: "Main", values: [] },
    };
    this.panels = new Map();
    this.ensureMainPanel();
  }

  ensureMainPanel() {
    let panel = this.stage.querySelector('[data-structure="main"]');
    if (!panel) {
      panel = document.createElement("div");
      panel.className = "viz-panel viz-panel-main";
      panel.dataset.structure = "main";
      panel.innerHTML = `
        <div class="viz-panel-header">
          <h3>Main</h3>
          <span class="viz-panel-meta"></span>
        </div>
        <div class="chart" aria-label="Main array"></div>
      `;
      this.stage.appendChild(panel);
    }
    const chart = panel.querySelector(".chart");
    this.panels.set("main", {
      panel,
      chart,
      visualizer: new Visualizer(chart),
      meta: panel.querySelector(".viz-panel-meta"),
      title: panel.querySelector("h3"),
    });
  }

  reset(array = []) {
    this.state = {
      main: { kind: "array", label: "Main", values: [...array] },
    };
    for (const [id, entry] of [...this.panels.entries()]) {
      if (id !== "main") {
        entry.panel.remove();
        this.panels.delete(id);
      }
    }
    this.stage.dataset.layout = "main-only";
    this.renderAll(null);
  }

  applyStepStructures(step) {
    const structures = step?.structures;
    if (!structures) {
      return;
    }
    for (const [id, payload] of Object.entries(structures)) {
      this.state[id] = {
        kind: payload.kind || "array",
        label: payload.label || id,
        values: payload.values,
      };
    }
  }

  ensurePanel(id, info) {
    if (this.panels.has(id)) {
      const entry = this.panels.get(id);
      entry.title.textContent = info.label || id;
      entry.panel.dataset.kind = info.kind || "array";
      return entry;
    }

    if (info.kind === "buckets") {
      const panel = document.createElement("div");
      panel.className = "viz-panel viz-panel-buckets";
      panel.dataset.structure = id;
      panel.dataset.kind = "buckets";
      panel.innerHTML = `
        <div class="viz-panel-header">
          <h3></h3>
          <span class="viz-panel-meta"></span>
        </div>
        <div class="buckets-grid"></div>
      `;
      panel.querySelector("h3").textContent = info.label || id;
      this.stage.appendChild(panel);
      const entry = {
        panel,
        grid: panel.querySelector(".buckets-grid"),
        meta: panel.querySelector(".viz-panel-meta"),
        title: panel.querySelector("h3"),
        bucketVisualizers: [],
      };
      this.panels.set(id, entry);
      return entry;
    }

    const panel = document.createElement("div");
    panel.className = "viz-panel";
    panel.dataset.structure = id;
    panel.dataset.kind = info.kind || "array";
    panel.innerHTML = `
      <div class="viz-panel-header">
        <h3></h3>
        <span class="viz-panel-meta"></span>
      </div>
      <div class="chart chart-aux" aria-label="${info.label || id}"></div>
    `;
    panel.querySelector("h3").textContent = info.label || id;
    this.stage.appendChild(panel);
    const chart = panel.querySelector(".chart");
    const entry = {
      panel,
      chart,
      visualizer: new Visualizer(chart, { showLabels: info.kind === "histogram" }),
      meta: panel.querySelector(".viz-panel-meta"),
      title: panel.querySelector("h3"),
    };
    this.panels.set(id, entry);
    return entry;
  }

  updateLayout() {
    const auxIds = Object.keys(this.state).filter((id) => id !== "main");
    const kinds = new Set(auxIds.map((id) => this.state[id]?.kind));
    if (kinds.has("buckets")) {
      this.stage.dataset.layout = "buckets";
    } else if (kinds.has("histogram")) {
      this.stage.dataset.layout = "histogram";
    } else if (
      auxIds.includes("left") ||
      auxIds.includes("right") ||
      auxIds.includes("mid") ||
      auxIds.includes("dest")
    ) {
      this.stage.dataset.layout = "merge";
    } else if (auxIds.length) {
      this.stage.dataset.layout = "aux";
    } else {
      this.stage.dataset.layout = "main-only";
    }

    for (const [id, entry] of [...this.panels.entries()]) {
      if (id !== "main" && !this.state[id]) {
        entry.panel.remove();
        this.panels.delete(id);
      }
    }
  }

  renderBuckets(id, info, step) {
    const entry = this.ensurePanel(id, info);
    const buckets = Array.isArray(info.values) ? info.values : [];
    const activeBucket = step?.structure === id ? step.bucket_index : null;
    const highlights =
      step?.structure === id && activeBucket != null ? highlightsFromStep(step) : emptyHighlights();

    if (entry.bucketVisualizers.length !== buckets.length) {
      entry.grid.replaceChildren();
      entry.bucketVisualizers = buckets.map((_, index) => {
        const cell = document.createElement("div");
        cell.className = "bucket-cell";
        cell.innerHTML = `<div class="bucket-label">B${index}</div><div class="chart chart-bucket"></div>`;
        entry.grid.appendChild(cell);
        return {
          cell,
          visualizer: new Visualizer(cell.querySelector(".chart")),
        };
      });
    }

    buckets.forEach((bucket, index) => {
      const bucketEntry = entry.bucketVisualizers[index];
      bucketEntry.cell.classList.toggle("active", activeBucket === index);
      const localHighlights = activeBucket === index ? highlights : emptyHighlights();
      bucketEntry.visualizer.render(bucket || [], localHighlights);
    });
  }

  renderAll(step) {
    this.updateLayout();
    const activeId = step?.structure || "main";

    for (const [id, info] of Object.entries(this.state)) {
      if (info.kind === "buckets") {
        this.renderBuckets(id, info, step);
        continue;
      }

      const entry = this.ensurePanel(id, info);
      entry.title.textContent = info.label || id;
      entry.panel.classList.toggle("active-structure", id === activeId);
      const highlights = id === activeId && step ? highlightsFromStep(step) : emptyHighlights();
      const labels =
        info.kind === "histogram" ? (info.values || []).map((_, index) => index) : null;
      entry.visualizer.render(info.values || [], highlights, { labels });
      if (step?.label && id === activeId) {
        entry.meta.textContent = step.label;
      } else {
        entry.meta.textContent = info.kind === "histogram" ? "histogram" : "";
      }
    }

    const mainEntry = this.panels.get("main");
    if (mainEntry && step?.type === "mark" && step.structure === "main" && step.label) {
      mainEntry.meta.textContent = step.label;
    }
  }

  renderStep(step, fallbackArray = []) {
    if (!this.state.main.values.length && fallbackArray.length) {
      this.state.main.values = [...fallbackArray];
    }
    if (step?.array && (!step.structure || step.structure === "main")) {
      this.state.main.values = [...step.array];
    } else if (step?.array && this.state.main) {
      // Keep main in sync when aux steps still embed the main snapshot.
      this.state.main.values = [...step.array];
    }
    this.applyStepStructures(step);
    this.renderAll(step);
  }
}
