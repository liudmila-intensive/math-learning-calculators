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
  "colon",
  "log",
  "ln",
  "quad",
  "qquad",
  "text",
  "mathbb",
].join("|");

const ESCAPED_COMMAND = new RegExp(String.raw`\\{2,}(${LATEX_COMMANDS})`, "g");
const ESCAPED_ROW_BREAK = /\\{4,}/g;

function repairCompactFraction(match, token) {
  const value = String(token);

  if (value.includes("}")) {
    return match;
  }

  const literalMatch = value.match(/^(-?\d*[a-zA-Z]+)(-?\d+)$/);
  if (literalMatch) {
    return `\\frac{${literalMatch[1]}}{${literalMatch[2]}}`;
  }

  if (/^-?\d+$/.test(value)) {
    const sign = value.startsWith("-") ? "-" : "";
    const digits = value.replace("-", "");

    if (digits.length <= 1) {
      return match;
    }

    const denominatorLength = digits.length >= 4 ? 2 : 1;
    const numerator = `${sign}${digits.slice(0, -denominatorLength)}`;
    const denominator = digits.slice(-denominatorLength);

    if (!numerator || Number(denominator) === 0) {
      return match;
    }

    return `\\frac{${numerator}}{${denominator}}`;
  }

  return match;
}

function repairLatex(latex) {
  return latex
    .replace(/\\begincases/g, "\\begin{cases}")
    .replace(/\\endcases/g, "\\end{cases}")
    .replace(/\\beginmatrix/g, "\\begin{matrix}")
    .replace(/\\endmatrix/g, "\\end{matrix}")
    .replace(/\\frac(?!\{)(-?\d*[a-zA-Z]+-?\d+|-?\d+)/g, repairCompactFraction)
    .replace(/(^|[^\w\\])(-?\d+)dot(?=\()/g, "$1$2\\cdot");
}

export function normalizeLatex(latex) {
  let normalized = String(latex);

  for (let index = 0; index < 4; index += 1) {
    const next = normalized
      .replace(ESCAPED_COMMAND, "\\$1")
      .replace(ESCAPED_ROW_BREAK, "\\\\");

    if (next === normalized) break;
    normalized = next;
  }

  return repairLatex(normalized);
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
