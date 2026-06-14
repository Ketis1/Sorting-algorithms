const COLORS = {
  default: "bar",
  compare: "bar compare",
  swap: "bar swap",
  mark: "bar mark",
  access: "bar access",
};

export class Visualizer {
  constructor(container) {
    this.container = container;
    this.bars = [];
    this.maxValue = 1;
  }

  render(array, highlights = {}) {
    const { compare = [], swap = [], mark = [], access = [] } = highlights;
    this.maxValue = Math.max(...array, 1);

    if (this.bars.length !== array.length) {
      this.container.innerHTML = "";
      this.bars = array.map((value) => {
        const bar = document.createElement("div");
        bar.className = COLORS.default;
        bar.title = String(value);
        this.container.appendChild(bar);
        return bar;
      });
    }

    array.forEach((value, index) => {
      const bar = this.bars[index];
      const height = Math.max((value / this.maxValue) * 100, 4);
      bar.style.height = `${height}%`;
      bar.title = String(value);

      let className = COLORS.default;
      if (swap.includes(index)) {
        className = COLORS.swap;
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
      return { swap: indices };
    case "access":
      return { access: indices };
    case "mark":
      return { mark: indices };
    default:
      return {};
  }
}
