import { FiX, FiRefreshCcw } from "react-icons/fi";
import { PiMathOperationsBold } from "react-icons/pi";

export default function CalculatorForm({
  expression,
  setExpression,
  onSimplify,
  onClear,
  loading,
}) {
  return (
    <section className="panel-card hero-card">
      <div className="hero-header">
        <div className="hero-title-wrap">
          <div className="hero-icon">
            <PiMathOperationsBold />
          </div>

          <div>
            <h1 className="page-title">Упростить выражение</h1>
            <p className="page-subtitle">
              Приведение подобных слагаемых и упрощение алгебраических выражений
            </p>
          </div>
        </div>

        <div className="hero-tag">Алгебра</div>
      </div>

      <div className="field-block">
        <label className="field-label">Введите выражение</label>

        <div className="input-wrap">
          <input
            type="text"
            className="expression-input"
            value={expression}
            onChange={(e) => setExpression(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                onSimplify();
              }
            }}
            placeholder="2x + 3x - x"
          />
          <button
            type="button"
            className="input-clear-btn"
            onClick={() => setExpression("")}
            aria-label="Очистить поле"
          >
            <FiX />
          </button>
        </div>

        <div className="under-input-hint">
          Используйте переменные: x, y, a, b. Примеры:
          <span className="mini-chip">2x + 3x - x</span>
          <span className="mini-chip">5(a + 2)</span>
        </div>
      </div>

      <div className="actions-block">
        <button className="primary-btn full-blue" onClick={onSimplify} disabled={loading}>
          <PiMathOperationsBold />
          <span>{loading ? "Упрощаем..." : "Упростить выражение"}</span>
        </button>

        <button className="ghost-note-btn" onClick={onClear} disabled={loading}>
          <FiRefreshCcw />
          <span>Очистить</span>
        </button>
      </div>

      <div className="enter-hint">Нажмите Enter для вычисления</div>
    </section>
  );
}