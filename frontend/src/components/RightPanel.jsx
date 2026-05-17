import { FiClock, FiTrash2 } from "react-icons/fi";
import { LuLightbulb } from "react-icons/lu";

export default function RightPanel({ history, onClearHistory }) {
  return (
    <aside className="right-panel">
      <section className="info-card tip-card">
        <div className="side-card-title">
          <LuLightbulb />
          <h3>Подсказка</h3>
        </div>

        <p>
          Можно использовать <strong>^</strong> для степени:
          <br />
          <strong>x^2 + 2*x + 1</strong>
        </p>
      </section>

      <section className="info-card history-card">
        <div className="side-card-title">
          <FiClock />
          <h3>История</h3>
        </div>

        <div className="history-list">
          {history.length === 0 ? (
            <p className="history-empty">История пока пуста</p>
          ) : (
            history.map((item, index) => (
              <div className="history-item" key={index}>
                <div className="history-expression">{item.expression}</div>
                <div className="history-result">{item.result}</div>
              </div>
            ))
          )}
        </div>

        <button className="secondary-btn full-width clear-history-btn" onClick={onClearHistory}>
          <FiTrash2 />
          <span>Очистить историю</span>
        </button>
      </section>
    </aside>
  );
}