import { useEffect, useState } from "react";
import {
  FiChevronDown,
  FiFolder,
  FiLayers,
  FiTrendingUp,
  FiBarChart2,
  FiCircle,
} from "react-icons/fi";

function groupForCalculator(activeCalculator) {
  if (["linear-system"].includes(activeCalculator)) {
    return "linear";
  }
  if (["simplex", "simplex-algebraic", "transport"].includes(activeCalculator)) {
    return "optimization";
  }
  return "algebra";
}

export default function Sidebar({ activeCalculator, setActiveCalculator }) {
  const activeGroup = groupForCalculator(activeCalculator);
  const [openGroups, setOpenGroups] = useState({
    algebra: activeGroup === "algebra",
    linear: activeGroup === "linear",
    optimization: activeGroup === "optimization",
    statistics: activeGroup === "statistics",
  });

  useEffect(() => {
    setOpenGroups((prev) => ({
      ...prev,
      [activeGroup]: true,
    }));
  }, [activeGroup]);

  function toggleGroup(group) {
    setOpenGroups((prev) => ({
      ...prev,
      [group]: !prev[group],
    }));
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <button
          type="button"
          className="sidebar-group-header algebra sidebar-group-toggle"
          onClick={() => toggleGroup("algebra")}
          aria-expanded={openGroups.algebra}
        >
          <div className="sidebar-group-title">
            <FiFolder />
            <span>Алгебра</span>
          </div>
          <FiChevronDown className={openGroups.algebra ? "chevron-open" : "chevron-closed"} />
        </button>

        {openGroups.algebra && (
          <div className="sidebar-group-body">
            <button
              className={activeCalculator === "simplify" ? "side-link active" : "side-link"}
              onClick={() => setActiveCalculator("simplify")}
            >
              <span className="side-bullet">•</span>
              <span>Упростить выражение</span>
            </button>

            <button
              className={activeCalculator === "equation" ? "side-link active" : "side-link"}
              onClick={() => setActiveCalculator("equation")}
            >
              <span className="side-bullet">•</span>
              <span>Решить уравнение</span>
            </button>
          </div>
        )}
      </div>

      <div className="sidebar-divider" />

      <div className="sidebar-section">
        <button
          type="button"
          className="sidebar-group-header sidebar-group-toggle"
          onClick={() => toggleGroup("linear")}
          aria-expanded={openGroups.linear}
        >
          <div className="sidebar-group-title">
            <FiLayers />
            <span>Линейная алгебра</span>
          </div>
          <FiChevronDown className={openGroups.linear ? "chevron-open" : "chevron-closed"} />
        </button>

        {openGroups.linear && (
          <div className="sidebar-group-body">
            <button
              className={activeCalculator === "linear-system" ? "side-link active" : "side-link"}
              onClick={() => setActiveCalculator("linear-system")}
            >
              <span className="side-bullet">•</span>
              <span>Системы линейных уравнений</span>
            </button>
          </div>
        )}
      </div>

      <div className="sidebar-divider" />

      <div className="sidebar-section">
        <button
          type="button"
          className="sidebar-group-header sidebar-group-toggle"
          onClick={() => toggleGroup("optimization")}
          aria-expanded={openGroups.optimization}
        >
          <div className="sidebar-group-title">
            <FiTrendingUp />
            <span>Оптимизация</span>
          </div>
          <FiChevronDown className={openGroups.optimization ? "chevron-open" : "chevron-closed"} />
        </button>

        {openGroups.optimization && (
          <div className="sidebar-group-body">
            <button
              className={activeCalculator === "simplex" ? "side-link active" : "side-link"}
              onClick={() => setActiveCalculator("simplex")}
            >
              <span className="side-bullet">•</span>
              <span>Симплекс-метод</span>
            </button>

            <button
              className={
                activeCalculator === "simplex-algebraic"
                  ? "side-link active"
                  : "side-link"
              }
              onClick={() => setActiveCalculator("simplex-algebraic")}
            >
              <span className="side-bullet">•</span>
              <span>Симплекс-метод (алгебраические преобразования)</span>
            </button>

            <button
              className={activeCalculator === "transport" ? "side-link active" : "side-link"}
              onClick={() => setActiveCalculator("transport")}
            >
              <span className="side-bullet">•</span>
              <span>Транспортная задача</span>
            </button>
          </div>
        )}
      </div>

      <div className="sidebar-divider" />

      <div className="sidebar-section">
        <button
          type="button"
          className="sidebar-group-header sidebar-group-toggle"
          onClick={() => toggleGroup("statistics")}
          aria-expanded={openGroups.statistics}
        >
          <div className="sidebar-group-title">
            <FiBarChart2 />
            <span>Статистика</span>
          </div>
          <FiChevronDown className={openGroups.statistics ? "chevron-open" : "chevron-closed"} />
        </button>

        {openGroups.statistics && (
          <div className="sidebar-group-body">
            <button className="side-link">
              <FiCircle className="side-icon" />
              <span>Среднее значение</span>
            </button>

            <button className="side-link">
              <FiCircle className="side-icon" />
              <span>Медиана</span>
            </button>

            <button className="side-link">
              <FiCircle className="side-icon" />
              <span>Мода</span>
            </button>

            <button className="side-link">
              <FiCircle className="side-icon" />
              <span>Корреляция</span>
              <span className="badge">Продвинуто</span>
            </button>
          </div>
        )}
      </div>
    </aside>
  );
}
