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
].join("|");

const DOUBLE_ESCAPED_COMMAND = new RegExp(`\\\\\\\\(${LATEX_COMMANDS})`, "g");

function normalizeLatex(latex) {
  return String(latex)
    .replace(DOUBLE_ESCAPED_COMMAND, "\\$1")
    .replace(/\\\\ /g, "\\ ");
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
