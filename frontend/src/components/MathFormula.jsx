import { BlockMath } from "react-katex";

export default function MathFormula({ latex }) {
  if (!latex) return null;

  return (
    <div className="math-formula">
      <BlockMath math={latex} />
    </div>
  );
}