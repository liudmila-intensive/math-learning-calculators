import { useState } from "react";
import Breadcrumbs from "../components/Breadcrumbs";
import CalculatorForm from "../components/CalculatorForm";
import ResultCard from "../components/ResultCard";
import StepsCard from "../components/StepsCard";
import RightPanel from "../components/RightPanel";
import { downloadSimplifyDocx, simplifyExpression } from "../services/api";
import MathFormula from "../components/MathFormula";

export default function SimplifyPage() {
  const [expression, setExpression] = useState("2x + 3x - x");
  const [result, setResult] = useState("");
  const [resultLatex, setResultLatex] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [steps, setSteps] = useState([]);
  const [downloading, setDownloading] = useState(false);
  const [showSubstitution, setShowSubstitution] = useState(false);
  const [substituteVariable, setSubstituteVariable] = useState("x");
  const [substituteValue, setSubstituteValue] = useState("");
  const [substitution, setSubstitution] = useState(null);

  const [history, setHistory] = useState([
    { expression: "2x + 3x - x", result: "4x" },
    { expression: "2(x + 3)", result: "2x + 6" },
    { expression: "x^2 - 9", result: "(x - 3)(x + 3)" },
  ]);

  async function handleSimplify() {
    setLoading(true);
    setError("");

    if (!expression.trim()) {
      setError("Введите выражение.");
      setResult("");
      setResultLatex("");
      setSteps([]);
      setSubstitution(null);
      setLoading(false);
      return;
    }

    try {
      const payload = {
        expression,
        substitute_variable: showSubstitution ? substituteVariable : null,
        substitute_value: showSubstitution ? substituteValue : null,
      };
      const data = await simplifyExpression(payload);

      setResult(data.result);
      setResultLatex(data.result_latex || "");
      setSteps(data.steps || []);
      setSubstitution(data.substitution || null);

      setHistory((prev) => [
        { expression, result: data.result },
        ...prev.slice(0, 4),
      ]);
    } catch (err) {
      const message =
        err?.response?.data?.detail || "Не удалось обработать выражение.";
      setError(message);
      setResult("");
      setResultLatex("");
      setSteps([]);
      setSubstitution(null);
    } finally {
      setLoading(false);
    }
  }

  function handleClear() {
    setExpression("");
    setResult("");
    setResultLatex("");
    setError("");
    setSteps([]);
    setSubstitution(null);
  }

  function handleClearHistory() {
    setHistory([]);
  }

  async function handleDownloadDocx() {
    setDownloading(true);
    try {
      await downloadSimplifyDocx({
        expression,
        substitute_variable: showSubstitution ? substituteVariable : null,
        substitute_value: showSubstitution ? substituteValue : null,
      });
    } finally {
      setDownloading(false);
    }
  }

  return (
    <>
      <Breadcrumbs />

      <div className="workspace-grid">
        <div className="workspace-main">
          <CalculatorForm
            expression={expression}
            setExpression={setExpression}
            onSimplify={handleSimplify}
            onClear={handleClear}
            loading={loading}
          />

          <section className="panel-card substitution-card">
            <div className="substitution-head">
              <div>
                <h3 className="card-title">Подстановка значения</h3>
                <p className="page-subtitle">
                  Включите, если в задании нужно найти значение выражения при заданной переменной.
                </p>
              </div>
              <button
                className="secondary-btn"
                onClick={() => setShowSubstitution((value) => !value)}
              >
                {showSubstitution ? "Убрать подстановку" : "Добавить подстановку"}
              </button>
            </div>

            {showSubstitution && (
              <div className="substitution-grid">
                <div>
                  <label>Переменная</label>
                  <input
                    value={substituteVariable}
                    onChange={(event) => setSubstituteVariable(event.target.value)}
                    placeholder="a"
                  />
                </div>
                <div>
                  <label>Значение</label>
                  <input
                    value={substituteValue}
                    onChange={(event) => setSubstituteValue(event.target.value)}
                    placeholder="-1/2"
                  />
                </div>
              </div>
            )}
          </section>

          <ResultCard result={result} resultLatex={resultLatex} error={error} />
          {substitution && (
            <section className="panel-card substitution-result-card">
              <h3 className="card-title">Значение при подстановке</h3>
              <MathFormula latex={substitution.chain_latex} />
            </section>
          )}
          {result && (
            <button
              className="secondary-btn download-docx-btn"
              onClick={handleDownloadDocx}
              disabled={downloading}
            >
              {downloading ? "Формируем файл..." : "Скачать Word"}
            </button>
          )}
          <StepsCard steps={steps} />
        </div>

        <RightPanel history={history} onClearHistory={handleClearHistory} />
      </div>

      <div className="bottom-note-row">
        <div className="bottom-tip">
          💡 <strong>Совет:</strong> Для умножения используйте скобки:
          <span className="bottom-formula"> 2(x + 3) → 2x + 6</span>
        </div>

        <div className="bottom-history-note">
          Все вычисления сохраняются в истории
        </div>
      </div>
    </>
  );
}
