import { toSubscript } from "../utils/mathFormat";

function formatPivotInfo(step) {
  if (
    step?.pivot_col === null ||
    step?.pivot_col === undefined ||
    step?.pivot_row === null ||
    step?.pivot_row === undefined
  ) {
    return null;
  }

  const colName = step.column_names?.[step.pivot_col] ?? "";
  const rowName = step.row_names?.[step.pivot_row] ?? "";
  const pivot = step.pivot_element ?? "";

  return { colName, rowName, pivot };
}

export default function SimplexNarrative({ step }) {
  const pivotInfo = formatPivotInfo(step);

  if (pivotInfo) {
    return (
      <div className="simplex-narrative">
        {step.description && <p>{toSubscript(step.description)}</p>}
        <p>
          Ведущий столбец — <strong>{toSubscript(pivotInfo.colName)}</strong>,
          ведущая строка — <strong>{toSubscript(pivotInfo.rowName)}</strong>,
          ведущий элемент — <strong>{pivotInfo.pivot}</strong>.
        </p>
      </div>
    );
  }

  if (step.description) {
    return (
      <div className="simplex-narrative">
        <p>{toSubscript(step.description)}</p>
      </div>
    );
  }

  if (step.title?.includes("неограниченности")) {
    return (
      <div className="simplex-narrative">
        <p>
          Допустимая разрешающая строка отсутствует. Следовательно, целевая функция
          не ограничена на множестве допустимых решений.
        </p>
      </div>
    );
  }

  return (
    <div className="simplex-narrative">
      <p>{toSubscript(step.description)}</p>
    </div>
  );
}
