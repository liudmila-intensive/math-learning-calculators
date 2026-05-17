import { HiOutlineCalculator } from "react-icons/hi";
import { FiSun } from "react-icons/fi";

function sectionForCalculator(activeCalculator) {
  if (["linear-system"].includes(activeCalculator)) {
    return "linear";
  }
  if (["simplex", "simplex-algebraic", "transport"].includes(activeCalculator)) {
    return "optimization";
  }
  return "algebra";
}

export default function Header({ activeCalculator, setActiveCalculator }) {
  const activeSection = sectionForCalculator(activeCalculator);

  return (
    <header className="topbar">
      <div className="brand">
        <div className="brand-icon">
          <HiOutlineCalculator />
        </div>

        <div>
          <div className="brand-title">Учебные калькуляторы</div>
          <div className="brand-subtitle">Математика для школьников</div>
        </div>
      </div>

      <nav className="topnav">
        <button
          className={activeSection === "algebra" ? "topnav-link active" : "topnav-link"}
          onClick={() => setActiveCalculator("simplify")}
        >
          Алгебра
        </button>
        <button
          className={activeSection === "linear" ? "topnav-link active" : "topnav-link"}
          onClick={() => setActiveCalculator("linear-system")}
        >
          Линейная алгебра
        </button>
        <button
          className={
            activeSection === "optimization" ? "topnav-link active" : "topnav-link"
          }
          onClick={() => setActiveCalculator("simplex")}
        >
          Оптимизация
        </button>
        <button className="topnav-link">Статистика</button>
      </nav>

      <button className="topbar-icon-btn" aria-label="Тема">
        <FiSun />
      </button>
    </header>
  );
}
