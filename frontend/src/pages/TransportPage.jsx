import { useEffect, useState } from "react";
import Breadcrumbs from "../components/Breadcrumbs";
import { downloadTransportDocx, solveTransport } from "../services/api";
import { toSubscript } from "../utils/mathFormat";

function supplierName(index, total) {
  return index === total - 1 ? "Фиктивный" : renderName(`A${index + 1}`);
}

function renderName(name) {
  return toSubscript(String(name));
}

function formatTransportText(text = "") {
  return toSubscript(String(text).replace(/A_(\d+)B_(\d+)/g, "A$1B$2"));
}

function reductionTrail(values) {
  const normalized = values.filter((value) => value !== undefined && value !== null);

  return (
    <span className="transport-reduction-trail">
      {normalized.map((value, index) => (
        <span
          key={`${value}-${index}`}
          className={index < normalized.length - 1 ? "crossed-value" : "current-value"}
        >
          {value}
        </span>
      ))}
    </span>
  );
}

function buildReductionMap(allocations = [], key, beforeKey, afterKey) {
  const result = new Map();

  allocations.forEach((item) => {
    const mapKey = item[key];
    const values = result.get(mapKey) || [];

    if (values.length === 0) {
      values.push(item[beforeKey]);
    }
    values.push(item[afterKey]);
    result.set(mapKey, values);
  });

  return result;
}

function TransportPlanTable({ step }) {
  const rows = step.plan || [];
  const cols = step.demand || [];
  const rowReductions = buildReductionMap(
    step.allocations,
    "row",
    "supply_before",
    "supply_after"
  );
  const colReductions = buildReductionMap(
    step.allocations,
    "col",
    "demand_before",
    "demand_after"
  );

  return (
    <div className="lp-table-wrap">
      <table className="transport-table">
        <thead>
          <tr>
            <th>Поставщик</th>
            <th colSpan={cols.length}>Потребитель</th>
            <th>Запас</th>
            {step.u?.length > 0 && <th>U</th>}
          </tr>
          <tr>
            <th></th>
            {cols.map((_, index) => (
              <th key={index}>{renderName(`B${index + 1}`)}</th>
            ))}
            <th></th>
            {step.u?.length > 0 && <th></th>}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              <th>{supplierName(i, rows.length)}</th>
              {row.map((value, j) => {
                const route = `A_${i + 1}B_${j + 1}`;
                const active = step.basis?.includes(route) && value !== "0";
                const cycleItem = step.cycle?.cycle?.find((item) => item.cell === route);

                return (
                  <td key={j} className={active ? "transport-active-cell" : ""}>
                    <div className="transport-amount">
                      {value !== "0" ? value : ""}
                      {cycleItem && (
                        <span className={cycleItem.sign === "+" ? "cycle-plus" : "cycle-minus"}>
                          [{cycleItem.sign}]
                        </span>
                      )}
                    </div>
                    <div className="transport-cost">{step.costs?.[i]?.[j]}</div>
                  </td>
                );
              })}
              <th>
                {rowReductions.has(i)
                  ? reductionTrail(rowReductions.get(i))
                  : step.supply?.[i]}
              </th>
              {step.u?.length > 0 && <th>{toSubscript(`u_${i + 1}`)}={step.u[i]}</th>}
            </tr>
          ))}
          <tr>
            <th>Потребность</th>
            {cols.map((value, index) => (
              <th key={index}>
                {colReductions.has(index)
                  ? reductionTrail(colReductions.get(index))
                  : value}
              </th>
            ))}
            <th></th>
            {step.v?.length > 0 && <th></th>}
          </tr>
          {step.v?.length > 0 && (
            <tr>
              <th>V</th>
              {step.v.map((value, index) => (
                <th key={index}>{toSubscript(`v_${index + 1}`)}={value}</th>
              ))}
              <th></th>
              <th></th>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

function PotentialCalculations({ lines }) {
  if (!lines?.length) {
    return null;
  }

  return (
    <div className="transport-estimates">
      <h3 className="sample-table-title">Вычисление потенциалов</h3>
      <div className="canonical-block">
        {lines.map((line, index) => (
          <div key={`${line}-${index}`}>{formatTransportText(line)}</div>
        ))}
      </div>
    </div>
  );
}

export default function TransportPage() {
  const [rows, setRows] = useState(3);
  const [cols, setCols] = useState(4);
  const [costs, setCosts] = useState([]);
  const [supply, setSupply] = useState([]);
  const [demand, setDemand] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setCosts((prev) =>
      Array.from({ length: rows }, (_, i) =>
        Array.from({ length: cols }, (_, j) => prev[i]?.[j] ?? "")
      )
    );
    setSupply((prev) => Array.from({ length: rows }, (_, i) => prev[i] ?? ""));
    setDemand((prev) => Array.from({ length: cols }, (_, i) => prev[i] ?? ""));
  }, [rows, cols]);

  function fillDemo() {
    setRows(3);
    setCols(4);
    setCosts([
      ["4", "5", "4", "6"],
      ["7", "5", "1", "5"],
      ["3", "1", "4", "4"],
    ]);
    setSupply(["26", "25", "25"]);
    setDemand(["20", "15", "23", "20"]);
    setResult(null);
    setError("");
  }

  function updateCost(i, j, value) {
    setCosts((prev) => {
      const next = prev.map((row) => [...row]);
      next[i][j] = value;
      return next;
    });
  }

  function buildPayload() {
    return {
      costs: costs.map((row) => row.map((value) => Number(value || 0))),
      supply: supply.map((value) => Number(value || 0)),
      demand: demand.map((value) => Number(value || 0)),
    };
  }

  async function handleSolve() {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const payload = buildPayload();
      setResult(await solveTransport(payload));
    } catch (err) {
      setError(err?.response?.data?.detail || "Ошибка решения задачи");
    } finally {
      setLoading(false);
    }
  }

  async function handleDownloadDocx() {
    setDownloading(true);
    try {
      await downloadTransportDocx(buildPayload());
    } finally {
      setDownloading(false);
    }
  }

  return (
    <>
      <Breadcrumbs category="Оптимизация" current="Транспортная задача" />

      <div className="simplex-page">
        <section className="panel-card">
          <div className="simplex-head">
            <div>
              <h1 className="page-title">Транспортная задача</h1>
              <p className="page-subtitle">
                Составление плана перевозок с минимальной общей стоимостью.
              </p>
            </div>
            <button className="secondary-btn" onClick={fillDemo}>
              Подставить пример
            </button>
          </div>

          <div className="setup-grid">
            <div>
              <label>Количество поставщиков</label>
              <input
                type="number"
                min="1"
                value={rows}
                onChange={(event) => setRows(Number(event.target.value))}
              />
            </div>
            <div>
              <label>Количество потребителей</label>
              <input
                type="number"
                min="1"
                value={cols}
                onChange={(event) => setCols(Number(event.target.value))}
              />
            </div>
          </div>
        </section>

        <section className="panel-card">
          <h2 className="card-title">Тарифы, запасы и потребности</h2>
          <div className="lp-table-wrap">
            <table className="lp-input-table">
              <thead>
                <tr>
                  <th>Поставщик</th>
                  {Array.from({ length: cols }).map((_, j) => (
                    <th key={j}>{renderName(`B${j + 1}`)}</th>
                  ))}
                  <th>Запас</th>
                </tr>
              </thead>
              <tbody>
                {Array.from({ length: rows }).map((_, i) => (
                  <tr key={i}>
                    <th>{renderName(`A${i + 1}`)}</th>
                    {Array.from({ length: cols }).map((_, j) => (
                      <td key={j}>
                        <input
                          type="number"
                          value={costs[i]?.[j] ?? ""}
                          onChange={(event) => updateCost(i, j, event.target.value)}
                        />
                      </td>
                    ))}
                    <td>
                      <input
                        type="number"
                        value={supply[i] ?? ""}
                        onChange={(event) => {
                          const next = [...supply];
                          next[i] = event.target.value;
                          setSupply(next);
                        }}
                      />
                    </td>
                  </tr>
                ))}
                <tr>
                  <th>Потребность</th>
                  {Array.from({ length: cols }).map((_, j) => (
                    <td key={j}>
                      <input
                        type="number"
                        value={demand[j] ?? ""}
                        onChange={(event) => {
                          const next = [...demand];
                          next[j] = event.target.value;
                          setDemand(next);
                        }}
                      />
                    </td>
                  ))}
                  <td></td>
                </tr>
              </tbody>
            </table>
          </div>

          <button className="primary-btn full-blue" onClick={handleSolve} disabled={loading}>
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
              <div className="objective-value-box">
                <strong>Минимальные затраты:</strong> {result.total_cost} ден. ед.
              </div>
              <button
                className="secondary-btn download-docx-btn"
                onClick={handleDownloadDocx}
                disabled={downloading}
              >
                {downloading ? "Формируем файл..." : "Скачать Word"}
              </button>
            </section>

            {result.steps?.map((step) => (
              <section key={step.title} className="panel-card">
                <h2 className="card-title">{step.title}</h2>
                <p className="tableau-description">{formatTransportText(step.note)}</p>
                <PotentialCalculations lines={step.potential_calculations} />
                <TransportPlanTable step={step} />

                {step.allocations?.length > 0 && (
                  <div className="transport-notes">
                    {step.allocations.map((item) => (
                      <span key={item.cell} className="mini-chip">
                        {renderName(item.cell)}:{" "}
                        {item.calculation}
                      </span>
                    ))}
                  </div>
                )}

                {step.estimates?.length > 0 && (
                  <div className="transport-estimates">
                    <h3 className="sample-table-title">Оценки свободных клеток</h3>
                    <div className="canonical-block">
                      {step.estimates.map((item) => (
                        <div key={item.cell} className={item.value.startsWith("-") ? "negative-estimate" : ""}>
                          {renderName(item.cell)}: {toSubscript(item.text)}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {step.cycle && (
                  <div className="objective-value-box">
                    <strong>Цикл перераспределения:</strong>{" "}
                    {step.cycle.cycle
                      .map((item) => `${renderName(item.cell)}[${item.sign}]`)
                      .join(" → ")}
                    . θ = {step.cycle.theta}
                  </div>
                )}

                <div className="objective-value-box">
                  <strong>Стоимость:</strong> {step.cost_formula} ден. ед.
                </div>
              </section>
            ))}

            <section className="panel-card">
              <h2 className="card-title">Ответ</h2>
              <TransportPlanTable
                step={{
                  plan: result.solution,
                  costs: result.balanced.costs,
                  supply: result.balanced.supply,
                  demand: result.balanced.demand,
                  basis: [],
                }}
              />
              <div className="objective-value-box">
                Smin = {result.total_cost} ден. ед.
              </div>
            </section>
          </>
        )}
      </div>
    </>
  );
}
