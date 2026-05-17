import MathFormula from "./MathFormula";

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
                  <MathFormula latex={step.latex} />
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
