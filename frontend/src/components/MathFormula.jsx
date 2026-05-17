import { BlockMath } from "react-katex";

const LATEX_COMMANDS = [
  "begin",
  "end",
  "frac",
  "left",
  "right",
  "cdot",
  "Delta",
  "delta",
  "Longleftrightarrow",
  "Leftrightarrow",
  "Longrightarrow",
  "Rightarrow",
  "sqrt",
  "pm",
  "le",
  "ge",
  "neq",
  "infty",
  "sum",
  "prod",
  "times",
  "cdots",
  "ldots",
  "log",
  "ln",
  "quad",
  "qquad",
  "text",
  "mathbb",
].join("|");

const ESCAPED_COMMAND = new RegExp(String.raw`\\{2,}(${LATEX_COMMANDS})`, "g");
const ESCAPED_SPACE = /\\{2,}\s/g;

export function normalizeLatex(latex) {
  let normalized = String(latex);

  for (let index = 0; index < 4; index += 1) {
    const next = normalized
      .replace(ESCAPED_COMMAND, "\\$1")
      .replace(ESCAPED_SPACE, "\\ ");

    if (next === normalized) break;
    normalized = next;
  }

  return normalized;
}

export default function MathFormula({ latex }) {
  if (!latex) return null;
  const normalizedLatex = normalizeLatex(latex);

  return (
    <div className="math-formula">
      <BlockMath math={normalizedLatex} throwOnError={false} />
    </div>
  );
}
