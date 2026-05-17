import { useEffect, useState } from "react";
import Breadcrumbs from "../components/Breadcrumbs";
import MathFormula from "../components/MathFormula";
import { solveLinearSystem } from "../services/api";
import { toSubscript } from "../utils/mathFormat";

function MatrixTable({ matrix }) {
  return (
    <div className="lp-table-wrap">
      <table className="lp-result-table linear-system-table">
        <tbody>
          {matrix.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((value, colIndex) => (
                <td key={colIndex}>{value}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function GaussTable({ state }) {
  return (
    <div className="lp-table-wrap gauss-table-wrap">
      <table className="lp-result-table gauss-table">
        <thead>
          <tr>
            <th>Б.П.</th>
            {state.columns.map((column) => (
              <th key={column}>{toSubscript(column)}</th>
            ))}
            <th>bᵢ</th>
            <th>Σ</th>
          </tr>
        </thead>
        <tbody>
          {state.rows.map((row, rowIndex) => (
            <tr key={rowIndex}>
              <td>{toSubscript(row.basis)}</td>
              {row.values.map((value, colIndex) => (
                <td key={colIndex}>
                  <span className={row.pivot_col === colIndex ? "pivot-mark" : ""}>
                    {value}
                  </span>
                </td>
              ))}
              <td>{row.rhs}</td>
              <td>{row.sum}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function CramerExpansion({ label, expansion }) {
  if (!expansion) {
    return null;
  }

  return (
    <div className="cramer-expansion">
      <MathFormula latex={`${label}=${expansion.expansion_latex}`} />
      <MathFormula latex={`${label}=${expansion.calculation_latex}`} />
    </div>
  );
}

export default function LinearSystemPage() {
  const [size, setSize] = useState(3);
  const [coefficients, setCoefficients] = useState([]);
  const [rhs, setRhs] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setCoefficients((prev) =>
      Array.from({ length: size }, (_, row) =>
        Array.from({ length: size }, (_, col) => prev[row]?.[col] ?? "")
      )
    );
    setRhs((prev) => Array.from({ length: size }, (_, row) => prev[row] ?? ""));
  }, [size]);

  function updateCoeff(row, col, value) {
    setCoefficients((prev) => {
      const next = prev.map((items) => [...items]);
      next[row][col] = value;
      return next;
    });
  }

  function updateRhs(row, value) {
    setRhs((prev) => {
      const next = [...prev];
      next[row] = value;
      return next;
    });
  }

  function fillDemo() {
    setSize(3);
    setCoefficients([
      ["-1", "2", "-5"],
      ["2", "1", "3"],
      ["1", "-4", "5"],
    ]);
    setRhs(["1", "1", "-10"]);
    setResult(null);
    setError("");
  }

  function updateSize(value) {
    const nextSize = Math.max(2, Math.min(5, Number(value) || 2));
    setSize(nextSize);
    setResult(null);
    setError("");
  }

  function buildPayload() {
    return { coefficients, rhs };
  }

  async function handleSolve() {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      setResult(await solveLinearSystem(buildPayload()));
    } catch (err) {
      setError(err?.response?.data?.detail || "Ошибка решения системы");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Breadcrumbs category="Линейная алгебра" current="Системы линейных уравнений" />

      <div className="simplex-page linear-system-page">
        <section className="panel-card">
          <div className="simplex-head">
            <div>
              <h1 className="page-title">Системы линейных уравнений</h1>
              <p className="page-subtitle">
                Решение матричным методом Гаусса, табличным методом Гаусса и методом Крамера.
              </p>
            </div>

            <button className="secondary-btn" onClick={fillDemo}>
              Подставить пример
            </button>
          </div>

          <div className="setup-grid linear-system-setup">
            <div>
              <label>Количество неизвестных</label>
              <input
                type="number"
                min="2"
                max="5"
                value={size}
                onChange={(event) => updateSize(event.target.value)}
              />
            </div>
          </div>
        </section>

        <section className="panel-card">
          <h3 className="card-title">Коэффициенты системы</h3>

          <div className="lp-table-wrap linear-input-wrap">
            <table className="lp-input-table linear-input-table">
              <thead>
                <tr>
                  {Array.from({ length: size }, (_, index) => (
                    <th key={index}>{toSubscript(`x_${index + 1}`)}</th>
                  ))}
                  <th>b</th>
                </tr>
              </thead>
              <tbody>
                {coefficients.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {row.map((value, colIndex) => (
                      <td key={colIndex}>
                        <input
                          type="text"
                          value={value}
                          onChange={(event) => updateCoeff(rowIndex, colIndex, event.target.value)}
                        />
                      </td>
                    ))}
                    <td>
                      <input
                        type="text"
                        value={rhs[rowIndex] ?? ""}
                        onChange={(event) => updateRhs(rowIndex, event.target.value)}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <button className="primary-btn full-blue" onClick={handleSolve} disabled={loading}>
            {loading ? "Решаем..." : "Решить систему"}
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
            <section className="panel-card result-card success">
              <h3 className="card-title">Ответ:</h3>
              <MathFormula latex={result.solution_latex} />
            </section>

            <section className="panel-card">
              <h3 className="card-title">Исходная система</h3>
              <MathFormula latex={result.equations_latex} />
            </section>

            <section className="panel-card">
              <h3 className="card-title">I. Матричный метод Гаусса</h3>
              <p className="tableau-description">
                Используем элементарные преобразования строк и приводим матрицу к
                треугольному виду.
              </p>
              <div className="gauss-chain">
                {result.matrix_gauss.chain_steps.map((step, index) => (
                  <div className="gauss-chain-item" key={index}>
                    {step.operation && <div className="gauss-operation">{step.operation}</div>}
                    <MathFormula latex={step.latex} />
                  </div>
                ))}
              </div>

              <p className="tableau-description">
                Восстановим по последней матрице систему уравнений и используем
                обратный ход Гаусса.
              </p>
              <MathFormula latex={result.matrix_gauss.triangular_latex} />

              <div className="back-substitution">
                {result.matrix_gauss.back_steps.map((step, index) => (
                  <MathFormula key={index} latex={step.latex} />
                ))}
              </div>
            </section>

            <section className="panel-card">
              <h3 className="card-title">II. Табличный метод Гаусса</h3>
              <p className="tableau-description">
                Записываем расширенную матрицу в таблицу. В столбце Σ указана сумма
                элементов строки.
              </p>

              {result.table_gauss.states.map((state, index) => (
                <div className="tableau-block" key={index}>
                  <div className="tableau-header">
                    <strong>{index === 0 ? "Исходная таблица" : `Преобразование ${index}`}</strong>
                  </div>
                  <GaussTable state={state} />
                </div>
              ))}
            </section>

            <section className="panel-card">
              <h3 className="card-title">III. Метод Крамера</h3>
              <p className="tableau-description">
                Используем формулы Крамера:
                {" "}
                <span className="inline-formula">x₁ = Δ₁/Δ, x₂ = Δ₂/Δ, x₃ = Δ₃/Δ</span>.
              </p>
              <CramerExpansion label="\\Delta" expansion={result.cramer.expansion} />
              {!result.cramer.expansion && (
                <MathFormula latex={`\\Delta=${result.cramer.determinant_latex}`} />
              )}

              <div className="cramer-grid">
                {result.cramer.items.map((item) => (
                  <div className="cramer-card" key={item.index}>
                    <h4>Δ{toSubscript(`_${item.index}`)}</h4>
                    <MatrixTable matrix={item.matrix} />
                    <CramerExpansion
                      label={`\\Delta_{${item.index}}`}
                      expansion={item.expansion}
                    />
                    <MathFormula
                      latex={`x_{${item.index}}=\\frac{\\Delta_{${item.index}}}{\\Delta}=\\frac{${item.determinant_latex}}{${result.cramer.determinant_latex}}=${item.value_latex}`}
                    />
                  </div>
                ))}
              </div>
            </section>
          </>
        )}
      </div>
    </>
  );
}
