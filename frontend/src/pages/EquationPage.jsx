import { useRef, useState } from "react";
import { FiCheckCircle, FiChevronDown, FiCopy, FiRefreshCcw, FiX } from "react-icons/fi";
import { PiMathOperationsBold } from "react-icons/pi";
import Breadcrumbs from "../components/Breadcrumbs";
import MathFormula from "../components/MathFormula";
import StepsCard from "../components/StepsCard";
import { downloadEquationDocx, solveEquation } from "../services/api";

export default function EquationPage() {
  const [equation, setEquation] = useState("2x + 3 = 7");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [templatesOpen, setTemplatesOpen] = useState(false);
  const inputRef = useRef(null);

  const templates = [
    { label: "Дробь", preview: "1/2", insert: "(1/2)", cursor: 2 },
    { label: "Смешанное", preview: "16(1/3)", insert: "16(1/3)", cursor: 0 },
    { label: "Степень", preview: "x^2", insert: "^2", cursor: 0 },
    { label: "Степенное", preview: "3ˣ·4ˣ", insert: "3^x*4^x=144^(x-2)", cursor: 0 },
    { label: "Корень", preview: "√", insert: "sqrt()", cursor: -1 },
    { label: "Логарифм", preview: "log₄( )", insert: "log_4()", cursor: -1 },
    { label: "Скобки", preview: "( )", insert: "()", cursor: -1 },
    { label: "Модуль", preview: "|x|", insert: "Abs()", cursor: -1 },
    { label: "Интеграл", preview: "∫", insert: "integrate(, x)", cursor: -4 },
  ];

  function fillDemo() {
    setEquation("x^2 - 5x + 6 = 0");
    setResult(null);
    setError("");
  }

  function payload() {
    return {
      equation,
      variable: null,
    };
  }

  async function handleSolve() {
    if (!equation.trim()) {
      setError("Введите уравнение.");
      setResult(null);
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      setResult(await solveEquation(payload()));
    } catch (err) {
      setError(err?.response?.data?.detail || "Не удалось решить уравнение.");
    } finally {
      setLoading(false);
    }
  }

  function handleClear() {
    setEquation("");
    setResult(null);
    setError("");
  }

  function insertTemplate(template) {
    const input = inputRef.current;
    const start = input?.selectionStart ?? equation.length;
    const end = input?.selectionEnd ?? equation.length;
    const nextEquation = `${equation.slice(0, start)}${template.insert}${equation.slice(end)}`;
    const nextCursor = start + template.insert.length + (template.cursor || 0);

    setEquation(nextEquation);
    setResult(null);
    setError("");

    window.setTimeout(() => {
      inputRef.current?.focus();
      inputRef.current?.setSelectionRange(nextCursor, nextCursor);
    }, 0);
  }

  async function handleDownloadDocx() {
    setDownloading(true);
    try {
      await downloadEquationDocx(payload());
    } finally {
      setDownloading(false);
    }
  }

  function copyResult() {
    if (result?.result) {
      navigator.clipboard.writeText(result.result);
    }
  }

  return (
    <>
      <Breadcrumbs current="Решить уравнение" />

      <div className="workspace-grid equation-workspace">
        <div className="workspace-main">
          <section className="panel-card hero-card">
            <div className="hero-header">
              <div className="hero-title-wrap">
                <div className="hero-icon">
                  <PiMathOperationsBold />
                </div>
                <div>
                  <h1 className="page-title">Решить уравнение</h1>
                  <p className="page-subtitle">
                    Перенос слагаемых, преобразование и нахождение корней.
                  </p>
                </div>
              </div>

              <div className="hero-actions">
                <div className="hero-tag">Алгебра</div>
                <button className="secondary-btn" onClick={fillDemo}>
                  Подставить пример
                </button>
              </div>
            </div>

            <div className="field-block">
              <label className="field-label">Введите уравнение</label>
              <div className="input-wrap">
                <input
                  ref={inputRef}
                  type="text"
                  className="expression-input"
                  value={equation}
                  onChange={(event) => setEquation(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      handleSolve();
                    }
                  }}
                  placeholder="2x + 3 = 7"
                />
                <button
                  type="button"
                  className="input-clear-btn"
                  onClick={() => setEquation("")}
                  aria-label="Очистить поле"
                >
                  <FiX />
                </button>
              </div>

              <div className="under-input-hint">
                Примеры:
                <span className="mini-chip">2x + 3 = 7</span>
                <span className="mini-chip">x^2 - 5x + 6 = 0</span>
              </div>

              <div className="math-template-box">
                <button
                  type="button"
                  className="template-toggle-btn"
                  onClick={() => setTemplatesOpen((current) => !current)}
                  aria-expanded={templatesOpen}
                >
                  <span>Вставить шаблон</span>
                  <FiChevronDown className={templatesOpen ? "rotated" : ""} />
                </button>

                {templatesOpen && (
                  <div className="math-template-grid">
                    {templates.map((template) => (
                      <button
                        key={template.label}
                        type="button"
                        className="math-template-btn"
                        onClick={() => insertTemplate(template)}
                      >
                        <strong>{template.preview}</strong>
                        <span>{template.label}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="actions-block">
              <button className="primary-btn full-blue" onClick={handleSolve} disabled={loading}>
                <PiMathOperationsBold />
                <span>{loading ? "Решаем..." : "Решить уравнение"}</span>
              </button>

              <button className="ghost-note-btn" onClick={handleClear} disabled={loading}>
                <FiRefreshCcw />
                <span>Очистить</span>
              </button>
            </div>
          </section>

          <section className={`panel-card result-card ${error ? "error" : "success"}`}>
            <div className="result-head">
              <div className="result-title-row">
                {!error && <FiCheckCircle className="result-status-icon" />}
                <h3 className="card-title">{error ? "Ошибка" : "Ответ:"}</h3>
              </div>

              {!error && result?.result && (
                <button className="copy-btn" onClick={copyResult}>
                  <FiCopy />
                  <span>Копировать</span>
                </button>
              )}
            </div>

            {error ? (
              <div className="result-text error-text">{error}</div>
            ) : result?.result_latex ? (
              <MathFormula latex={result.result_latex} />
            ) : (
              <div className="result-text muted">Здесь появится ответ</div>
            )}
          </section>

          {result && (
            <button
              className="secondary-btn download-docx-btn"
              onClick={handleDownloadDocx}
              disabled={downloading}
            >
              {downloading ? "Формируем файл..." : "Скачать Word"}
            </button>
          )}

          <StepsCard steps={result?.steps || []} />
        </div>

        <aside className="right-panel">
          <section className="info-card tip-card">
            <h3 className="card-title">Подсказка</h3>
            <p>
              Можно вводить линейные и квадратные уравнения. Для степени используйте
              символ <strong>^</strong>.
            </p>
            <p>
              Логарифм записывайте так: <strong>log_4(x+3)</strong>, где 4 — основание,
              а выражение в скобках — то, что стоит под логарифмом.
            </p>
            <p>
              Степенные уравнения можно вводить через <strong>^</strong>, например
              <strong> 3^x*4^x=144^(x-2)</strong>.
            </p>
            <p>
              Корень записывайте через <strong>sqrt(...)</strong>, например
              <strong> sqrt(5x-1)=5-x</strong>.
            </p>
            <div className="mini-chip">x^2 - 5x + 6 = 0</div>
            <div className="mini-chip">log_4(x+3)=log_4(4x-15)</div>
            <div className="mini-chip">3^x*4^x=144^(x-2)</div>
            <div className="mini-chip">sqrt(5x-1)=5-x</div>
          </section>
        </aside>
      </div>
    </>
  );
}
