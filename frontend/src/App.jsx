import { useState } from "react";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import SimplifyPage from "./pages/SimplifyPage";
import EquationPage from "./pages/EquationPage";
import SimplexPage from "./pages/SimplexPage";
import SimplexAlgebraicPage from "./pages/SimplexAlgebraicPage";
import TransportPage from "./pages/TransportPage";
import LinearSystemPage from "./pages/LinearSystemPage";

export default function App() {
  const [activeCalculator, setActiveCalculator] = useState("simplify");

  function selectCalculator(calculator) {
    setActiveCalculator(calculator);

    if (window.innerWidth <= 1024) {
      window.requestAnimationFrame(() => {
        document.querySelector(".content-area")?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      });
    }
  }

  return (
    <div className="app-shell">
      <Header
        activeCalculator={activeCalculator}
        setActiveCalculator={selectCalculator}
      />

      <div className="app-body">
        <Sidebar
          activeCalculator={activeCalculator}
          setActiveCalculator={selectCalculator}
        />

        <main className="content-area">
          {activeCalculator === "simplify" && <SimplifyPage />}
          {activeCalculator === "equation" && <EquationPage />}
          {activeCalculator === "linear-system" && <LinearSystemPage />}
          {activeCalculator === "simplex" && <SimplexPage />}
          {activeCalculator === "simplex-algebraic" && <SimplexAlgebraicPage />}
          {activeCalculator === "transport" && <TransportPage />}
        </main>
      </div>
    </div>
  );
}
