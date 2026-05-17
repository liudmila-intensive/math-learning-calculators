import { useEffect, useMemo, useState } from "react";
import Breadcrumbs from "../components/Breadcrumbs";
import { downloadSimplexAlgebraicDocx, solveSimplexAlgebraic } from "../services/api";
import { toSubscript } from "../utils/mathFormat";

function formatSolution(solution) {
  return Object.entries(solution || {}).map(([name, value]) => (
    <span key={name} className="solution-item">
      <strong>{toSubscript(name)}</strong> = {value}
    </span>
  ));
}

export default function SimplexAlgebraicPage() {
  const [numVariables, setNumVariables] = useState(2);
  const [numConstraints, setNumConstraints] = useState(4);
  const [objectiveType, setObjectiveType] = useState("max");
  const [objective, setObjective] = useState([]);
  const [coeffs, setCoeffs] = useState([]);
  const [relations, setRelations] = useState([]);
  const [rhs, setRhs] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setObjective((prev) =>
      Array.from({ length: numVariables }, (_, i) => prev[i] ?? "")
    );
    setCoeffs((prev) =>
      Array.from({ length: numConstraints }, (_, r) =>
        Array.from({ length: numVariables }, (_, c) => prev[r]?.[c] ?? "")
      )
    );
    setRelations((prev) =>
      Array.from({ length: numConstraints }, (_, i) => prev[i] ?? "<=")
    );
    setRhs((prev) =>
      Array.from({ length: numConstraints }, (_, i) => prev[i] ?? "")
    );
  }, [numVariables, numConstraints]);

  const variableLabels = useMemo(
    () => Array.from({ length: numVariables }, (_, i) => `x_${i + 1}`),
    [numVariables]
  );

  function updateCoeff(row, col, value) {
    setCoeffs((prev) => {
      const next = prev.map((items) => [...items]);
      while (next.length <= row) next.push([]);
      while (next[row].length <= col) next[row].push("");
      next[row][col] = value;
      return next;
    });
  }

  function updateObjective(col, value) {
    setObjective((prev) => {
      const next = [...prev];
      while (next.length <= col) next.push("");
      next[col] = value;
      return next;
    });
  }

  function updateRelation(row, value) {
    setRelations((prev) => {
      const next = [...prev];
      while (next.length <= row) next.push("<=");
      next[row] = value;
      return next;
    });
  }

  function updateRhs(row, value) {
    setRhs((prev) => {
      const next = [...prev];
      while (next.length <= row) next.push("");
      next[row] = value;
      return next;
    });
  }

  function fillDemo() {
    setNumVariables(2);
    setNumConstraints(4);
    setObjectiveType("max");
    setObjective(["1", "2"]);
    setCoeffs([
      ["-1", "2"],
      ["1", "1"],
      ["1", "-1"],
      ["0", "1"],
    ]);
    setRelations([">=", ">=", "<=", "<="]);
    setRhs(["2", "4", "2", "6"]);
    setResult(null);
    setError("");
  }

  function buildPayload() {
    return {
        num_variables: numVariables,
        num_constraints: numConstraints,
        objective_type: objectiveType,
        objective: objective.map((value) => Number(value || 0)),
        constraints: coeffs.map((row, i) => ({
          coefficients: row.map((value) => Number(value || 0)),
          relation: relations[i],
          rhs: Number(rhs[i] || 0),
        })),
      };
  }

  async function handleSolve() {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const payload = buildPayload();
      setResult(await solveSimplexAlgebraic(payload));
    } catch (err) {
      setError(err?.response?.data?.detail || "Ошибка решения задачи");
    } finally {
      setLoading(false);
    }
  }

  async function handleDownloadDocx() {
    setDownloading(true);
    try {
      await downloadSimplexAlgebraicDocx(buildPayload());
    } finally {
      setDownloading(false);
    }
  }

  return (
    <>
      <Breadcrumbs
        category="Оптимизация"
        current="Симплекс-метод (алгебраические преобразования)"
      />

      <div className="simplex-page">
        <section className="panel-card">
          <div className="simplex-head">
            <div>
              <h1 className="page-title">
                Симплекс-метод с алгебраическими преобразованиями
              </h1>
              <p className="page-subtitle">
                Метод показывает переходы между базисами через выражения основных
                переменных, без симплекс-таблиц.
              </p>
            </div>

            <button className="secondary-btn" onClick={fillDemo}>
              Подставить пример
            </button>
          </div>

          <div className="setup-grid">
            <div>
              <label>Количество переменных</label>
              <input
                type="number"
                min="1"
                value={numVariables}
                onChange={(event) => setNumVariables(Number(event.target.value))}
              />
            </div>
            <div>
              <label>Количество ограничений</label>
              <input
                type="number"
                min="1"
                value={numConstraints}
                onChange={(event) => setNumConstraints(Number(event.target.value))}
              />
            </div>
            <div>
              <label>Тип задачи</label>
              <select
                value={objectiveType}
                onChange={(event) => setObjectiveType(event.target.value)}
              >
                <option value="max">max</option>
                <option value="min">min</option>
              </select>
            </div>
          </div>
        </section>

        <section className="panel-card">
          <h2 className="card-title">Ограничения</h2>

          <div className="lp-table-wrap simplex-constraints-wrap">
            <table className="lp-input-table simplex-constraints-table">
              <thead>
                <tr>
                  {variableLabels.map((label) => (
                    <th key={label}>{toSubscript(label)}</th>
                  ))}
                  <th>Знак</th>
                  <th>b</th>
                </tr>
              </thead>
              <tbody>
                {Array.from({ length: numConstraints }).map((_, row) => (
                  <tr key={row}>
                    {Array.from({ length: numVariables }).map((_, col) => (
                      <td key={col}>
                        <input
                          type="number"
                          value={coeffs[row]?.[col] ?? ""}
                          onChange={(event) => updateCoeff(row, col, event.target.value)}
                        />
                      </td>
                    ))}
                    <td>
                      <select
                        value={relations[row] ?? "<="}
                        onChange={(event) => updateRelation(row, event.target.value)}
                      >
                        <option value="<=">{"<="}</option>
                        <option value=">=">{">="}</option>
                      </select>
                    </td>
                    <td>
                      <input
                        type="number"
                        value={rhs[row] ?? ""}
                        onChange={(event) => updateRhs(row, event.target.value)}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h2 className="card-title">Целевая функция</h2>
          <div className="objective-row">
            {variableLabels.map((label, index) => (
              <div key={label} className="objective-item">
                <input
                  type="number"
                  value={objective[index] ?? ""}
                  onChange={(event) => updateObjective(index, event.target.value)}
                />
                <span>{toSubscript(label)}</span>
              </div>
            ))}
            <span className="objective-type">→ {objectiveType}</span>
          </div>

          <button
            className="primary-btn full-blue"
            onClick={handleSolve}
            disabled={loading}
          >
            {loading ? "Решаем..." : "Решить"}
          </button>
        </section>

        {error && (
          <section className="panel-card result-card error">
            <h3 className="card-title">Ошибка</h3>
            <div className="result-text error-text">{error}</div>
          </section>
        )}

        {result && (
          <>
            <section className="panel-card">
              <h2 className="card-title">Результат</h2>
              <div className="simplex-status-row">
                <div className="simplex-status-badge">{result.status}</div>
                <div>{result.message}</div>
              </div>
              {result.objective_value && (
                <div className="objective-value-box">
                  <strong>Значение целевой функции:</strong> {result.objective_value}
                </div>
              )}
              <div className="solution-grid">{formatSolution(result.solution)}</div>
              <button
                className="secondary-btn download-docx-btn"
                onClick={handleDownloadDocx}
                disabled={downloading}
              >
                {downloading ? "Формируем файл..." : "Скачать Word"}
              </button>
            </section>

            <section className="panel-card">
              <h2 className="card-title">Каноническая форма</h2>
              <div className="canonical-block">
                {result.canonical_system?.map((line, index) => (
                  <div key={index} className="canonical-line">
                    {toSubscript(line)}
                  </div>
                ))}
              </div>
            </section>

            <section className="panel-card">
              <h2 className="card-title">Ход решения</h2>

              {result.steps?.map((step) => (
                <div key={step.title} className="algebraic-step">
                  <div className="tableau-header">
                    <h3 className="sample-table-title">{step.title}</h3>
                    {step.pivot && (
                      <div className="pivot-note">
                        {toSubscript(step.pivot.entering)} вместо{" "}
                        {toSubscript(step.pivot.leaving)}
                      </div>
                    )}
                  </div>

                  <p className="tableau-description">
                    {toSubscript(step.description)}
                  </p>

                  <div className="basis-line">
                    <strong>Основные переменные:</strong>{" "}
                    {step.basis.map(toSubscript).join(", ")}
                  </div>
                  <div className="basis-line">
                    <strong>Неосновные переменные:</strong>{" "}
                    {step.free.map(toSubscript).join(", ")}
                  </div>

                  <div className="equation-system">
                    {step.equations.map((line, index) => (
                      <div key={index} className="canonical-line">
                        {toSubscript(line)}
                      </div>
                    ))}
                  </div>

                  <div className="canonical-line objective-expression">
                    {toSubscript(step.objective_expression)}
                  </div>

                  <div className="solution-grid">
                    {formatSolution(step.basic_solution)}
                  </div>
                </div>
              ))}
            </section>
          </>
        )}
      </div>
    </>
  );
}
