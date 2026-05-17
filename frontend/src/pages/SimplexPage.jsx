import { useEffect, useMemo, useState } from "react";
import Breadcrumbs from "../components/Breadcrumbs";
import { downloadSimplexDocx, solveSimplex } from "../services/api";
import SimplexSampleTable from "../components/SimplexSampleTable";
import SimplexNarrative from "../components/SimplexNarrative";
import { toSubscript } from "../utils/mathFormat";

export default function SimplexPage() {
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

  function updateCoeff(r, c, value) {
    setCoeffs((prev) => {
      const next = prev.map((row) => [...row]);

      while (next.length <= r) {
        next.push(Array.from({ length: numVariables }, () => ""));
      }

      while (next[r].length <= c) {
        next[r].push("");
      }

      next[r][c] = value;
      return next;
    });
  }

  function updateObjective(c, value) {
    setObjective((prev) => {
      const next = [...prev];
      while (next.length <= c) next.push("");
      next[c] = value;
      return next;
    });
  }

  function updateRelation(r, value) {
    setRelations((prev) => {
      const next = [...prev];
      while (next.length <= r) next.push("<=");
      next[r] = value;
      return next;
    });
  }

  function updateRhs(r, value) {
    setRhs((prev) => {
      const next = [...prev];
      while (next.length <= r) next.push("");
      next[r] = value;
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
        objective: objective.map((x) => Number(x || 0)),
        constraints: coeffs.map((row, i) => ({
          coefficients: row.map((x) => Number(x || 0)),
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
      const data = await solveSimplex(payload);
      setResult(data);
    } catch (err) {
      setError(err?.response?.data?.detail || "Ошибка решения задачи");
    } finally {
      setLoading(false);
    }
  }

  async function handleDownloadDocx() {
    setDownloading(true);
    try {
      await downloadSimplexDocx(buildPayload());
    } finally {
      setDownloading(false);
    }
  }

  return (
    <>
      <Breadcrumbs category="Оптимизация" current="Симплекс-метод" />

      <div className="simplex-page">
        <section className="panel-card">
          <div className="simplex-head">
            <div>
              <h1 className="page-title">Симплекс-метод</h1>
              <p className="page-subtitle">
                Введите коэффициенты ограничений и целевой функции, затем
                постройте симплекс-таблицы.
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
                onChange={(e) => setNumVariables(Number(e.target.value))}
              />
            </div>

            <div>
              <label>Количество ограничений</label>
              <input
                type="number"
                min="1"
                value={numConstraints}
                onChange={(e) => setNumConstraints(Number(e.target.value))}
              />
            </div>

            <div>
              <label>Тип задачи</label>
              <select
                value={objectiveType}
                onChange={(e) => setObjectiveType(e.target.value)}
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
                  {variableLabels.map((v) => (
                    <th key={v}>{toSubscript(v)}</th>
                  ))}
                  <th>Знак</th>
                  <th>b</th>
                </tr>
              </thead>
              <tbody>
                {Array.from({ length: numConstraints }).map((_, r) => (
                  <tr key={r}>
                    {Array.from({ length: numVariables }).map((_, c) => (
                      <td key={c}>
                        <input
                          type="number"
                          value={coeffs[r]?.[c] ?? ""}
                          onChange={(e) => updateCoeff(r, c, e.target.value)}
                        />
                      </td>
                    ))}

                    <td>
                      <select
                        value={relations[r] ?? "<="}
                        onChange={(e) => updateRelation(r, e.target.value)}
                      >
                        <option value="<=">{"<="}</option>
                        <option value=">=">{">="}</option>
                        <option value="=">{"="}</option>
                      </select>
                    </td>

                    <td>
                      <input
                        type="number"
                        value={rhs[r] ?? ""}
                        onChange={(e) => updateRhs(r, e.target.value)}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h2 className="card-title">Целевая функция</h2>

          <div className="objective-row">
            {variableLabels.map((v, i) => (
              <div key={v} className="objective-item">
                <input
                  type="number"
                  value={objective[i] ?? ""}
                  onChange={(e) => updateObjective(i, e.target.value)}
                />
                <span>{toSubscript(v)}</span>
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
                <div>{result.message || "Решение получено."}</div>
              </div>

              {result.objective_value && (
                <div className="objective-value-box">
                  <strong>Значение целевой функции:</strong> {result.objective_value}
                </div>
              )}

              {result.solution && Object.keys(result.solution).length > 0 && (
                <div className="solution-grid">
                  {Object.entries(result.solution).map(([key, value]) => (
                    <div key={key} className="solution-item">
                      <strong>{toSubscript(key)}</strong> = {value}
                    </div>
                  ))}
                </div>
              )}

              <button
                className="secondary-btn download-docx-btn"
                onClick={handleDownloadDocx}
                disabled={downloading}
              >
                {downloading ? "Формируем файл..." : "Скачать Word"}
              </button>
            </section>

            {result.canonical_system?.length > 0 && (
              <section className="panel-card">
                <h2 className="card-title">Каноническая форма</h2>
                <div className="canonical-block">
                  {result.canonical_system.map((line, i) => (
                    <div key={i} className="canonical-line">
                      {toSubscript(line)}
                    </div>
                  ))}
                </div>
              </section>
            )}

            {result.basis_expressions?.length > 0 && (
              <section className="panel-card">
                <h2 className="card-title">Базисные переменные через свободные</h2>
                <div className="canonical-block">
                  {result.basis_expressions.map((line, i) => (
                    <div key={i} className="canonical-line">
                      {toSubscript(line)}
                    </div>
                  ))}
                </div>
              </section>
            )}

            {result.objective_expression && (
              <section className="panel-card">
                <h2 className="card-title">Целевая функция</h2>
                <div className="canonical-line">
                  {toSubscript(result.objective_expression)}
                </div>
              </section>
            )}

            <section className="panel-card">
              <h2 className="card-title">Симплекс-таблицы</h2>

              {result.steps?.length ? (
                result.steps.map((step, idx) => (
                  <div key={idx} className="tableau-block">
                    <SimplexSampleTable
                      step={step}
                      stepIndex={idx}
                      prevStep={idx > 0 ? result.steps[idx - 1] : null}
                    />

                    <SimplexNarrative step={step} stepIndex={idx} />
                  </div>
                ))
              ) : (
                <div className="muted">Шаги решения отсутствуют.</div>
              )}
            </section>
          </>
        )}
      </div>
    </>
  );
}
