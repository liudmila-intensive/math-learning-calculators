import MathFormula, { normalizeLatex } from "./MathFormula";

function ChainMathFormula({ latex }) {
  const parts = normalizeLatex(latex)
    .split(/\s*\\Longleftrightarrow\s*/g)
    .map((part) => part.trim())
    .filter(Boolean);

  if (parts.length <= 1) {
    return <MathFormula latex={latex} />;
  }

  return (
    <div className="chain-formula">
      {parts.map((part, index) => (
        <div
          className={index === 0 ? "chain-formula-line first" : "chain-formula-line"}
          key={`${part}-${index}`}
        >
          {index > 0 && <span className="chain-sign">⇔</span>}
          <MathFormula latex={part} />
        </div>
      ))}
    </div>
  );
}

export default function StepsCard({ steps }) {
  return (
    <section className="panel-card steps-card">
      <h3 className="card-title">Пошаговое решение:</h3>

      {steps.length === 0 ? (
        <p className="muted">После вычисления здесь появятся шаги решения.</p>
      ) : (
        <div className="steps-list">
          {steps.map((step, index) => {
            if (step.is_section) {
              return (
                <div className="step-section-title" key={index}>
                  {step.expression}
                </div>
              );
            }

            const isChain = step.is_chain || (steps.length === 1 && step.latex?.includes(" = "));

            return (
            <div
              className={isChain ? "step-chain-row" : "step-row"}
              key={index}
            >
              {!isChain && <div className="step-number">{index + 1}</div>}

              <div className="step-content">
                {step.latex ? (
                  isChain ? (
                    <ChainMathFormula latex={step.latex} />
                  ) : (
                    <MathFormula latex={step.latex} />
                  )
                ) : (
                  <div className="step-expression">{step.expression}</div>
                )}
              </div>

              {step.explanation && (
                <div className="step-explanation">{step.explanation}</div>
              )}
            </div>
          );
          })}
        </div>
      )}
    </section>
  );
}
