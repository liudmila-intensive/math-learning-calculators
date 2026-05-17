import { toSubscript } from "../utils/mathFormat";

function getDisplayColumns(step) {
  const basisNames = new Set((step.row_names || []).filter((name) => name !== "F"));
  const allCols = (step.column_names || []).filter((name) => name !== "b");

  return allCols.filter((name) => !basisNames.has(name));
}

function getColumnIndexMap(step) {
  const map = {};
  (step.column_names || []).forEach((name, index) => {
    map[name] = index;
  });
  return map;
}

function invertSign(value) {
  if (value === null || value === undefined || value === "") return "";
  const text = String(value).trim();

  if (text === "0") return "0";
  if (text.startsWith("-")) return text.slice(1);
  return `-${text}`;
}

function getHelperCoefficients(prevStep) {
  if (!prevStep) return null;
  if (prevStep.pivot_col === null || prevStep.pivot_col === undefined) return null;

  return prevStep.data.map((row, rowIndex) => {
    if (rowIndex === prevStep.pivot_row) return "";
    return invertSign(row[prevStep.pivot_col]);
  });
}

function getBIndex(step) {
  return (step.column_names || []).indexOf("b");
}

export default function SimplexSampleTable({ step, stepIndex, prevStep }) {
  const displayCols = getDisplayColumns(step);
  const colIndexMap = getColumnIndexMap(step);
  const helperCoeffs = getHelperCoefficients(prevStep);
  const bIndex = getBIndex(step);

  return (
    <div className="sample-table-block">
      <h3 className="sample-table-title">{step.title || `Таблица ${stepIndex + 1}`}</h3>

      <div className="lp-table-wrap">
        <table className="sample-simplex-table">
          <thead>
            <tr>
              <th rowSpan="2">Базисные неизвестные</th>
              <th rowSpan="2">Свободные члены</th>
              <th colSpan={Math.max(displayCols.length, 1)}>Свободные неизвестные</th>
              <th rowSpan="2">Вспомогательные коэффициенты</th>
            </tr>
            <tr>
              {displayCols.length > 0 ? (
                displayCols.map((col) => {
                  const colIdx = colIndexMap[col];
                  const isPivotCol = step.pivot_col === colIdx;

                  return (
                    <th key={col} className={isPivotCol ? "pivot-col-header" : ""}>
                      {toSubscript(col)}
                    </th>
                  );
                })
              ) : (
                <th>—</th>
              )}
            </tr>
          </thead>

          <tbody>
            {step.data.map((row, rowIndex) => {
              const rhs = bIndex >= 0 ? row[bIndex] : "";
              const basisName = step.row_names?.[rowIndex] ?? "";

              return (
                <tr
                  key={rowIndex}
                  className={step.pivot_row === rowIndex ? "pivot-row-highlight" : ""}
                >
                  <td className="basis-cell">{toSubscript(basisName)}</td>
                  <td>{rhs}</td>

                  {displayCols.length > 0 ? (
                    displayCols.map((col) => {
                      const colIdx = colIndexMap[col];
                      const isPivot =
                        step.pivot_row === rowIndex && step.pivot_col === colIdx;

                      return (
                        <td key={col} className={isPivot ? "pivot-cell" : ""}>
                          {row[colIdx]}
                        </td>
                      );
                    })
                  ) : (
                    <td>—</td>
                  )}

                  <td className="helper-cell">
                    {helperCoeffs ? helperCoeffs[rowIndex] : ""}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
