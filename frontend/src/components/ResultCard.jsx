import { FiCheckCircle, FiCopy } from "react-icons/fi";
import MathFormula from "./MathFormula";

export default function ResultCard({ result, resultLatex, error }) {
  function handleCopy() {
    if (!result || error) return;
    navigator.clipboard.writeText(result);
  }

  return (
    <section className={`panel-card result-card ${error ? "error" : "success"}`}>
      <div className="result-head">
        <div className="result-title-row">
          {!error && <FiCheckCircle className="result-status-icon" />}
          <h3 className="card-title">{error ? "Ошибка" : "Результат:"}</h3>
        </div>

        {!error && result && (
          <button className="copy-btn" onClick={handleCopy}>
            <FiCopy />
            <span>Копировать</span>
          </button>
        )}
      </div>

      {error ? (
        <div className="result-text error-text">{error}</div>
      ) : resultLatex ? (
        <MathFormula latex={resultLatex} />
      ) : result ? (
        <div className="result-text success-text">{result}</div>
      ) : (
        <div className="result-text muted">Здесь появится результат</div>
      )}
    </section>
  );
}